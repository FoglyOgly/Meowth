from meowth import Cog, command
from meowth.utils import get_match
import re

import discord

from . import users_checks

class MeowthUser:

    def __init__(self, bot, user):
        self.bot = bot
        self.user = user

    @property
    def _data(self):
        users_table = self.bot.dbi.table('users')
        query = users_table.query()
        query.where(id=self.user.id)
        return query
    
    @property
    def _insert(self):
        users_table = self.bot.dbi.table('users')
        insert = users_table.insert()
        return insert
    
    @property
    def _update(self):
        users_table = self.bot.dbi.table('users')
        update = users_table.update()
        update.where(id=self.user.id)
        return update

    @classmethod
    def from_id(cls, bot, user_id):
        user = bot.get_user(user_id)
        return cls(bot, user)
    
    async def team(self):
        data = self._data
        data.select('team')
        team = await data.get_value()
        return team
    
    async def pokebattler(self):
        data = self._data
        data.select('pokebattler')
        pbid = await data.get_value()
        return pbid
    
    async def silph(self):
        data = self._data
        data.select('silph')
        silphid = await data.get_value()
        return silphid
    
    async def set_team(self, team_id):
        update = self._update
        update.values(team=team_id)
        await update.commit()
    
    async def set_pokebattler(self, pb_id):
        update = self._update
        update.values(pokebattler=pb_id)
        await update.commit()
    
    async def set_silph(self, silph):
        update = self._update
        update.values(silph=silph)
        await update.commit()
    
    async def party(self):
        data = self._data
        data.select('party')
        party = await data.get_value()
        if not party:
            party = [0,0,0,1]
        return party
    
    async def set_party(self, party: list = [0,0,0,1]):
        data = await self._data.get()
        if data:
            update = self._update
            update.values(party=party)
            await update.commit()
        else:
            insert = self._insert
            insert.row(id=self.user.id, party=party)
            await insert.commit()
    
    async def party_list(self, total=0, *teamcounts):
        if not teamcounts:
            if not total:
                return await self.party()
            else:
                team = await self.team()
                if not team:
                    unknowncount = total
                    bluecount = yellowcount = redcount = 0
                elif team == 1:
                    bluecount = total
                    yellowcount = redcount = unknowncount = 0
                elif team == 2:
                    yellowcount = total
                    bluecount = redcount = unknowncount = 0
                elif team == 3:
                    redcount = total
                    bluecount = yellowcount = unknowncount = 0
            return [bluecount, yellowcount, redcount, unknowncount]
        else:
            mystic = 0
            instinct = 0
            valor = 0
            unknown = 0
            mystic_aliases = ['mystic', 'blue', 'm', 'b']
            instinct_aliases = ['instinct', 'yellow', 'i', 'y']
            valor_aliases = ['valor', 'red', 'v', 'r']
            unknown_aliases = ['unknown', 'grey', 'gray', 'u', 'g']
            regx = re.compile('([a-zA-Z]+)([0-9]+)|([0-9]+)([a-zA-Z]+)')
            for count in teamcounts:
                match = regx.match(count)
                if match:
                    match = regx.match(count).groups()
                    str_match = match[0] or match[3]
                    int_match = match[1] or match[2]
                    if str_match in mystic_aliases:
                        mystic += int(int_match)
                    elif str_match in instinct_aliases:
                        instinct += int(int_match)
                    elif str_match in valor_aliases:
                        valor += int(int_match)
                    elif str_match in unknown_aliases:
                        unknown += int(int_match)
            if total:
                if sum((mystic, instinct, valor, unknown)) > total:
                    total = sum((mystic, instinct, valor, unknown))
                unknown = total - sum((mystic, instinct, valor))
        return [mystic, instinct, valor, unknown]


    async def rsvp(self, raid_id, status, bosses: list=[], party=[0,0,0,1]):
        estimator = await self.raid_estimator(raid_id)
        d = {
            'user_id': self.user.id,
            'raid_id': raid_id,
            'status': status,
            'estimator': estimator,
            'bosses': bosses,
            'party': party
        }
        rsvp_table = self.bot.dbi.table('raid_rsvp')
        current_rsvp = rsvp_table.query().where(user_id=self.user.id, raid_id=raid_id)
        current_rsvp = await current_rsvp.get()
        if current_rsvp:
            old_d = dict(current_rsvp[0])
            if old_d == d:
                return
        insert = rsvp_table.insert()
        insert.row(**d)
        await insert.commit(do_update=True)
    
    async def raid_estimator(self, raid_id):
        rsvp_table = self.bot.dbi.table('raid_rsvp')
        query = rsvp_table.query('estimator')
        query.where(user_id=self.user.id, raid_id=raid_id)
        return await query.get_value()
    
    async def set_estimator(self, raid_id, estimator, est_20):
        rsvp_table = self.bot.dbi.table('raid_rsvp')
        current_rsvp = rsvp_table.query().where(user_id=self.user.id, raid_id=raid_id)
        current_rsvp = await current_rsvp.get()
        if current_rsvp:
            d = dict(current_rsvp[0])
            d['estimator'] = estimator
            total = sum(d['party'])
            d['est_power'] = 1/estimator + (total-1)/est_20
        else:
            party = await self.party()
            total = sum(party)
            est_power = 1/estimator + (total-1)/est_20
            d = {
                'user_id': self.user.id,
                'raid_id': raid_id,
                'estimator': estimator,
                'party': party,
                'est_power': est_power
            }
        insert = rsvp_table.insert()
        insert.row(**d)
        return await insert.commit(do_update=True)
        

        


