from meowth import Cog, command, bot, checks
from meowth.exts.map import Gym, Pokestop, ReportChannel, PartialPOI, S2_L10, POI
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
from .objects import Raid, RaidBoss, Train, Meetup

from math import ceil
import discord
from discord.ext import commands
from discord import Embed
import asyncio
import aiohttp
import time
from datetime import datetime
from dateparser import parse
from pytz import timezone
import typing
import re

emoji_letters = ['🇦','🇧','🇨','🇩','🇪','🇫','🇬','🇭','🇮','🇯','🇰','🇱',
    '🇲','🇳','🇴','🇵','🇶','🇷','🇸','🇹','🇺','🇻','🇼','🇽','🇾','🇿'
]

class time_converter(commands.Converter):
    async def convert(self, ctx, argument):
        zone = await ctx.tz()
        hatch_dt = parse(argument, settings={'TIMEZONE': zone, 'RETURN_AS_TIMEZONE_AWARE': True})
        if not hatch_dt:
            return None
        tz = timezone(zone)
        now_dt = datetime.now(tz=tz)
        if hatch_dt.day != now_dt.day and ctx.command.name not in ['exraid', 'meetup']:
            hatch_dt = hatch_dt.replace(day=now_dt.day)
        if ctx.command.name == 'group':
            raid = Raid.by_channel.get(str(ctx.channel.id))
            end_dt = raid.local_datetime(raid.end)
            hatch_dt = hatch_dt.replace(day=end_dt.day)
        if hatch_dt < now_dt:
            if hatch_dt.hour < 12:
                hatch_dt = hatch_dt.replace(hour=hatch_dt.hour+12)
        return hatch_dt.timestamp()



        

