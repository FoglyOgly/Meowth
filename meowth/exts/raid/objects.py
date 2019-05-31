from meowth.exts.map import Gym, ReportChannel, Mapper, PartialPOI, POI
from meowth.exts.users import MeowthUser
from meowth.exts.pkmn import Pokemon, Move
from meowth.exts.weather import Weather
from meowth.exts.want import Want
from meowth.utils import formatters, snowflake
from meowth.utils.converters import ChannelMessage
from .errors import *
from .raid_checks import archive_category

import asyncio
import aiohttp
from datetime import datetime
from math import ceil
import discord
from discord.ext import commands
import time
from pytz import timezone

emoji_letters = ['🇦','🇧','🇨','🇩','🇪','🇫','🇬','🇭','🇮','🇯','🇰','🇱',
    '🇲','🇳','🇴','🇵','🇶','🇷','🇸','🇹','🇺','🇻','🇼','🇽','🇾','🇿'
]

class RaidBoss(Pokemon):

    def __init__(self, pkmn):
        self.bot = pkmn.bot
        self.id = pkmn.id
        self.form = pkmn.form
        self.shiny = False
        self.gender = None
        self.quickMoveid = pkmn.quickMoveid
        self.chargeMoveid = pkmn.chargeMoveid
        self.chargeMove2id = None

    async def boss_data(self):
        table = self.bot.dbi.table('raid_bosses')
        query = table.query
        query.where(pokemon_id=self.id)
        return await query.get()

    async def raid_level(self):
        boss_data = await self.boss_data()
        if not boss_data:
            return None
        boss_data = boss_data[0]
        level = boss_data['level']
        return level

    async def _shiny_available(self):
        if not await super()._shiny_available():
            return False
        elif await super()._evolves_from():
            return False
        return True
    
    @classmethod
    async def convert(cls, ctx, arg):
        pkmn = await Pokemon.convert(ctx, arg)
        return cls(pkmn)   


class Meetup:

    instances = dict()
    by_message = dict()
    by_channel = dict()

    def __new__(cls, meetup_id, *args, **kwargs):
        if meetup_id in cls.instances:
            return cls.instances[meetup_id]
        instance = super().__new__(cls)
        cls.instances[meetup_id] = instance
        return instance
    
    def __init__(self, meetup_id, bot, guild_id, channel_id, report_channel_id, location, start, tz):
        self.id = meetup_id
        self.bot = bot
        self.guild_id = guild_id
        self.report_channel_id = report_channel_id
        self.location = location
        self.start = start
        self.tz = tz
        self.message_ids = []
        self.channel_id = channel_id
        self.trainer_dict = {}
    
    def to_dict(self):
        if isinstance(self.location, POI):
            locid = str(self.location.id)
        else:
            locid = f'{self.location.city}/{self.location.arg}'
        d = {
            'id': self.id,
            'guild_id': self.guild_id,
            'report_channel_id': self.report_channel_id,
            'channel_id': self.channel_id,
            'location': locid,
            'start': self.start,
            'tz': self.tz,
            'message_ids': self.message_ids
        }
        return d
    
    @property
    def _data(self):
        table = self.bot.dbi.table('meetups')
        query = table.query.where(id=self.id)
        return query
    
    @property
    def _insert(self):
        table = self.bot.dbi.table('meetups')
        insert = table.insert
        d = self.to_dict()
        insert.row(**d)
        return insert
    
    async def upsert(self):
        insert = self._insert
        await insert.commit(do_update=True)

    @property
    def guild(self):
        return self.bot.get_guild(self.guild_id)
    
    @property
    def channel(self):
        return self.bot.get_channel(self.channel_id)
    
    @property
    def report_channel(self):
        return self.bot.get_channel(self.report_channel_id)
    
    async def get_trainer_dict(self):
        def data(rcrd):
            trainer = rcrd['user_id']
            status = rcrd.get('status')
            party = rcrd.get('party', [0,0,0,1])
            rcrd_dict = {
                'status': status,
                'party': party,
            }
            return trainer, rcrd_dict
        trainer_dict = {}
        user_table = self.bot.dbi.table('meetup_rsvp')
        query = user_table.query()
        query.where(meetup_id=self.id)
        rsvp_data = await query.get()
        for rcrd in rsvp_data:
            trainer, rcrd_dict = data(rcrd)
            trainer_dict[trainer] = rcrd_dict
        return trainer_dict
    
    async def update_rsvp(self, user_id=None, status=None):
        self.trainer_dict = await self.get_trainer_dict()
        has_embed = False
        for idstring in self.message_ids:
            chn, msg = await ChannelMessage.from_id_string(self.bot, idstring)
            if not msg:
                continue
            if not has_embed:
                meetup_embed = MeetupEmbed(msg.embeds[0])
                meetup_embed.status_str = self.status_str
                meetup_embed.team_str = self.team_str
                embed = meetup_embed.embed
                has_embed = True
            await msg.edit(embed=embed)
        if user_id and status:
            chn = self.channel
            if chn:
                rsvpembed = RSVPEmbed.from_meetup(self).embed
                guild = self.guild
                member = guild.get_member(user_id)
                if status == 'maybe':
                    display_status = 'is interested'
                elif status == 'coming':
                    display_status = 'is attending'
                elif status == 'here':
                    display_status = 'is at the meetup'
                elif status == 'cancel':
                    display_status = 'has canceled'
                else:
                    return
                content = f"{member.display_name} {display_status}!"
                newmsg = await chn.send(content, embed=rsvpembed)
    
    @property
    def react_list(self):
        status_reacts = list(self.bot.config.emoji.values())
        return status_reacts
    
    async def process_reactions(self, payload):
        user = self.bot.get_user(payload.user_id)
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        meowthuser = MeowthUser(self.bot, user)
        if payload.guild_id:
            guild = self.bot.get_guild(payload.guild_id)
            user = guild.get_member(user.id)
        trainer_dict = self.trainer_dict
        trainer_data = trainer_dict.get(payload.user_id, {})
        old_status = trainer_data.get('status')
        party = await meowthuser.party()
        if payload.emoji.is_custom_emoji():
            emoji = payload.emoji.id
        else:
            emoji = str(payload.emoji)
        if emoji not in self.react_list:
            return
        for k, v in self.bot.config.emoji.items():
            if v == emoji:
                new_status = k
        if isinstance(emoji, int):
            emoji = self.bot.get_emoji(emoji)
        await message.remove_reaction(emoji, user)
        if new_status != old_status:
            await meowthuser.meetup_rsvp(self, new_status, party=party)
    
    async def meetup_embed(self):
        return (await MeetupEmbed.from_meetup(self)).embed
    
    @staticmethod
    def status_dict(trainer_dict):
        d = {
            'maybe': 0,
            'coming': 0,
            'here': 0,
        }
        for trainer in trainer_dict:
            total = sum(trainer_dict[trainer]['party'])
            status = trainer_dict[trainer]['status']
            d[status] += total
        return d
    
    @property
    def status_str(self):
        status_str = self.status_string(self.bot, self.trainer_dict)
        return status_str
    
    @staticmethod
    def status_string(bot, trainer_dict):
        status_dict = Meetup.status_dict(trainer_dict)
        status_str = f"{bot.config.emoji['maybe']}: **{status_dict['maybe']}** | "
        status_str += f"{bot.config.emoji['coming']}: **{status_dict['coming']}** | "
        status_str += f"{bot.get_emoji(bot.config.emoji['here'])}: **{status_dict['here']}**"
        return status_str
    
    @staticmethod
    def team_dict(trainer_dict):
        d = {
            'mystic': 0,
            'instinct': 0,
            'valor': 0,
            'unknown': 0
        }
        for trainer in trainer_dict:
            bluecount = trainer_dict[trainer]['party'][0]
            yellowcount = trainer_dict[trainer]['party'][1]
            redcount = trainer_dict[trainer]['party'][2]
            unknowncount = trainer_dict[trainer]['party'][3]
            d['mystic'] += bluecount
            d['instinct'] += yellowcount
            d['valor'] += redcount
            d['unknown'] += unknowncount
        return d

    @property
    def team_str(self):
        team_str = self.team_string(self.bot, self.trainer_dict)
        return team_str

    @staticmethod
    def team_string(bot, trainer_dict):
        team_dict = Meetup.team_dict(trainer_dict)
        team_str = f"{bot.config.team_emoji['mystic']}: {team_dict['mystic']} | "
        team_str += f"{bot.config.team_emoji['instinct']}: {team_dict['instinct']} | "
        team_str += f"{bot.config.team_emoji['valor']}: {team_dict['valor']} | "
        team_str += f"{bot.config.team_emoji['unknown']}: {team_dict['unknown']}"
        return team_str
    
    @property
    def current_local_datetime(self):
        zone = self.tz
        localzone = timezone(zone)
        return datetime.now(tz=localzone)
    
    def local_datetime(self, stamp):
        zone = self.tz
        localzone = timezone(zone)
        return datetime.fromtimestamp(stamp, tz=localzone)
    
    @property
    def start_datetime(self):
        return self.local_datetime(self.start)
    
    def update_time(self, new_time: float):
        meetup_table = self.bot.dbi.table('meetups')
        update = meetup_table.update
        update.where(id=self.id)
        update.values(start=new_time)
        self.start = new_time
        self.bot.loop.create_task(update.commit())

    @classmethod
    async def from_data(cls, bot, data):
        if data['location'].isdigit():
            location = POI(bot, int(data['location']))
        else:
            city, arg = data['location'].split('/', 1)
            location = PartialPOI(bot, city, arg)
        meetup_id = data['id']
        guild_id = data['guild_id']
        report_channel_id = data['report_channel_id']
        start = data['start']
        tz = data['tz']
        channel_id = data['channel_id']
        meetup = cls(meetup_id, bot, guild_id, channel_id, report_channel_id, location, start, tz)
        message_ids = data['message_ids']
        meetup.message_ids = message_ids
        meetup.trainer_dict = await meetup.get_trainer_dict()
        cls.by_channel[channel_id] = meetup
        for msgid in meetup.message_ids:
            cls.by_message[msgid] = meetup
        return meetup


