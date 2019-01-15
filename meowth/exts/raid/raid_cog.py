from meowth import Cog, command, bot, checks
from meowth.exts.map import Gym, ReportChannel
from meowth.exts.pkmn import Pokemon, Move
from meowth.exts.weather import Weather
from meowth.exts.want import Want
from meowth.exts.users import MeowthUser
from meowth.utils import formatters
from meowth.utils.converters import ChannelMessage
from . import raid_info
from . import raid_checks

from math import ceil
import discord
from discord import Embed
import asyncio
import aiohttp
import time
from pytz import timezone
from datetime import datetime
from dateparser import parse
from copy import deepcopy
import re
from string import ascii_lowercase

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

    

    @property
    def raid_level(self):
        for level in self.bot.raid_info.raid_lists:
            if self.id in self.bot.raid_info.raid_lists[level]:
                return level
        
    
    @classmethod
    async def convert(cls, ctx, arg):
        pkmn = await Pokemon.convert(ctx, arg)
        return cls(pkmn)   

class Raid():

    def __init__(self, bot, guild_id, gym=None, level=None,
        pkmn: RaidBoss=None, hatch: float=None, end: float=None, tz: str=None, created: float=time.time()):
        self.bot = bot
        self.guild_id = guild_id
        self.gym = gym
        self.level = level
        self.pkmn = pkmn
        if hatch:
            self.hatch = hatch
            active_time = bot.raid_info.raid_times[level][1]
            self.end = hatch + active_time*60
        elif end:
            self.end = end
            self.hatch = hatch
        self.trainer_dict = {}
        self.group_list = []
        self.tz = tz
        self.created = created
    
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
        status_reacts.append('\u25b6')
        grp_reacts = [x['emoji'] for x in self.group_list]
        if self.status == 'egg':
            if len(self.boss_list) == 1:
                react_list = status_reacts
            else:
                react_list = boss_reacts
        elif self.status == 'hatched':
            react_list = []
        elif self.status == 'active':
            react_list = status_reacts
        else:
            return None
        react_list = react_list + grp_reacts
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
    
    def update_time(self, new_time: float):
        if new_time < 0:
            raise
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
                raise
        else:
            if not max_hatch:
                max_hatch = 0
            max_stamp = created + max_active*60 + max_hatch*60
            if new_time < max_stamp:
                self.end = new_time
    
    @property
    def boss_list(self):
        level = self.level
        boss_list = self.bot.raid_info.raid_lists[level]
        return boss_list
    
    async def boss_list_str(self, weather=None):
        boss_names = []
        boss_list = self.boss_list
        boss_interest_dict = await self.boss_interest_dict()
        if not weather:
            weather = await self.weather()
        weather = Weather(self.bot, weather)
        for i in range(len(boss_list)):
            x = boss_list[i]
            interest = boss_interest_dict[x]
            boss = RaidBoss(Pokemon(self.bot, x))
            name = f'{i+1}\u20e3 '
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
                grp_str = f"{emoji}: Starting {time} ({est}%)"
                grps_str.append(grp_str)
        grps_str.append(f"Ungrouped: ({ungrp_est}%)")
        return "\n".join(grps_str)
    
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
        json_url = 'https://fight.pokebattler.com/raids/defenders/'
        json_url += f"{pkmnid}/levels/RAID_LEVEL_{level}/attackers/levels/"
        json_url += f"{att_level}/strategies/CINEMATIC_ATTACK_WHEN_POSSIBLE/"
        json_url += f"DEFENSE_RANDOM_MC"
        json_url += f"?sort=ESTIMATOR&weatherCondition={weather}"
        json_url += "&dodgeStrategy=DODGE_REACTION_TIME"
        json_url += "&aggregation=AVERAGE&randomAssistants=-1"
        return json_url
    
    @staticmethod
    def user_pokebattler_data_url(pkmnid, level, pb_id, weather):
        json_url = 'https://fight.pokebattler.com/raids/defenders/'
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
    def current_local_datetime(self):
        zone = self.tz
        localzone = timezone(zone)
        return datetime.now(tz=localzone)
    
    def local_datetime(self, stamp):
        zone = self.tz
        localzone = timezone(zone)
        return datetime.fromtimestamp(stamp, tz=localzone)
    
    async def on_raw_reaction_add(self, payload):
        id_string = f"{payload.channel_id}/{payload.message_id}"
        if id_string not in self.message_ids or payload.user_id == self.bot.user.id:
            return
        user = self.bot.get_user(payload.user_id)
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.get_message(payload.message_id)
        meowthuser = MeowthUser(self.bot, user)
        if payload.guild_id:
            guild = self.bot.get_guild(payload.guild_id)
            user = guild.get_member(user.id)
        trainer_dict = self.trainer_dict
        trainer_data = trainer_dict.get(payload.user_id, {})
        old_bosses = trainer_data.get('bosses', [])
        old_status = trainer_data.get('status')
        party = await meowthuser.party()
        total = party['total']
        bluecount = party['bluecount']
        yellowcount = party['yellowcount']
        redcount = party['redcount']
        unknowncount = party['unknowncount']
        if payload.emoji.is_custom_emoji():
            emoji = payload.emoji.id
        else:
            emoji = str(payload.emoji)
        if emoji not in self.react_list:
            return
        if isinstance(emoji, str):
            if emoji in emoji_letters:
                for group in self.group_list:
                    if emoji == group['emoji']:
                        await message.remove_reaction(emoji, user)
                        return await self.join_grp(payload.user_id, group)
        if self.status == 'egg':
            new_status = 'maybe'
            i = self.react_list.index(emoji)
            bossid = self.boss_list[i]
            if bossid not in old_bosses:
                new_bosses = old_bosses + [bossid]
            else:
                new_bosses = old_bosses
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
        await message.remove_reaction(emoji, user)
        if new_bosses != old_bosses or new_status != old_status:
            await meowthuser.rsvp(self.id, new_status, bosses=new_bosses, total=total, 
                bluecount=bluecount, yellowcount=yellowcount, 
                redcount=redcount, unknowncount=unknowncount)
    
    async def on_command_completion(self, ctx):
        if ctx.command.name not in ('counters', 'group', 'starting', 'weather', 'moveset', 'timer'):
            return
        if str(ctx.channel.id) not in self.channel_ids:
            return
        if ctx.command.name == 'timer':
            newtime = ctx.args[2]
            if newtime.isdigit():
                stamp = time.time() + 60*newtime
            else:
                try:
                    zone = self.tz
                    newdt = parse(newtime, settings={'TIMEZONE': zone})
                    stamp = newdt.timestamp()
                except:
                    raise
            self.update_time(stamp)
            for idstring in self.message_ids:
                chn, msg = await ChannelMessage.from_id_string(self.bot, idstring)
                embed = msg.embeds[0]
                embed.timestamp = stamp
                has_embed = False
                await msg.edit(embed=embed)
            return
        if ctx.command.name == 'moveset':
            if self.status != 'active':
                raise
            move1 = ctx.args[2]
            move2 = ctx.args[3]
            return await self.set_moveset(move1, move2=move2)
        if ctx.command.name == 'weather':
            weather = ctx.kwargs['weather']
            return await self.correct_weather(weather)
        if ctx.command.name == 'starting':
            if self.status != 'active':
                raise
            grp = self.user_grp(ctx.author.id)
            if not grp:
                grp = self.here_grp
            return await self.start_grp(grp, ctx.author, channel=ctx.channel)
        elif ctx.command.name == 'counters':
            if self.status != 'active':
                raise
            meowthuser = MeowthUser.from_id(ctx.bot, ctx.author.id)
            embed = await self.counters_embed(meowthuser)
            if not embed:
                return await ctx.author.send("You likely have better counters than the ones in your Pokebattler Pokebox! Please update your Pokebox!")
            await ctx.author.send(embed=embed)
            await self.update_grps()
        elif ctx.command.name == 'group':
            group_table = ctx.bot.dbi.table('raid_groups')
            insert = group_table.insert()
            num_current_groups = len(self.group_list)
            emoji = emoji_letters[num_current_groups]
            grptime = ctx.args[2]
            if grptime.isdigit():
                stamp = time.time() + int(grptime)*60
                if stamp > self.end:
                    raise
                elif self.hatch and stamp < self.hatch:
                    raise
                d = {
                    'raid_id': self.id,
                    'emoji': emoji,
                    'starttime': stamp,
                    'users': [],
                    'est_power': 0
                }
                insert.row(**d)
                await insert.commit()
                self.group_list.append(d)
                for idstring in self.message_ids:
                    chn, msg = await ChannelMessage.from_id_string(self.bot, idstring)
                    has_embed = False
                    if not has_embed:
                        if self.status == 'active':
                            raid_embed = RaidEmbed(msg.embeds[0])
                            raid_embed.grps_str = self.grps_str
                            embed = raid_embed.embed
                            has_embed = True
                        elif self.status == 'egg':
                            egg_embed = EggEmbed(msg.embeds[0])
                            egg_embed.grps_str = self.grps_str
                            embed = egg_embed.embed
                            has_embed = True
                    await msg.edit(embed=embed)
                    await msg.add_reaction(emoji)
    
    async def start_grp(self, grp, author, channel=None):
        if not self.grp_is_here(grp):
            if channel:
                return await channel.send('Please wait until your whole group is here!')
        else:
            if not channel:
                for user in grp['users']:
                    meowthuser = MeowthUser.from_id(self.bot, user)
                    await meowthuser.rsvp(self.id, "lobby")
                await self.update_rsvp()
                await asyncio.sleep(120)
                user_table = self.bot.dbi.table('users')
                update = user_table.update().where(user_table['id'].in_(grp['users']))
                update.values(lobby=None)
                await update.commit()
                self.group_list.remove(grp)
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
                await meowthuser.rsvp(self.id, "lobby")
            await self.update_rsvp()
            msg_list = []
            for chn in self.channel_ids:
                chan = self.bot.get_channel(int(chn))
                lobbymsg = await chan.send(f"Group {grp['emoji']} has entered the lobby! You can join them by reacting with ▶, or ask them to backout with ⏸")
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
                    await meowthuser.rsvp(self.id, "lobby")
                    await self.update_rsvp()
                    continue
                elif payload and str(payload.emoji) == '⏸':
                    mention_str = ""
                    for user in grp['users']:
                        meowthuser = MeowthUser.from_id(self.bot, user)
                        mention = meowthuser.user.mention + " "
                        mention_str += mention
                    backoutmsg = await channel.send(f'{mention_str}A backout has been requested! Please confirm by reacting with ✅')
                    backoutload = await formatters.ask(self.bot, [backoutmsg], timeout=starttime-time.time())
                    if backoutload and str(backoutload.emoji) == '✅':
                        for user in grp['users']:
                            meowthuser = MeowthUser.from_id(self.bot, user)
                            await meowthuser.rsvp(self.id, "here")
                        for chn in self.channel_ids:
                            chan = self.bot.get_channel(int(chn))
                            await chan.send(f"Group {grp['emoji']} has backed out! Be sure to thank them!")
                        await self.update_rsvp()
                        return
                    else:
                        continue
                else:
                    await lobbymsg.edit(content=f"Group {grp['emoji']} has entered the raid!")
            user_table = self.bot.dbi.table('users')
            update = user_table.update().where(user_table['id'].in_(grp['users']))
            update.values(lobby=None)
            await update.commit()
            self.group_list.remove(grp)
            await self.update_rsvp()
            return                

    def _rsvp(self, connection, pid, channel, payload):
        if channel != f'rsvp_{self.id}':
            return
        userid, status = payload.split('/')
        user_id = int(userid)
        event_loop = asyncio.get_event_loop()
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
            for ctr in ctrs_list:
                name = await ctr.name()
                fast = Move(self.bot, ctr.quickMoveid)
                fast_name = await fast.name()
                fast_emoji = await fast.emoji()
                charge = Move(self.bot, ctr.chargeMoveid)
                charge_name = await charge.name()
                charge_emoji = await charge.emoji()
                ctr_str = f"**{name}**: {fast_name} {fast_emoji} | {charge_name} {charge_emoji}"
                ctrs_str.append(ctr_str)
            ctrs_str.append(f'[Results courtesy of Pokebattler](https://www.pokebattler.com/raids/{self.pkmn.id})')
            ctrs_str = "\n".join(ctrs_str)
            rec_str = await self.rec_group_size(weather=weather.value)
        elif self.status == 'egg':
            boss_str = await self.boss_list_str(weather=weather.value)
        has_embed = False
        for idstring in self.message_ids:
            chn, msg = await ChannelMessage.from_id_string(self.bot, idstring)
            if not has_embed:
                if self.status == 'active':
                    raid_embed = RaidEmbed(msg.embeds[0])
                    raid_embed.set_weather(weather_str, cp_str, ctrs_str, rec_str)
                    embed = raid_embed.embed
                    has_embed = True
                elif self.status == 'egg':
                    egg_embed = EggEmbed(msg.embeds[0])
                    egg_embed.set_weather(weather_str, boss_list_str)
                    embed = egg_embed.embed
                    has_embed = True
            await msg.edit(embed=embed)
    
    async def join_grp(self, user_id, group):
        user_est = self.user_est_power(user_id)
        group_table = self.bot.dbi.table('raid_groups')
        insert = group_table.insert()
        old_query = group_table.query()
        old_query.where(raid_id=self.id)
        old_query.where(group_table['users'].contains_(user_id))
        old_grp = await old_query.get()
        if old_grp:
            old_grp = dict(old_grp[0])
            if old_grp['emoji'] == group['emoji']:
                return
            old_grp['users'].remove(user_id)
            old_grp['est_power'] = self.grp_est_power(old_grp)
            insert.row(**old_grp)
        group['users'].append(user_id)
        group['est_power'] = self.grp_est_power(group)
        insert.row(**group)
        await insert.commit(do_update=True)
        await self.update_grps(user_id=user_id, group=group)
    
    async def update_grps(self, user_id=None, group=None):
        self.group_list = await self.get_grp_list()
        has_embed = False
        for idstring in self.message_ids:
            chn, msg = await ChannelMessage.from_id_string(self.bot, idstring)
            if not has_embed:
                if self.status == 'active':
                    raid_embed = RaidEmbed(msg.embeds[0])
                    raid_embed.grps_str = self.grps_str
                    embed = raid_embed.embed
                    has_embed = True
                elif self.status == 'egg':
                    egg_embed = EggEmbed(msg.embeds[0])
                    egg_embed.grps_str = self.grps_str
                    embed = egg_embed.embed
                    has_embed = True
            await msg.edit(embed=embed)
        if user_id and group:
            if self.channel_ids and self.status != 'egg':
                for chnid in self.channel_ids:
                    rsvpembed = RSVPEmbed.from_raidgroup(self, group).embed
                    guild = self.bot.get_guild(self.guild_id)
                    member = guild.get_member(user_id)
                    chn = self.bot.get_channel(int(chnid))
                    content = f"{member.display_name} has joined Group {group['emoji']}!"
                    newmsg = await chn.send(content, embed=rsvpembed)

    async def update_rsvp(self, user_id=None, status=None):
        self.trainer_dict = await self.get_trainer_dict()
        estimator_20 = await self.estimator_20()
        has_embed = False
        for idstring in self.message_ids:
            chn, msg = await ChannelMessage.from_id_string(self.bot, idstring)
            if not has_embed:
                if self.status == 'active':
                    raid_embed = RaidEmbed(msg.embeds[0])
                    raid_embed.status_str = self.status_str
                    raid_embed.team_str = self.team_str
                    embed = raid_embed.embed
                    has_embed = True
                elif self.status == 'egg':
                    egg_embed = EggEmbed(msg.embeds[0])
                    egg_embed.team_str = self.team_str
                    egg_embed.boss_str = await self.boss_list_str()
                    embed = egg_embed.embed
                    has_embed = True
            await msg.edit(embed=embed)
        if user_id and status:
            if self.channel_ids and self.status != 'egg':
                for chnid in self.channel_ids:
                    rsvpembed = RSVPEmbed.from_raid(self).embed
                    guild = self.bot.get_guild(self.guild_id)
                    member = guild.get_member(user_id)
                    chn = self.bot.get_channel(int(chnid))
                    if status == 'maybe':
                        display_status = 'is interested'
                    elif status == 'coming':
                        display_status = 'is on the way'
                    elif status == 'here':
                        display_status = 'is at the raid'
                    elif status == 'cancel':
                        display_status = 'has canceled'
                    content = f"{member.display_name} {display_status}!"
                    newmsg = await chn.send(content, embed=rsvpembed)
        await self.update_grps()

        
    
    async def monitor_status(self):
        while True:
            hatch = self.hatch
            end = self.end
            if hatch:
                sleeptime = time.time() - hatch
                await asyncio.sleep(sleeptime)
                hatch = self.hatch
                if hatch <= time.time():
                    await self.hatch_egg()
                    continue
                else:
                    continue
            else:
                sleeptime = time.time() - end
                await asyncio.sleep(sleeptime)
                end = self.end
                if end <= time.time():
                    await self.expire_raid()
                else:
                    continue
        

    
    async def weather(self):
        gym = self.gym
        weather = await gym.weather()
        return weather
    
    async def is_boosted(self, weather=None):
        if not weather:
            weather = await self.weather()
        pkmn = self.pkmn
        return await pkmn.is_boosted(weather)
    
    async def cp_range(self, weather=None):
        boost = await self.is_boosted(weather=weather)
        if boost:
            self.pkmn.lvl = 25
        else:
            self.pkmn.lvl = 20
        self.pkmn.attiv = 10
        self.pkmn.defiv = 10
        self.pkmn.staiv = 10
        low_cp = await self.pkmn.calculate_cp()
        self.pkmn.attiv = 15
        self.pkmn.defiv = 15
        self.pkmn.staiv = 15
        high_cp = await self.pkmn.calculate_cp()
        return [low_cp, high_cp]
    
    async def pb_data(self, weather=None):
        data_table = self.bot.dbi.table('counters_data')
        if not weather:
            weather = await self.weather()
        boss = self.pkmn
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
        return (await query.get())[0]
    
    async def generic_counters_data(self, weather=None):
        data = await self.pb_data(weather=weather)
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
        estimator = data['estimator_20']
        return estimator
    
    async def estimator_min(self, weather=None):
        data = await self.pb_data(weather=weather)
        estimator = query_dict['estimator_min']
        return estimator
    
    async def rec_group_size(self, weather=None):
        estimator = await self.estimator_20(weather=weather)
        return ceil(estimator)
    
    async def min_group_size(self):
        estimator = await self.estimator_min()
        return ceil(estimator)
    
    def user_est_power(self, user_id):
        trainer_dict = self.trainer_dict.get(user_id)
        if trainer_dict:
            est_power = trainer_dict.get('est_power')
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
        pkmnid = self.pkmn.id
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
                    print(data_url)
        boss_fast = self.pkmn.quickMoveid
        boss_charge = self.pkmn.chargeMoveid
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
        has_rsvp = await user.has_rsvp(self.id)
        if has_rsvp:
            total = self.trainer_dict[user.user.id]['total']
            user_power = 1 / estimator
            extra_power = (total - 1) / est_20
            calc_power = user_power + extra_power
            self.trainer_dict[user.user.id]['est_power'] = calc_power
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
        quick_move = Move(self.bot, fast) if fast else None
        charge_move = Move(self.bot, charge) if charge else None
        self.pkmn.quickMoveid = quick_move.id
        self.pkmn.chargeMoveid = charge_move.id
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
        moveset_str = f"{quick_name} {quick_emoji}| {charge_name} {charge_emoji}"
        ctrs_list = await self.generic_counters_data()
        ctrs_str = []
        for ctr in ctrs_list:
            name = await ctr.name()
            fast = Move(self.bot, ctr.quickMoveid)
            fast_name = await fast.name()
            fast_emoji = await fast.emoji()
            charge = Move(self.bot, ctr.chargeMoveid)
            charge_name = await charge.name()
            charge_emoji = await charge.emoji()
            ctr_str = f"**{name}**: {fast_name} {fast_emoji} | {charge_name} {charge_emoji}"
            ctrs_str.append(ctr_str)
        ctrs_str.append(f'[Results courtesy of Pokebattler](https://www.pokebattler.com/raids/{self.pkmn.id})')
        ctrs_str = "\n".join(ctrs_str)
        rec = await self.rec_group_size()
        rec_str = str(rec)
        has_embed = False
        for idstring in self.message_ids:
            chn, msg = await ChannelMessage.from_id_string(self.bot, idstring)
            if not has_embed:
                raid_embed = RaidEmbed(msg.embeds[0])
                raid_embed.set_moveset(moveset_str, ctrs_str, rec_str)
                embed = raid_embed.embed
                has_embed = True
            await msg.edit(embed=embed)

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
            directions_text = gym.name + " (Unknown Gym)"
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
    

    
    async def update_messages(self, content=''):
        msg_list = []
        react_list = self.react_list
        message_ids = self.message_ids
        if self.hatch and self.hatch > time.time():
            embed = await self.egg_embed()
        elif self.pkmn is None:
            embed = await self.hatched_embed()
        elif self.end > time.time():
            embed = await self.raid_embed()
        else:
            embed = self.expired_embed()
        for messageid in message_ids:
            chn, msg = await ChannelMessage.from_id_string(self.bot, messageid)
            if not content:
                content = msg.content
            await msg.edit(content=content, embed=embed)
            msg_list.append(msg)
        if self.channel_ids:
            for chanid in self.channel_ids:
                channel = self.bot.get_channel(int(chanid))
                new_name = await self.channel_name()
                if new_name != channel.name:
                    await channel.edit(name=new_name)
        if react_list:
            for msg in msg_list:
                for react in react_list:
                    if isinstance(react, int):
                        react = self.bot.get_emoji(react)
                    await msg.add_reaction(react)
        return msg_list

    
    
    async def hatch_egg(self):
        content = "This raid egg has hatched! React below to report the boss!"
        boss_list = self.boss_list
        length = len(boss_list)
        react_list = formatters.mc_emoji(length)
        boss_dict = dict(zip(react_list, boss_list))
        msg_list = await self.update_messages(content=content)
        response = await formatters.ask(self.bot, msg_list, timeout=(self.end-time.time()),
            react_list=react_list)
        if response:
            emoji = str(response.emoji)
            pkmn = boss_dict[emoji]
            return await self.report_hatch(pkmn)
        

    async def report_hatch(self, pkmn):
        self.pkmn = RaidBoss(Pokemon(self.bot, pkmn))
        raid_table = self.bot.dbi.table('raids')
        update = raid_table.update()
        update.where(id=self.id)
        d = {
            'pkmn': (self.pkmn.id, None, None)
        }
        update.values(**d)
        await update.commit()
        return await self.update_messages()

    async def correct_weather(self, weather):
        if isinstance(self.gym, Gym):
            await self.gym.correct_weather(weather.value)
        else:
            await self.change_weather(weather.value)
        

        
    
    async def expire_raid(self):
        await self.update_messages()
        if self.channel_ids:
            for chanid in self.channel_ids:
                channel = self.bot.get_channel(int(chanid))
                await channel.delete()
        raid_table = self.bot.dbi.table('raids')
        query = raid_table.query().where(id=self.id)
        await query.delete()
    
    # async def update_gym(self, gym):

    async def boss_interest_dict(self):
        boss_list = self.boss_list
        d = {x: 0 for x in boss_list}
        trainer_dict = self.trainer_dict
        for trainer in trainer_dict:
            total = trainer_dict[trainer]['total']
            bosses = trainer_dict[trainer]['bosses']
            for boss in bosses:
                d[boss] += total
        return d

    @property
    def status_dict(self):
        d = {
            'maybe': 0,
            'coming': 0,
            'here': 0,
            'lobby': 0
        }
        trainer_dict = self.trainer_dict
        for trainer in trainer_dict:
            total = trainer_dict[trainer]['total']
            status = trainer_dict[trainer]['status']
            d[status] += total
        return d
    
    @property
    def status_str(self):
        status_dict = self.status_dict
        status_str = f"{self.bot.config.emoji['maybe']}: {status_dict['maybe']} | "
        status_str += f"{self.bot.config.emoji['coming']}: {status_dict['coming']} | "
        status_str += f"{self.bot.get_emoji(self.bot.config.emoji['here'])}: {status_dict['here']}"
        return status_str
    
    @property
    def team_dict(self):
        d = {
            'mystic': 0,
            'instinct': 0,
            'valor': 0,
            'unknown': 0
        }
        trainer_dict = self.trainer_dict
        for trainer in trainer_dict:
            bluecount = trainer_dict[trainer]['bluecount']
            yellowcount = trainer_dict[trainer]['yellowcount']
            redcount = trainer_dict[trainer]['redcount']
            unknowncount = trainer_dict[trainer]['unknowncount']
            d['mystic'] += bluecount
            d['instinct'] += yellowcount
            d['valor'] += redcount
            d['unknown'] += unknowncount
        return d

    @property
    def team_str(self):
        team_dict = self.team_dict
        team_str = f"{self.bot.config.team_emoji['mystic']}: {team_dict['mystic']} | "
        team_str += f"{self.bot.config.team_emoji['instinct']}: {team_dict['instinct']} | "
        team_str += f"{self.bot.config.team_emoji['valor']}: {team_dict['valor']} | "
        team_str += f"{self.bot.config.team_emoji['unknown']}: {team_dict['unknown']}"
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
            total = trainer_dict[trainer]['total']
            status = trainer_dict[trainer]['status']
            d[status] += total
        return d
    
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
            bluecount = trainer_dict[trainer]['bluecount']
            yellowcount = trainer_dict[trainer]['yellowcount']
            redcount = trainer_dict[trainer]['redcount']
            unknowncount = trainer_dict[trainer]['unknowncount']
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
        query = group_table.query()
        query.where(raid_id=self.id)
        grp_data = await query.get()
        for rcrd in grp_data:
            grp = {
                'raid_id': self.id,
                'emoji': rcrd['emoji'],
                'starttime': rcrd.get('starttime'),
                'users': rcrd.get('users', []),
                'est_power': rcrd['est_power']
            }
            group_list.append(grp)
        return group_list


    async def get_trainer_dict(self):
        def data(rcrd):
            trainer = rcrd['id']
            bosses = rcrd.get('bosses')
            total = rcrd['total']
            bluecount = rcrd.get('bluecount')
            yellowcount = rcrd.get('yellowcount')
            redcount = rcrd.get('redcount')
            unknowncount = rcrd.get('unknowncount')
            rcrd_dict = {
                'bosses': bosses,
                'total': total,
                'bluecount': bluecount,
                'yellowcount': yellowcount,
                'redcount': redcount,
                'unknowncount': unknowncount
            }
            interested_list = rcrd.get('interested_list')
            coming = rcrd.get('coming')
            here = rcrd.get('here')
            if self.id in interested_list:
                status = 'maybe'
            elif self.id == coming:
                status = 'coming'
            elif self.id == here:
                status = 'here'
            rcrd_dict['status'] = status
            return trainer, rcrd_dict
        old_dict = self.trainer_dict
        if self.status == 'active':
            est_20 = await self.estimator_20()
        else:
            est_20 = 0
        trainer_dict = {}
        user_table = self.bot.dbi.table('users')
        query = user_table.query()
        query.where((
            user_table['interested_list'].contains_(self.id),
            user_table['coming'] == self.id,
            user_table['here'] == self.id))
        rsvp_data = await query.get()
        for rcrd in rsvp_data:
            trainer, rcrd_dict = data(rcrd)
            old_data = old_dict.get(trainer, {})
            old_total = old_data.get('total', 0)
            if self.status == 'active':
                old_est = old_data.get('est_power', 0)
                if old_total == rcrd_dict['total'] and old_est:
                    rcrd_dict['est_power'] = old_est
                else:
                    rcrd_dict['est_power'] = rcrd_dict['total'] / est_20
            trainer_dict[trainer] = rcrd_dict
        return trainer_dict


    @classmethod
    async def from_data(cls, bot, data, listen: bool=False):
        gym = Gym(bot, data['gym'])
        level = data['level']
        guild_id = data['guild']
        pkmnid, quick, charge = data.get('pkmn', (None, None, None))
        if pkmnid:
            pkmn = Pokemon(bot, pkmnid, quickMoveid=quick, chargeMoveid=charge)
            boss = RaidBoss(pkmn)
        else:
            boss = None
        hatch = data.get('hatch')
        end = data['endtime']
        raid = cls(bot, guild_id, gym, level=level, pkmn=boss, hatch=hatch, end=end)
        raid.channel_ids = data.get('channels')
        raid.message_ids = data.get('messages')
        raid.id = data['id']
        raid.trainer_dict = await raid.get_trainer_dict()
        raid.group_list = await raid.get_grp_list()
        if listen:
            bot.add_listener(raid.on_raw_reaction_add)
        return raid
    


        

