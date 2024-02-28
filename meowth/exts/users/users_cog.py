from meowth import Cog, command
from meowth.utils import get_match
import re

import discord
from discord.ext import commands
import pytz
from pytz import timezone
from datetime import datetime, timedelta
import time
import asyncio
import typing

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
    
    @classmethod
    async def from_ign(cls, bot, ign):
        users_table = bot.dbi.table('users')
        query = users_table.query('id')
        query.where(ign=ign)
        user_id = await query.get_value()
        if user_id:
            return cls.from_id(bot, user_id)
        else:
            return None
    
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

    async def ign(self):
        data = self._data
        data.select('ign')
        ign = await data.get_value()
        return ign

    async def friendcode(self):
        data = self._data
        data.select('friendcode')
        fc = await data.get_value()
        return fc
    
    async def set_team(self, team_id):
        update = self._update
        update.values(team=team_id)
        await update.commit()
    
    async def set_pokebattler(self, pb_id):
        update = self._update
        update.values(pokebattler=pb_id)
        await update.commit()
    
    async def party(self):
        data = self._data
        data.select('party')
        party = await data.get_value()
        if not party:
            team = await self.team()
            if not team:
                party = [0,0,0,1]
            else:
                party = [0, 0, 0, 0]
                party[team-1] = 1
        return party

    async def default_party(self):
        data = self._data
        data.select('default_party')
        party = await data.get_value()
        if not party:
            team = await self.team()
            if not team:
                party = [0,0,0,1]
            else:
                party = [0, 0, 0, 0]
                party[team-1] = 1
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
    
    async def clear_party(self, clear_time):
        party = await self.default_party()
        sleeptime = clear_time - time.time()
        await asyncio.sleep(sleeptime)
        await self.set_party(party)
        
    
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
        if sum((mystic, instinct, valor, unknown)) == 0:
            return await self.party()
        return [mystic, instinct, valor, unknown]


    async def rsvp(self, raid_id, status, bosses: list=[], party=[0,0,0,1]):
        estimator = await self.raid_estimator(raid_id)
        d = {
            'user_id': self.user.id,
            'raid_id': raid_id,
            'status': status,
            'estimator': estimator,
            'bosses': bosses,
            'party': party,
            'invites': []
        }
        rsvp_table = self.bot.dbi.table('raid_rsvp')
        current_rsvp = rsvp_table.query().where(user_id=self.user.id, raid_id=raid_id)
        current_rsvp = await current_rsvp.get()
        if current_rsvp:
            old_d = dict(current_rsvp[0])
            d['invites'] = old_d.get('invites', [])
            if old_d == d:
                return
        insert = rsvp_table.insert()
        insert.row(**d)
        await insert.commit(do_update=True)
        raid_table = self.bot.dbi.table('raids')
        query = raid_table.query('tz')
        query.where(id=raid_id)
        zone = await query.get_value()
        tz = timezone(zone)
        now_dt = datetime.now(tz=tz)
        midnight_dt = now_dt + timedelta(days=1)
        midnight_dt = midnight_dt.replace(hour=0, minute=0, second=0)
        midnight_dt = midnight_dt.astimezone(pytz.utc)
        stamp = midnight_dt.timestamp()
        if hasattr(self, 'party_expire_task'):
            self.party_expire_task.cancel()
        self.party_expire_task = self.bot.loop.create_task(self.clear_party(stamp))
    
    async def raid_invite(self, raid_id, invitee_id):
        rsvp_table = self.bot.dbi.table('raid_rsvp')
        current_rsvp = rsvp_table.query().where(user_id=self.user.id, raid_id=raid_id)
        current_rsvp = await current_rsvp.get()
        if current_rsvp:
            old_d = dict(current_rsvp[0])
        else:
            return
        old_invites = old_d.get('invites', [])
        if invitee_id in old_invites:
            return
        old_invites.append(invitee_id)
        insert = rsvp_table.insert()
        insert.row(**old_d)
        await insert.commit(do_update=True)
    
    async def train_rsvp(self, train, party=[0,0,0,1]):
        d = {
            'user_id': self.user.id,
            'train_id': train.id,
            'party': party
        }
        train_rsvp_table = self.bot.dbi.table('train_rsvp')
        insert = train_rsvp_table.insert
        insert.row(**d)
        await insert.commit(do_update=True)
        if train.current_raid:
            raid_id = train.current_raid.id
            rsvp_table = self.bot.dbi.table('raid_rsvp')
            current_rsvp = rsvp_table.query().where(user_id=self.user.id, raid_id=raid_id)
            current_rsvp = await current_rsvp.get()
            if current_rsvp:
                old_d = dict(current_rsvp[0])
                old_party = old_d.get('party')
                if old_party != party:
                    old_d['party'] = party
                    insert = rsvp_table.insert
                    insert.row(**old_d)
                    await insert.commit(do_update=True)
                    raid_table = self.bot.dbi.table('raids')
                    query = raid_table.query('tz')
                    query.where(id=raid_id)
                    zone = await query.get_value()
                    tz = timezone(zone)
                    now_dt = datetime.now(tz=tz)
                    midnight_dt = now_dt + timedelta(days=1)
                    midnight_dt = midnight_dt.replace(hour=0, minute=0, second=0)
                    midnight_dt = midnight_dt.astimezone(pytz.utc)
                    stamp = midnight_dt.timestamp()
                    if hasattr(self, 'party_expire_task'):
                        self.party_expire_task.cancel()
                    self.party_expire_task = self.bot.loop.create_task(self.clear_party(stamp))
    
    async def meetup_rsvp(self, meetup, status, party=[0,0,0,1]):
        d = {
            'user_id': self.user.id,
            'meetup_id': meetup.id,
            'status': status,
            'party': party
        }
        meetup_rsvp_table = self.bot.dbi.table('meetup_rsvp')
        insert = meetup_rsvp_table.insert
        insert.row(**d)
        await insert.commit(do_update=True)
        meetup_table = self.bot.dbi.table('meetups')
        query = meetup_table.query('tz')
        query.where(id=meetup.id)
        zone = await query.get_value()
        tz = timezone(zone)
        now_dt = datetime.now(tz=tz)
        midnight_dt = now_dt + timedelta(days=1)
        midnight_dt = midnight_dt.replace(hour=0, minute=0, second=0)
        midnight_dt = midnight_dt.astimezone(pytz.utc)
        stamp = midnight_dt.timestamp()
        if hasattr(self, 'party_expire_task'):
            self.party_expire_task.cancel()
        self.party_expire_task = self.bot.loop.create_task(self.clear_party(stamp))
    
    async def leave_train(self, train):
        train_rsvp_table = self.bot.dbi.table('train_rsvp')
        query = train_rsvp_table.query
        query.where(user_id=self.user.id, train_id=train.id)
        await query.delete()

    async def cancel_rsvp(self, raid_id):
        rsvp_table = self.bot.dbi.table('raid_rsvp')
        current_rsvp = rsvp_table.query().where(user_id=self.user.id, raid_id=raid_id)
        await current_rsvp.delete()
    
    async def cancel_mrsvp(self, meetup):
        meetup_rsvp_table = self.bot.dbi.table('meetup_rsvp')
        query = meetup_rsvp_table.query
        query.where(user_id=self.user.id, meetup_id=meetup)
        await query.delete()
    
    async def cancel_train(self):
        train_rsvp_table = self.bot.dbi.table('train_rsvp')
        query = train_rsvp_table.query.where(user_id=self.user.id)
        await query.delete()
    
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

    @classmethod
    async def convert(cls, ctx, arg):
        converter = commands.MemberConverter()
        member = await converter.convert(ctx, arg)
        user_id = member.id
        return cls.from_id(ctx.bot, user_id)
        

        