class Raid:

    instances = dict()
    by_message = dict()
    by_channel = dict()
    by_trainreport = dict()

    def __new__(cls, raid_id, *args, **kwargs):
        if raid_id in cls.instances:
            return cls.instances[raid_id]
        instance = super().__new__(cls)
        cls.instances[raid_id] = instance
        return instance

    def __init__(self, raid_id, bot, guild_id, report_channel_id, reporter_id, gym=None, level=None,
        pkmn: RaidBoss=None, hatch: float=None, end: float=None, tz: str=None, completed_by=[]):
        self.id = raid_id
        self.bot = bot
        self.guild_id = guild_id
        self.report_channel_id = report_channel_id
        self.gym = gym
        self.level = level
        self.pkmn = pkmn
        self.hatch = hatch
        if not self.pkmn:
            active_time = bot.raid_info.raid_times[level][1]
            self.end = hatch + active_time*60
        elif end:
            self.end = end
        self.trainer_dict = {}
        self.group_list = []
        self.tz = tz
        self.created = time.time()
        self.reporter_id = reporter_id
        self.monitor_task = None
        self.hatch_task = None
        self.expire_task = None
        self.train_msgs = []
        self._weather = "NO_WEATHER"
        self.completed_by = completed_by
    
    def __eq__(self, other):
        if isinstance(other, Raid):
            return self.id == other.id
        else:
            return False
    
    def __hash__(self):
        return hash(self.id)
    
    def to_dict(self):
        if isinstance(self.gym, Gym):
            gymid = str(self.gym.id)
        else:
            gymid = f'{self.gym.city}/{self.gym.arg}'
        d = {
            'id': self.id,
            'gym': gymid,
            'guild': self.guild_id,
            'report_channel': self.report_channel_id,
            'reporter_id': self.reporter_id,
            'level': self.level,
            'pkmn': (self.pkmn.id, self.pkmn.quickMoveid or None, self.pkmn.chargeMoveid or None) if self.pkmn else (None, None, None),
            'hatch': self.hatch,
            'endtime': self.end,
            'messages': self.message_ids,
            'channels': self.channel_ids,
            'tz': self.tz,
            'train_msgs': self.train_msgs,
            'completed_by': self.completed_by
        }
        return d
    
    @property
    def _data(self):
        table = self.bot.dbi.table('raids')
        query = table.query.where(id=self.id)
        return query
    
    @property
    def _insert(self):
        table = self.bot.dbi.table('raids')
        insert = table.insert
        d = self.to_dict()
        insert.row(**d)
        return insert
    
    async def upsert(self):
        insert = self._insert
        await insert.commit(do_update=True)
    
    @property
    def status(self):
        if self.hatch and time.time() < self.hatch:
            return "egg"
        elif not self.pkmn:
            return "hatched"
        elif time.time() < self.end:
            return "active"
        else:
            return "expired"
    
    @property
    def react_list(self):
        boss_reacts = formatters.mc_emoji(len(self.boss_list))
        status_reacts = list(self.bot.config.emoji.values())
        grp_reacts = [x['emoji'] for x in self.group_list]
        if self.status == 'egg':
            if len(self.boss_list) == 1:
                react_list = status_reacts
            else:
                react_list = boss_reacts + status_reacts
        elif self.status == 'hatched':
            react_list = []
        elif self.status == 'active':
            status_reacts.append('\u25b6')
            react_list = status_reacts
        else:
            return None
        react_list = react_list + grp_reacts
        react_list.append('\u2754')
        return react_list

    @property
    def max_hatch(self):
        level = self.level
        max_times = self.bot.raid_info.raid_times[level]
        return max_times[0]
    
    @property
    def max_active(self):
        level = self.level
        max_times = self.bot.raid_info.raid_times[level]
        return max_times[1]
    
    @property
    def guild(self):
        return self.bot.get_guild(self.guild_id)
    
    @property
    def report_channel(self):
        return self.bot.get_channel(self.report_channel_id)
    
    def update_time(self, new_time: float):
        if self.monitor_task:
            self.monitor_task.cancel()
        level = self.level
        max_times = self.bot.raid_info.raid_times[level]
        max_hatch = max_times[0]
        max_active = max_times[1]
        created = self.created
        if self.status == 'egg':
            if max_hatch:
                max_stamp = created + max_hatch*60
            else:
                max_stamp = None
            if (max_stamp and new_time < max_stamp) or not max_stamp:
                self.hatch = new_time
                self.end = new_time + max_active*60
            else:
                raise InvalidTime
        else:
            if not max_hatch:
                max_stamp = time.time() + max_active*60
            else:
                if not self.hatch:
                    max_hatch = 0
                max_stamp = created + max_active*60 + max_hatch*60
            if new_time < max_stamp:
                self.end = new_time
            else:
                raise InvalidTime
        raid_table = self.bot.dbi.table('raids')
        update = raid_table.update()
        update.where(id=self.id)
        update.values(hatch=self.hatch, endtime=self.end)
        self.bot.loop.create_task(update.commit())
        self.monitor_task = self.bot.loop.create_task(self.monitor_status())
    
    async def get_boss_list(self):
        level = self.level
        report_channel = ReportChannel(self.bot, self.report_channel)
        boss_lists = await report_channel.get_raid_lists()
        boss_list = list(boss_lists[level].keys())
        self.boss_list = boss_list
        return boss_list
    
    async def boss_list_str(self, weather=None):
        boss_names = []
        boss_list = await self.get_boss_list()
        boss_interest_dict = await self.boss_interest_dict()
        emoji = formatters.mc_emoji(len(boss_list))
        if not weather:
            weather = await self.weather()
        weather = Weather(self.bot, weather)
        for i in range(len(boss_list)):
            x = boss_list[i]
            interest = boss_interest_dict[x]
            boss = RaidBoss(Pokemon(self.bot, x))
            name = emoji[i]
            name += await boss.name()
            is_boosted = await boss.is_boosted(weather.value)
            if is_boosted:
                name += ' (Boosted)'
            type_emoji = await boss.type_emoji()
            shiny_available = await boss._shiny_available()
            if shiny_available:
                name += ' :sparkles:'
            boss_names.append(f"{name} {type_emoji}: **{interest}**")
        boss_list_str = "\n".join(boss_names)
        boss_list_str += "\n<:silph:548259248442703895>Boss list provided by [The Silph Road](https://thesilphroad.com/raid-bosses)"
        return boss_list_str
    
    @property
    def grps_str(self):
        ungrp = self.ungrp
        ungrp_est = str(round(ungrp['est_power']*100))
        grps_str = []
        groups = self.group_list
        if groups:
            for group in groups:
                emoji = group['emoji']
                dt = self.local_datetime(group['starttime'])
                time = dt.strftime('%I:%M %p')
                est = str(round(group['est_power']*100))
                if est != '0':
                    grp_str = f"{emoji}: Starting {time} ({est}%)"
                else:
                    grp_str = f"{emoji}: Starting {time}"
                grps_str.append(grp_str)
        if ungrp_est != '0':
            grps_str.append(f"\u2754: ({ungrp_est}%)")
        return "\n".join(grps_str) + '\u200b'
    
    async def raidgroup_ask(self, channel, user):
        member = self.guild.get_member(user)
        grps_str = self.grps_str
        embed = formatters.make_embed(title='Groups (Boss Damage Estimate)', content=grps_str)
        msg = await channel.send(f"{member.mention}: select a group from the list below!, or use \u2754 to remain ungrouped!", embed=embed)
        groups = self.group_list
        emoji_list = [x['emoji'] for x in groups]
        emoji_list += '\u2754'
        payload = await formatters.ask(self.bot, [msg], [user], react_list=emoji_list)
        if not payload:
            return await msg.delete()
        if payload.emoji.is_custom_emoji():
            emoji = payload.emoji.id
        else:
            emoji = str(payload.emoji)
        if emoji == '\u2754':
            await self.leave_grp(payload.user_id)
        for group in self.group_list:
            if emoji == group['emoji']:
                await self.join_grp(payload.user_id, group)

        
    
    @property
    def grpd_users(self):
        return [x for y in self.group_list for x in y['users']]
    
    def user_grp(self, user):
        for grp in self.group_list:
            if user in grp['users']:
                return grp
        return None
    
    def grp_is_here(self, grp):
        for user in grp['users']:
            status = self.trainer_dict.get(user, {}).get('status')
            if status != 'here':
                return False
        return True

    @property
    def ungrp(self):
        d = {'users': []}
        for x in self.trainer_dict:
            if x not in self.grpd_users:
                if self.trainer_dict[x]['status'] in ['coming', 'here']:
                    d['users'].append(x)
        d['est_power'] = self.grp_est_power(d)
        return d
    
    def grp_others(self, grp):
        d = {'users': []}
        for x in self.trainer_dict:
            if x not in grp['users']:
                if self.trainer_dict[x]['status'] in ['coming', 'here']:
                    d['users'].append(x)
        d['est_power'] = self.grp_est_power(d)
        if len(d['users']) == 0:
            return None
        return d
    
    @property
    def coming_grp(self):
        d = {'users': [x for x in self.trainer_dict if self.trainer_dict[x]['status'] == 'coming']}
        d['est_power'] = self.grp_est_power(d)
        return d

    @property
    def here_grp(self):
        d = {'users': [x for x in self.trainer_dict if self.trainer_dict[x]['status'] == 'here']}
        d['est_power'] = self.grp_est_power(d)
        d['emoji'] = self.bot.get_emoji(self.bot.config.emoji['here'])
        return d
    
    @property
    def pokebattler_url(self):
        pkmnid = self.pkmn.id
        url = f"https://www.pokebattler.com/raids/{pkmnid}"
        return url
        
    @staticmethod
    def pokebattler_data_url(pkmnid, level, att_level, weather):
        json_url = 'https://fight2.pokebattler.com/raids/defenders/'
        json_url += f"{pkmnid}/levels/RAID_LEVEL_{level}/attackers/levels/"
        json_url += f"{att_level}/strategies/CINEMATIC_ATTACK_WHEN_POSSIBLE/"
        json_url += f"DEFENSE_RANDOM_MC"
        json_url += f"?sort=ESTIMATOR&weatherCondition={weather}"
        json_url += "&dodgeStrategy=DODGE_REACTION_TIME"
        json_url += "&aggregation=AVERAGE&randomAssistants=-1"
        return json_url
    
    @staticmethod
    def user_pokebattler_data_url(pkmnid, level, pb_id, weather):
        json_url = 'https://fight2.pokebattler.com/raids/defenders/'
        json_url += f"{pkmnid}/levels/RAID_LEVEL_{level}/attackers/users/"
        json_url += f"{pb_id}/strategies/CINEMATIC_ATTACK_WHEN_POSSIBLE/"
        json_url += "DEFENSE_RANDOM_MC"
        json_url += f"?sort=ESTIMATOR&weatherCondition={weather}"
        json_url += "&dodgeStrategy=DODGE_REACTION_TIME"
        json_url += "&aggregation=AVERAGE&randomAssistants=-1"
        return json_url
    
    async def channel_name(self):
        if isinstance(self.gym, Gym):
            gym_name = await self.gym._name()
        else:
            gym_name = self.gym._name
        if self.pkmn:
            boss_name = await self.pkmn.name()
            return f"{boss_name}-{gym_name}"
        else:
            if self.status == 'hatched':
                return f"hatched-{self.level}-{gym_name}"
            else:
                return f"{self.level}-{gym_name}"
    
    @property
    def channel_topic(self):
        topic_str = ""
        if self.status == 'egg':
            hatchlocal = self.local_datetime(self.hatch)
            hatchtimestr = hatchlocal.strftime('%I:%M %p')
            hatchdatestr = hatchlocal.strftime('%b %d')
            if self.level == 'EX':
                topic_str += f"Hatches on {hatchdatestr} at {hatchtimestr} | "
            else:
                topic_str += f"Hatches at {hatchtimestr} | "
        endlocal = self.local_datetime(self.end)
        endtimestr = endlocal.strftime('%I:%M %p')
        enddatestr = endlocal.strftime('%b %d')
        if self.level == 'EX':
            topic_str += f"Ends on {enddatestr} at {endtimestr}"
        else:
            topic_str += f"Ends at {endtimestr}"
        return topic_str
    
    @property
    def current_local_datetime(self):
        zone = self.tz
        localzone = timezone(zone)
        return datetime.now(tz=localzone)
    
    def local_datetime(self, stamp):
        if not stamp:
            return None
        zone = self.tz
        if not zone:
            localzone = None
        else:
            localzone = timezone(zone)
        return datetime.fromtimestamp(stamp, tz=localzone)
    
    async def process_reactions(self, payload):
        user = self.bot.get_user(payload.user_id)
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        meowthuser = MeowthUser(self.bot, user)
        if payload.guild_id:
            guild = self.bot.get_guild(payload.guild_id)
            user = guild.get_member(user.id)
        trainer_dict = self.trainer_dict
        trainer_data = trainer_dict.get(payload.user_id, {})
        old_bosses = trainer_data.get('bosses', [])
        old_status = trainer_data.get('status')
        new_status = None
        party = await meowthuser.party()
        if payload.emoji.is_custom_emoji():
            emoji = payload.emoji.id
        else:
            emoji = str(payload.emoji)
        if emoji not in self.react_list:
            return
        if isinstance(emoji, str):
            for group in self.group_list:
                if emoji == group['emoji']:
                    await message.remove_reaction(emoji, user)
                    await self.join_grp(payload.user_id, group)
                    if not old_status or old_status == 'maybe':
                        new_status = 'coming'
        if emoji == '\u2754':
            await message.remove_reaction(emoji, user)
            return await formatters.get_raid_help('!', self.bot.user.avatar_url, user)
        if emoji == '❌':
            await message.remove_reaction(emoji, user)
            return await meowthuser.cancel_rsvp(self.id)
        if self.status == 'egg':
            boss_list = self.boss_list
            if len(boss_list) > 1:
                if self.react_list.index(emoji) <= len(boss_list) - 1:
                    new_status = 'maybe'
                    i = self.react_list.index(emoji)
                    bossid = boss_list[i]
                    if bossid not in old_bosses:
                        new_bosses = old_bosses + [bossid]
                    else:
                        new_bosses = old_bosses
                else:
                    for k, v in self.bot.config.emoji.items():
                        if v == emoji:
                            new_status = k
                    if old_bosses:
                        new_bosses = old_bosses
                    else:
                        new_bosses = boss_list
            else:
                for k, v in self.bot.config.emoji.items():
                    if v == emoji:
                        new_status = k
                if old_bosses:
                    new_bosses = old_bosses
                else:
                    new_bosses = boss_list
        elif self.status == 'active':
            if emoji == '\u25b6':
                if self.trainer_dict[payload.user_id]['status'] == 'here':
                    grp = self.user_grp(payload.user_id)
                    if not grp:
                        grp = self.here_grp
                    if self.channel_ids:
                        return await self.start_grp(grp, user, channel=channel)
                    else:
                        return await self.start_grp(grp, user)
                else:
                    return await message.remove_reaction(emoji, user)
            for k, v in self.bot.config.emoji.items():
                if v == emoji:
                    new_status = k
            new_bosses = []
        else:
            return
        if isinstance(emoji, int):
            emoji = self.bot.get_emoji(emoji)
        try:
            await message.remove_reaction(emoji, user)
        except:
            pass
        if not new_status:
            return
        if new_bosses != old_bosses or new_status != old_status:
            await meowthuser.rsvp(self.id, new_status, bosses=new_bosses, party=party)
    
    async def start_grp(self, grp, author, channel=None):
        if not self.grp_is_here(grp):
            if channel:
                return await channel.send('Please wait until your whole group is here!')
        else:
            mention_str = ""
            if self.grp_total(grp) > 20:
                raise GroupTooBig
            if not channel:
                for user in grp['users']:
                    meowthuser = MeowthUser.from_id(self.bot, user)
                    party = await meowthuser.party()
                    await meowthuser.rsvp(self.id, "lobby", party=party)
                await self.update_rsvp()
                await asyncio.sleep(120)
                rsvp_table = self.bot.dbi.table('raid_rsvp')
                query = user_table.query().where(user_table['user_id'].in_(grp['users']))
                query.where(raid_id=self.id)
                await query.delete()
                if grp in self.group_list:
                    self.group_list.remove(grp)
                    grp_table = self.bot.dbi.table('raid_groups')
                    grp_query = grp_table.query
                    grp_query.where(raid_id=self.id)
                    grp_query.where(starttime=grp['starttime'])
                    await grp_query.delete()
                for user in grp['users']:
                    if user not in self.completed_by:
                        self.completed_by.append(user)
                await self.upsert()
                return await self.update_rsvp()
            grp_est = self.grp_est_power(grp)
            if grp_est < 1:
                msg = await channel.send('Your current group may not be able to win the raid on your own! If you want to go ahead anyway, react to this message with the check mark!')
                payload = await formatters.ask(self.bot, [msg], user_list = author.id)
                if not payload or str(payload.emoji) == '❎':
                    rec_size = await self.rec_group_size()
                    return await channel.send(f'The recommended group size for this raid is {rec_size}!')
            elif grp_est > 3:
                msg = await channel.send('Your current group could possibly split into smaller groups and still win the raid! If you want to go ahead anyway, react to this message with the check mark!')
                payload = await formatters.ask(self.bot, [msg], user_list = author.id)
                if not payload or str(payload.emoji) == '❎':
                    rec_size = await self.rec_group_size()
                    return await channel.send(f'The recommended group size for this raid is {rec_size}!')
            grp_others = self.grp_others(grp)
            if grp_others:
                others_est = self.grp_est_power(grp_others)
                if others_est < 1:
                    msg = await channel.send("The trainers not in this group may not be able to win the raid on their own! Please consider including them. If you want to go ahead anyway, react to this message with the check mark.")
                    payload = await formatters.ask(self.bot, [msg], user_list = author.id)
                    if not payload or str(payload.emoji) == '❎':
                        return await channel.send('Thank you for waiting!')
            for user in grp['users']:
                meowthuser = MeowthUser.from_id(self.bot, user)
                mention = meowthuser.user.mention + " "
                mention_str += mention
                party = await meowthuser.party()
                await meowthuser.rsvp(self.id, "lobby", party=party)
            await self.update_rsvp()
            msg_list = []
            for chn in self.channel_ids:
                chan = self.bot.get_channel(int(chn))
                lobbymsg = await chan.send(f"{mention_str}: Group {grp['emoji']} is entering the lobby! Other trainers: you can join them by reacting with ▶, or ask them to backout with ⏸")
                msg_list.append(lobbymsg)
            starttime = time.time() + 120
            while time.time() < starttime:
                payload = await formatters.ask(self.bot, msg_list, timeout=starttime-time.time(), react_list=['▶','⏸'])
                if payload and str(payload.emoji) == '▶':
                    user_id = payload.user_id
                    react_channel = self.bot.get_channel(payload.channel_id)
                    if self.trainer_dict[user_id]['status'] != 'here':
                        await react_channel.send('You must be at the raid to join the lobby!')
                        continue
                    grp['users'].append(user_id)
                    meowthuser = MeowthUser.from_id(self.bot, user_id)
                    party = await meowthuser.party()
                    await meowthuser.rsvp(self.id, "lobby", party=party)
                    await react_channel.send(f'{meowthuser.user.display_name} has entered the lobby!')
                    await self.update_rsvp()
                    continue
                elif payload and str(payload.emoji) == '⏸':
                    for user in grp['users']:
                        meowthuser = MeowthUser.from_id(self.bot, user)
                    backoutmsg = await channel.send(f'{mention_str}: A backout has been requested! Please confirm by reacting with ✅')
                    backoutload = await formatters.ask(self.bot, [backoutmsg], timeout=starttime-time.time())
                    if backoutload and str(backoutload.emoji) == '✅':
                        for user in grp['users']:
                            meowthuser = MeowthUser.from_id(self.bot, user)
                            party = await meowthuser.party()
                            await meowthuser.rsvp(self.id, "here", party=party)
                        for chn in self.channel_ids:
                            chan = self.bot.get_channel(int(chn))
                            await chan.send(f"Group {grp['emoji']} has backed out! Be sure to thank them!")
                        await self.update_rsvp()
                        return
                    else:
                        continue
                else:
                    await lobbymsg.edit(content=f"Group {grp['emoji']} has entered the raid!")
            for user in grp['users']:
                    if user not in self.completed_by:
                        self.completed_by.append(user)
            await self.upsert()
            user_table = self.bot.dbi.table('raid_rsvp')
            query = user_table.query.where(user_table['user_id'].in_(grp['users']))
            query.where(raid_id=self.id)
            await query.delete()
            if grp in self.group_list:
                self.group_list.remove(grp)
                grp_table = self.bot.dbi.table('raid_groups')
                grp_query = grp_table.query
                grp_query.where(raid_id=self.id)
                grp_query.where(starttime=grp['starttime'])
                await grp_query.delete()
            await self.update_rsvp()
            return                

    def _rsvp(self, connection, pid, channel, payload):
        if channel != f'rsvp_{self.id}':
            return
        event_loop = asyncio.get_event_loop()
        if payload == 'power' or payload == 'bosses':
            event_loop.create_task(self.update_rsvp())
            return
        userid, status = payload.split('/')
        user_id = int(userid)
        event_loop.create_task(self.update_rsvp(user_id=user_id, status=status))
    
    def _weather(self, connection, pid, channel, payload):
        if not isinstance(self.gym, Gym):
            return
        event_loop = asyncio.get_event_loop()
        event_loop.create_task(self.change_weather(payload))
    
    async def change_weather(self, payload):
        weather = Weather(self.bot, payload)
        weather_name = await weather.name()
        emoji = await weather.boosted_emoji_str()
        weather_str = weather_name + " " + emoji
        if self.status == 'active':
            is_boosted = await self.pkmn.is_boosted(weather.value)
            cp_range = await self.cp_range(weather=weather.value)
            cp_str = f"{cp_range[0]}-{cp_range[1]}"
            ctrs_list = await self.generic_counters_data(weather=weather.value)
            ctrs_str = []
            if ctrs_list:
                for ctr in ctrs_list:
                    name = await ctr.name()
                    fast = Move(self.bot, ctr.quickMoveid)
                    fast_name = await fast.name()
                    if await fast.is_legacy(ctr.id):
                        fast_name += " (Legacy)"
                    fast_emoji = await fast.emoji()
                    charge = Move(self.bot, ctr.chargeMoveid)
                    charge_name = await charge.name()
                    if await charge.is_legacy(ctr.id):
                        charge_name += " (Legacy)"
                    charge_emoji = await charge.emoji()
                    ctr_str = f"**{name}**: {fast_name} {fast_emoji} | {charge_name} {charge_emoji}"
                    ctrs_str.append(ctr_str)
                ctrs_str.append(f'[Results courtesy of Pokebattler](https://www.pokebattler.com/raids/{self.pkmn.id})')
                ctrs_str = "\n".join(ctrs_str)
                rec_str = await self.rec_group_size(weather=weather.value)
            else:
                ctrs_str = "Currently unavailable"
                rec_str = None
        elif self.status == 'egg':
            boss_str = await self.boss_list_str(weather=weather.value)
        has_embed = False
        for idstring in self.message_ids:
            chn, msg = await ChannelMessage.from_id_string(self.bot, idstring)
            if not msg:
                continue
            if not str(chn.id) in self.channel_ids:
                continue
            if not has_embed:
                if self.status == 'active':
                    raid_embed = RaidEmbed(msg.embeds[0])
                    raid_embed.set_weather(weather_str, cp_str, ctrs_str, rec_str)
                    embed = raid_embed.embed
                    has_embed = True
                elif self.status == 'egg' or self.status == 'hatched':
                    egg_embed = EggEmbed(msg.embeds[0])
                    egg_embed.set_weather(weather_str, boss_str)
                    embed = egg_embed.embed
                    has_embed = True
            await msg.edit(embed=embed)
    
    async def join_grp(self, user_id, group):
        old_rsvp = self.trainer_dict.get(user_id, {})
        old_status = old_rsvp.get('status')
        if not old_status or old_status == 'maybe':
            meowthuser = MeowthUser.from_id(self.bot, user_id)
            party = await meowthuser.party()
            bosses = old_rsvp.get('bosses')
            if not bosses:
                bosses = await self.get_boss_list()
            await meowthuser.rsvp(self.id, "coming", bosses=bosses, party=party)
        group_table = self.bot.dbi.table('raid_groups')
        insert = group_table.insert()
        old_query = group_table.query()
        old_query.where(raid_id=self.id)
        old_query.where(group_table['users'].contains_(user_id))
        old_grp = await old_query.get()
        if old_grp:
            old_grp = dict(old_grp[0])
            if old_grp['grp_id'] == group['grp_id']:
                return
            old_grp['users'].remove(user_id)
            old_grp['est_power'] = self.grp_est_power(old_grp)
            if len(old_grp['users']) == 0:
                del_query = group_table.query
                del_query.where(raid_id=self.id)
                del_query.where(grp_id=old_grp['grp_id'])
                await del_query.delete()
            else:
                insert.row(**old_grp)
        group['users'].append(user_id)
        group['est_power'] = self.grp_est_power(group)
        d = {
            'raid_id': self.id,
            'grp_id': group['grp_id'],
            'starttime': group['starttime'],
            'users': group['users'],
            'est_power': group['est_power']
        }
        insert.row(**d)
        await insert.commit(do_update=True)
        await self.update_rsvp(user_id=user_id, group=group)
    
    async def leave_grp(self, user_id):
        group_table = self.bot.dbi.table('raid_groups')
        insert = group_table.insert
        old_query = group_table.query
        old_query.where(raid_id=self.id)
        old_query.where(group_table['users'].contains_(user_id))
        old_grp = await old_query.get()
        if not old_grp:
            return
        old_grp = dict(old_grp[0])
        old_grp['users'].remove(user_id)
        old_grp['est_power'] = self.grp_est_power(old_grp)
        if len(old_grp['users']) == 0:
            del_query = group_table.query
            del_query.where(raid_id=self.id)
            del_query.where(grp_id=old_grp['grp_id'])
            await del_query.delete()
        else:
            insert.row(**old_grp)
            await insert.commit(do_update=True)
        await self.update_rsvp()
    

    async def update_rsvp(self, user_id=None, status=None, group=None):
        self.trainer_dict = await self.get_trainer_dict()
        self.group_list = await self.get_grp_list()
        if self.status == 'active':
            estimator_20 = await self.estimator_20()
        else:
            estimator_20 = None
        has_embed = False
        has_report_embed = False
        for idstring in self.message_ids:
            chn, msg = await ChannelMessage.from_id_string(self.bot, idstring)
            if not msg:
                continue
            group_emojis = [x['emoji'] for x in self.group_list]
            msg_reactions = msg.reactions
            msg_emojis = [x.emoji for x in msg_reactions]
            for reaction in msg_reactions:
                emoji = reaction.emoji
                if '\u20e3' not in str(emoji):
                    continue
                if emoji not in group_emojis:
                    try:
                        await reaction.remove(self.guild.me)
                    except:
                        pass
            for emoji in group_emojis:
                if emoji not in msg_emojis:
                    await msg.add_reaction(emoji)
            if self.channel_ids and str(chn.id) not in self.channel_ids:
                if not has_report_embed:
                    report_embed = await self.report_embed()
                    has_report_embed = True
                await msg.edit(embed=report_embed)
                continue
            if not has_embed:
                if self.status == 'active':
                    raid_embed = RaidEmbed(msg.embeds[0])
                    raid_embed.status_str = self.status_str
                    raid_embed.team_str = self.team_str
                    if estimator_20:
                        raid_embed.grps_str = "Groups (Boss Damage Estimate)", self.grps_str
                    else:
                        raid_embed.grps_str = "Groups", self.grps_str
                    embed = raid_embed.embed
                    has_embed = True
                elif self.status == 'egg':
                    egg_embed = EggEmbed(msg.embeds[0])
                    egg_embed.status_str = self.status_str
                    egg_embed.team_str = self.team_str
                    egg_embed.boss_str = await self.boss_list_str()
                    egg_embed.grps_str = "Groups", self.grps_str
                    embed = egg_embed.embed
                    has_embed = True
                else:
                    return
            await msg.edit(embed=embed)
        if user_id and status:
            if self.channel_ids:
                for chnid in self.channel_ids:
                    chn = self.bot.get_channel(int(chnid))
                    if not chn:
                        continue
                    rsvpembed = RSVPEmbed.from_raid(self).embed
                    guild = self.bot.get_guild(self.guild_id)
                    member = guild.get_member(user_id)
                    if status == 'maybe':
                        display_status = 'is interested'
                    elif status == 'coming':
                        display_status = 'is on the way'
                    elif status == 'here':
                        display_status = 'is at the raid'
                    elif status == 'cancel':
                        display_status = 'has canceled'
                    else:
                        break
                    content = f"{member.display_name} {display_status}!"
                    newmsg = await chn.send(content, embed=rsvpembed)
                    if self.group_list:
                        grp = self.user_grp(member.id)
                        if not grp and status in ('coming', 'here'):
                            return await self.raidgroup_ask(chn, member.id)
        elif user_id and group:
            if self.channel_ids:
                for chnid in self.channel_ids:
                    chn = self.bot.get_channel(int(chnid))
                    if not chn:
                        continue
                    rsvpembed = RSVPEmbed.from_raidgroup(self, group).embed
                    guild = self.bot.get_guild(self.guild_id)
                    member = guild.get_member(user_id)
                    content = f"{member.display_name} has joined Group {group['emoji']}!"
                    newmsg = await chn.send(content, embed=rsvpembed)
        
    
    async def monitor_status(self):
        try:
            hatch = self.hatch
            end = self.end
            if not self.pkmn:
                sleeptime = hatch - time.time()
                await asyncio.sleep(sleeptime)
                if getattr(self, 'hatch_routine', False):
                    return
                self.hatch_task = self.bot.loop.create_task(self.hatch_egg())
                return
            else:
                sleeptime = end - time.time()
                await asyncio.sleep(sleeptime)
                self.expire_task = self.bot.loop.create_task(self.expire_raid())
                return
        except asyncio.CancelledError:
            if self.hatch_task:
                self.hatch_task.cancel()
            elif self.expire_task:
                self.expire_task.cancel()
        

    
    async def weather(self):
        gym = self.gym
        if isinstance(gym, Gym):
            weather = await gym.weather()
            self._weather = weather
        return self._weather
    
    async def is_boosted(self, weather=None):
        if not weather:
            weather = await self.weather()
        pkmn = self.pkmn
        if not pkmn:
            boss_list = self.boss_list
            if len(boss_list) == 1:
                pkmn = RaidBoss(Pokemon(self.bot, boss_list[0]))
        return await pkmn.is_boosted(weather)
    
    async def cp_range(self, weather=None):
        boost = await self.is_boosted(weather=weather)
        pkmn = self.pkmn
        if not pkmn:
            boss_list = self.boss_list
            if len(boss_list) == 1:
                pkmn = RaidBoss(Pokemon(self.bot, boss_list[0]))
        if boost:
            pkmn.lvl = 25
        else:
            pkmn.lvl = 20
        pkmn.attiv = 10
        pkmn.defiv = 10
        pkmn.staiv = 10
        low_cp = await pkmn.calculate_cp()
        pkmn.attiv = 15
        pkmn.defiv = 15
        pkmn.staiv = 15
        high_cp = await pkmn.calculate_cp()
        return [low_cp, high_cp]
    
    async def pb_data(self, weather=None):
        data_table = self.bot.dbi.table('counters_data')
        if not weather:
            weather = await self.weather()
        boss = self.pkmn
        if not boss:
            boss_list = self.boss_list
            if len(boss_list) == 1:
                boss = RaidBoss(Pokemon(self.bot, boss_list[0]))
        boss_id = boss.id
        level = self.level
        query = data_table.query().select().where(
            boss_id=boss_id, weather=weather, level=level)
        if boss.quickMoveid:
            fast_move_id = boss.quickMoveid
            query.where(fast_move=boss.quickMoveid)
        else:
            fast_move_id = 'random'
        if boss.chargeMoveid:
            charge_move_id = boss.chargeMoveid
            query.where(charge_move=boss.chargeMoveid)
        else:
            charge_move_id = 'random'
        if fast_move_id == 'random' and charge_move_id == 'random':
            query.where(fast_move='random', charge_move='random')
        data = await query.get()
        if data:
            return data[0]
        else:
            return None
    
    async def generic_counters_data(self, weather=None):
        data = await self.pb_data(weather=weather)
        if not data:
            return None
        ctrs_list = []
        for x in range(1,7):
            ctrid = data[f'counter_{x}_id']
            ctrfast = data[f'counter_{x}_fast']
            ctrcharge = data[f'counter_{x}_charge']
            ctr = Pokemon(self.bot, ctrid, quickMoveid=ctrfast, chargeMoveid=ctrcharge)
            ctrs_list.append(ctr)
        return ctrs_list
    
    async def estimator_20(self, weather=None):
        data = await self.pb_data(weather=weather)
        if not data:
            return None
        estimator = data['estimator_20']
        return estimator
    
    async def estimator_min(self, weather=None):
        data = await self.pb_data(weather=weather)
        if not data:
            return None
        estimator = query_dict['estimator_min']
        return estimator
    
    async def rec_group_size(self, weather=None):
        estimator = await self.estimator_20(weather=weather)
        if not estimator:
            return None
        return ceil(estimator)
    
    async def min_group_size(self):
        estimator = await self.estimator_min()
        if not estimator:
            return None
        return ceil(estimator)
    
    def user_est_power(self, user_id):
        trainer_dict = self.trainer_dict.get(user_id)
        if trainer_dict:
            est_power = trainer_dict.get('est_power', 0)
            return est_power
        else:
            return 0
    
    def grp_est_power(self, group):
        est = 0
        users = group['users']
        for user in users:
            est_power = self.user_est_power(user)
            est += est_power
        return est

    async def user_counters_data(self, user: MeowthUser):
        pkmn = self.pkmn
        if not pkmn:
            boss_list = self.boss_list
            if len(boss_list) == 1:
                    pkmn = RaidBoss(Pokemon(self.bot, boss_list[0]))
        pkmnid = pkmn.id
        level = self.level
        if level == 'EX':
            url_level = 5
        else:
            url_level = level
        pb_id = await user.pokebattler()
        if not pb_id:
            return await self.generic_counters_data()
        weather = await self.weather()
        data_url = self.user_pokebattler_data_url(
            pkmnid, url_level, pb_id, weather
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(data_url) as resp:
                try:
                    data = await resp.json()
                    data = data['attackers'][0]
                except KeyError:
                    pass
        boss_fast = pkmn.quickMoveid
        boss_charge = pkmn.chargeMoveid
        if not (boss_fast and boss_charge):
            ctrs = data['randomMove']['defenders'][-6:]
            estimator = data['randomMove']['total']['estimator']
        elif (boss_fast and boss_charge):
            for moveset in data['byMove']:
                if moveset['move1'] == boss_fast and moveset['move2'] == boss_charge:
                    ctrs = moveset['defenders'][-6:]
                    estimator = moveset['total']['estimator']
                else:
                    continue
        else:
            for moveset in data['byMove']:
                if moveset['move2'] == boss_charge or moveset['move1'] == boss_fast:
                    ctrs = moveset['defenders'][-6:]
                    estimator = moveset['total']['estimator']
                else:
                    continue
        ctrs_list = []
        est_20 = await self.estimator_20()
        for ctr in reversed(ctrs):
            ctrid = ctr['pokemonId']
            ctr_nick = ctr.get('name')
            moveset = ctr['byMove'][-1]
            fast_move = moveset['move1']
            charge_move = moveset['move2']
            charge_move_2 = moveset.get('move3')
            if charge_move_2 == 'MOVE_NONE':
                charge_move_2 = None
            cp = ctr['cp']
            counter = Pokemon(self.bot, ctrid, cp=cp, quickMoveid=fast_move,
                chargeMoveid=charge_move, chargeMove2id=charge_move_2)
            if ctr_nick:
                counter.nick = ctr_nick
            ctrs_list.append(counter)
        if estimator < est_20:
            await user.set_estimator(self.id, estimator, est_20)
            self.trainer_dict = await self.get_trainer_dict()
        return ctrs_list

    async def set_moveset(self, move1, move2=None):
        fast = self.pkmn.quickMoveid or None
        charge = self.pkmn.chargeMoveid or None
        if await move1._fast():
            fast = move1.id
        else:
            charge = move1.id
        if move2:
            if await move2._fast():
                fast = move2.id
            else:
                charge = move2.id
        self.pkmn.quickMoveid = fast
        self.pkmn.chargeMoveid = charge
        self.pkmn = await self.pkmn.validate('raid')
        quick_move = Move(self.bot, fast) if fast else None
        charge_move = Move(self.bot, charge) if charge else None
        if quick_move:
            self.pkmn.quickMoveid = quick_move.id
            quick_name = await quick_move.name()
            quick_emoji = await quick_move.emoji()
        else:
            quick_name = "Unknown"
            quick_emoji = ""
        if charge_move:
            self.pkmn.chargeMoveid = charge_move.id
            charge_name = await charge_move.name()
            charge_emoji = await charge_move.emoji()
        else:
            charge_name = "Unknown"
            charge_emoji = ""
        moveset_str = f"{quick_name} {quick_emoji}| {charge_name} {charge_emoji}"
        ctrs_list = await self.generic_counters_data()
        ctrs_str = []
        for ctr in ctrs_list:
            name = await ctr.name()
            fast = Move(self.bot, ctr.quickMoveid)
            fast_name = await fast.name()
            if await fast.is_legacy(ctr.id):
                fast_name += " (Legacy)"
            fast_emoji = await fast.emoji()
            charge = Move(self.bot, ctr.chargeMoveid)
            charge_name = await charge.name()
            if await charge.is_legacy(ctr.id):
                charge_name += " (Legacy)"
            charge_emoji = await charge.emoji()
            ctr_str = f"**{name}**: {fast_name} {fast_emoji} | {charge_name} {charge_emoji}"
            ctrs_str.append(ctr_str)
        ctrs_str.append(f'[Results courtesy of Pokebattler](https://www.pokebattler.com/raids/{self.pkmn.id})')
        ctrs_str = "\n".join(ctrs_str)
        rec = await self.rec_group_size()
        rec_str = str(rec)
        moveset_embed = discord.Embed(description=moveset_str)
        has_embed = False
        for idstring in self.message_ids:
            chn, msg = await ChannelMessage.from_id_string(self.bot, idstring)
            if not msg:
                continue
            if self.channel_ids and str(chn.id) not in self.channel_ids:
                continue
            if not has_embed:
                raid_embed = RaidEmbed(msg.embeds[0])
                raid_embed.set_moveset(moveset_str, ctrs_str, rec_str)
                embed = raid_embed.embed
                has_embed = True
            await msg.edit(embed=embed)
        if self.channel_ids:
            for chanid in self.channel_ids:
                channel = self.bot.get_channel(int(chanid))
                await channel.send("This raid boss's moveset has been updated!",embed=moveset_embed)

    async def egg_embed(self):
        return (await EggEmbed.from_raid(self)).embed
    
    async def counters_embed(self, user):
        countersembed = await CountersEmbed.from_raid(user, self)
        if not countersembed:
            return None
        return countersembed.embed
    
    async def hatched_embed(self):
        raid_icon = 'https://media.discordapp.net/attachments/423492585542385664/512682888236367872/imageedit_1_9330029197.png'
        footer_icon = 'https://media.discordapp.net/attachments/346766728132427777/512699022822080512/imageedit_10_6071805149.png'
        level = self.level
        egg_img_url = self.bot.raid_info.egg_images[level]
        # color = await formatters.url_color(egg_img_url)
        boss_list = self.boss_list
        end = self.end
        enddt = datetime.fromtimestamp(end)
        gym = self.gym
        if isinstance(gym, Gym):
            directions_url = await gym.url()
            directions_text = await gym._name()
            exraid = await gym._exraid()
        else:
            directions_url = gym.url
            directions_text = gym._name + " (Unknown Gym)"
            exraid = False
        if exraid:
            directions_text += " (EX Raid Gym)"
        weather = await self.weather()
        weather = Weather(self.bot, weather)
        weather_name = await weather.name()
        weather_emoji = await weather.boosted_emoji_str()
        boss_names = []
        for i in range(len(boss_list)):
            x = boss_list[i]
            boss = RaidBoss(Pokemon(self.bot, x))
            name = await boss.name()
            type_emoji = await boss.type_emoji()
            shiny_available = await boss._shiny_available()
            if shiny_available:
                name += ':sparkles:'
            boss_names.append(f"{name} {type_emoji}")
        length = len(boss_list)
        react_list = formatters.mc_emoji(length)
        choice_list = [react_list[i] + ' ' + boss_names[i] for i in range(len(react_list))]
        half_length = ceil(len(boss_names)/2)
        bosses_left = choice_list[:(half_length)]
        bosses_right = choice_list[(half_length):]
        fields = {
            "Weather": (False, f"{weather_name} {weather_emoji}"),
            "Possible Bosses:": "\n".join(bosses_left),
            "\u200b": "\n".join(bosses_right)
        }
        footer_text = "Ending"
        embed = formatters.make_embed(icon=raid_icon, title=directions_text,
            thumbnail=egg_img_url, title_url=directions_url, # msg_colour=color,
            fields=fields, footer=footer_text, footer_icon=footer_icon)
        embed.timestamp = enddt
        return embed

    async def raid_embed(self):
        return (await RaidEmbed.from_raid(self)).embed

    def expired_embed(self):
        embed = formatters.make_embed(content="This raid has expired!", footer="Expired")
        embed.timestamp = datetime.fromtimestamp(self.end)
        return embed
    
    async def report_embed(self):
        return (await ReportEmbed.from_raid(self)).embed

    
    async def update_messages(self, content=''):
        msg_list = []
        await self.get_boss_list()
        react_list = self.react_list
        message_ids = self.message_ids
        train_msgs = self.train_msgs
        if self.hatch and self.hatch > time.time():
            embed = await self.egg_embed()
        elif self.end > time.time():
            embed = await self.raid_embed()
        else:
            embed = self.expired_embed()
        for messageid in message_ids:
            chn, msg = await ChannelMessage.from_id_string(self.bot, messageid)
            if not msg:
                continue
            if self.channel_ids and str(chn.id) not in self.channel_ids and self.status != 'expired':
                report_embed = await self.report_embed()
                try:
                    await msg.edit(content=content, embed=report_embed)
                except:
                    pass
                msg_list.append(msg)
                continue
            try:
                await msg.edit(content=content, embed=embed)
            except Exception as e:
                continue
            try:
                await msg.clear_reactions()
            except discord.Forbidden:
                continue
            msg_list.append(msg)
        for msgid in train_msgs:
            chn, msg = await ChannelMessage.from_id_string(self.bot, messageid)
            if not msg:
                continue
            t = Train.by_channel.get(chn.id)
            if not t:
                continue
            train_embed = await TRaidEmbed.from_raid(t, self)
            train_content = "Use the reaction below to vote for this raid next!"
            await msg.edit(content=train_content, embed=train_embed.embed)
            try:
                await msg.clear_reactions()
            except discord.Forbidden:
                raise commands.BotMissingPermissions(['Manage Messages'])
            await msg.add_reaction('\u2b06')
        if self.channel_ids:
            for chanid in self.channel_ids:
                channel = self.bot.get_channel(int(chanid))
                if not channel:
                    continue
                t = Train.by_channel.get(int(chanid))
                if t:
                    continue
                new_name = await self.channel_name()
                new_topic = self.channel_topic
                if new_name != channel.name:
                    try:
                        await channel.edit(name=new_name, topic=new_topic)
                    except discord.Forbidden:
                        raise commands.BotMissingPermissions(['Manage Channels'])
                await channel.send(content, embed=embed)
        if react_list:
            for msg in msg_list:
                for react in react_list:
                    if isinstance(react, int):
                        react = self.bot.get_emoji(react)
                    await msg.add_reaction(react)
        return msg_list

    
    
    async def hatch_egg(self):
        try:
            if self.end < time.time():
                self.bot.loop.create_task(self.expire_raid())
                return
            content = "This raid egg has hatched! React below to report the boss!"
            msg_list = []
            boss_list = await self.get_boss_list()
            length = len(boss_list)
            if length == 1:
                return await self.report_hatch(boss_list[0])
            react_list = formatters.mc_emoji(length)
            boss_dict = dict(zip(react_list, boss_list))
            embed = await self.hatched_embed()
            channel_list = []
            if self.channel_ids:
                for chanid in self.channel_ids:
                    channel = self.bot.get_channel(int(chanid))
                    if not channel:
                        self.channel_ids.remove(chanid)
                        continue
                    if Train.by_channel.get(channel.id):
                        continue
                    channel_list.append(channel)
                    new_name = await self.channel_name()
                    if new_name != channel.name:
                        try:
                            await channel.edit(name=new_name)
                        except discord.Forbidden:
                            raise commands.BotMissingPermissions(['Manage Channels'])
                    newmsg = await channel.send(content, embed=embed)
                    msg_list.append(newmsg)
            for messageid in self.message_ids:
                chn, msg = await ChannelMessage.from_id_string(self.bot, messageid)
                if not msg:
                    continue
                if chn in channel_list:
                    continue
                await msg.edit(content=content, embed=embed)
                try:
                    await msg.clear_reactions()
                except discord.Forbidden:
                    pass
                msg_list.append(msg)
            for msgid in self.train_msgs:
                chn, msg = await ChannelMessage.from_id_string(self.bot, msgid)
                if not msg:
                    continue
                if chn in channel_list:
                    continue
                await msg.edit(content=content, embed=embed)
                try:
                    await msg.clear_reactions()
                except discord.Forbidden:
                    raise commands.BotMissingPermissions(['Manage Messages'])
                msg_list.append(msg)
            for msg in msg_list:
                for react in react_list:
                    if isinstance(react, int):
                        react = self.bot.get_emoji(react)
                    await msg.add_reaction(react)
            response = await formatters.ask(self.bot, msg_list, timeout=(self.end-time.time()),
                react_list=react_list)
            if response:
                emoji = str(response.emoji)
                for m in msg_list:
                    idstring = f'{m.channel.id}/{m.id}'
                    if idstring not in self.message_ids:
                        chn, msg = await ChannelMessage.from_id_string(self.bot, idstring)
                        if msg:
                            try:
                                await msg.delete()
                            except:
                                pass
                pkmn = boss_dict[emoji]
                return await self.report_hatch(pkmn)
            else:
                return await self.expire_raid()
        except asyncio.CancelledError:
            for m in msg_list:
                idstring = f'{m.channel.id}/{m.id}'
                if idstring not in self.message_ids:
                    chn, msg = await ChannelMessage.from_id_string(self.bot, idstring)
                    if not msg:
                        continue
                    try:
                        await msg.delete()
                    except:
                        pass

        

    async def report_hatch(self, pkmn):
        trainer_dict = self.trainer_dict
        int_list = []
        cancel_list = []
        for trainer in trainer_dict:
            bosses = trainer_dict[trainer]['bosses']
            if pkmn in bosses:
                int_list.append(trainer)
            else:
                meowthuser = MeowthUser.from_id(self.bot, trainer)
                cancel_list.append(meowthuser)
        mention_list = []
        for user_id in int_list:
            member = self.guild.get_member(user_id)
            mention = member.mention
            mention_list.append(mention)
        self.pkmn = RaidBoss(Pokemon(self.bot, pkmn))
        name = await self.pkmn.name()
        content = f"Trainers {' '.join(mention_list)}: The egg has hatched into a {name} raid! RSVP using commands or reactions!" 
        raid_table = self.bot.dbi.table('raids')
        update = raid_table.update()
        update.where(id=self.id)
        d = {
            'pkmn': (self.pkmn.id, None, None)
        }
        update.values(**d)
        await update.commit()
        await self.update_messages(content=content)
        for user in cancel_list:
            await user.rsvp(self.id, "cancel")
        self.bot.loop.create_task(self.monitor_status())

    async def correct_weather(self, weather):
        if isinstance(self.gym, Gym):
            await self.gym.correct_weather(weather.value)
        else:
            await self.change_weather(weather.value)
        

        
    
    async def expire_raid(self):
        try:
            self.bot.loop.create_task(self.update_messages())
            await asyncio.sleep(60)
            try:
                del Raid.instances[self.id]
            except:
                pass
            for message_id in self.message_ids:
                try:
                    del Raid.by_message[message_id]
                except:
                    pass
            if self.channel_ids:
                for chanid in self.channel_ids:
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
                    archive_table = self.bot.dbi.table('to_archive')
                    query = archive_table.query
                    query.where(channel_id=int(chanid))
                    data = await query.get()
                    if data:
                        d = data[0]
                        user_id = d.get('user_id')
                        reason = d.get('reason')
                        await self.archive_raid(channel, user_id, reason)
                        continue
                    try:
                        await channel.delete()
                    except:
                        pass
            if self.completed_by:
                raid_score = 1 + len(self.completed_by)
            else:
                raid_score = 1
            score_table = self.bot.dbi.table('scoreboard')
            query = score_table.query
            query.where(guild_id=self.guild_id)
            query.where(user_id=self.reporter_id)
            old_data = await query.get()
            if not old_data:
                d = {
                    'guild_id': self.guild_id,
                    'user_id': self.reporter_id,
                    'raid': 0,
                    'wild': 0,
                    'trade': 0,
                    'research': 0,
                    'service': 0
                }
            else:
                d = dict(old_data[0])
            d['raid'] += raid_score
            insert = score_table.insert
            insert.row(**d)
            await insert.commit(do_update=True)
            raid_table = self.bot.dbi.table('raids')
            query = raid_table.query().where(id=self.id)
            self.bot.loop.create_task(query.delete())
            rsvp_table = self.bot.dbi.table('raid_rsvp')
            rsvp = rsvp_table.query().where(raid_id=self.id)
            self.bot.loop.create_task(rsvp.delete())
            grp_table = self.bot.dbi.table('raid_groups')
            grps = grp_table.query().where(raid_id=self.id)
            self.bot.loop.create_task(grps.delete())
        except asyncio.CancelledError:
            raise
    
    async def archive_raid(self, channel, user_id, reason=None):
        guild = channel.guild
        bot = self.bot
        old_name = channel.name
        new_name = 'archived-' + old_name
        category = await archive_category(bot, guild)
        if category:
            sync = True
        else:
            sync = False
        await channel.edit(name=new_name, category=category, sync_permissions=sync)
        member = guild.get_member(user_id)
        content = f"Channel archive initiated by {member.display_name}."
        if reason:
            content += f" Reason: {reason}"
        content += "\nDeleted messages from this channel will be posted below."
        await channel.send(content)
        table = self.bot.dbi.table('discord_messages')
        query = table.query
        query.where(channel_id=channel.id)
        query.where(deleted=True)
        data = await query.get()
        for row in data:
            embed = formatters.deleted_message_embed(self.bot, row)
            await channel.send(embed=embed)
        raid_table = self.bot.dbi.table('raids')
        query = raid_table.query().where(id=self.id)
        self.bot.loop.create_task(query.delete())
        rsvp_table = self.bot.dbi.table('raid_rsvp')
        rsvp = rsvp_table.query().where(raid_id=self.id)
        self.bot.loop.create_task(rsvp.delete())
        grp_table = self.bot.dbi.table('raid_groups')
        grps = grp_table.query().where(raid_id=self.id)
        self.bot.loop.create_task(grps.delete())




    # async def update_gym(self, gym):

    async def get_wants(self):
        wants = []
        wants.append(self.level)
        if self.pkmn:
            family = await self.pkmn._familyId()
            wants.append(family)
        else:
            boss_list = await self.get_boss_list()
            if len(boss_list) == 1:
                pkmn = Pokemon(self.bot, boss_list[0])
                family = await pkmn._familyId()
                wants.append(family)
        if isinstance(self.gym, Gym):
            if await self.gym._exraid():
                wants.append('exgym')
        wants = [Want(self.bot, x, self.guild_id) for x in wants]
        want_dict = {x: await x.role() for x in wants}
        return want_dict

        

    async def boss_interest_dict(self):
        boss_list = self.boss_list
        d = {x: 0 for x in boss_list}
        trainer_dict = self.trainer_dict
        for trainer in trainer_dict:
            if not trainer_dict[trainer].get('status'):
                continue
            total = sum(trainer_dict[trainer]['party'])
            bosses = trainer_dict[trainer]['bosses']
            for boss in bosses:
                if boss in boss_list:
                    d[boss] += total
        return d

    @staticmethod
    def status_dict(trainer_dict):
        d = {
            'maybe': 0,
            'coming': 0,
            'here': 0,
            'lobby': 0
        }
        for trainer in trainer_dict:
            total = sum(trainer_dict[trainer]['party'])
            status = trainer_dict[trainer]['status']
            if status and status != 'cancel':
                d[status] += total
        return d
    
    @property
    def status_str(self):
        status_str = self.status_string(self.bot, self.trainer_dict)
        return status_str
    
    @staticmethod
    def status_string(bot, trainer_dict):
        status_dict = Raid.status_dict(trainer_dict)
        status_str = f"{bot.config.emoji['maybe']}: **{status_dict['maybe']}** | "
        status_str += f"{bot.config.emoji['coming']}: **{status_dict['coming']}** | "
        status_str += f"{bot.get_emoji(bot.config.emoji['here'])}: **{status_dict['here']}**"
        return status_str
    
    @staticmethod
    def team_dict(trainer_dict):
        d = {
            'mystic': 0,
            'instinct': 0,
            'valor': 0,
            'unknown': 0
        }
        for trainer in trainer_dict:
            if not trainer_dict[trainer].get('status'):
                continue
            bluecount = trainer_dict[trainer]['party'][0]
            yellowcount = trainer_dict[trainer]['party'][1]
            redcount = trainer_dict[trainer]['party'][2]
            unknowncount = trainer_dict[trainer]['party'][3]
            d['mystic'] += bluecount
            d['instinct'] += yellowcount
            d['valor'] += redcount
            d['unknown'] += unknowncount
        return d

    @property
    def team_str(self):
        team_str = self.team_string(self.bot, self.trainer_dict)
        return team_str

    @staticmethod
    def team_string(bot, trainer_dict):
        team_dict = Raid.team_dict(trainer_dict)
        team_str = f"{bot.config.team_emoji['mystic']}: {team_dict['mystic']} | "
        team_str += f"{bot.config.team_emoji['instinct']}: {team_dict['instinct']} | "
        team_str += f"{bot.config.team_emoji['valor']}: {team_dict['valor']} | "
        team_str += f"{bot.config.team_emoji['unknown']}: {team_dict['unknown']}"
        return team_str
    
    def grp_status_dict(self, group):
        d = {
            'maybe': 0,
            'coming': 0,
            'here': 0,
            'lobby': 0
        }
        trainer_dict = self.trainer_dict
        for trainer in group['users']:
            total = sum(trainer_dict[trainer]['party'])
            status = trainer_dict[trainer]['status']
            d[status] += total
        return d
    
    def grp_total(self, group):
        total = 0
        trainer_dict = self.trainer_dict
        for trainer in group['users']:
            total += sum(trainer_dict[trainer]['party'])
        return total
    
    def grp_status_str(self, group):
        status_dict = self.grp_status_dict(group)
        status_str = f"{self.bot.config.emoji['maybe']}: {status_dict['maybe']} | "
        status_str += f"{self.bot.config.emoji['coming']}: {status_dict['coming']} | "
        status_str += f"{self.bot.get_emoji(self.bot.config.emoji['here'])}: {status_dict['here']}"
        return status_str
    
    def grp_team_dict(self, group):
        d = {
            'mystic': 0,
            'instinct': 0,
            'valor': 0,
            'unknown': 0
        }
        trainer_dict = self.trainer_dict
        for trainer in group['users']:
            bluecount = trainer_dict[trainer]['party'][0]
            yellowcount = trainer_dict[trainer]['party'][1]
            redcount = trainer_dict[trainer]['party'][2]
            unknowncount = trainer_dict[trainer]['party'][3]
            d['mystic'] += bluecount
            d['instinct'] += yellowcount
            d['valor'] += redcount
            d['unknown'] += unknowncount
        return d
    
    def grp_team_str(self, group):
        team_dict = self.grp_team_dict(group)
        team_str = f"{self.bot.config.team_emoji['mystic']}: {team_dict['mystic']} | "
        team_str += f"{self.bot.config.team_emoji['instinct']}: {team_dict['instinct']} | "
        team_str += f"{self.bot.config.team_emoji['valor']}: {team_dict['valor']} | "
        team_str += f"{self.bot.config.team_emoji['unknown']}: {team_dict['unknown']}"
        return team_str

    async def get_grp_list(self):
        group_list = []
        group_table = self.bot.dbi.table('raid_groups')
        query = group_table.query
        query.where(raid_id=self.id)
        query.order_by(group_table['starttime'], asc=True)
        grp_data = await query.get()
        for i in range(len(grp_data)):
            rcrd = grp_data[i]
            grp = {
                'raid_id': self.id,
                'grp_id': rcrd['grp_id'],
                'emoji': f'{i+1}\u20e3',
                'starttime': rcrd.get('starttime'),
                'users': rcrd.get('users', []),
            }
            grp['est_power'] = self.grp_est_power(grp)
            group_list.append(grp)
        return group_list
    
    async def list_rsvp(self, channel, tags=False):
        trainer_dict = self.trainer_dict
        interested_users = []
        coming_users = []
        here_users = []
        lobby_users = []
        for trainer in trainer_dict:
            member = self.guild.get_member(trainer)
            if tags:
                name = member.mention
            else:
                name = member.display_name
            party = trainer_dict[trainer]['party']
            total = sum(party)
            status = trainer_dict[trainer]['status']
            sumstr = name
            if total != 1:
                sumstr += f' ({total})'
            if status == 'maybe':
                interested_users.append(sumstr)
            elif status == 'coming':
                coming_users.append(sumstr)
            elif status == 'here':
                here_users.append(sumstr)
            elif status == 'lobby':
                lobby_users.append(sumstr)
        liststr = ""
        if interested_users:
            liststr += f"\n\n{self.bot.config.emoji['maybe']}: {', '.join(interested_users)}"
        if coming_users:
            liststr += f"\n\n{self.bot.config.emoji['coming']}: {', '.join(coming_users)}"
        if here_users:
            liststr += f"\n\n{self.bot.get_emoji(self.bot.config.emoji['here'])}: {', '.join(here_users)}"
        if lobby_users:
            liststr += f"\n\nLobby: {', '.join(lobby_users)}"
        if tags:
            return await channel.send(f'Current Raid RSVP Totals\n\n{liststr}')
        embed = formatters.make_embed(title="Current Raid RSVP Totals", content=liststr)
        return await channel.send(embed=embed)
    
    async def list_teams(self, channel, tags=False):
        trainer_dict = self.trainer_dict
        mystic_list = []
        instinct_list = []
        valor_list = []
        other_list = []
        for trainer in trainer_dict:
            member = self.guild.get_member(trainer)
            if not member:
                continue
            if tags:
                name = member.mention
            else:
                name = member.display_name
            party = trainer_dict[trainer]['party']
            total = sum(party)
            sumstr = name
            if total != 1:
                sumstr += f' ({total})'
            if party[0] == total:
                mystic_list.append(sumstr)
            elif party[1] == total:
                instinct_list.append(sumstr)
            elif party[2] == total:
                valor_list.append(sumstr)
            else:
                other_list.append(sumstr)
        liststr = ""
        if mystic_list:
            liststr += f"\n\n{self.bot.config.team_emoji['mystic']}: {', '.join(mystic_list)}"
        if instinct_list:
            liststr += f"\n\n{self.bot.config.team_emoji['instinct']}: {', '.join(instinct_list)}"
        if valor_list:
            liststr += f"\n\n{self.bot.config.team_emoji['valor']}: {', '.join(valor_users)}"
        if other_list:
            liststr += f"\n\nOther: {', '.join(other_list)}"
        if tags:
            return await channel.send(f'Current Raid Team Totals\n\n{liststr}')
        embed = formatters.make_embed(title="Current Raid Team Totals", content=liststr)
        return await channel.send(embed=embed)
    
    async def list_groups(self, channel, tags=False):
        liststr = ""
        group_list = self.group_list
        trainer_dict = self.trainer_dict
        for group in group_list:
            user_strs = []
            users = group['users']
            emoji = group['emoji']
            start = self.local_datetime(group['starttime'])
            time = start.strftime('%I:%M %p')
            for user in users:
                member = self.guild.get_member(user)
                if not member:
                    continue
                if tags:
                    name = member.mention
                else:
                    name = member.display_name
                party = trainer_dict[user]['party']
                total = sum(party)
                sumstr = name
                if total != 1:
                    sumstr += f' ({total})'
                user_strs.append(sumstr)
            liststr += f"\n\n {emoji}: {', '.join(user_strs)}"
            liststr += f"\nStarting at {time}"
        if tags:
            return await channel.send(f'Current Raid Groups\n\n{liststr}')
        embed = formatters.make_embed(title="Current Raid Groups", content=liststr)
        return await channel.send(embed=embed)
    
    async def list_bosses(self, channel, tags=False):
        trainer_dict = self.trainer_dict
        boss_list = self.boss_list
        boss_dict = {x: [] for x in boss_list}
        for trainer in trainer_dict:
            member = self.guild.get_member(trainer)
            if not member:
                continue
            if tags:
                name = member.mention
            else:
                name = member.display_name
            bosses = trainer_dict[trainer]['bosses']
            party = trainer_dict[trainer]['party']
            total = sum(party)
            sumstr = name
            if total != 1:
                sumstr += f' ({total})'
            for x in bosses:
                boss_dict[x].append(sumstr)
        boss_str = []
        for x in boss_dict:
            pkmn = Pokemon(self.bot, x)
            pkmn_name = await pkmn.name()
            boss_str.append(f"{pkmn_name}: {', '.join(boss_dict[x])}")
        liststr = "\n\n".join(boss_str)
        if tags:
            return await channel.send(f'Current Raid Boss Totals\n\n{liststr}')
        embed = formatters.make_embed(title="Current Raid Boss Totals", content=liststr)
        return await channel.send(embed=embed)

    async def get_trainer_dict(self):
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
        query.where(raid_id=self.id)
        rsvp_data = await query.get()
        if self.status == 'active':
            est_20 = await self.estimator_20()
        else:
            est_20 = None
        for rcrd in rsvp_data:
            trainer, rcrd_dict = data(rcrd)
            total = sum(rcrd_dict['party'])
            if est_20:
                estimator = rcrd_dict.get('estimator')
                if estimator:
                    est_power = 1/estimator + (total-1)/est_20
                else:
                    est_power = total/est_20
                rcrd_dict['est_power'] = est_power
            trainer_dict[trainer] = rcrd_dict
        return trainer_dict


    @classmethod
    async def from_data(cls, bot, data):
        if data['gym'].isdigit():
            gym = Gym(bot, int(data['gym']))
        else:
            city, arg = data['gym'].split('/', 1)
            gym = PartialPOI(bot, city, arg)
        level = data['level']
        guild_id = data['guild']
        report_channel_id = data['report_channel']
        pkmnid, quick, charge = data.get('pkmn', (None, None, None))
        if pkmnid:
            pkmn = Pokemon(bot, pkmnid, quickMoveid=quick, chargeMoveid=charge)
            boss = RaidBoss(pkmn)
        else:
            boss = None
        hatch = data.get('hatch')
        end = data['endtime']
        raid_id = data['id']
        reporter_id = data['reporter_id']
        completed_by = data.get('completed_by', [])
        if not completed_by:
            completed_by = []
        raid = cls(raid_id, bot, guild_id, report_channel_id, reporter_id, gym, level=level, pkmn=boss, hatch=hatch, end=end, completed_by=completed_by)
        raid.channel_ids = data.get('channels')
        raid.message_ids = data.get('messages')
        raid.train_msgs = data.get('train_msgs')
        for message_id in raid.message_ids:
            Raid.by_message[message_id] = raid
        for channel_id in raid.channel_ids:
            Raid.by_channel[channel_id] = raid
        for idstring in raid.train_msgs:
            chnid, msgid = idstring.split('/')
            Raid.by_trainreport[msgid] = raid
        raid.trainer_dict = await raid.get_trainer_dict()
        raid.group_list = await raid.get_grp_list()
        raid.tz = data['tz']
        await raid.get_boss_list()
        return raid
    
    
    async def summary_str(self):
        if self.status == 'egg':
            pre_str = f'**Level {self.level} Raid at'
            hatchdt = self.local_datetime(self.hatch)
            time = hatchdt.strftime('%I:%M %p')
            post_str = f"Hatches at {time}"
        elif self.status == 'hatched':
            pre_str = f'**Level {self.level} Raid at'
            enddt = self.local_datetime(self.end)
            time = enddt.strftime('%I:%M %p')
            post_str = f"Ends at {time}"
        elif self.status == 'active':
            pre_str = f'**{await self.pkmn.name()} Raid at'
            enddt = self.local_datetime(self.end)
            time = enddt.strftime('%I:%M %p')
            post_str = f"Ends at {time}"
        else:
            return None
        if isinstance(self.gym, Gym):
            gym_str = await self.gym._name()
        else:
            gym_str = self.gym._name
        status_str = self.status_str
        summary_str = f'{pre_str} {gym_str}**\nRSVPs: {status_str}'
        if self.channel_ids:
            channel = self.bot.get_channel(int(self.channel_ids[0]))
            if not channel:
                self.bot.loop.create_task(self.expire_raid())
                return None
            channel_str = channel.mention
            summary_str += f' | {channel_str}'
        summary_str += f"\n{post_str}"
        return summary_str

    async def train_summary(self):
        if self.status == 'egg' or self.status == 'hatched':
            pre_str = f'**Level {self.level} Raid at'
        elif self.status == 'active':
            pre_str = f'**{await self.pkmn.name()} Raid at'
        else:
            return None
        if isinstance(self.gym, Gym):
            gym_str = await self.gym._name()
        else:
            gym_str = self.gym._name
        summary_str = f'{pre_str} {gym_str}**'
        return summary_str

class Train:

    instances = dict()
    by_channel = dict()
    by_message = dict()

    def __new__(cls, train_id, *args, **kwargs):
        if train_id in cls.instances:
            return cls.instances[train_id]
        instance = super().__new__(cls)
        cls.instances[train_id] = instance
        return instance

    def __init__(self, train_id, bot, guild_id, channel_id, report_channel_id):
        self.id = train_id
        self.bot = bot
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.report_channel_id = report_channel_id
        self.current_raid = None
        self.next_raid = None
        self.done_raids = []
        self.report_msg_ids = []
        self.multi_msg_ids = []
        self.message_ids = []
        self.trainer_dict = {}
    
    def to_dict(self):
        d = {
            'id': self.id,
            'guild_id': self.guild_id,
            'channel_id': self.channel_id,
            'report_channel_id': self.report_channel_id,
            'current_raid_id': self.current_raid.id if self.current_raid else None,
            'next_raid_id': self.next_raid.id if self.next_raid else None,
            'done_raid_ids': [x.id for x in self.done_raids if x],
            'report_msg_ids': self.report_msg_ids,
            'multi_msg_ids': self.multi_msg_ids,
            'message_ids': self.message_ids
        }
        return d
    
    @property
    def _data(self):
        table = self.bot.dbi.table('trains')
        query = table.query.where(id=self.id)
        return query
    
    @property
    def _insert(self):
        table = self.bot.dbi.table('trains')
        insert = table.insert
        d = self.to_dict()
        insert.row(**d)
        return insert

    async def upsert(self):
        insert = self._insert
        await insert.commit(do_update=True)
    
    @property
    def guild(self):
        return self.bot.get_guild(self.guild_id)
    
    @property
    def channel(self):
        return self.bot.get_channel(self.channel_id)
    
    async def messages(self):
        for msgid in self.message_ids:
            chn, msg = await ChannelMessage.from_id_string(self.bot, msgid)
            if msg:
                yield msg
            else:
                continue
    
    @property
    def report_channel(self):
        rchan = self.bot.get_channel(self.report_channel_id)
        return ReportChannel(self.bot, rchan)
    
    async def report_msgs(self):
        for msgid in self.report_msg_ids:
            try:
                msg = await self.channel.fetch_message(msgid)
                if msg:
                    yield msg
            except:
                continue
        
    async def clear_reports(self):
        async for msg in self.report_msgs():
            try:
                await msg.delete()
            except:
                pass
        self.report_msg_ids = []
    
    async def multi_msgs(self):
        for msgid in self.multi_msg_ids:
            chn, msg = await ChannelMessage.from_id_string(self.bot, msgid)
            if msg:
                yield msg
            else:
                continue
    
    async def clear_multis(self):
        async for msg in self.multi_msgs():
            try:
                await msg.delete()
            except:
                pass
        self.multi_msg_ids = []
    
    async def reported_raids(self):
        for msgid in self.report_msg_ids:
            raid = Raid.by_trainreport.get(msgid)
            msg = await self.channel.fetch_message(msgid)
            yield (msg, raid)
    
    async def report_results(self):
        async for msg, raid in self.reported_raids():
            reacts = msg.reactions
            for react in reacts:
                if react.emoji != '\u2b06':
                    continue
                count = react.count
                yield (raid, count)
    
    async def possible_raids(self):
        idlist = await self.report_channel.get_all_raids()
        raid_list = [Raid.instances.get(x) for x in idlist if Raid.instances.get(x)]
        raid_list = [x for x in raid_list if x.level != 'EX']
        return raid_list
    
    async def select_raid(self, raid):
        if not raid:
            await self.end_train()
        self.current_raid = raid
        train_embed = await self.train_embed()
        content = "A raid train is coming to this raid! React to this message to join the train!"
        for chanid in raid.channel_ids:
            channel_id = int(chanid)
            if not Train.by_channel.get(channel_id):
                channel = self.bot.get_channel(channel_id)
                msg = await channel.send(content, embed=train_embed.embed)
                self.message_ids.append(f'{channel.id}/{msg.id}')
                await msg.add_reaction('🚂')
                await msg.add_reaction('❌')
                Train.by_message[msg.id] = self
        raid.channel_ids.append(str(self.channel_id))
        if raid.status == 'active':
            embed = await raid.raid_embed()
        elif raid.status == 'egg':
            embed = await raid.egg_embed()
        elif raid.status == 'hatched':
            embed = await raid.hatched_embed()
        raidmsg = await self.channel.send(embed=embed)
        react_list = raid.react_list
        for react in react_list:
            if isinstance(react, int):
                react = self.bot.get_emoji(react)
            await raidmsg.add_reaction(react)
        idstring = f'{self.channel_id}/{raidmsg.id}'
        raid.message_ids.append(idstring)
        await raid.upsert()
        Raid.by_message[idstring] = raid
        Raid.by_channel[str(self.channel_id)] = raid
        self.next_raid = None
        await self.upsert()
        self.bot.loop.create_task(self.poll_next_raid())
    
    async def finish_current_raid(self):
        raid = self.current_raid
        if raid:
            self.done_raids.append(raid)
            if str(self.channel_id) in raid.channel_ids:
                raid.channel_ids.remove(str(self.channel_id))
            for msgid in raid.message_ids:
                if msgid.startswith(str(self.channel_id)):
                    chn, msg = await ChannelMessage.from_id_string(self.bot, msgid)
                    if not msg:
                        continue
                    try:
                        await msg.delete()
                    except:
                        pass
                    try:
                        raid.message_ids.remove(msgid)
                        del Raid.by_message[msgid]
                    except:
                        pass
            await raid.upsert()
        if not self.poll_task.done():
            self.poll_task.cancel()
            self.next_raid = await self.poll_task
        await self.clear_reports()
        await self.clear_multis()
        await self.select_raid(self.next_raid)

    async def get_trainer_dict(self):
        def data(rcrd):
            trainer = rcrd['user_id']
            party = rcrd.get('party', [0,0,0,1])
            return trainer, party
        trainer_dict = {}
        user_table = self.bot.dbi.table('train_rsvp')
        query = user_table.query()
        query.where(train_id=self.id)
        rsvp_data = await query.get()
        for rcrd in rsvp_data:
            trainer, party = data(rcrd)
            trainer_dict[trainer] = party
        if not trainer_dict:
            await self.end_train()
        return trainer_dict

    @staticmethod
    def team_dict(trainer_dict):
        d = {
            'mystic': 0,
            'instinct': 0,
            'valor': 0,
            'unknown': 0
        }
        for trainer in trainer_dict:
            bluecount = trainer_dict[trainer][0]
            yellowcount = trainer_dict[trainer][1]
            redcount = trainer_dict[trainer][2]
            unknowncount = trainer_dict[trainer][3]
            d['mystic'] += bluecount
            d['instinct'] += yellowcount
            d['valor'] += redcount
            d['unknown'] += unknowncount
        return d

    @property
    def team_str(self):
        team_str = self.team_string(self.bot, self.trainer_dict)
        return team_str

    @staticmethod
    def team_string(bot, trainer_dict):
        team_dict = Train.team_dict(trainer_dict)
        team_str = f"{bot.config.team_emoji['mystic']}: {team_dict['mystic']} | "
        team_str += f"{bot.config.team_emoji['instinct']}: {team_dict['instinct']} | "
        team_str += f"{bot.config.team_emoji['valor']}: {team_dict['valor']} | "
        team_str += f"{bot.config.team_emoji['unknown']}: {team_dict['unknown']}"
        return team_str

    async def list_teams(self, channel, tags=False):
        trainer_dict = self.trainer_dict
        mystic_list = []
        instinct_list = []
        valor_list = []
        other_list = []
        for trainer in trainer_dict:
            member = self.guild.get_member(trainer)
            name = member.display_name
            party = trainer_dict[trainer]['party']
            total = sum(party)
            sumstr = name
            if total != 1:
                sumstr += f' ({total})'
            if party[0] == total:
                mystic_list.append(sumstr)
            elif party[1] == total:
                instinct_list.append(sumstr)
            elif party[2] == total:
                valor_list.append(sumstr)
            else:
                other_list.append(sumstr)
        liststr = ""
        if mystic_list:
            liststr += f"\n\n{self.bot.config.team_emoji['mystic']}: {', '.join(mystic_list)}"
        if instinct_list:
            liststr += f"\n\n{self.bot.config.team_emoji['instinct']}: {', '.join(instinct_list)}"
        if valor_list:
            liststr += f"\n\n{self.bot.config.team_emoji['valor']}: {', '.join(valor_users)}"
        if other_list:
            liststr += f"\n\nOther: {', '.join(other_list)}"
        embed = formatters.make_embed(title="Current Train Team Totals", content=liststr)
        return await channel.send(embed=embed)

    async def select_first_raid(self, author):
        raids = await self.possible_raids()
        if not raids:
            return await self.report_channel.channel.send("No raids reported! Report a raid before starting a train!")
        react_list = formatters.mc_emoji(len(raids))
        content = "Select your first raid from the list below!"
        multi = None
        async for embed in self.display_choices(raids, react_list):
            multi = await self.report_channel.channel.send(content, embed=embed)
            content = ""
            self.multi_msg_ids.append(f'{self.report_channel_id}/{multi.id}')
        payload = await formatters.ask(self.bot, [multi], user_list=[author.id], 
            react_list=react_list)
        choice_dict = dict(zip(react_list, raids))
        first_raid = choice_dict[str(payload.emoji)]
        await self.clear_multis()
        await self.select_raid(first_raid)
    
    async def poll_next_raid(self):
        raids = await self.possible_raids()
        if self.current_raid:
            raids.remove(self.current_raid)
        raids = [x for x in raids if x not in self.done_raids and x.status != 'expired']
        react_list = formatters.mc_emoji(len(raids))
        content = "Vote on the next raid from the list below!"
        multi = None
        async for embed in self.display_choices(raids, react_list):
            multi = await self.channel.send(content, embed=embed)
            content = ""
            self.multi_msg_ids.append(f'{self.channel_id}/{multi.id}')
        await self.upsert()
        self.poll_task = self.bot.loop.create_task(self.get_poll_results(multi, raids, react_list))
        
    async def get_poll_results(self, multi, raids, react_list):
        results = None
        if multi:
            multitask = self.bot.loop.create_task(formatters.poll(self.bot, [multi],
                react_list=react_list))
            try:
                results = await multitask
            except asyncio.CancelledError:
                multitask.cancel()
                results = await multitask
        if results:
            emoji = results[0][0]
            count = results[0][1]
        else:
            emoji = None
            count = 0
        report_results = [(x, y) async for x, y in self.report_results()]
        if report_results:
            sorted_reports = sorted(report_results, key=lambda x: x[1], reverse=True)
            report_max = sorted_reports[0][1]
        else:
            report_max = 0
        if report_max and report_max >= count:
            return sorted_reports[0][0]
        elif emoji:
            choice_dict = dict(zip(react_list, raids))
            return choice_dict[str(emoji)]
        else:
            return
    
    async def display_choices(self, raids, react_list):
        dest_dict = {}
        eggs_list = []
        hatched_list = []
        active_list = []
        if self.current_raid:
            if isinstance(self.current_raid.gym, Gym):
                origin = self.current_raid.gym.id
                known_dest_ids = [x.id for x in raids if isinstance(x.gym, Gym)]
                dests = [Raid.instances[x].gym.id for x in known_dest_ids]
                try:
                    times = await Mapper.get_travel_times(self.bot, [origin], dests)
                except:
                    times = []
                dest_dict = {}
                for d in times:
                    if d['origin_id'] == origin and d['dest_id'] in dests:
                        dest_dict[d['dest_id']] = d['travel_time']
        urls = {x.id: await self.route_url(x) for x in raids}
        react_list = formatters.mc_emoji(len(raids))
        for i in range(len(raids)):
            x = raids[i]
            e = react_list[i]
            summary_str = await x.summary_str()
            if not summary_str:
                continue
            summary = f'{e} {summary_str}'
            if x.gym.id in dest_dict:
                travel = f'Travel Time: {dest_dict[x.gym.id]//60} mins'
            else:
                travel = "Travel Time: Unknown"
            directions = f'[{travel}]({urls[x.id]})'
            summary += f"\n{directions}"
            if x.status == 'egg':
                eggs_list.append(summary)
            elif x.status == 'active' or x.status == 'hatched':
                active_list.append(summary)
        number = len(raids)
        pages = ceil(number/3)
        for i in range(pages):
            fields = {}
            left = 3
            if pages == 1:
                title = 'Raid Choices'
            else:
                title = f'Raid Choices (Page {i+1} of {pages})'
            if len(active_list) > left:
                fields['Active'] = "\n\n".join(active_list[:3])
                active_list = active_list[3:]
                embed = formatters.make_embed(title=title, fields=fields)
                yield embed
                continue
            elif active_list:
                fields['Active'] = "\n\n".join(active_list) + "\n\u200b"
                left -= len(active_list)
                active_list = []
            if not left:
                embed = formatters.make_embed(title=title, fields=fields)
                yield embed
                continue
            if not left:
                embed = formatters.make_embed(title=title, fields=fields)
                yield embed
                continue
            if len(eggs_list) > left:
                fields['Eggs'] = "\n\n".join(eggs_list[:left])
                eggs_list = eggs_list[left:]
                embed = formatters.make_embed(title=title, fields=fields)
                yield embed
                continue
            elif eggs_list:
                fields['Eggs'] = "\n\n".join(eggs_list)
            embed = formatters.make_embed(title=title, fields=fields)
            yield embed

    async def route_url(self, next_raid):
        if isinstance(next_raid.gym, Gym):
            return await next_raid.gym.url()
        else:
            return next_raid.gym.url
    
    async def new_raid(self, raid: Raid):
        embed = await TRaidEmbed.from_raid(self, raid)
        content = "Use the reaction below to vote for this raid next!"
        msg = await self.channel.send(content, embed=embed.embed)
        self.report_msg_ids.append(msg.id)
        Raid.by_trainreport[msg.id] = raid
        raid.train_msgs.append(f'{msg.channel.id}/{msg.id}')
        await msg.add_reaction('\u2b06')
        await self.upsert()
        
    async def update_rsvp(self, user_id, status):
        self.trainer_dict = await self.get_trainer_dict()
        has_embed = False
        async for msg in self.messages():
            if not has_embed:
                train_embed = TrainEmbed(msg.embeds[0])
                train_embed.team_str = self.team_str
            await msg.edit(embed=train_embed.embed)
        channel = self.channel
        guild = channel.guild
        member = guild.get_member(user_id)
        if status == 'join':
            status_str = ' has joined the train!'
        elif status == 'cancel':
            status_str =' has left the train!'
        content = f'{member.display_name}{status_str}'
        embed = TRSVPEmbed.from_train(self).embed
        await channel.send(content, embed=embed)
        if not self.trainer_dict:
            await self.end_train()

    
    async def end_train(self):
        try:
            await self.channel.send('This train is now empty! This channel will be deleted in one minute.')
        except:
            pass
        await asyncio.sleep(60)
        await self._data.delete()
        train_rsvp_table = self.bot.dbi.table('train_rsvp')
        query = train_rsvp_table.query
        query.where(train_id=self.id)
        await query.delete()
        if self.current_raid:
            try:
                self.current_raid.channel_ids.remove(self.channel_id)
                await self.current_raid.upsert()
            except ValueError:
                pass
        try:
            del Train.by_channel[self.channel_id]
            for msgid in self.message_ids:
                del Train.by_message[msgid]
            del Train.instances[self.id]
        except KeyError:
            pass
        archive_table = self.bot.dbi.table('to_archive')
        query = archive_table.query
        query.where(channel_id=self.channel_id)
        data = await query.get()
        if data:
            d = data[0]
            user_id = d.get('user_id')
            reason = d.get('reason')
            await self.archive_train(channel, user_id, reason)
        else:
            try:
                await self.channel.delete()
            except:
                pass
        async for msg in self.messages():
            await msg.clear_reactions()
            embed = formatters.make_embed(content="This raid train has ended!")
            await msg.edit(content="", embed=embed)
    
    async def archive_train(self, channel, user_id, reason):
        guild = channel.guild
        bot = self.bot
        old_name = channel.name
        new_name = 'archived-' + old_name
        category = await archive_category(bot, guild)
        await channel.edit(name=new_name, category=category, sync_permissions=True)
        member = guild.get_member(user_id)
        content = f"Channel archive initiated by {member.display_name}."
        if reason:
            content += f" Reason: {reason}"
        content += "\nDeleted messages from this channel will be posted below."
        await channel.send(content)
        table = self.bot.dbi.table('discord_messages')
        query = table.query
        query.where(channel_id=channel.id)
        query.where(deleted=True)
        data = await query.get()
        for row in data:
            embed = formatters.deleted_message_embed(self.bot, row)
            await channel.send(embed=embed)
    
    async def train_embed(self):
        return await TrainEmbed.from_train(self)

    @classmethod
    async def from_data(cls, bot, data):
        train_id = data['id']
        guild_id = data['guild_id']
        channel_id = data['channel_id']
        report_channel_id = data['report_channel_id']
        current_raid_id = data.get('current_raid_id')
        next_raid_id = data.get('next_raid_id')
        done_raid_ids = data.get('done_raid_ids', [])
        report_msg_ids = data.get('report_msg_ids', [])
        multi_msg_ids = data.get('multi_msg_ids', [])
        message_ids = data['message_ids']
        train = cls(train_id, bot, guild_id, channel_id, report_channel_id)
        train.trainer_dict = await train.get_trainer_dict()
        train.current_raid = Raid.instances.get(current_raid_id) if current_raid_id else None
        train.next_raid = Raid.instances.get(next_raid_id) if next_raid_id else None
        train.done_raids = [Raid.instances.get(x) for x in done_raid_ids]
        train.report_msg_ids = report_msg_ids
        train.multi_msg_ids = multi_msg_ids
        train.message_ids = message_ids
        cls.by_channel[channel_id] = train
        for msgid in message_ids:
            cls.by_message[msgid] = train
        if multi_msg_ids:
            idstring = multi_msg_ids[-1]
            chn, multi = await ChannelMessage.from_id_string(bot, idstring)
            if not multi:
                bot.loop.create_task(train.poll_next_raid())
            else:
                raids = await train.possible_raids()
                if train.current_raid:
                    raids.remove(train.current_raid)
                raids = [x for x in raids if x not in train.done_raids and x.status != 'expired']
                react_list = formatters.mc_emoji(len(raids))
                train.poll_task = bot.loop.create_task(train.get_poll_results(multi, raids, react_list))
        else:
            bot.loop.create_task(train.poll_next_raid())
        return train

class ReportEmbed():

    def __init__(self, embed):
        self.embed = embed
    
    raid_icon = 'https://media.discordapp.net/attachments/423492585542385664/512682888236367872/imageedit_1_9330029197.png' #TODO
    footer_icon = 'https://media.discordapp.net/attachments/346766728132427777/512699022822080512/imageedit_10_6071805149.png'

    boss_index = 0
    gym_index = 1
    status_index = 2
    team_index = 3
    boss_list_index = 4

    @classmethod
    async def from_raid(cls, raid: Raid):
        if raid.status == 'active':
            bossfield = "Boss"
            boss = raid.pkmn
            name = await boss.name()
            type_emoji = await boss.type_emoji()
            shiny_available = await boss._shiny_available()
            if shiny_available:
                name += " :sparkles:"
            name += f" {type_emoji}"
            img_url = await boss.sprite_url()
            enddt = datetime.fromtimestamp(raid.end)
        else:
            bossfield = "Level"
            name = raid.level
            img_url = raid.bot.raid_info.egg_images[name]
            enddt = datetime.fromtimestamp(raid.hatch)
        bot = raid.bot
        # color = await boss.color()
        gym = raid.gym
        if isinstance(gym, Gym):
            directions_url = await gym.url()
            directions_text = await gym._name()
            exraid = await gym._exraid()
        else:
            directions_url = gym.url
            directions_text = gym._name + " (Unknown Gym)"
            exraid = False
        if exraid:
            directions_text += " (EX Raid Gym)"
        status_str = raid.status_str
        team_str = raid.team_str
        fields = {
            bossfield: name,
            "Gym": f"[{directions_text}]({directions_url})",
            "Status List": status_str,
            "Team List": team_str
        }
        footer = 'Ending'
        if raid.status == 'egg':
            boss_str = await raid.boss_list_str()
            fields['Boss Interest'] = boss_str
            footer = 'Hatching'
        embed = formatters.make_embed(icon=RaidEmbed.raid_icon, title="Raid Report", # msg_colour=color,
            thumbnail=img_url, fields=fields, footer=footer, footer_icon=RaidEmbed.footer_icon)
        embed.timestamp = enddt
        return cls(embed)

class RaidEmbed():

    def __init__(self, embed):
        self.embed = embed

    raid_icon = 'https://media.discordapp.net/attachments/423492585542385664/512682888236367872/imageedit_1_9330029197.png' #TODO
    footer_icon = 'https://media.discordapp.net/attachments/346766728132427777/512699022822080512/imageedit_10_6071805149.png'

    boss_index = 0
    weather_index = 1
    weak_index = 2
    resist_index = 3
    cp_index = 4
    moveset_index = 5
    status_index = 6
    team_index = 7
    ctrs_index = 8
    rec_index = 10
    group_index = 9

    def set_boss(self, boss_dict):
        name = boss_dict['name']
        shiny_available = boss_dict['shiny_available']
        cp_str = boss_dict['cp_str']
        resists = boss_dict['resists']
        weaks = boss_dict['weaks']
        ctrs_str = boss_dict['ctrs_str']
        moveset_str = "Unknown | Unknown"

        self.embed.set_field_at(RaidEmbed.boss_index, name="Boss", value=name)
        self.embed.set_field_at(RaidEmbed.weak_index, name="Weaknesses", value=weaks)
        self.embed.set_field_at(RaidEmbed.resist_index, name="Resistances", value=resists)
        self.embed.set_field_at(RaidEmbed.cp_index, name="CP Range", value=cp_str)
        self.embed.set_field_at(RaidEmbed.ctrs_index, name="<:pkbtlr:512707623812857871> Counters", value=ctrs_str)
        self.embed.set_field_at(RaidEmbed.moveset_index, name="Moveset", value=moveset_str)
        return self
    
    def set_weather(self, weather_str, cp_str, ctrs_str, rec_str=None):
        self.embed.set_field_at(RaidEmbed.weather_index, name="Weather", value=weather_str)
        self.embed.set_field_at(RaidEmbed.cp_index, name="CP Range", value=cp_str)
        self.embed.set_field_at(RaidEmbed.ctrs_index, name='<:pkbtlr:512707623812857871> Counters', value=ctrs_str)
        if rec_str:
            self.embed.set_field_at(RaidEmbed.rec_index, name="Recommended Group Size", value=rec_str)
        return self
    
    def set_moveset(self, moveset_str, ctrs_str, rec_str=None):
        self.embed.set_field_at(RaidEmbed.moveset_index, name="Moveset", value=moveset_str)
        self.embed.set_field_at(RaidEmbed.ctrs_index, name='<:pkbtlr:512707623812857871> Counters', value=ctrs_str)
        if rec_str:
            self.embed.set_field_at(RaidEmbed.rec_index, name="Recommended Group Size", value=rec_str)
        return self
    
    @property
    def status_str(self):
        return self.embed.fields[RaidEmbed.status_index].value
    
    @status_str.setter
    def status_str(self, status_str):
        self.embed.set_field_at(RaidEmbed.status_index, name="Status List", value=status_str)
    
    @property
    def team_str(self):
        return self.embed.fields[RaidEmbed.team_index].value
    
    @team_str.setter
    def team_str(self, team_str):
        self.embed.set_field_at(RaidEmbed.team_index, name="Team List", value=team_str)

    @property
    def rec_str(self):
        return self.embed.fields[RaidEmbed.rec_index].value
    
    @rec_str.setter
    def rec_str(self, rec_str):
        self.embed.set_field_at(RaidEmbed.rec_index, name="Recommended Group Size", value=rec_str)
    
    @property
    def grps_str(self):
        return self.embed.fields[RaidEmbed.group_index].value
    
    @grps_str.setter
    def grps_str(self, grps_tuple):
        self.embed.set_field_at(RaidEmbed.group_index, name=grps_tuple[0], value=grps_tuple[1], inline=False)



    @classmethod
    async def from_raid(cls, raid: Raid):
        boss = raid.pkmn
        bot = raid.bot
        name = await boss.name()
        type_emoji = await boss.type_emoji()
        shiny_available = await boss._shiny_available()
        if shiny_available:
            name += ' :sparkles:'
        quick_move = Move(bot, boss.quickMoveid) if boss.quickMoveid else None
        charge_move = Move(bot, boss.chargeMoveid) if boss.chargeMoveid else None
        if quick_move:
            quick_name = await quick_move.name()
            quick_emoji = await quick_move.emoji()
        else:
            quick_name = "Unknown"
            quick_emoji = ""
        if charge_move:
            charge_name = await charge_move.name()
            charge_emoji = await charge_move.emoji()
        else:
            charge_name = "Unknown"
            charge_emoji = ""
        moveset = f"{quick_name} {quick_emoji}| {charge_name} {charge_emoji}"
        weather = await raid.weather()
        weather = Weather(bot, weather)
        weather_name = await weather.name()
        weather_emoji = await weather.boosted_emoji_str()
        is_boosted = await boss.is_boosted(weather.value)
        cp_range = await raid.cp_range()
        cp_str = f"{cp_range[0]}-{cp_range[1]}"
        end = raid.end
        enddt = datetime.fromtimestamp(end)
        if is_boosted:
            cp_str += " (Boosted)"
        img_url = await boss.sprite_url()
        # color = await boss.color()
        gym = raid.gym
        if isinstance(gym, Gym):
            directions_url = await gym.url()
            directions_text = await gym._name()
            exraid = await gym._exraid()
        else:
            directions_url = gym.url
            directions_text = gym._name + " (Unknown Gym)"
            exraid = False
        if exraid:
            directions_text += " (EX Raid Gym)"
        resists = await boss.resistances_emoji()
        weaks = await boss.weaknesses_emoji()
        status_str = raid.status_str
        team_str = raid.team_str
        fields = {
            "Boss": f"{name} {type_emoji}",
            "Weather": f"{weather_name} {weather_emoji}",
            "Weaknesses": weaks,
            "Resistances": resists,
            "CP Range": f"{cp_range[0]}-{cp_range[1]}",
            "Moveset": moveset,
            "Status List": status_str,
            "Team List": team_str
        }
        i = 1
        ctrs_list = await raid.generic_counters_data()
        if ctrs_list:
            ctrs_str = []
            for ctr in ctrs_list:
                name = await ctr.name()
                fast = Move(raid.bot, ctr.quickMoveid)
                fast_name = await fast.name()
                if await fast.is_legacy(ctr.id):
                    fast_name += " (Legacy)"
                try:
                    fast_emoji = await fast.emoji()
                except:
                    fast_emoji = ""
                charge = Move(raid.bot, ctr.chargeMoveid)
                charge_name = await charge.name()
                if await charge.is_legacy(ctr.id):
                    charge_name += " (Legacy)"
                try:
                    charge_emoji = await charge.emoji()
                except:
                    charge_emoji = ""
                ctr_str = f"**{name}**: {fast_name} {fast_emoji} | {charge_name} {charge_emoji}"
                ctrs_str.append(ctr_str)
                i += 1
            ctrs_str.append(f'[Results courtesy of Pokebattler](https://www.pokebattler.com/raids/{boss.id})')
            fields['<:pkbtlr:512707623812857871> Counters'] = "\n".join(ctrs_str)
        else:
            ctrs_str = "Currently unavailable"
            fields['<:pkbtlr:512707623812857871> Counters'] = (False, ctrs_str)
        grps_str = raid.grps_str + "\u200b"
        if ctrs_list:
            fields['Groups (Boss Damage Estimate)'] = grps_str
            rec = await raid.rec_group_size()
            fields['Recommended Group Size'] = str(rec)
        else:
            fields['Groups'] = (False, grps_str)
        reporter = raid.guild.get_member(raid.reporter_id)
        if reporter:
            reporter = reporter.display_name
        footer = f"Reported by {reporter} • Ending"
        embed = formatters.make_embed(icon=RaidEmbed.raid_icon, title=directions_text, # msg_colour=color,
            title_url=directions_url, thumbnail=img_url, fields=fields, footer=footer,
            footer_icon=RaidEmbed.footer_icon)
        embed.timestamp = enddt
        return cls(embed)

class RSVPEmbed():

    def __init__(self, embed):
        self.embed = embed

    raid_icon = 'https://media.discordapp.net/attachments/423492585542385664/512682888236367872/imageedit_1_9330029197.png' #TODO
    footer_icon = 'https://media.discordapp.net/attachments/346766728132427777/512699022822080512/imageedit_10_6071805149.png'

    status_index = 0
    team_index = 1

    @property
    def status_str(self):
        return self.embed.fields[RSVPEmbed.status_index].value
    
    @status_str.setter
    def status_str(self, status_str):
        self.embed.set_field_at(RSVPEmbed.status_index, name="Status List", value=status_str)
    
    @property
    def team_str(self):
        return self.embed.fields[RSVPEmbed.team_index].value
    
    @team_str.setter
    def team_str(self, team_str):
        self.embed.set_field_at(RSVPEmbed.team_index, name="Team List", value=team_str)
    
    @classmethod
    def from_meetup(cls, meetup: Meetup):
        bot = meetup.bot

        start_dt = meetup.start_datetime

        status_str = meetup.status_str
        team_str = meetup.team_str

        fields = {
            "Status List": status_str,
            "Team List": team_str
        }

        embed = formatters.make_embed(title="Current RSVP Totals", fields=fields, footer="Starting")
        embed.timestamp = start_dt
        return cls(embed)
    
    @classmethod
    def from_raid(cls, raid: Raid):
        bot = raid.bot

        end = raid.end
        enddt = datetime.fromtimestamp(end)

        status_str = raid.status_str
        team_str = raid.team_str
        fields = {
            "Status List": status_str,
            "Team List": team_str
        }
        grps_str = raid.grps_str + "\u200b"
        fields['Groups'] = (False, grps_str)
        embed = formatters.make_embed(icon=RSVPEmbed.raid_icon, title="Current RSVP Totals",
            fields=fields, footer="Ending", footer_icon=RSVPEmbed.footer_icon)
        embed.timestamp = enddt
        return cls(embed)
    
    @classmethod
    def from_raidgroup(cls, raid: Raid, group):
        bot = raid.bot
        end = raid.end
        enddt = datetime.fromtimestamp(end)

        status_str = raid.grp_status_str(group)
        team_str = raid.grp_team_str(group)
        est = group.get('est_power', 0)
        start = raid.local_datetime(group['starttime'])
        time = start.strftime('%I:%M %p')

        fields = {
            "Status List": status_str,
            "Team List": team_str
        }
        embed = formatters.make_embed(icon=RSVPEmbed.raid_icon, title="Current Group RSVP Totals",
            fields=fields, footer="Ending", footer_icon=RSVPEmbed.footer_icon)
        if est:
            embed.add_field(name='Starting (Boss Damage Estimate)', value=f'{time} ({str(round(est*100)) + "%"})', inline=False)
        else:
            embed.add_field(name='Starting', value=time, inline=False)
        embed.timestamp = enddt
        return cls(embed)
    
class EggEmbed():

    def __init__(self, embed):
        self.embed = embed
    
    raid_icon = 'https://media.discordapp.net/attachments/423492585542385664/512682888236367872/imageedit_1_9330029197.png'
    footer_icon = 'https://media.discordapp.net/attachments/346766728132427777/512699022822080512/imageedit_10_6071805149.png'
            
    level_index = 0
    status_index = 2
    team_index = 3
    boss_list_index = 4
    weather_index = 1
    group_index = 5

    def set_weather(self, weather_str, boss_list_str):
        self.embed.set_field_at(EggEmbed.weather_index, name="Weather", value=weather_str)
        self.boss_str = boss_list_str
        return self
    
    @property
    def status_str(self):
        return self.embed.fields[EggEmbed.status_index].value
    
    @status_str.setter
    def status_str(self, status_str):
        self.embed.set_field_at(EggEmbed.status_index, name="Status List", value=status_str)
    
    @property
    def team_str(self):
        return self.embed.fields[EggEmbed.team_index].value
    
    @team_str.setter
    def team_str(self, team_str):
        self.embed.set_field_at(EggEmbed.team_index, name="Team List", value=team_str)
    
    @property
    def boss_str(self):
        return self.embed.fields[EggEmbed.boss_list_index].value
    
    @boss_str.setter
    def boss_str(self, boss_str):
        self.embed.set_field_at(EggEmbed.boss_list_index, name="Boss Interest", value=boss_str)
    
    @property
    def grps_str(self):
        return self.embed.fields[EggEmbed.group_index].value
    
    @grps_str.setter
    def grps_str(self, grps_tuple):
        self.embed.set_field_at(EggEmbed.group_index, name=grps_tuple[0], value=grps_tuple[1], inline=False)

    

    
    @classmethod
    async def from_raid(cls, raid: Raid):
        level = raid.level
        egg_img_url = raid.bot.raid_info.egg_images[level]
        # color = await formatters.url_color(egg_img_url)
        hatch = raid.hatch
        hatchdt = datetime.fromtimestamp(hatch)
        gym = raid.gym
        if isinstance(gym, Gym):
            directions_url = await gym.url()
            directions_text = await gym._name()
            exraid = await gym._exraid()
        else:
            directions_url = gym.url
            directions_text = gym._name + " (Unknown Gym)"
            exraid = False
        if exraid:
            directions_text += " (EX Raid Gym)"
        weather = await raid.weather()
        weather = Weather(raid.bot, weather)
        weather_name = await weather.name()
        weather_emoji = await weather.boosted_emoji_str()
        status_str = raid.status_str
        team_str = raid.team_str
        boss_str = await raid.boss_list_str()
        fields = {
            "Raid Level": level,
            "Weather": f"{weather_name} {weather_emoji}",
            "Status List": status_str,
            "Team List": team_str,
            "Boss Interest:": boss_str,
        }
        grps_str = raid.grps_str + "\u200b"
        fields['Groups'] = (False, grps_str)
        reporter = raid.guild.get_member(raid.reporter_id)
        if reporter:
            reporter = reporter.display_name
        footer_text = f"Reported by {reporter} • Hatching"
        embed = formatters.make_embed(icon=EggEmbed.raid_icon, title=directions_text,
            thumbnail=egg_img_url, title_url=directions_url, # msg_colour=color,
            fields=fields, footer=footer_text, footer_icon=EggEmbed.footer_icon)
        embed.timestamp = hatchdt
        return cls(embed)

class CountersEmbed():

    def __init__(self, embed):
        self.embed = embed
    
    raid_icon = 'https://media.discordapp.net/attachments/423492585542385664/512682888236367872/imageedit_1_9330029197.png' #TODO
    footer_icon = 'https://media.discordapp.net/attachments/346766728132427777/512699022822080512/imageedit_10_6071805149.png'

    boss_index = 0
    weather_index = 1
    cp_index = 2
    moveset_index = 3
    ctrs_index = 4

    @classmethod
    async def from_raid(cls, user: MeowthUser, raid: Raid):
        boss = raid.pkmn
        if not boss:
            boss_list = raid.boss_list
            if len(boss_list) == 1:
                boss = RaidBoss(Pokemon(raid.bot, boss_list[0]))
            else:
                return
        bot = raid.bot
        name = await boss.name()
        type_emoji = await boss.type_emoji()
        shiny_available = await boss._shiny_available()
        if shiny_available:
            name += ' :sparkles:'
        quick_move = Move(bot, boss.quickMoveid) if boss.quickMoveid else None
        charge_move = Move(bot, boss.chargeMoveid) if boss.chargeMoveid else None
        if quick_move:
            quick_name = await quick_move.name()
            quick_emoji = await quick_move.emoji()
        else:
            quick_name = "Unknown"
            quick_emoji = ""
        if charge_move:
            charge_name = await charge_move.name()
            charge_emoji = await charge_move.emoji()
        else:
            charge_name = "Unknown"
            charge_emoji = ""
        moveset = f"{quick_name} {quick_emoji}| {charge_name} {charge_emoji}"
        weather = await raid.weather()
        weather = Weather(bot, weather)
        weather_name = await weather.name()
        weather_emoji = await weather.boosted_emoji_str()
        is_boosted = await boss.is_boosted(weather.value)
        cp_range = await raid.cp_range()
        cp_str = f"{cp_range[0]}-{cp_range[1]}"
        end = raid.end
        enddt = datetime.fromtimestamp(end)
        if is_boosted:
            cp_str += " (Boosted)"
        img_url = await boss.sprite_url()
        ctrs_list = await raid.user_counters_data(user)
        if not ctrs_list:
            return None
        fields = {
            "Boss": f"{name} {type_emoji}",
            "Weather": f"{weather_name} {weather_emoji}",
            "CP Range": cp_str,
            "Moveset": moveset,
        }
        i = 1
        ctrs_str = []
        for ctr in ctrs_list:
            name = await ctr.name()
            if getattr(ctr, 'nick', None):
                name = ctr.nick + f" ({name})"
            fast = Move(bot, ctr.quickMoveid)
            fast_name = await fast.name()
            fast_emoji = await fast.emoji()
            charge = Move(bot, ctr.chargeMoveid)
            charge_name = await charge.name()
            charge_emoji = await charge.emoji()
            ctr_str = f"**{name}**: {fast_name} {fast_emoji} | {charge_name} {charge_emoji}"
            if ctr.chargeMove2id:
                charge_2 = Move(bot, ctr.chargeMove2id)
                charge_2_name = await charge_2.name()
                charge_2_emoji = await charge_2.emoji()
                ctr_str += f" | {charge_2_name} {charge_2_emoji}"
            ctrs_str.append(ctr_str)
            i += 1
        ctrs_str.append(f'[Results courtesy of Pokebattler](https://www.pokebattler.com/raids/{boss.id})')
        fields['<:pkbtlr:512707623812857871> Counters'] = "\n".join(ctrs_str)
        footer_text = "Ending"
        embed = formatters.make_embed(icon=CountersEmbed.raid_icon, thumbnail=img_url, # msg_colour=color,
            fields=fields, footer=footer_text, footer_icon=CountersEmbed.footer_icon)
        embed.timestamp = enddt
        return cls(embed)

class TrainEmbed():

    def __init__(self, embed):
        self.embed = embed
    
    title = "Raid Train"
    current_raid_index = 1 
    team_index = 2
    channel_index = 0

    @property
    def team_str(self):
        return self.embed.fields[TrainEmbed.team_index].value
    
    @team_str.setter
    def team_str(self, team_str):
        self.embed.set_field_at(TrainEmbed.team_index, name="Team List", value=team_str)
    
    @classmethod
    async def from_train(cls, train: Train):
        title = cls.title
        if train.current_raid:
            current_raid_str = await train.current_raid.train_summary()
        else:
            current_raid_str = "None"
        channel_str = train.channel.mention
        team_str = train.team_str
        fields = {
            'Channel': channel_str,
            'Current Raid': current_raid_str,
            'Team List': team_str
        }
        embed = formatters.make_embed(title=title, fields=fields)
        return cls(embed)

class TRSVPEmbed():

    def __init__(self, embed):
        self.embed = embed
    
    title = 'Current Train Totals'
    
    @classmethod
    def from_train(cls, train: Train):
        title = cls.title
        team_str = train.team_str
        fields = {
            'Team List': team_str
        }
        embed = formatters.make_embed(title=title, fields=fields)
        return cls(embed)



class TRaidEmbed():

    def __init__(self, embed):
        self.embed = embed
    
    @classmethod
    async def from_raid(cls, train: Train, raid: Raid):
        if raid.status == 'active':
            bossfield = "Boss"
            boss = raid.pkmn
            name = await boss.name()
            type_emoji = await boss.type_emoji()
            shiny_available = await boss._shiny_available()
            if shiny_available:
                name += " :sparkles:"
            name += f" {type_emoji}"
            img_url = await boss.sprite_url()
        elif raid.status == 'egg':
            bossfield = "Level"
            name = raid.level
            img_url = raid.bot.raid_info.egg_images[name]
        bot = raid.bot
        end = raid.end
        enddt = datetime.fromtimestamp(end)
        # color = await boss.color()
        gym = raid.gym
        travel_time = "Unknown"
        if isinstance(gym, Gym):
            directions_url = await gym.url()
            directions_text = await gym._name()
            exraid = await gym._exraid()
            if train.current_raid:
                current_gym = train.current_raid.gym
                if isinstance(current_gym, Gym):
                    times = await Mapper.get_travel_times(bot, [current_gym.id], [gym.id])
                    travel_time = times[0]['travel_time']
        else:
            directions_url = gym.url
            directions_text = gym._name + " (Unknown Gym)"
            exraid = False
        if exraid:
            directions_text += " (EX Raid Gym)"
        fields = {
            bossfield: name,
            "Gym": f"[{directions_text}]({directions_url})",
            "Travel Time": travel_time
        }
        embed = formatters.make_embed(title="Raid Report", # msg_colour=color,
            thumbnail=img_url, fields=fields, footer="Ending")
        embed.timestamp = enddt
        return cls(embed)

class MeetupEmbed:

    def __init__(self, embed):
        self.embed = embed
    
    status_index = 0
    team_index = 1

    @property
    def status_str(self):
        return self.embed.fields[MeetupEmbed.status_index].value
    
    @status_str.setter
    def status_str(self, status_str):
        self.embed.set_field_at(MeetupEmbed.status_index, name="Status List", value=status_str)
    
    @property
    def team_str(self):
        return self.embed.fields[MeetupEmbed.team_index].value
    
    @team_str.setter
    def team_str(self, team_str):
        self.embed.set_field_at(MeetupEmbed.team_index, name="Team List", value=team_str)
    
    @classmethod
    async def from_meetup(cls, meetup: Meetup):
        location = meetup.location
        if isinstance(location, POI):
            directions_url = await location.url()
            directions_text = await location._name()
        else:
            directions_url = location.url
            directions_text = location._name + " (Unknown Location)"
            exraid = False
        status_str = meetup.status_str
        team_str = meetup.team_str
        fields = {
            "Status List": status_str,
            "Team List": team_str
        }
        footer_text = "Starting"
        embed = formatters.make_embed(title=directions_text,
            thumbnail='', title_url=directions_url, # msg_colour=color,
            fields=fields, footer=footer_text)
        embed.timestamp = meetup.start_datetime
        return cls(embed)