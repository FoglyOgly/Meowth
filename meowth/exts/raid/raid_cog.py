from meowth import Cog, command, bot, checks
from meowth.exts.map import Gym, ReportChannel, PartialPOI, S2_L10
from meowth.exts.pkmn import Pokemon, Move
from meowth.exts.pkmn.errors import MoveInvalid
from meowth.exts.weather import Weather
from meowth.exts.want import Want
from meowth.exts.users import MeowthUser
from meowth.utils import formatters, snowflake
from meowth.utils.converters import ChannelMessage
from . import raid_info
from . import raid_checks
from .errors import *
from .objects import Raid, RaidBoss, Train

from math import ceil
import discord
from discord.ext import commands
from discord import Embed
import asyncio
import aiohttp
import time
from datetime import datetime
from dateparser import parse
import typing

emoji_letters = ['🇦','🇧','🇨','🇩','🇪','🇫','🇬','🇭','🇮','🇯','🇰','🇱',
    '🇲','🇳','🇴','🇵','🇶','🇷','🇸','🇹','🇺','🇻','🇼','🇽','🇾','🇿'
]

class hatch_converter(commands.Converter):
    async def convert(self, ctx, argument):
        zone = await ctx.tz()
        hatch_dt = parse(argument, settings={'TIMEZONE': zone, 'RETURN_AS_TIMEZONE_AWARE': True})
        return hatch_dt.timestamp()



        