class Team:

    def __init__(self, bot, guild_id, team_id):
        self.bot = bot
        self.guild = guild_id
        self.id = team_id
        
    async def role(self):
        settings_table = self.bot.dbi.table('team_roles')
        query = settings_table.query()
        if self.id == 1:
            query.select('blue_role_id')
        elif self.id == 2:
            query.select('yellow_role_id')
        elif self.id == 3:
            query.select('red_role_id')
        query.where(guild_id=self.guild)
        result = await query.get_value()
        if not result:
            return None
        guild = self.bot.get_guild(self.guild)
        role = discord.utils.get(guild.roles, id=result)
        if role:
            return role
        else:
            return None
    
    async def emoji(self):
        team_table = self.bot.dbi.table('teams')
        query = team_table.query('emoji')
        query.where(team_id=self.id)
        result = await query.get_value()
        emoji = self.bot.get_emoji(result)
        return emoji

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
            return
        
        return cls(ctx.bot, ctx.guild.id, team_id)

        

class Users(Cog):

    @Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            if ctx.command.name == 'team':
                return await ctx.send('Contact appropriate server personnel if you need to be manually added to a team role.')

    @command()
    @users_checks.users_enabled()
    async def team(self, ctx, *, chosen_team: Team):
        """Set your Pokemon Go team."""

        if chosen_team is None:
            return await ctx.send("Team not found!")
        meowthuser = MeowthUser(ctx.bot, ctx.author)
        data = await meowthuser._data.get()
        if len(data) == 0:
            insert = meowthuser._insert
            d = {
                'id': ctx.author.id,
                'team': chosen_team.id
            }
            insert.row(**d)
            await insert.commit()
        else:
            data = data[0]
            old_team_id = data.get('team')
            if old_team_id:
                old_team = Team(ctx.bot, ctx.guild.id, old_team_id)
                old_role = await old_team.role()
                if old_role:
                    try:
                        await ctx.author.remove_roles(old_role)
                    except discord.Forbidden:
                        await ctx.error("Missing permissions")
            update = meowthuser._update
            update.values(team=chosen_team.id)
            await update.commit()
        role = await chosen_team.role()
        if role:
            try:
                await ctx.author.add_roles(role)
                await ctx.success("Adding role succeeded")
            except discord.Forbidden:
                await ctx.error("Missing permissions")
            except discord.HTTPException:
                await ctx.error("Adding roles failed")
    
    @command()
    @users_checks.users_enabled()
    async def pokebattler(self, ctx, pb_id: int):
        """Set your Pokebattler ID."""

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
    
    @command()
    @users_checks.users_enabled()
    async def ign(self, ctx, ign):
        """Set your in-game name."""

        user_table = ctx.bot.dbi.table('users')
        meowthuser = MeowthUser(ctx.bot, ctx.author)
        data = await meowthuser._data.get()
        if len(data) == 0:
            insert = meowthuser._insert
            d = {'id': ctx.author.id, 'ign': ign}
            insert.row(**d)
            await insert.commit()
        else:
            update = meowthuser._update
            update.values(ign=ign)
            await update.commit()
        return await ctx.send(f'In-game name set to {ign}')

    @command(aliases=['friendcode', 'fc', 'tc'])
    @users_checks.users_enabled()
    async def trainercode(self, ctx, *, user_or_code):
        """Set your in-game trainer code or look up another user's trainer code.
        To look up a trainer, user_or_code should be a username or mention.
        To set your trainer code, user_or_code should be a 12-digit number.
        """

        try:
            meowthuser = await MeowthUser.convert(ctx, user_or_code)
        except:
            meowthuser = None
        if meowthuser:
            fc = await meowthuser.friendcode()
            if not fc:
                return await ctx.error('Trainer code not found')
            await ctx.send(f'Trainer code for {meowthuser.user.display_name}:')
            return await ctx.send(fc)
        user_or_code = user_or_code.replace(' ', '')
        if not user_or_code.isdigit() or len(user_or_code) != 12:
            return await ctx.error('Invalid friend code')


        user_table = ctx.bot.dbi.table('users')
        meowthuser = MeowthUser(ctx.bot, ctx.author)
        data = await meowthuser._data.get()
        if len(data) == 0:
            insert = meowthuser._insert
            d = {'id': ctx.author.id, 'friendcode': user_or_code}
            insert.row(**d)
            await insert.commit()
        else:
            update = meowthuser._update
            update.values(friendcode=user_or_code)
            await update.commit()
        return await ctx.send(f'Friend code set to {user_or_code}')

    @command()
    @users_checks.users_enabled()
    async def whois(self, ctx, ign):
        """Lookup player by in-game name."""

        user_table = ctx.bot.dbi.table('users')
        query = user_table.query('ign')
        ign_list = await query.get_values()
        ign_list = [x for x in ign_list if x]
        if not ign_list:
            return await ctx.send(f"No match for {ign}")
        match = get_match(ign_list, ign)[0]
        if match:
            meowthuser = await MeowthUser.from_ign(ctx.bot, match)
            member = ctx.guild.get_member(meowthuser.user.id)
            if not member:
                member = await ctx.guild.fetch_member(meowthuser.user.id)
            if member:
                name = member.display_name
            else:
                name = str(meowthuser.user)
            return await ctx.send(f'Closest match for {ign}: {name}')
        else:
            return await ctx.send(f"No match for {ign}")
    
    @command()
    @users_checks.users_enabled()
    async def iam(self, ctx, roles: commands.Greedy[discord.Role]):
        table = ctx.bot.dbi.table('custom_roles')
        if not roles:
            query = table.query
            query.where(guild_id=ctx.guild.id)
            records = await query.get()
            custom_roles = 'This server has the following custom roles: '
            for row in records:
                role_id = row['role_id']
                role = discord.utils.get(ctx.guild.roles, id=role_id)
                if role:
                    custom_roles = custom_roles + '`' + role.name + '`, '
            custom_roles = custom_roles[:-2] + '.'
            return await ctx.send(custom_roles)
        valid_roles = []
        for role in roles:
            query = table.query
            query.where(guild_id=ctx.guild.id)
            query.where(role_id=role.id)
            data = await query.get()
            if data:
                valid_roles.append(role)
        if valid_roles:
            role_names = [x.name for x in valid_roles]
            await ctx.author.add_roles(*valid_roles)
            return await ctx.success('Roles Added', details="\n".join(role_names))
        return await ctx.error('No valid roles found')
    
    @command()
    @users_checks.users_enabled()
    async def iamnot(self, ctx, roles: commands.Greedy[discord.Role]):
        if not roles:
            return await ctx.error('No roles found')
        valid_roles = []
        table = ctx.bot.dbi.table('custom_roles')
        for role in roles:
            query = table.query
            query.where(guild_id=ctx.guild.id)
            query.where(role_id=role.id)
            data = await query.get()
            if data:
                valid_roles.append(role)
        if valid_roles:
            role_names = [x.name for x in valid_roles]
            await ctx.author.remove_roles(*valid_roles)
            return await ctx.success('Roles Removed', details="\n".join(role_names))
        return await ctx.error('No valid roles found')
    
    @command(name='party')
    @users_checks.users_enabled()
    async def default_party(self, ctx, total: typing.Optional[int]=None, *teamcounts):
        """Set your default raiding party composition.

        **Arguments**
        *total (optional):* Number of trainers you are bringing. Defaults to
            your last RSVP total, or 1.
        
        *teamcounts (optional):* Counts of each team in your group. Format:
            `3m 2v 1i` means 3 Mystic, 2 Valor, 1 Instinct.
        
        Meowth resets your raid party to this value
        at midnight local time."""

        meowthuser = MeowthUser(ctx.bot, ctx.author)

        if total or teamcounts:
            party = await meowthuser.party_list(total, *teamcounts)
        else:
            party = await meowthuser.party()
        
        data = await meowthuser._data.get()
        if len(data) == 0:
            insert = meowthuser._insert
            d = {'id': ctx.author.id, 'default_party': party, 'party': party}
            insert.row(**d)
            await insert.commit()
        else:
            update = meowthuser._update
            update.values(default_party=party, party=party)
            await update.commit()
        table = ctx.bot.dbi.table('raid_rsvp')
        update = table.update
        try:
            update.where(user_id=ctx.author.id)
            update.values(party=party)
            await update.commit()
        except:
            pass
        party_str = f"{ctx.bot.config.team_emoji['mystic']}: {party[0]} | "
        party_str += f"{ctx.bot.config.team_emoji['instinct']}: {party[1]} | "
        party_str += f"{ctx.bot.config.team_emoji['valor']}: {party[2]} | "
        party_str += f"{ctx.bot.config.team_emoji['unknown']}: {party[3]}"
        return await ctx.send(f'Default party set to {party_str}')
        

        


