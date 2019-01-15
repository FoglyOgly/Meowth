from meowth import Cog, command
from meowth.utils import get_match

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
    
    async def interested_list(self):
        data = self._data
        data.select('interested_list')
        intlist = await data.get_value()
        if not intlist:
            return []
        return intlist
    
    async def coming(self):
        data = self._data
        data.select('coming')
        coming = await data.get_value()
        return coming
    
    async def here(self):
        data = self._data
        data.select('here')
        here = await data.get_value()
        return here
    
    async def has_rsvp(self, raid_id):
        intlist = await self.interested_list()
        if raid_id in intlist:
            return True
        coming = await self.coming()
        if raid_id == coming:
            return True
        here = await self.here()
        if raid_id == here:
            return True
        lobby = await self.lobby()
        if raid_id == lobby:
            return True
        return False
    
    async def lobby(self):
        data = self._data
        data.select('lobby')
        lobby = await data.get_value()
        return lobby
    
    async def total(self):
        data = self._data
        data.select('total')
        total = await data.get_value()
        if total is None:
            return 1
        return total
    
    async def bluecount(self):
        data = self._data
        data.select('bluecount')
        bluecount = await data.get_value()
        if bluecount is None:
            return 0
        return bluecount
    
    async def yellowcount(self):
        data = self._data
        data.select('yellowcount')
        yellowcount = await data.get_value()
        if yellowcount is None:
            return 0
        return yellowcount

    async def redcount(self):
        data = self._data
        data.select('redcount')
        redcount = await data.get_value()
        if redcount is None:
            return 0
        return redcount
    
    async def unknowncount(self):
        data = self._data
        data.select('unknowncount')
        unknowncount = await data.get_value()
        if unknowncount is None:
            return 0
        return unknowncount
    
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
        total = await self.total()
        bluecount = await self.bluecount()
        yellowcount = await self.yellowcount()
        redcount = await self.redcount()
        unknowncount = await self.unknowncount()
        if not any((bluecount, yellowcount, redcount)):
            team = await self.team()
            if team == 1:
                bluecount = total
            elif team == 2:
                yellowcount = total
            elif team == 3:
                redcount = total
        unknowncount = total - sum((bluecount, yellowcount, redcount))
        d = {
            'total': total,
            'bluecount': bluecount,
            'yellowcount': yellowcount,
            'redcount': redcount,
            'unknowncount': unknowncount
        }
        return d
    
    async def set_party(self, total, bluecount=0, yellowcount=0, redcount=0):
        update = self._update
        unknowncount = total - sum((bluecount, yellowcount, redcount))
        d = {
            'total': total,
            'bluecount': bluecount,
            'yellowcount': yellowcount,
            'redcount': redcount,
            'unknowncount': unknowncount
        }
        update.values(**d)
        await update.commit()
    
    async def party_list(self, total=0, *teamcounts):
        if not teamcounts:
            if not total:
                party = await self.party()
                total = party['total']
                bluecount = party['bluecount']
                yellowcount = party['yellowcount']
                redcount = party['redcount']
                unknowncount = party['unknowncount']
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
        return [mystic, instinct, valor, unknown]


    async def rsvp(self, raid_id, status, bosses: list=None, total: int=1,
        bluecount: int=0, yellowcount: int=0, redcount: int=0, unknowncount: int=0):
        data = await self._data.get()
        if not data:
            upsert = self._insert
            action = "insert"
            data = {}
        else:
            data = data[0]
            upsert = self._update
            action = "update"
        d = {
            'total': total,
            'bluecount': bluecount,
            'yellowcount': yellowcount,
            'redcount': redcount,
            'unknowncount': unknowncount
        }
        intlist = data.get('interested_list', [])
        oldcoming = data.get('coming')
        oldhere = data.get('here')
        oldlobby = data.get('lobby')
        if status == 'cancel':
            if raid_id in intlist:
                intlist.remove(raid_id)
                newcoming = oldcoming
                newhere = oldhere
                newlobby = oldlobby
            elif raid_id == oldcoming:
                newcoming = None
                newhere = oldhere
                newlobby = oldlobby
            elif raid_id == oldhere:
                newhere = None
                newcoming = oldcoming
                newlobby = oldlobby
            elif raid_id == oldlobby:
                newlobby = None
                newhere = oldhere
                newcoming = oldcoming
        elif status == 'maybe':
            if bosses:
                d['bosses'] = bosses
            if raid_id not in intlist:
                intlist.append(raid_id)
            if raid_id == oldcoming:
                newcoming = None
                newhere = oldhere
                newlobby = oldlobby
            elif raid_id == oldhere:
                newhere = None
                newcoming = oldcoming
                newlobby = oldlobby
            elif raid_id == oldlobby:
                newlobby = None
                newcoming = oldcoming
                newhere = oldhere
            else:
                newcoming = oldcoming
                newhere = oldhere
                newlobby = oldlobby
        elif status == 'coming':
            if raid_id in intlist:
                intlist.remove(raid_id)
            newcoming = raid_id
            newhere = None
            newlobby = None
        elif status == 'here':
            if raid_id in intlist:
                intlist.remove(raid_id)
            newhere = raid_id
            newcoming = None
            newlobby = None
        elif status == 'lobby':
            if raid_id in intlist:
                intlist.remove(raid_id)
            newhere = None
            newcoming = None
            newlobby = raid_id
        d['interested_list'] = intlist
        d['coming'] = newcoming
        d['here'] = newhere
        d['lobby'] = newlobby
        if action == "insert":
            d['id'] = self.user.id
            upsert.row(**d)
        elif action == "update":
            upsert.values(**d)
        await upsert.commit()
        


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