class RaidCog(Cog):
    
    def __init__(self, bot):
        bot.raid_info = raid_info
        self.bot = bot
        self.bot.loop.create_task(self.pickup_raiddata())
        self.bot.loop.create_task(self.pickup_traindata())
        self.bot.loop.create_task(self.pickup_meetupdata())
        self.bot.loop.create_task(self.add_listeners())
    
    async def add_listeners(self):
        if self.bot.dbi.raid_listener:
            await self.bot.dbi.pool.release(self.bot.dbi.raid_listener)
        self.bot.dbi.raid_listener = await self.bot.dbi.pool.acquire()
        rsvp_listener = ('rsvp', self._rsvp)
        weather_listener = ('weather', self._weather)
        trainrsvp = ('train', self._trsvp)
        meetuprsvp = ('meetup', self._mrsvp)
        await self.bot.dbi.raid_listener.add_listener(*rsvp_listener)
        await self.bot.dbi.raid_listener.add_listener(*weather_listener)
        await self.bot.dbi.raid_listener.add_listener(*trainrsvp)
        await self.bot.dbi.raid_listener.add_listener(*meetuprsvp)

    
    async def pickup_raiddata(self):
        raid_table = self.bot.dbi.table('raids')
        query = raid_table.query()
        data = await query.get()
        for rcrd in data:
            self.bot.loop.create_task(self.pickup_raid(rcrd))
    
    async def pickup_raid(self, rcrd):
        raid = await Raid.from_data(self.bot, rcrd)
        self.bot.loop.create_task(raid.monitor_status())

    async def pickup_meetupdata(self):
        meetup_table = self.bot.dbi.table('meetups')
        query = meetup_table.query
        data = await query.get()
        for rcrd in data:
            self.bot.loop.create_task(self.pickup_meetup(rcrd))
    
    async def pickup_meetup(self, rcrd):
        meetup = await Meetup.from_data(self.bot, rcrd)
        return meetup
    
    async def pickup_traindata(self):
        train_table = self.bot.dbi.table('trains')
        query = train_table.query
        data = await query.get()
        for rcrd in data:
            self.bot.loop.create_task(self.pickup_train(rcrd))

    async def pickup_train(self, rcrd):
        train = await Train.from_data(self.bot, rcrd)
    
    async def get_raid_lists(self):
        raid_lists = {
            "1": {},
            "2": {},
            "3": {},
            "4": {},
            "5": {},
            "6": {},
            "EX": {}
        }
        table = self.bot.dbi.table('raid_bosses')
        query = table.query
        rows = await query.get()
        def data(rcrd):
            d = {
                'verified': rcrd.get('verified', False),
                'available': rcrd.get('available', False),
                'shiny': rcrd.get('shiny', False),
                'is_regional': rcrd.get('is_regional', False),
                'start_time': rcrd.get('start_time'),
                'end_time': rcrd.get('end_time')
            }
            boss_id = rcrd.get('pokemon_id')
            level = rcrd.get('level')
            return level, boss_id, d
        for rcrd in rows:
            level, boss_id, d = data(rcrd)
            raid_lists[level][boss_id] = d
        return raid_lists

    async def archive_cat_phrases(self, guild):
        table = self.bot.dbi.table('archive')
        query = table.query
        query.where(guild_id=guild.id)
        data = await query.get()
        if data:
            data = data[0]
        else:
            return None, None
        catid = data['category']
        cat = self.bot.get_channel(catid)
        phrase_list = data.get('phrase_list', [])
        return cat, phrase_list
    
    @Cog.listener()
    async def on_message(self, message):
        channel = message.channel
        if not hasattr(channel, 'guild'):
            return
        guild = channel.guild
        raid = Raid.by_channel.get(str(channel.id))
        train = Train.by_channel.get(channel.id)
        meetup = Meetup.by_channel.get(channel.id)
        if not (raid or train or meetup):
            return
        url_re = '(http(s?)://)?((maps\.google\./)|((www\.)?google\.com/maps/)|(goo.gl/maps/))\S*'
        match = re.search(url_re, message.content)
        if match:
            url = match.group()
            if raid:
                return await raid.update_url(url)
            elif meetup:
                return await meetup.update_url(url)
        category, phrase_list = await self.archive_cat_phrases(guild)
        if not phrase_list:
            return
        for phrase in phrase_list:
            if phrase in message.content:
                return await self.mark_for_archival(channel.id, guild.me.id, reason=f'{phrase} was said by {message.author.display_name}')
        
        
    
    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        idstring = f'{payload.channel_id}/{payload.message_id}'
        train = Train.by_message.get(payload.message_id)
        raid = Raid.by_message.get(idstring)
        meetup = Meetup.by_message.get(idstring)
        if (not raid and not train and not meetup) or payload.user_id == self.bot.user.id:
            return
        if meetup:
            return await meetup.process_reactions(payload)
        if train:
            channel = self.bot.get_channel(payload.channel_id)
            msg = await channel.fetch_message(payload.message_id)
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
        elif isinstance(error, MeetupDisabled):
            await ctx.error('Meetup command disabled in current channel.')
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
    
    @Cog.listener()
    async def on_command_completion(self, ctx):
        if ctx.command.name == 'list':
            try:
                if await raid_checks.is_raid_enabled(ctx):
                    if len(ctx.args) == 2 or 'raids' in ctx.args:
                        return await self.list_raids(ctx.channel)
            except RaidDisabled:
                pass
            try:
                if await raid_checks.is_raid_or_meetup(ctx):
                    raid = Raid.by_channel.get(str(ctx.channel.id))
                    if not raid:
                        raid = Meetup.by_channel.get(ctx.channel.id)
                    tags = False
                    if 'tags' in ctx.args:
                        tags = True
                        ctx.args.remove('tags')
                    if len(ctx.args) == 2 or 'rsvp' in ctx.args:
                        return await raid.list_rsvp(ctx.channel, tags=tags)
                    if 'teams' in ctx.args:
                        return await raid.list_teams(ctx.channel, tags=tags)
                    if 'groups' in ctx.args:
                        if isinstance(raid, Meetup):
                            return await raid.list_rsvp(ctx.channel, tags=tags)
                        return await raid.list_groups(ctx.channel, tags=tags)
                    if 'bosses' in ctx.args:
                        if isinstance(raid, Meetup):
                            return await raid.list_rsvp(ctx.channel, tags=tags)
                        return await raid.list_bosses(ctx.channel, tags=tags)
                    return await raid.list_rsvp(ctx.channel, tags=tags)
            except NotRaidChannel:
                pass
        
    @Cog.listener()
    async def on_guild_channel_delete(self, channel):
        meetup = Meetup.by_channel.get(channel.id)
        if not meetup:
            return
        meetup_table = self.bot.dbi.table('meetups')
        query = meetup_table.query
        query.where(id=meetup.id)
        await query.delete()
        rsvp_table = self.bot.dbi.table('meetup_rsvp')
        query = rsvp_table.query
        query.where(meetup_id=meetup.id)
        await query.delete()
        for msgid in meetup.message_ids:
            del Meetup.by_message[msgid]
        del Meetup.by_channel[channel.id]
        del Meetup.instances[meetup.id]
        
    
    async def mark_for_archival(self, channel_id, user_id, reason=None):
        d = {
            'channel_id': channel_id,
            'user_id': user_id,
            'reason': reason
        }
        table = self.bot.dbi.table('to_archive')
        insert = table.insert
        insert.row(**d)
        await insert.commit(do_update=True)

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
    
    def _mrsvp(self, connection, pid, channel, payload):
        if channel != 'meetup':
            return
        payload_args = payload.split('/')
        meetup_id = int(payload_args[0])
        meetup = Meetup.instances.get(meetup_id)
        if not meetup:
            return
        event_loop = asyncio.get_event_loop()
        if payload_args[1].isdigit():
            user_id = int(payload_args[1])
            status = payload_args[2]
            event_loop.create_task(meetup.update_rsvp(user_id, status))
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
    
    @command()
    @raid_checks.meetup_enabled()
    @checks.location_set()
    async def meetup(self, ctx, location: POI, *, start_time: time_converter):
        """Create a Meetup channel.
        
        **Arguments**
        *location:* Location of the Meetup. Meowth searches 
            for known locations (Gyms and Pokestops) and returns a guess if
            no match is found.
        *start_time:* The date and time of the Meetup.
        
        Remember to wrap multi-word arguments in quotes."""

        guild = ctx.guild
        guild_id = guild.id
        if isinstance(location, POI):
            loc_name = await location._name()
        else:
            loc_name = location._name
        channel_name = f'meetup-{loc_name}'
        overwrites = ctx.channel.overwrites
        category = await raid_checks.meetup_category(ctx)
        meetup_channel = await guild.create_text_channel(channel_name, overwrites=overwrites, category=category)
        meetup_id = next(snowflake.create())
        tz = await ctx.tz()
        meetup = Meetup(meetup_id, ctx.bot, guild_id, meetup_channel.id, ctx.channel.id, location, start_time, tz)
        topic = meetup.channel_topic
        await meetup_channel.edit(topic=topic)
        reportcontent = f"Plan for this meetup in {meetup_channel.mention}!"
        embed = await meetup.meetup_embed()
        reportmsg = await ctx.send(reportcontent, embed=embed)
        reportid = f'{ctx.channel.id}/{reportmsg.id}'
        meetup.message_ids.append(reportid)
        chanmsg = await meetup_channel.send(embed=embed)
        chanmsgid = f'{meetup_channel.id}/{chanmsg.id}'
        meetup.message_ids.append(chanmsgid)
        await meetup.upsert()
        for message_id in meetup.message_ids:
            Meetup.by_message[message_id] = meetup
        Meetup.by_channel[meetup_channel.id] = meetup
        react_list = meetup.react_list
        for react in react_list:
            if isinstance(react, int):
                react = self.bot.get_emoji(react)
            await reportmsg.add_reaction(react)
            await chanmsg.add_reaction(react)

        

    @command()
    @raid_checks.archive_enabled()
    @raid_checks.temp_channel()
    async def archive(self, ctx, *, reason=None):
        """Mark a temporary channel for archival rather than deletion.
        
        **Arguments**
        *reason (optional):* Reason for archiving the channel."""
        await ctx.message.delete()
        channel_id = ctx.channel.id
        user_id = ctx.author.id
        await self.mark_for_archival(channel_id, user_id, reason)

    @command(aliases=['r'], category='Raid')
    @raid_checks.raid_enabled()
    @checks.location_set()
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
        zone = await ctx.tz()
        if ':' in gym_split[-1]:
            converter = time_converter()
            stamp = await converter.convert(ctx, gym_split[-1])
            dt = stamp - time.time()
            if dt > 0:
                endtime = dt/60
            else:
                endtime = None
            del gym_split[-1]
            gymstr = " ".join(gym_split)
        elif gym_split[-1].isdigit():
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
                        if not channel:
                            continue
                        mention = channel.mention
                        mentions.append(mention)
                    if mentions:
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
            level = await boss.raid_level()
            if not endtime or endtime > ctx.bot.raid_info.raid_times[level][1]:
                end = time.time() + 60*ctx.bot.raid_info.raid_times[level][1]
            else:
                end = time.time() + 60*endtime
            hatch = None
        raid_id = next(snowflake.create())
        new_raid = Raid(raid_id, ctx.bot, ctx.guild.id, ctx.channel.id, ctx.author.id, gym, level=level, pkmn=boss, hatch=hatch, end=end, tz=zone)
        ctx.raid = new_raid
        return await self.setup_raid(ctx, new_raid)

    
    async def list_raids(self, channel):
        color = channel.guild.me.color
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
                embed = formatters.make_embed(title=title, fields=fields, msg_colour=color)
                await channel.send(embed=embed)
                continue
            elif active_list:
                fields['Active'] = "\n\n".join(active_list) + "\n\u200b"
                left -= len(active_list)
                active_list = []
            if not left:
                embed = formatters.make_embed(title=title, fields=fields, msg_colour=color)
                await channel.send(embed=embed)
                continue
            if len(hatched_list) > left:
                fields['Hatched'] = "\n\n".join(hatched_list[:left])
                hatched_list = hatched_list[left:]
                embed = formatters.make_embed(title=title, fields=fields, msg_colour=color)
                await channel.send(embed=embed)
                continue
            elif hatched_list:
                fields['Hatched'] = "\n\n".join(hatched_list) + "\n\u200b"
                left -= len(hatched_list)
                hatched_list = []
            if not left:
                embed = formatters.make_embed(title=title, fields=fields, msg_colour=color)
                await channel.send(embed=embed)
                continue
            if len(eggs_list) > left:
                fields['Eggs'] = "\n\n".join(eggs_list[:left])
                eggs_list = eggs_list[left:]
                embed = formatters.make_embed(title=title, fields=fields, msg_colour=color)
                await channel.send(embed=embed)
                continue
            elif eggs_list:
                fields['Eggs'] = "\n\n".join(eggs_list)
            embed = formatters.make_embed(title=title, fields=fields, msg_colour=color)
            return await channel.send(embed=embed)



    
    async def setup_raid(self, ctx, new_raid: Raid):
        boss = new_raid.pkmn
        gym = new_raid.gym
        level = new_raid.level
        hatch = new_raid.hatch
        end = new_raid.end
        reporter = new_raid.reporter
        await new_raid.get_boss_list()
        raid_table = ctx.bot.dbi.table('raids')
        wants = await new_raid.get_wants()
        mentions = [wants.get(x) for x in wants if wants.get(x)]
        mention_str = "\u200b".join(mentions)
        new_raid.channel_ids = []
        new_raid.message_ids = []
        react_list = new_raid.react_list
        if new_raid.hatch:
            embed = await new_raid.egg_embed()
        else:
            embed = await new_raid.raid_embed()
        reportembed = await new_raid.report_embed()
        exgymcat = None
        if isinstance(gym, Gym):
            if level != 'EX':
                if await gym._exraid():
                    exgymcat = await raid_checks.raid_category(ctx, 'ex_gyms')
        raid_mode = exgymcat if exgymcat else await raid_checks.raid_category(ctx, level)
        if not raid_mode:
            return await ctx.error(f'Level {level} Raid reports not permitted in this channel')
        report_channels = []
        report_channel = ReportChannel(ctx.bot, ctx.channel)
        train_ids = await report_channel.get_all_trains()
        trains = [Train.instances.get(x) for x in train_ids]
        if trains:
            for t in trains:
                if t.channel:
                    await t.new_raid(new_raid)
                else:
                    ctx.bot.loop.create_task(t.end_train())
        if isinstance(gym, Gym):
            channel_list = await gym.get_all_channels('raid', level=level)
            report_channels.extend(channel_list)
        if report_channel not in report_channels:
            report_channels.append(report_channel)
        if raid_mode == 'message':
            if mention_str:
                reportcontent = mention_str + " - "
            else:
                reportcontent = ""
            reportcontent += "Coordinate this raid here using the reactions below!"
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
        elif raid_mode == 'none':
            category = None
        if raid_mode != 'message':
            if mention_str:
                raidcontent = mention_str + " - "
            else:
                raidcontent = ""
            raidcontent += f"Raid reported in {ctx.channel.mention}!"
            raid_channel_name = await new_raid.channel_name()
            raid_channel_position = int(new_raid.end)
            raid_channel_topic = new_raid.channel_topic
            if len(report_channels) > 1:
                raid_channel_overwrites = formatters.perms_or(report_channels)
            else:
                raid_channel_overwrites = dict(ctx.channel.overwrites)
            try:
                raid_channel = await ctx.guild.create_text_channel(raid_channel_name,
                    category=category, overwrites=raid_channel_overwrites,
                    position=raid_channel_position, topic=raid_channel_topic)
            except discord.Forbidden:
                raise commands.BotMissingPermissions(['Manage Channels'])
            new_raid.channel_ids.append(str(raid_channel.id))
            raidmsg = await raid_channel.send(raidcontent, embed=embed)
            await raidmsg.pin()
            for react in react_list:
                if isinstance(react, int):
                    react = self.bot.get_emoji(react)
                await raidmsg.add_reaction(react)
            new_raid.message_ids.append(f"{raidmsg.channel.id}/{raidmsg.id}")
            reportcontent = f"Coordinate this raid in {raid_channel.mention}!"
            for channel in report_channels:
                try:
                    reportmsg = await channel.channel.send(reportcontent, embed=reportembed)
                except:
                    continue
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
    @checks.location_set()
    @raid_checks.bot_has_permissions()
    async def exraid(self, ctx, gym: Gym, *, hatch_time: time_converter):
        """Report an EX Raid.

        **Arguments**
        *gym:* Name of the gym. Must be wrapped in quotes if multiple words.

        *hatch_time:* Date and time the EX Raid will begin.
            Does not need to be wrapped in quotes.
        
        **Example:** `!exraid "city park" April 9 1:00 PM`
        Reports an EX Raid at City Park beginning on April 9 at 1:00 PM.
        """
        if not hatch_time:
            raise InvalidTime
        zone = await ctx.tz()
        raid_id = next(snowflake.create())
        new_exraid = Raid(raid_id, ctx.bot, ctx.guild.id, ctx.channel.id, ctx.author.id, gym, level="EX", hatch=hatch_time, tz=zone)
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
    
    async def rsvp(self, ctx, status, bosses=[], total=None, *teamcounts):
        raid_id = await self.get_raidid(ctx)
        report_channel = ctx.bot.get_channel(ctx.report_channel_id)
        report_channel = ReportChannel(ctx.bot, report_channel)
        raid_lists = await report_channel.get_raid_lists()
        meowthuser = MeowthUser.from_id(ctx.bot, ctx.author.id)
        if status == 'cancel':
            return await meowthuser.cancel_rsvp(raid_id)
        if bosses:
            boss_ids = []
            for boss in bosses:
                boss_ids.append(boss.id)
        else:
            level = await self.get_raidlevel(ctx)
            boss_list = list(raid_lists[level].keys())
            boss_ids = boss_list
        if total or teamcounts:
            party = await meowthuser.party_list(total, *teamcounts)
            await meowthuser.set_party(party=party)
        else:
            party = await meowthuser.party()
        await meowthuser.rsvp(raid_id, status, bosses=boss_ids, party=party)
    
    async def mrsvp(self, ctx, status, total=None, *teamcounts):
        meetup = Meetup.by_channel[ctx.channel.id]
        meetup_id = meetup.id
        meowthuser = MeowthUser.from_id(ctx.bot, ctx.author.id)
        if status == 'cancel':
            return await meowthuser.cancel_mrsvp(meetup_id)
        if total or teamcounts:
            party = await meowthuser.party_list(total, *teamcounts)
            await meowthuser.set_party(party=party)
        else:
            party = await meowthuser.party()
        await meowthuser.meetup_rsvp(meetup, status, party=party)
    
    @command(aliases=['i', 'maybe'], category="RSVP")
    @raid_checks.raid_or_meetup()
    @raid_checks.bot_has_permissions()
    async def interested(self, ctx, bosses: commands.Greedy[Pokemon], total: typing.Optional[int]=None, *teamcounts):
        """RSVP as interested to the current raid or meetup.

        **Arguments**
        *bosses (optional):* Names of the bosses you are interested in.

        *total (optional):* Number of trainers you are bringing. Defaults to
            your last RSVP total, or 1.
        
        *teamcounts (optional):* Counts of each team in your group. Format:
            `3m 2v 1i` means 3 Mystic, 2 Valor, 1 Instinct.
        """
        if total and total < 1:
            return
        meetup = Meetup.by_channel.get(ctx.channel.id)
        if meetup:
            return await self.mrsvp(ctx, "maybe", total, *teamcounts)
        await self.rsvp(ctx, "maybe", bosses, total, *teamcounts)
        
    @command(aliases=['c', 'omw'], category="RSVP")
    @raid_checks.raid_or_meetup()
    @raid_checks.bot_has_permissions()
    async def coming(self, ctx, bosses: commands.Greedy[Pokemon], total: typing.Optional[int]=None, *teamcounts):
        """RSVP as on your way to the current raid or meetup.

       **Arguments**
        *bosses (optional):* Names of the bosses you are interested in.

        *total (optional):* Number of trainers you are bringing. Defaults to
            your last RSVP total, or 1.
        
        *teamcounts (optional):* Counts of each team in your group. Format:
            `3m 2v 1i` means 3 Mystic, 2 Valor, 1 Instinct.
        """
        if total and total < 1:
            return
        meetup = Meetup.by_channel.get(ctx.channel.id)
        if meetup:
            return await self.mrsvp(ctx, "coming", total, *teamcounts)
        await self.rsvp(ctx, "coming", bosses, total, *teamcounts)
    
    @command(aliases=['h'], category="RSVP")
    @raid_checks.raid_or_meetup()
    @raid_checks.bot_has_permissions()
    async def here(self, ctx, bosses: commands.Greedy[Pokemon], total: typing.Optional[int]=None, *teamcounts):
        """RSVP as being at the current raid or meetup.

        **Arguments**
        *bosses (optional):* Names of the bosses you are interested in.

        *total (optional):* Number of trainers you are bringing. Defaults to
            your last RSVP total, or 1.
        
        *teamcounts (optional):* Counts of each team in your group. Format:
            `3m 2v 1i` means 3 Mystic, 2 Valor, 1 Instinct.
        """
        if total and total < 1:
            return
        meetup = Meetup.by_channel.get(ctx.channel.id)
        if meetup:
            return await self.mrsvp(ctx, "here", total, *teamcounts)
        await self.rsvp(ctx, "here", bosses, total, *teamcounts)
    
    @command(aliases=['x'], category="RSVP")
    @raid_checks.raid_or_meetup()
    @raid_checks.bot_has_permissions()
    async def cancel(self, ctx):
        """Cancel your RSVP to the current raid or meetup."""
        meetup = Meetup.by_channel.get(ctx.channel.id)
        if meetup:
            return await self.mrsvp(ctx, "cancel")
        await self.rsvp(ctx, "cancel")
        

    @command(category="Raid Info")
    @raid_checks.raid_channel()
    @raid_checks.bot_has_permissions()
    async def counters(self, ctx):
        """Request your optimal counters for the current box from Pokebattler.

        Use `!pokebattler` before using this command to link your
        Pokebattler account.
        """
        raid = Raid.by_channel.get(str(ctx.channel.id))
        if not raid:
            return
        if raid.status != 'active':
            if len(raid.boss_list) > 1:
                raise RaidNotActive
        meowthuser = MeowthUser.from_id(ctx.bot, ctx.author.id)
        embed = await raid.counters_embed(meowthuser)
        await ctx.author.send(embed=embed)
        await raid.update_rsvp()
        
    @command(aliases=['starttime'], category="Raid RSVP")
    @raid_checks.raid_channel()
    @raid_checks.bot_has_permissions()
    async def group(self, ctx, *, group_time=None):
        """Create a group for the current raid.

        **Arguments**
        *group_time:* Number of minutes until the group
            will enter the raid.
        If group_time is omitted, Meowth will list the
        current groups and ask if the user would like to join one.
        """
        raid = Raid.by_channel.get(str(ctx.channel.id))
        if not raid:
            raise NotRaidChannel
        if not group_time:
            return await raid.raidgroup_ask(ctx.channel, ctx.author.id)
        ctx._tz = raid.tz
        group_table = ctx.bot.dbi.table('raid_groups')
        insert = group_table.insert()
        i = len(raid.group_list)
        if group_time.isdigit():
            stamp = time.time() + int(group_time)*60
            if stamp > raid.end:
                raise InvalidTime
            elif raid.hatch and stamp < raid.hatch:
                raise InvalidTime
        else:
            converter = time_converter()
            stamp = await converter.convert(ctx, group_time)
        if stamp > raid.end:
            raise InvalidTime
        elif raid.hatch and stamp < raid.hatch:
            raise InvalidTime
        grp_id = next(snowflake.create())
        d = {
            'raid_id': raid.id,
            'grp_id': grp_id,
            'starttime': stamp,
            'users': [],
            'est_power': 0
        }
        insert.row(**d)
        await insert.commit()
        raid.group_list = await raid.get_grp_list()
        for grp in raid.group_list:
            if grp['grp_id'] == grp_id:
                await raid.join_grp(ctx.author.id, grp)
    
    @command(aliases=['start'], category="Raid RSVP")
    @raid_checks.bot_has_permissions()
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
    @raid_checks.bot_has_permissions()
    async def weather(self, ctx, *, weather: Weather):
        """Report the weather at the current raid.

        If the raid is at a known gym, this command will update
        the weather at all other known gyms in the cell.
        Possible weather: sunny, clear, rainy, cloudy, partlycloudy, fog, snow, windy
        Use 'unknown' to remove the weather.
        """
        raid = Raid.by_channel.get(str(ctx.channel.id))
        if not raid:
            return
        return await raid.correct_weather(weather)
    
    @command(category="Raid Info")
    @raid_checks.raid_channel()
    @raid_checks.bot_has_permissions()
    @checks.is_mod()
    async def boss(self, ctx, *, boss: RaidBoss):
        """Correct the boss in an existing raid channel.

        Usable only by mods."""
        raid = Raid.by_channel.get(str(ctx.channel.id))
        if raid.status == 'egg':
            raise RaidNotActive
        elif raid.status == 'hatched':
            return await raid.report_hatch(boss.id)
        raid.pkmn = boss
        await raid.upsert()
        await raid.update_messages(content="The raid boss has been corrected!")
    
    @command(category="Raid Info")
    @raid_checks.raid_channel()
    @raid_checks.bot_has_permissions()
    @checks.is_mod()
    async def level(self, ctx, *, level):
        """Correct the raid level in an existing raid channel.

        Usable only by mods."""
        possible_levels = ['1', '2', '3', '4', '5', 'EX']
        if level not in possible_levels:
            return
        raid = Raid.by_channel.get(str(ctx.channel.id))
        if raid.status == 'active':
            raid.pkmn = None
            raid.hatch = raid.end
            raid.end = raid.hatch + 60*ctx.bot.raid_info.raid_times[level][1]
        raid.level = level
        await raid.upsert()
        await raid.update_messages(content="The raid level has been corrected!")
    
    @command(aliases=['location'], category="Raid Info")
    @raid_checks.raid_or_meetup()
    @raid_checks.bot_has_permissions()
    @checks.is_mod()
    async def gym(self, ctx, *, location):
        """Correct the raid gym in an existing raid channel.

        Usable only by mods."""
        try:
            raid = Raid.instances.get(ctx.raid_id)
        except AttributeError:
            meetup = Meetup.by_channel.get(ctx.channel.id)
            if meetup:
                ctx.report_channel_id = meetup.report_channel_id
                location = await POI.convert(ctx, location)
                meetup.location = location
                await meetup.upsert()
                embed = await meetup.meetup_embed()
                return await meetup.channel.send('The meetup location has been updated!', embed=embed)
        else:
            if raid:
                gym = await Gym.convert(ctx, location)
                raid.gym = gym
                await raid.upsert()
                return await raid.update_messages(content="The raid gym has been corrected!")
    
    @command(aliases=['move'], category="Raid Info")
    @raid_checks.raid_channel()
    @raid_checks.bot_has_permissions()
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
    @raid_checks.raid_or_meetup()
    @raid_checks.bot_has_permissions()
    async def timerset(self, ctx, *, newtime):
        """Set the raid's hatch time or expire time.

        If *newtime* is an integer, it is assumed
        to be the number of minutes until hatch/expire.
        Otherwise, Meowth attempts to parse newtime as a
        time.
        **Examples:** `!timerset 12:00 PM`
        `!timerset 5`
        """
        raid_or_meetup = Raid.by_channel.get(str(ctx.channel.id))
        if not raid_or_meetup:
            raid_or_meetup = Meetup.by_channel.get(ctx.channel.id)
            if not raid_or_meetup:
                return
        zone = raid_or_meetup.tz
        if newtime.isdigit():
            stamp = time.time() + 60*int(newtime)
        else:
            try:
                newdt = parse(newtime, settings={'TIMEZONE': zone, 'RETURN_AS_TIMEZONE_AWARE': True})
                if isinstance(raid_or_meetup, Raid):
                    oldstamp = raid_or_meetup.end
                elif isinstance(raid_or_meetup, Meetup):
                    oldstamp = raid_or_meetup.start
                olddt = raid_or_meetup.local_datetime(oldstamp)
                nowdt = raid_or_meetup.local_datetime(time.time())
                if newdt.date() == nowdt.date():
                    newdt = newdt.combine(olddt.date(), newdt.timetz())
                stamp = newdt.timestamp()
            except:
                raise
        try:
            raid_or_meetup.update_time(stamp)
        except:
            raise
        if isinstance(raid_or_meetup, Raid):
            raid = raid_or_meetup
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
            await ctx.channel.edit(topic=raid_or_meetup.channel_topic)
        elif isinstance(raid_or_meetup, Meetup):
            meetup = raid_or_meetup
            dt = datetime.fromtimestamp(meetup.start)
            local = meetup.local_datetime(meetup.start)
            timestr = local.strftime('%I:%M %p')
            datestr = local.strftime('%b %d')
            title = "Start Time Updated"
            details = f"This Meetup will start on {datestr} at {timestr}"
        has_embed = False
        for idstring in raid_or_meetup.message_ids:
            chn, msg = await ChannelMessage.from_id_string(self.bot, idstring)
            if not msg:
                continue
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
        raid_lists = await self.get_raid_lists()
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
                    try:
                        random_move_ctrs = data_20['randomMove']['defenders'][-6:]
                        estimator_20 = data_20['randomMove']['total']['estimator']
                        estimator_min = data_min['randomMove']['defenders'][-1]['total']['estimator']
                    except KeyError:
                        print(pkmnid)
                        print(weather)
                        continue
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
    @raid_checks.bot_has_permissions()
    async def train(self, ctx):
        """Reports a raid train.

        If used in a report channel, Meowth will
        ask for the first raid. If used in a raid channel,
        Meowth will assume the current raid to be the first raid.
        """
        report_channel = ReportChannel(self.bot, ctx.channel)
        data = await report_channel.get_all_raids()
        if not data:
            return await ctx.send('No raids reported!')
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
    @raid_checks.train_channel()
    @raid_checks.bot_has_permissions()
    async def next(self, ctx):
        """Switch the train channel to the next raid.

        The next raid is the raid which got the most reaction
        votes during the previous raid."""
        train = Train.by_channel.get(ctx.channel.id)
        if not train:
            return
        await train.finish_current_raid()
    
    @command(category="Raid Train")
    @raid_checks.train_channel()
    @raid_checks.bot_has_permissions()
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
    @raid_checks.train_channel()
    @raid_checks.bot_has_permissions()
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
    
    @command()
    @raid_checks.raid_channel()
    async def duplicate(self, ctx):
        """Report the current raid channel as a duplicate.
        Meowth will ask you to select from a list of raids of the same
        level or boss. Then Meowth will copy the RSVPs and raid groups 
        from the duplicate to the original."""
        raid = Raid.by_channel.get(str(ctx.channel.id))
        if not raid:
            return
        rchan = raid.report_channel
        report_channel = ReportChannel(ctx.bot, rchan)
        raid_ids = await report_channel.get_possible_duplicates(raid)
        raids = [Raid.instances.get(x) for x in raid_ids if Raid.instances.get(x)]
        summaries = [await x.summary_str() for x in raids if await x.summary_str()]
        if len(raids) == 1:
            old_raid = raids[0]
        else:
            react_list = formatters.mc_emoji(len(raids))
            choice_dict = dict(zip(react_list, raids))
            display_dict = dict(zip(react_list, summaries))
            embed = formatters.mc_embed(display_dict)
            dupask = await ctx.send('Which existing raid is this a duplicate of? Use the reactions to select from the choices below.', embed=embed)
            payload = await formatters.ask(ctx.bot, [dupask], user_list=[ctx.author.id],
                react_list=react_list)
            old_raid = choice_dict[str(payload.emoji)]
            await dupask.delete()
        rsvp_table = ctx.bot.dbi.table('raid_rsvp')
        update = rsvp_table.update
        update.where(raid_id=raid.id)
        update.values(raid_id=old_raid.id)
        try:
            await update.commit()
        except:
            pass
        groups_table = ctx.bot.dbi.table('raid_groups')
        update = groups_table.update
        update.where(raid_id=raid.id)
        update.values(raid_id=old_raid.id)
        await update.commit()
        await old_raid.update_rsvp()
        try:
            del Raid.instances[raid.id]
        except:
            pass
        for message_id in raid.message_ids:
            try:
                del Raid.by_message[message_id]
            except:
                pass
            chn, msg = await ChannelMessage.from_id_string(self.bot, message_id)
            try:
                await msg.delete()
            except:
                pass
        if raid.channel_ids:
            for chanid in raid.channel_ids:
                try:
                    del Raid.by_channel[chanid]
                except:
                    pass
                channel = self.bot.get_channel(int(chanid))
                if not channel:
                    continue
                t = Train.by_channel.get(int(chanid))
                if t:
                    continue
                await channel.delete()
        raid_table = self.bot.dbi.table('raids')
        query = raid_table.query.where(id=raid.id)
        self.bot.loop.create_task(query.delete())
    
    @command()
    @raid_checks.raid_or_meetup()
    @checks.is_mod()
    async def setstatus(self, ctx, user: discord.Member, status, 
        bosses: commands.Greedy[Pokemon], total: typing.Optional[int]=1, *teamcounts):
        """RSVP to a raid on behalf of another user. 
        
        Usable only by mods."""
        if total < 1:
            return
        possible_status = ['i', 'interested', 'maybe', 'c', 'coming', 'omw', 'h', 'here', 'x', 'cancel']
        if status not in possible_status:
            return
        ctx.author = user
        if status in ['i', 'interested', 'maybe']:
            status = 'maybe'
        elif status in ['c', 'coming', 'omw']:
            status = 'coming'
        elif status in ['h', 'here']:
            status = 'here'
        elif status in ['x', 'cancel']:
            status = 'cancel'
        meetup = Meetup.by_channel.get(ctx.channel.id)
        if meetup:
            if status == 'cancel':
                return await self.mrsvp(ctx, status)
            return await self.mrsvp(ctx, status, total, *teamcounts)
        if status == 'cancel':
            return await self.rsvp(ctx, status)
        await self.rsvp(ctx, status, bosses, total, *teamcounts)