class RaidCog(Cog):
    
    def __init__(self, bot):
        bot.raid_info = raid_info
        self.bot = bot

    
    @command()
    @raid_checks.raid_enabled()
    async def raid(self, ctx, level_or_boss, gym: Gym, endtime: int):
        raid_table = ctx.bot.dbi.table('raids')
        if isinstance(gym, Gym):
            debugurl = await gym.url()
            print(debugurl)
            query = raid_table.query()
            query.where(gym=gym.id, guild=ctx.guild.id)
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
            want = Want(ctx.bot, level, ctx.guild.id)
            role = await want.role()
            boss = None
            hatch = time.time() + 60*endtime
            end = hatch + 60*ctx.bot.raid_info.raid_times[level][1]
        else:
            boss = await RaidBoss.convert(ctx, level_or_boss)
            want = Want(ctx.bot, boss.id, ctx.guild.id)
            role = await want.role()
            level = boss.raid_level
            end = time.time() + 60*endtime
            hatch = None
        zone = await ctx.tz()
        new_raid = Raid(ctx.bot, ctx.guild.id, gym, level=level, pkmn=boss, hatch=hatch, end=end, tz=zone)
        new_raid.channel_ids = []
        new_raid.message_ids = []
        react_list = new_raid.react_list
        if new_raid.hatch:
            embed = await new_raid.egg_embed()
        else:
            embed = await new_raid.raid_embed()
        if role:
            reportcontent = role.mention + " - "
        else:
            reportcontent = ""
        raid_mode = await raid_checks.raid_category(ctx, level)
        if raid_mode == 'message':
            reportcontent += "Coordinate this raid here using the reactions below!"
            if not role:
                dm_content = f"Coordinate this raid in {ctx.channel.name}!"
                dms = await want.notify_users(dm_content, embed)
                new_raid.message_ids.extend(dms)
            reportmsg = await ctx.send(reportcontent, embed=embed)
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
            raid_channel = await ctx.guild.create_text_channel(raid_channel_name,
                category=category)
            new_raid.channel_ids.append(str(raid_channel.id))
            raidmsg = await raid_channel.send(reportcontent, embed=embed)
            for react in react_list:
                if isinstance(react, int):
                    react = self.bot.get_emoji(react)
                await raidmsg.add_reaction(react)
            new_raid.message_ids.append(f"{raidmsg.channel.id}/{raidmsg.id}")
            reportcontent += f"Coordinate this raid in {raid_channel.mention}!"
            if not role:
                dm_content = f"Coordinate this raid in {raid_channel.name}!"
                dms = await want.notify_users(dm_content, embed)
                new_raid.message_ids.extend(dms)
            reportmsg = await ctx.send(reportcontent, embed=embed)
            for react in react_list:
                if isinstance(react, int):
                    react = self.bot.get_emoji(react)
                await reportmsg.add_reaction(react)
            new_raid.message_ids.append(f"{reportmsg.channel.id}/{reportmsg.id}")
        insert = raid_table.insert()
        data = {
            'gym': getattr(gym, 'id', 0),
            'guild': ctx.guild.id,
            'level': level,
            'pkmn': (boss.id, boss.quickMoveid or None, boss.chargeMoveid or None) if boss else (None, None, None),
            'hatch': hatch,
            'endtime': end,
            'messages': new_raid.message_ids,
            'channels': new_raid.channel_ids
        }
        insert.row(**data)
        insert.returning('id')
        rcrd = await insert.commit()
        new_raid.id = rcrd[0][0]
        ctx.bot.add_listener(new_raid.on_raw_reaction_add)
        ctx.bot.add_listener(new_raid.on_command_completion)
        loop = asyncio.get_event_loop()
        loop.create_task(new_raid.monitor_status())
        await ctx.bot.dbi.add_listener(f'rsvp_{new_raid.id}', new_raid._rsvp)
        if isinstance(gym, Gym):
            cellid = await gym._L10()
            await ctx.bot.dbi.add_listener(f'weather_{cellid}', new_raid._weather)
    
    @staticmethod
    async def get_raidid(ctx):
        raid_table = ctx.bot.dbi.table('raids')
        id_query = raid_table.query('id')
        id_query.where(raid_table['channels'].contains_(str(ctx.channel.id)))
        raid_id = await id_query.get_value()
        return raid_id
    
    async def rsvp(self, ctx, status, total: int=0, *teamcounts):
        raid_id = await self.get_raidid(ctx)
        meowthuser = MeowthUser.from_id(ctx.bot, ctx.author.id)
        party = await meowthuser.party_list(total=total, *teamcounts)
        bluecount, yellowcount, redcount, unknowncount = party
        if not total or total < sum(party):
            total = sum(party)
        elif total > sum(party):
            unknowncount = total - sum(party[:-1])
        await meowthuser.rsvp(raid_id, status, total=total, bluecount=bluecount,
            yellowcount=yellowcount, redcount=redcount, unknowncount=unknowncount)
    
    @command()
    @raid_checks.raid_channel()
    async def interested(self, ctx, total: int=0, *teamcounts):
        await self.rsvp(ctx, "maybe", total=total, *teamcounts)
        
    @command()
    @raid_checks.raid_channel()
    async def coming(self, ctx, total: int=0, *teamcounts):
        await self.rsvp(ctx, "coming", total=total, *teamcounts)
    
    @command()
    @raid_checks.raid_channel()
    async def here(self, ctx, total: int=0, *teamcounts):
        await self.rsvp(ctx, "here", total=total, *teamcounts)

    @command()
    @raid_checks.raid_channel()
    async def counters(self, ctx):
        pass
        
    @command()
    @raid_checks.raid_channel()
    async def group(self, ctx, time):
        pass
    
    @command()
    @raid_checks.raid_channel()
    async def starting(self, ctx):
        pass
    
    @command()
    @raid_checks.raid_channel()
    async def weather(self, ctx, *, weather: Weather):
        pass
    
    @command()
    @raid_checks.raid_channel()
    async def moveset(self, ctx, move1: Move, move2: Move=None):
        pass
    
    @command()
    @raid_checks.raid_channel()
    async def timer(self, ctx, time):
        pass
    
    @command()
    @checks.is_co_owner()
    async def countersupdate(self, ctx):
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
                                print(data_url)
                    async with aiohttp.ClientSession() as session:
                        async with session.get(data_url_min) as resp:
                            try:
                                data_min = await resp.json()
                                data_min = data_min['attackers'][0]
                            except KeyError:
                                print(data_url_min)
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
    
    def set_weather(self, weather_str, cp_str, ctrs_str, rec_str):
        self.embed.set_field_at(RaidEmbed.weather_index, name="Weather", value=weather_str)
        self.embed.set_field_at(RaidEmbed.cp_index, name="CP Range", value=cp_str)
        self.embed.set_field_at(RaidEmbed.ctrs_index, name='<:pkbtlr:512707623812857871> Counters', value=ctrs_str)
        self.embed.set_field_at(RaidEmbed.rec_index, name="Recommended Group Size", value=rec_str)
        return self
    
    def set_moveset(self, moveset_str, ctrs_str, rec_str):
        self.embed.set_field_at(RaidEmbed.moveset_index, name="Moveset", value=moveset_str)
        self.embed.set_field_at(RaidEmbed.ctrs_index, name='<:pkbtlr:512707623812857871> Counters', value=ctrs_str)
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
    def grps_str(self, grps_str):
        self.embed.set_field_at(RaidEmbed.group_index, name="Groups (Boss Damage Estimate)", value=grps_str)



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
            print(directions_url)
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
        ctrs_str = []
        for ctr in ctrs_list:
            name = await ctr.name()
            fast = Move(bot, ctr.quickMoveid)
            fast_name = await fast.name()
            fast_emoji = await fast.emoji()
            charge = Move(bot, ctr.chargeMoveid)
            charge_name = await charge.name()
            charge_emoji = await charge.emoji()
            ctr_str = f"**{name}**: {fast_name} {fast_emoji} | {charge_name} {charge_emoji}"
            ctrs_str.append(ctr_str)
            i += 1
        ctrs_str.append(f'[Results courtesy of Pokebattler](https://www.pokebattler.com/raids/{boss.id})')
        fields['<:pkbtlr:512707623812857871> Counters'] = "\n".join(ctrs_str)
        grps_str = raid.grps_str
        if grps_str:
            fields['Groups (Boss Damage Estimate)'] = grps_str
        else:
            fields['Groups (Boss Damage Estimate)'] = "\u200b"
        rec = await raid.rec_group_size()
        fields['Recommended Group Size'] = str(rec)
        embed = formatters.make_embed(icon=RaidEmbed.raid_icon, title=directions_text, # msg_colour=color,
            title_url=directions_url, thumbnail=img_url, fields=fields, footer="Ending",
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
        est = group['est_power']

        fields = {
            "Status List": status_str,
            "Team List": team_str,
            "Boss Damage Estimate": (False, str(round(est*100)) + "%")
        }
        
        embed = formatters.make_embed(icon=RSVPEmbed.raid_icon, title="Current Group RSVP Totals",
            fields=fields, footer="Ending", footer_icon=RSVPEmbed.footer_icon)
        embed.timestamp = enddt
        return cls(embed)
    
class EggEmbed():

    def __init__(self, embed):
        self.embed = embed
    
    raid_icon = 'https://media.discordapp.net/attachments/423492585542385664/512682888236367872/imageedit_1_9330029197.png'
    footer_icon = 'https://media.discordapp.net/attachments/346766728132427777/512699022822080512/imageedit_10_6071805149.png'
            
    weather_index = 0
    team_index = 1
    boss_list_index = 2

    def set_weather(self, weather_str, boss_list_str):
        self.embed.set_field_at(EggEmbed.weather_index, name="Weather", value=weather_str)
        self.boss_str = boss_list_str
        return self
    
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
        team_str = raid.team_str
        boss_str = await raid.boss_list_str()
        fields = {
            "Weather": f"{weather_name} {weather_emoji}",
            "Team List": team_str,
            "Boss Interest:": boss_str
        }
        footer_text = "Hatching"
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