class RaidCog(Cog):
    
    def __init__(self, bot):
        bot.raid_info = raid_info
        self.bot = bot
        self.bot.loop.create_task(self.pickup_raiddata())
        self.bot.loop.create_task(self.pickup_traindata())
        self.bot.loop.create_task(self.add_listeners())
    
    async def add_listeners(self):
        if self.bot.dbi.raid_listener:
            await self.bot.dbi.pool.release(self.bot.dbi.raid_listener)
        self.bot.dbi.raid_listener = await self.bot.dbi.pool.acquire()
        rsvp_listener = ('rsvp', self._rsvp)
        weather_listener = ('weather', self._weather)
        trainrsvp = ('train', self._trsvp)
        await self.bot.dbi.raid_listener.add_listener(*rsvp_listener)
        await self.bot.dbi.raid_listener.add_listener(*weather_listener)
        await self.bot.dbi.raid_listener.add_listener(*trainrsvp)

    
    async def pickup_raiddata(self):
        raid_table = self.bot.dbi.table('raids')
        query = raid_table.query()
        data = await query.get()
        for rcrd in data:
            self.bot.loop.create_task(self.pickup_raid(rcrd))
    
    async def pickup_raid(self, rcrd):
        raid = await Raid.from_data(self.bot, rcrd)
        self.bot.loop.create_task(raid.monitor_status())
    
    async def pickup_traindata(self):
        train_table = self.bot.dbi.table('trains')
        query = train_table.query
        data = await query.get()
        for rcrd in data:
            self.bot.loop.create_task(self.pickup_train(rcrd))

    async def pickup_train(self, rcrd):
        train = await Train.from_data(self.bot, rcrd)
    
    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        idstring = f'{payload.channel_id}/{payload.message_id}'
        train = Train.by_message.get(payload.message_id)
        raid = Raid.by_message.get(idstring)
        if (not raid and not train) or payload.user_id == self.bot.user.id:
            return
        if train:
            channel = self.bot.get_channel(payload.channel_id)
            msg = await channel.get_message(payload.message_id)
            user = self.bot.get_user(payload.user_id)
            meowthuser = MeowthUser(self.bot, user)
            if payload.emoji.is_custom_emoji():
                emoji = payload.emoji.id
            else:
                emoji = str(payload.emoji)
            await msg.remove_reaction(emoji, user)
            if emoji == '🚂':
                party = await meowthuser.party()
                return await self._join(meowthuser, train, party)
            elif emoji == '❌':
                return await self._leave(meowthuser, train)
        return await raid.process_reactions(payload)

    @Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, RaidDisabled):
            await ctx.error('Raid command disabled in current channel.')
        elif isinstance(error, TrainDisabled):
            await ctx.error('Train command disabled in current channel.')
        elif isinstance(error, InvalidTime):
            await ctx.error(f'Invalid time for {ctx.prefix}{ctx.invoked_with}')
        elif isinstance(error, GroupTooBig):
            await ctx.error('This group is too big for the raid!')
        elif isinstance(error, NotRaidChannel):
            await ctx.error(f'{ctx.prefix}{ctx.invoked_with} must be used in a Raid Channel!')
        elif isinstance(error, NotTrainChannel):
            await ctx.error(f'{ctx.prefix}{ctx.invoked_with} must be used in a Train Channel!')
        elif isinstance(error, RaidNotActive):
            await ctx.error(f'Raid must be active to use {ctx.prefix}{ctx.invoked_with}')
        


    def _rsvp(self, connection, pid, channel, payload):
        if channel != 'rsvp':
            return
        payload_args = payload.split('/')
        raid_id = int(payload_args[0])
        raid = Raid.instances.get(raid_id)
        if not raid:
            return
        event_loop = asyncio.get_event_loop()
        if payload_args[1].isdigit():
            user_id = int(payload_args[1])
            status = payload_args[2]
            event_loop.create_task(raid.update_rsvp(user_id=user_id, status=status))
            return
        elif payload_args[1] == 'power' or payload_args[1] == 'bosses':
            event_loop.create_task(raid.update_rsvp())
            return
        
    def _trsvp(self, connection, pid, channel, payload):
        if channel != 'train':
            return
        payload_args = payload.split('/')
        train_id = int(payload_args[0])
        train = Train.instances.get(train_id)
        if not train:
            return
        event_loop = asyncio.get_event_loop()
        if payload_args[1].isdigit():
            user_id = int(payload_args[1])
            status = payload_args[2]
            event_loop.create_task(train.update_rsvp(user_id, status))
            return

    def _weather(self, connection, pid, channel, payload):
        if channel != 'weather':
            return
        cellid, new_weather = payload.split('/')
        event_loop = asyncio.get_event_loop()
        event_loop.create_task(self.correct_weather(cellid, new_weather))
    
    async def correct_weather(self, cellid, weather):
        cell = S2_L10(self.bot, cellid)
        raids = await cell.get_all_raids()
        for raid_id in raids:
            raid = Raid.instances.get(raid_id)
            if not raid:
                continue
            self.bot.loop.create_task(raid.change_weather(weather))
        

    @command(aliases=['r'], category='Raid')
    @raid_checks.raid_enabled()
    @raid_checks.bot_has_permissions()
    async def raid(self, ctx, level_or_boss, *, gym_and_time):
        """Report a raid or raid egg.

        **Arguments**
        *level_or_boss:* Either level of the raid egg (1-5) or
            name of the raid boss. If the boss's name is multiple
            words, wrap it in quotes.
        *gym_and_time:* Name of the gym optionally followed by 
            the number of minutes until hatch (if raid egg) 
            or expire (if active raid)

        **Example:** `!raid "Raichu Alola" city park 33`
        Reports a Raichu (Alola) raid at City Park with 33 minutes
        until expiry.
        """
        gym_split = gym_and_time.split()
        if gym_split[-1].isdigit():
            endtime = int(gym_split.pop(-1))
            if endtime == 0:
                endtime = 1
            gymstr = " ".join(gym_split)
        else:
            gymstr = " ".join(gym_split)
            endtime = None
        gym = await Gym.convert(ctx, gymstr)
        raid_table = ctx.bot.dbi.table('raids')
        if isinstance(gym, Gym):
            query = raid_table.query()
            query.where(gym=str(gym.id), guild=ctx.guild.id)
            old_raid = await query.get()
            if old_raid:
                old_raid = old_raid[0]
                old_raid = await Raid.from_data(ctx.bot, old_raid)
                if old_raid.hatch:
                    embed = await old_raid.egg_embed()
                else:
                    embed = await old_raid.raid_embed()
                if old_raid.channel_ids:
                    mentions = []
                    for channelid in old_raid.channel_ids:
                        channel = ctx.guild.get_channel(int(channelid))
                        mention = channel.mention
                        mentions.append(mention)
                    return await ctx.send(f"""There is already a raid reported at this gym! Coordinate here: {", ".join(mentions)}""", embed=embed)
                else:
                    msg = await ctx.send(f"""There is already a raid reported at this gym! Coordinate here!""", embed=embed)
                    old_raid.message_ids.append(f"{msg.channel.id}/{msg.id}")
                    return msg
        if level_or_boss.isdigit():
            level = level_or_boss
            boss = None
            if not endtime or endtime > ctx.bot.raid_info.raid_times[level][0]:
                hatch = time.time() + 60*ctx.bot.raid_info.raid_times[level][0]
            else:
                hatch = time.time() + 60*endtime
            end = hatch + 60*ctx.bot.raid_info.raid_times[level][1]
        else:
            boss = await RaidBoss.convert(ctx, level_or_boss)
            level = boss.raid_level
            if not endtime or endtime > ctx.bot.raid_info.raid_times[level][1]:
                end = time.time() + 60*ctx.bot.raid_info.raid_times[level][1]
            else:
                end = time.time() + 60*endtime
            hatch = None
        zone = await ctx.tz()
        raid_id = next(snowflake.create())
        new_raid = Raid(raid_id, ctx.bot, ctx.guild.id, ctx.channel.id, gym, level=level, pkmn=boss, hatch=hatch, end=end, tz=zone)
        return await self.setup_raid(ctx, new_raid)
    
    @command(name='list')
    @raid_checks.raid_enabled()
    async def _list(self, ctx):
        return await self.list_raids(ctx.channel)
    
    async def list_raids(self, channel):
        report_channel = ReportChannel(self.bot, channel)
        data = await report_channel.get_all_raids()
        eggs_list = []
        hatched_list = []
        active_list = []
        if not data:
            return await channel.send('No raids reported!')
        for raid_id in data:
            raid = Raid.instances.get(raid_id)
            if not raid:
                continue
            if raid.status == 'egg':
                eggs_list.append(await raid.summary_str())
            elif raid.status == 'hatched':
                hatched_list.append(await raid.summary_str())
            elif raid.status == 'active':
                active_list.append(await raid.summary_str())
        number = len(data)
        pages = ceil(number/3)
        for i in range(pages):
            fields = {}
            left = 3
            if pages == 1:
                title = 'Current Raids'
            else:
                title = f'Current Raids (Page {i+1} of {pages})'
            if len(active_list) > left:
                fields['Active'] = "\n\n".join(active_list[:3])
                active_list = active_list[3:]
                embed = formatters.make_embed(title=title, fields=fields)
                await channel.send(embed=embed)
                continue
            elif active_list:
                fields['Active'] = "\n\n".join(active_list) + "\n\u200b"
                left -= len(active_list)
                active_list = []
            if not left:
                embed = formatters.make_embed(title=title, fields=fields)
                await channel.send(embed=embed)
                continue
            if len(hatched_list) > left:
                fields['Hatched'] = "\n\n".join(hatched_list[:left])
                hatched_list = hatched_list[left:]
                embed = formatters.make_embed(title=title, fields=fields)
                await channel.send(embed=embed)
                continue
            elif hatched_list:
                fields['Hatched'] = "\n\n".join(hatched_list) + "\n\u200b"
                left -= len(hatched_list)
                hatched_list = []
            if not left:
                embed = formatters.make_embed(title=title, fields=fields)
                await channel.send(embed=embed)
                continue
            if len(eggs_list) > left:
                fields['Eggs'] = "\n\n".join(eggs_list[:left])
                eggs_list = eggs_list[left:]
                embed = formatters.make_embed(title=title, fields=fields)
                await channel.send(embed=embed)
                continue
            elif eggs_list:
                fields['Eggs'] = "\n\n".join(eggs_list)
            embed = formatters.make_embed(title=title, fields=fields)
            return await channel.send(embed=embed)



    
    async def setup_raid(self, ctx, new_raid: Raid):
        boss = new_raid.pkmn
        gym = new_raid.gym
        level = new_raid.level
        hatch = new_raid.hatch
        end = new_raid.end
        raid_table = ctx.bot.dbi.table('raids')
        wants = await new_raid.get_wants()
        role_wants = [wants.get(x) for x in wants if wants.get(x)]
        dm_wants = [x for x in wants if not wants.get(x)]
        role_mentions = "\u200b".join([x.mention for x in role_wants])
        new_raid.channel_ids = []
        new_raid.message_ids = []
        react_list = new_raid.react_list
        if new_raid.hatch:
            embed = await new_raid.egg_embed()
        else:
            embed = await new_raid.raid_embed()
        reportembed = await new_raid.report_embed()
        if role_mentions:
            reportcontent = role_mentions + " - "
        else:
            reportcontent = ""
        exgymcat = None
        if isinstance(gym, Gym):
            if level != 'EX':
                if await gym._exraid():
                    exgymcat = await raid_checks.raid_category(ctx, 'ex_gyms')
        raid_mode = exgymcat if exgymcat else await raid_checks.raid_category(ctx, level)
        report_channels = []
        report_channel = ReportChannel(ctx.bot, ctx.channel)
        train_ids = await report_channel.get_all_trains()
        trains = [Train.instances.get(x) for x in train_ids]
        if trains:
            train_content = "Use the reaction below to vote for this raid next!"
            for t in trains:
                if t:
                    train_embed = await t.train_embed()
                    msg = await t.channel.send(train_content, embed=train_embed.embed)
                    await msg.add_reaction('\u2b06')
                    new_raid.train_msgs.append(f'{msg.channel.id}/{msg.id}')
                    t.report_msg_ids.append(msg.id)
                    Raid.by_trainreport[msg.id] = new_raid
                    await t.upsert()
        if isinstance(gym, Gym):
            channel_list = await gym.get_all_channels('raid')
            report_channels.extend(channel_list)
        else:
            report_channels.append(report_channel)
        if raid_mode == 'message':
            reportcontent += "Coordinate this raid here using the reactions below!"
            if dm_wants:
                dm_content = f"Coordinate this raid in {ctx.channel.name}!"
                for want in dm_wants:
                    dms = await want.notify_users(dm_content, embed)
                    new_raid.message_ids.extend(dms)
            for channel in report_channels:
                reportmsg = await channel.channel.send(reportcontent, embed=embed)
                for react in react_list:
                    if isinstance(react, int):
                        react = self.bot.get_emoji(react)
                    await reportmsg.add_reaction(react)
                new_raid.message_ids.append(f"{reportmsg.channel.id}/{reportmsg.id}")
        elif raid_mode.isdigit():
            catid = int(raid_mode)
            if catid:
                category = ctx.guild.get_channel(catid)
            else:
                category = None
            raid_channel_name = await new_raid.channel_name()
            if len(report_channels) > 1:
                raid_channel_overwrites = formatters.perms_or(report_channels)
            else:
                raid_channel_overwrites = dict(ctx.channel.overwrites)
            try:
                raid_channel = await ctx.guild.create_text_channel(raid_channel_name,
                    category=category, overwrites=raid_channel_overwrites)
            except discord.Forbidden:
                raise commands.BotMissingPermissions(['Manage Channels'])
            new_raid.channel_ids.append(str(raid_channel.id))
            raidmsg = await raid_channel.send(reportcontent, embed=embed)
            for react in react_list:
                if isinstance(react, int):
                    react = self.bot.get_emoji(react)
                await raidmsg.add_reaction(react)
            new_raid.message_ids.append(f"{raidmsg.channel.id}/{raidmsg.id}")
            reportcontent += f"Coordinate this raid in {raid_channel.mention}!"
            for channel in report_channels:
                if dm_wants:
                    dm_content = f"Coordinate this raid in {raid_channel.name}!"
                    for want in dm_wants:
                        dms = await want.notify_users(dm_content, embed)
                        new_raid.message_ids.extend(dms)
                reportmsg = await channel.channel.send(reportcontent, embed=reportembed)
                for react in react_list:
                    if isinstance(react, int):
                        react = self.bot.get_emoji(react)
                    await reportmsg.add_reaction(react)
                new_raid.message_ids.append(f"{reportmsg.channel.id}/{reportmsg.id}")
        await new_raid.upsert()
        for message_id in new_raid.message_ids:
            Raid.by_message[message_id] = new_raid
        for channel_id in new_raid.channel_ids:
            Raid.by_channel[channel_id] = new_raid
        new_raid.monitor_task = self.bot.loop.create_task(new_raid.monitor_status())
    
    @command(aliases=['ex'], category='Raid')
    @raid_checks.raid_enabled()
    async def exraid(self, ctx, gym: Gym, *, hatch_time: hatch_converter):
        """Report an EX Raid.

        **Arguments**
        *gym:* Name of the gym. Must be wrapped in quotes if multiple words.

        *hatch_time:* Date and time the EX Raid will begin.
            Does not need to be wrapped in quotes.
        
        **Example:** `!exraid "city park" April 9 1:00 PM`
        Reports an EX Raid at City Park beginning on April 9 at 1:00 PM.
        """
        zone = await ctx.tz()
        raid_id = next(snowflake.create())
        new_exraid = Raid(raid_id, ctx.bot, ctx.guild.id, ctx.channel.id, gym, level="EX", hatch=hatch_time, tz=zone)
        return await self.setup_raid(ctx, new_exraid)

    
    @staticmethod
    async def get_raidid(ctx):
        raid_table = ctx.bot.dbi.table('raids')
        id_query = raid_table.query('id')
        id_query.where(raid_table['channels'].contains_(str(ctx.channel.id)))
        raid_id = await id_query.get_value()
        return raid_id

    async def get_raid_trainerdict(self, raid_id):
        def data(rcrd):
            trainer = rcrd['user_id']
            status = rcrd.get('status')
            bosses = rcrd.get('bosses')
            party = rcrd.get('party', [0,0,0,1])
            estimator = rcrd.get('estimator')
            rcrd_dict = {
                'bosses': bosses,
                'status': status,
                'party': party,
                'estimator': estimator
            }
            return trainer, rcrd_dict
        trainer_dict = {}
        user_table = self.bot.dbi.table('raid_rsvp')
        query = user_table.query()
        query.where(raid_id=raid_id)
        rsvp_data = await query.get()
        for rcrd in rsvp_data:
            trainer, rcrd_dict = data(rcrd)
            total = sum(rcrd_dict['party'])
            trainer_dict[trainer] = rcrd_dict
        return trainer_dict

    @staticmethod
    async def get_raidlevel(ctx):
        raid_table = ctx.bot.dbi.table('raids')
        level_query = raid_table.query('level')
        level_query.where(raid_table['channels'].contains_(str(ctx.channel.id)))
        level = await level_query.get_value()
        return level
    
    async def rsvp(self, ctx, status, bosses=[], total: int=0, *teamcounts):
        raid_id = await self.get_raidid(ctx)
        meowthuser = MeowthUser.from_id(ctx.bot, ctx.author.id)
        if status == 'cancel':
            return await meowthuser.cancel_rsvp(raid_id)
        if bosses:
            boss_ids = []
            for boss in bosses:
                boss_ids.append(boss.id)
        else:
            level = await self.get_raidlevel(ctx)
            boss_list = self.bot.raid_info.raid_lists[level]
            boss_ids = boss_list
        if total or teamcounts:
            party = await meowthuser.party_list(total, *teamcounts)
            await meowthuser.set_party(party=party)
        else:
            party = await meowthuser.party()
        await meowthuser.rsvp(raid_id, status, bosses=boss_ids, party=party)
    
    @command(aliases=['i', 'maybe'], category="Raid RSVP")
    @raid_checks.raid_channel()
    async def interested(self, ctx, bosses: commands.Greedy[Pokemon], total: typing.Optional[int]=1, *teamcounts):
        """RSVP as interested to the current raid.

        **Arguments**
        *bosses (optional):* Names of the bosses you are interested in.

        *total (optional):* Number of trainers you are bringing. Defaults to
            your last RSVP total, or 1.
        
        *teamcounts (optional):* Counts of each team in your group. Format:
            `3m 2v 1i` means 3 Mystic, 2 Valor, 1 Instinct.
        """
        if total < 1:
            return
        await self.rsvp(ctx, "maybe", bosses, total, *teamcounts)
        
    @command(aliases=['c', 'omw'], category="Raid RSVP")
    @raid_checks.raid_channel()
    async def coming(self, ctx, bosses: commands.Greedy[Pokemon], total: typing.Optional[int]=1, *teamcounts):
        """RSVP as on your way to the current raid.

       **Arguments**
        *bosses (optional):* Names of the bosses you are interested in.

        *total (optional):* Number of trainers you are bringing. Defaults to
            your last RSVP total, or 1.
        
        *teamcounts (optional):* Counts of each team in your group. Format:
            `3m 2v 1i` means 3 Mystic, 2 Valor, 1 Instinct.
        """
        if total < 1:
            return
        await self.rsvp(ctx, "coming", bosses, total, *teamcounts)
    
    @command(aliases=['h'])
    @raid_checks.raid_channel()
    async def here(self, ctx, bosses: commands.Greedy[Pokemon], total: typing.Optional[int]=1, *teamcounts):
        """RSVP as being at the current raid.

        **Arguments**
        *bosses (optional):* Names of the bosses you are interested in.

        *total (optional):* Number of trainers you are bringing. Defaults to
            your last RSVP total, or 1.
        
        *teamcounts (optional):* Counts of each team in your group. Format:
            `3m 2v 1i` means 3 Mystic, 2 Valor, 1 Instinct.
        """
        if total < 1:
            return
        await self.rsvp(ctx, "here", bosses, total, *teamcounts)
    
    @command(aliases=['x'], category="Raid RSVP")
    @raid_checks.raid_channel()
    async def cancel(self, ctx):
        """Cancel your RSVP to the current raid."""
        await self.rsvp(ctx, "cancel")

    @command(category="Raid Info")
    @raid_checks.raid_channel()
    async def counters(self, ctx):
        """Request your optimal counters for the current box from Pokebattler.

        Use `!set pokebattler` before using this command to link your
        Pokebattler account.
        """
        raid = Raid.by_channel.get(str(ctx.channel.id))
        if not raid:
            return
        if raid.status != 'active':
            raise RaidNotActive
        meowthuser = MeowthUser.from_id(ctx.bot, ctx.author.id)
        embed = await self.counters_embed(meowthuser)
        if not embed:
            return await ctx.author.send("You likely have better counters than the ones in your Pokebattler Pokebox! Please update your Pokebox!")
        await ctx.author.send(embed=embed)
        await raid.update_rsvp()
        
    @command(category="Raid RSVP")
    @raid_checks.raid_channel()
    async def group(self, ctx, group_time):
        """Create a group for the current raid.

        **Arguments**
        *group_time:* Number of minutes until the group
            will enter the raid.
        """
        raid = Raid.by_channel.get(str(ctx.channel.id))
        if not raid:
            raise NotRaidChannel
        group_table = ctx.bot.dbi.table('raid_groups')
        insert = group_table.insert()
        i = len(raid.group_list)
        emoji = f'{i+1}\u20e3'
        if group_time.isdigit():
            stamp = time.time() + int(group_time)*60
            if stamp > raid.end:
                raise InvalidTime
            elif raid.hatch and stamp < raid.hatch:
                raise InvalidTime
            d = {
                'raid_id': raid.id,
                'emoji': emoji,
                'starttime': stamp,
                'users': [],
                'est_power': 0
            }
            insert.row(**d)
            await insert.commit()
            raid.group_list.append(d)
            for idstring in raid.message_ids:
                chn, msg = await ChannelMessage.from_id_string(self.bot, idstring)
                await msg.add_reaction(emoji)
            return await raid.join_grp(ctx.author.id, d)
    
    @command(aliases=['start'], category="Raid RSVP")
    @raid_checks.raid_channel()
    async def starting(self, ctx):
        """Notify Meowth that your group is entering the raid lobby.

        If the user is not in a group, Meowth assumes everyone
        listed as 'here' is starting the raid.
        A backout can be requested via reaction for two minutes
        after this command is sent."""
        raid = Raid.by_channel.get(str(ctx.channel.id))
        if not raid:
            return
        if raid.status != 'active':
            raise RaidNotActive
        grp = raid.user_grp(ctx.author.id)
        if not grp:
            grp = raid.here_grp
        return await raid.start_grp(grp, ctx.author, channel=ctx.channel)
    
    @command(category="Raid Info")
    @raid_checks.raid_channel()
    async def weather(self, ctx, *, weather: Weather):
        """Report the weather at the current raid.

        If the raid is at a known gym, this command will update
        the weather at all other known gyms in the cell.
        """
        raid = Raid.by_channel.get(str(ctx.channel.id))
        if not raid:
            return
        return await raid.correct_weather(weather)
    
    @command(aliases=['move'], category="Raid Info")
    @raid_checks.raid_channel()
    async def moveset(self, ctx, move1: Move, move2: Move=None):
        """Report the raid boss's moveset.

        One or both moves may be given. If the name of the move
        is multiple words long, wrap it in quotes.
        **Example:** `!moveset "hydro pump"`"""
        raid = Raid.by_channel.get(str(ctx.channel.id))
        if not raid:
            raise NotRaidChannel
        if raid.status != 'active':
            raise RaidNotActive
        if not move2:
            return await raid.set_moveset(move1, move2=move2)
        try:
            return await raid.set_moveset(move1, move2=move2)
        except MoveInvalid as e:
            if e.move == move2.id:
                move = await move2.name()
                pokemon = await raid.pkmn.name()
                await ctx.warning(f'{pokemon} does not learn {move}.')
                return await raid.set_moveset(move1)
            elif e.move == move1.id:
                move = await move1.name()
                pokemon = await raid.pkmn.name()
                await ctx.warning(f'{pokemon} does not learn {move}.')
                return await raid.set_moveset(move2)
    
    @command(aliases=['timer'], category="Raid Info")
    @raid_checks.raid_channel()
    async def timerset(self, ctx, *, newtime):
        """Set the raid's hatch time or expire time.

        If *newtime* is an integer, it is assumed
        to be the number of minutes until hatch/expire.
        Otherwise, Meowth attempts to parse newtime as a
        time.
        **Examples:** `!timerset 12:00 PM`
        `!timerset 5`
        """
        raid = Raid.by_channel.get(str(ctx.channel.id))
        if not raid:
            return
        zone = raid.tz
        if newtime.isdigit():
            stamp = time.time() + 60*int(newtime)
        else:
            try:
                newdt = parse(newtime, settings={'TIMEZONE': zone, 'RETURN_AS_TIMEZONE_AWARE': True})
                stamp = newdt.timestamp()
            except:
                raise
        try:
            raid.update_time(stamp)
        except:
            raise
        if raid.status == 'egg' or raid.status == 'hatched':
            dt = datetime.fromtimestamp(raid.hatch)
            local = raid.local_datetime(raid.hatch)
            timestr = local.strftime('%I:%M %p')
            datestr = local.strftime('%b %d')
            title = "Hatch Time Updated"
            if raid.level == 'EX':
                details = f"This EX Raid Egg will hatch on {datestr} at {timestr}"
            else:
                details = f"This Raid Egg will hatch at {timestr}"
        elif raid.status == 'active' or raid.status == 'expired':
            title = "Expire Time Updated"
            dt = datetime.fromtimestamp(raid.end)
            localdt = raid.local_datetime(raid.end)
            timestr = localdt.strftime('%I:%M %p')
            datestr = localdt.strftime('%b %d')
            if raid.level == 'EX':
                details = f"This EX Raid will end at {timestr}"
            else:
                details = f"This Raid will end at {timestr}"
        has_embed = False
        for idstring in raid.message_ids:
            chn, msg = await ChannelMessage.from_id_string(self.bot, idstring)
            if not has_embed:
                embed = msg.embeds[0]
                embed.timestamp = dt
                has_embed = True
            await msg.edit(embed=embed)
        return await ctx.success(title=title, details=details)
    
    @command()
    @checks.is_co_owner()
    async def countersupdate(self, ctx):
        """Updates the generic counters data.

        Must be bot co-owner to use."""
        data_table = ctx.bot.dbi.table('counters_data')
        raid_lists = ctx.bot.raid_info.raid_lists
        weather_list = ['CLEAR', 'PARTLY_CLOUDY', 'OVERCAST', 'RAINY', 'SNOW', 'FOG', 'WINDY', 'NO_WEATHER']
        ctrs_data_list = []
        for level in raid_lists:
            for pkmnid in raid_lists[level]:
                if level == 'EX':
                    url_level = 5
                else:
                    url_level = level
                for weather in weather_list:
                    data_url = Raid.pokebattler_data_url(
                        pkmnid, url_level, "20", weather
                    )
                    data_url_min = Raid.pokebattler_data_url(
                        pkmnid, url_level, "40", weather
                    )
                    async with aiohttp.ClientSession() as session:
                        async with session.get(data_url) as resp:
                            try:
                                data_20 = await resp.json()
                                data_20 = data_20['attackers'][0]
                            except KeyError:
                                pass
                    async with aiohttp.ClientSession() as session:
                        async with session.get(data_url_min) as resp:
                            try:
                                data_min = await resp.json()
                                data_min = data_min['attackers'][0]
                            except KeyError:
                                pass
                    random_move_ctrs = data_20['randomMove']['defenders'][-6:]
                    estimator_20 = data_20['randomMove']['total']['estimator']
                    estimator_min = data_min['randomMove']['defenders'][-1]['total']['estimator']
                    random_move_dict = {
                        'boss_id': pkmnid,
                        'level': level,
                        'weather': weather,
                        'fast_move': 'random',
                        'charge_move': 'random',
                        'estimator_20': estimator_20,
                        'estimator_min': estimator_min
                    }
                    ctr_index = 1
                    for ctr in reversed(random_move_ctrs):
                        ctrid = ctr['pokemonId']
                        moveset = ctr['byMove'][-1]
                        fast_move = moveset['move1']
                        charge_move = moveset['move2']
                        random_move_dict[f'counter_{ctr_index}_id'] = ctrid
                        random_move_dict[f'counter_{ctr_index}_fast'] = fast_move
                        random_move_dict[f'counter_{ctr_index}_charge'] = charge_move
                        ctr_index += 1
                    ctrs_data_list.append(random_move_dict)
                    for moveset in data_20['byMove']:
                        ctrs = moveset['defenders'][-6:]
                        boss_fast = moveset['move1']
                        boss_charge = moveset['move2']
                        estimator_20 = moveset['total']['estimator']
                        for moveset_min in data_min['byMove']:
                            if moveset_min['move1'] == boss_fast and moveset_min['move2'] == boss_charge:
                                estimator_min = moveset_min['defenders'][-1]['total']['estimator']
                                break
                            else:
                                continue
                        moveset_dict = {
                            'boss_id': pkmnid,
                            'level': level,
                            'weather': weather,
                            'fast_move': boss_fast,
                            'charge_move': boss_charge,
                            'estimator_20': estimator_20,
                            'estimator_min': estimator_min
                        }
                        ctr_index = 1
                        for ctr in reversed(ctrs):
                            ctrid = ctr['pokemonId']
                            moveset = ctr['byMove'][-1]
                            fast_move = moveset['move1']
                            charge_move = moveset['move2']
                            moveset_dict[f'counter_{ctr_index}_id'] = ctrid
                            moveset_dict[f'counter_{ctr_index}_fast'] = fast_move
                            moveset_dict[f'counter_{ctr_index}_charge'] = charge_move
                            ctr_index += 1
                        ctrs_data_list.append(moveset_dict)
        
        insert = data_table.insert().rows(ctrs_data_list)
        await insert.commit(do_update=True)
        return await ctx.send("Counters update successful")

    @command(category="Raid Train")
    @raid_checks.train_enabled()
    async def train(self, ctx):
        """Reports a raid train.

        If used in a report channel, Meowth will
        ask for the first raid. If used in a raid channel,
        Meowth will assume the current raid to be the first raid.
        """
        report_channel = ReportChannel(self.bot, ctx.channel)
        city = await report_channel.city()
        city = city.split()[0]
        name = f'{city}-raid-train'
        cat = ctx.channel.category
        ow = dict(ctx.channel.overwrites)
        try:
            train_channel = await ctx.guild.create_text_channel(name, category=cat, overwrites=ow)
        except discord.Forbidden:
            raise commands.BotMissingPermissions(['Manage Channels'])
        train_id = next(snowflake.create())
        new_train = Train(train_id, self.bot, ctx.guild.id, train_channel.id, ctx.channel.id)
        if ctx.raid_id:
            first_raid = Raid.instances.get(ctx.raid_id)
            if first_raid:
                await new_train.select_raid(first_raid)
            else:
                await new_train.select_first_raid(ctx.author)
        else:
            await new_train.select_first_raid(ctx.author)
        Train.by_channel[train_channel.id] = new_train
        embed = await new_train.train_embed()
        msg = await ctx.send(f"{ctx.author.display_name} has started a raid train! You can join by reacting to this message and coordinate in {train_channel.mention}!", embed=embed.embed)
        await msg.add_reaction('🚂')
        await msg.add_reaction('❌')
        new_train.message_ids.append(f'{ctx.channel.id}/{msg.id}')
        await new_train.upsert()
        Train.by_message[msg.id] = new_train
        meowthuser = MeowthUser(self.bot, ctx.author)
        party = await meowthuser.party()
        await self._join(meowthuser, new_train, party=party)
    
    @command(category="Raid Train")
    async def next(self, ctx):
        """Switch the train channel to the next raid.

        The next raid is the raid which got the most reaction
        votes during the previous raid."""
        train = Train.by_channel.get(ctx.channel.id)
        if not train:
            return
        await train.finish_current_raid()
    
    @command(category="Raid Train")
    async def join(self, ctx, total: typing.Optional[int]=1, *teamcounts):
        """Join a raid train.

        This does not automatically RSVP you to the raids
        in the train. You must still RSVP for yourself or else
        have another user count you in their RSVP."""
        train = Train.by_channel.get(ctx.channel.id)
        if not train:
            return
        meowthuser = MeowthUser.from_id(ctx.bot, ctx.author.id)
        if total or teamcounts:
            party = await meowthuser.party_list(total, *teamcounts)
            await meowthuser.set_party(party=party)
        else:
            party = await meowthuser.party()
        await self._join(meowthuser, train, party=party)
    
    async def _join(self, user, train, party=[0,0,0,1]):
        await user.train_rsvp(train, party=party)
    
    @command(category="Raid Train")
    async def leave(self, ctx):
        """Leave a raid train.

        This does not affect your RSVP to the current raid."""
        train = Train.by_channel.get(ctx.channel.id)
        if not train:
            return
        meowthuser = MeowthUser.from_id(ctx.bot, ctx.author.id)
        await self._leave(meowthuser, train)
    
    async def _leave(self, user, train):
        await user.leave_train(train)