class Team:

    def __init__(self, bot, guild_id, team_id):
        self.bot = bot
        self.guild = guild_id
        self.id = team_id
        
    async def role(self):
        settings_table = self.bot.dbi.table('TeamSettings')
        query = settings_table.query()
        if self.id == 1:
            query.select('blue_role_id')
        elif self.id == 2:
            query.select('red_role_id')
        elif self.id == 3:
            query.select('yellow_role_id')
        query.where(guild_id=self.guild)
        result = await query.get_value()
        guild = self.bot.get_guild(self.guild)
        role = discord.utils.get(guild.roles, id=result)
        return role
    
    async def emoji(self):
        team_table = self.bot.dbi.table('teams')
        query = team_table.query('emoji')
        query.where(team_id=self.id)
        result = await query.get_value()
        return result

    @classmethod
    async def convert(cls, ctx, argument):
        argument = argument.lower()

        team_names_table = ctx.bot.dbi.table('team_names')
        team_names_query = team_names_table.query.select(
            'team_name')
        team_names = await team_names_query.get_values()
        match = get_match(team_names, argument, score_cutoff=80)[0]
        if match:
            query = team_names_table.query('team_id')
            query.where(team_name=match)
            team_id = await query.get_value()
        else:
            return await ctx.send("Team not found!")
        
        return cls(ctx.bot, ctx.guild.id, team_id)

        

class Users(Cog):

    @command()
    @users_checks.team_not_set()
    async def team(self, ctx, *, chosen_team: Team):
        """Set your Pokemon Go team."""

        role = await chosen_team.role()
        try:
            await ctx.author.add_roles(role)
            await ctx.send("Adding role succeeded")
        except discord.Forbidden:
            await ctx.send("Missing permissions")
        except discord.HTTPException:
            await ctx.send("Adding roles failed")
    
    @command()
    async def pokebattler(self, ctx, pb_id: int):
        """Set your Pokebattler ID."""

        user_table = ctx.bot.dbi.table('users')
        meowthuser = MeowthUser(ctx.bot, ctx.author)
        data = await meowthuser._data.get()
        if len(data) == 0:
            insert = meowthuser._insert
            d = {'id': ctx.author.id, 'pokebattler': pb_id}
            insert.row(**d)
            await insert.commit()
        else:
            update = meowthuser._update
            update.values(pokebattler=pb_id)
            await update.commit()
        return await ctx.send(f'Pokebattler ID set to {pb_id}')



