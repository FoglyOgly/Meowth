from meowth import Cog, command, bot, checks
from meowth.exts.map import POI, Gym, Pokestop, ReportChannel, PartialPOI
from meowth.exts.pkmn import Pokemon, Move
from meowth.exts.pkmn.errors import PokemonInvalidContext
from meowth.exts.weather import Weather
from meowth.exts.want import Want
from meowth.exts.users import MeowthUser
from meowth.utils import formatters, snowflake, fuzzymatch
from meowth.utils.converters import ChannelMessage

import time
from datetime import datetime
import asyncio
from pytz import timezone
from math import ceil
from discord.ext import commands
from discord.ext.commands import Greedy
from typing import Optional

from . import wild_info
from . import wild_checks

class Wild():

    instances = dict()
    by_message = dict()

    def __new__(cls, wild_id, *args, **kwargs):
        if wild_id in cls.instances:
            return cls.instances[wild_id]
        instance = super().__new__(cls)
        cls.instances[wild_id] = instance
        return instance

    def __init__(self, wild_id, bot, guild_id, reporter_id, location, pkmn: Pokemon, caught_by=None):
        self.id = wild_id
        self.bot = bot
        self.guild_id = guild_id
        self.reporter_id = reporter_id
        self.location = location
        self.pkmn = pkmn
        self.created = time.time()
        self.message_ids = []
        self.react_list = bot.wild_info.emoji
        if caught_by is None:
            self.caught_by = []
        else:
            self.caught_by = caught_by
        self.monitor_task = None
    
    def to_dict(self):
        location = self.location
        if isinstance(location, POI):
            if isinstance(location, Gym):
                loc_id = 'gym/' + str(location.id)
            elif isinstance(location, Pokestop):
                loc_id = 'pokestop/' + str(location.id)
        else:
            loc_id = f'{location.city}/{location.arg}'
        d = {
            'id': self.id,
            'guild': self.guild_id,
            'location': loc_id,
            'reporter_id': self.reporter_id,
            'pkmn': self.pkmn.id,
            'created': self.created,
            'messages': self.message_ids,
            'caught_by': self.caught_by
        }
        return d
    
    @property
    def _data(self):
        table = self.bot.dbi.table('wilds')
        query = table.query.where(id=self.id)
        return query
    
    @property
    def _insert(self):
        table = self.bot.dbi.table('wilds')
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

    async def summary_str(self, tz):
        name = await self.pkmn.name()
        if isinstance(self.location, POI):
            locname = await self.location._name()
        else:
            locname = self.location._name
        stamp = self.created
        localzone = timezone(tz)
        reported_dt = datetime.fromtimestamp(stamp, tz=localzone)
        reported_str = reported_dt.strftime('%I:%M %p')
        summary = f'{name} at {locname} reported at {reported_str}'
        return summary

    async def monitor_status(self):
        halfhourdespawn = self.created + 1800
        hourdespawn = self.created + 3600
        halfsleep = halfhourdespawn - time.time()
        if halfsleep > 0:
            await asyncio.sleep(halfsleep)
        await self.probably_despawned()
        hoursleep = hourdespawn - time.time()
        if hoursleep > 0:
            await asyncio.sleep(hoursleep)
        self.monitor_task = None
        await self.despawn_wild()
    
    async def weather(self):
        if isinstance(self.location, POI):
            return await self.location.weather()
        else:
            return "NO_WEATHER"

    async def users_channels_messages(self):
        channels_users = {}
        message_list = []
        for idstring in self.message_ids:
            chn, msg = await ChannelMessage.from_id_string(self.bot, idstring)
            if not msg:
                continue
            channels_users[chn] = []
            message_list.append(msg)
            for react in msg.reactions:
                if react.emoji == self.react_list['coming']:
                    usrs = await react.users().flatten()
                    channels_users[chn].extend(usrs)
                    channels_users[chn].remove(self.bot.user)
                    break
                continue
        return (channels_users, message_list)
    
    async def get_wants(self):
        wants = []
        family = await self.pkmn._familyId()
        wants.append(Want(self.bot, family, self.guild_id))
        return wants
    
    async def despawned_embed(self):
        name = await self.pkmn.name()
        embed = formatters.make_embed(content=f"This {name} has despawned!", footer="Despawned")
        embed.timestamp = datetime.fromtimestamp(self.end)
        return embed
    
    async def probably_despawned(self):
        channels_users, message_list = await self.users_channels_messages()
        name = await self.pkmn.name()
        for message in message_list:
            await message.edit(content=f"This {name} has probably despawned!")

    async def despawn_wild(self):
        channels_users, message_list = await self.users_channels_messages()
        del Wild.instances[self.id]
        for idstring in self.message_ids:
            del Wild.by_message[idstring]
        has_embed = False
        self.expired = True
        self.end = time.time()
        name = await self.pkmn.name()
        for message in message_list:
            if not has_embed:
                embed = await self.despawned_embed()
                has_embed = True
            await message.edit(content="", embed=embed)
            try:
                await message.clear_reactions()
            except:
                pass
        for channel in channels_users:
            mentions = [x.mention for x in channels_users[channel]]
            if len(mentions) > 0:
                content = f"{' '.join(mentions)} - The {name} has despawned!"
                await channel.send(content)
        score_table = self.bot.dbi.table('scoreboard')
        wild_score = 1 + len(self.caught_by)
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
        d['wild'] += wild_score
        insert = score_table.insert
        insert.row(**d)
        await insert.commit(do_update=True)
        wild_table = self.bot.dbi.table('wilds')
        query = wild_table.query
        query.where(id=self.id)
        await query.delete()
        if self.monitor_task:
            self.monitor_task.cancel()

    async def get_additional_info(self, channel, user):
        content = "Specify information about the wild spawn! You can give as many of the below options as you like."
        info_options = """
            Set CP to #### -
            Set IVs Atk/Def/Sta -
            Set Level to ## - 
            Set Moveset to MOVENAME -
            Set Gender - 
            """
        info_strings = """
            `cp####`
            `iv##/##/##`
            `lvl##`
            `@movename`
            `male` or `female`
            """
        fields = {
            'Options': info_options,
            '\u200b': info_strings
        }
        embed = formatters.make_embed(content=content, fields=fields)
        msg = await channel.send(embed=embed)
        def check(m):
            return m.author == user and m.channel == channel
        try:
            reply = await self.bot.wait_for('message', check=check, timeout=60)
        except asyncio.TimeoutError:
            return await msg.delete()
        else:
            args = reply.content.lower().split()
            for arg in args:
                await self.pkmn.get_info_from_arg(self.bot, arg)
            weather = await self.weather()
            if weather == 'NO_WEATHER':
                weather = None
            pkmn = await self.pkmn.validate('wild',weather=weather)
            self.pkmn = pkmn
            new_embed = (await WildEmbed.from_wild(self)).embed
            try:
                await reply.delete()
            except:
                pass
            try:
                await msg.delete()
            except:
                pass
            for idstring in self.message_ids:
                chn, msg = await ChannelMessage.from_id_string(self.bot, idstring)
                if not msg:
                    continue
                old_embed = msg.embeds[0]
                old_fields = old_embed.to_dict()['fields']
                new_fields = new_embed.to_dict()['fields']
                if old_fields == new_fields:
                    badmsg = await channel.send('No valid arguments were received!')
                    await asyncio.sleep(10)
                    return await badmsg.delete()
                await msg.edit(embed=new_embed)

    
    async def process_reactions(self, payload):
        user = self.bot.get_user(payload.user_id)
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if payload.guild_id:
            guild = self.bot.get_guild(payload.guild_id)
            user = guild.get_member(user.id)
        if payload.emoji.is_custom_emoji():
            emoji = payload.emoji.id
        else:
            emoji = str(payload.emoji)
        if emoji not in self.react_list.values():
            await message.remove_reaction(emoji, user)
            return
        if emoji == self.react_list['despawn']:
            return await self.despawn_wild()
        elif emoji == self.react_list['info']:
            await message.remove_reaction(emoji, user)
            return await self.get_additional_info(channel, user)
        elif emoji == self.react_list['caught']:
            if user.id not in self.caught_by:
                self.caught_by.append(user.id)
            await message.remove_reaction(payload.emoji, user)
            return await self.upsert()
        elif emoji == self.react_list['coming']:
            pass  # TODO
    
    @classmethod
    async def from_data(cls, bot, data):
        if data['location'].startswith('gym/'):
            loc_id = data['location'].split('/', maxsplit=1)[1]
            location = Gym(bot, int(loc_id))
        elif data['location'].startswith('pokestop/'):
            loc_id = data['location'].split('/', maxsplit=1)[1]
            location = Pokestop(bot, int(loc_id))
        else:
            city, arg = data['location'].split('/', maxsplit=1)
            location = PartialPOI(bot, city, arg)
        guild_id = data['guild']
        pkmn_id = data['pkmn']
        pkmn = Pokemon(bot, pkmn_id)
        wild_id = data['id']
        caught_by = data.get('caught_by', [])
        reporter_id = data.get('reporter_id')
        wild = cls(wild_id, bot, guild_id, reporter_id, location, pkmn, caught_by=caught_by)
        wild.message_ids = data['messages']
        for idstring in wild.message_ids:
            Wild.by_message[idstring] = wild
        wild.created = data['created']
        wild.monitor_task = bot.loop.create_task(wild.monitor_status())
        return wild


class Modifier():
    instances = dict()
    by_message = dict()

    def __new__(cls, mod_id, *args, **kwargs):
        if mod_id in cls.instances:
            return cls.instances[mod_id]
        instance = super().__new__(cls)
        cls.instances[mod_id] = instance
        return instance

    def __init__(self, mod_id, bot, guild_id, reporter_id, location, kind):
        self.id = mod_id
        self.bot = bot
        self.guild_id = guild_id
        self.reporter_id = reporter_id
        self.location = location
        self.kind = kind
        self.created = time.time()
        self.message_ids = []
        emoji = {
            'coming': '🚗',
            'despawn': '💨',
        }
        if kind == 'rocket':
            emoji['caught'] = 581146003177078784
        self.react_list = emoji
        self.monitor_task = None

    def to_dict(self):
        location = self.location
        if isinstance(location, Pokestop):
            loc_id = 'pokestop/' + str(location.id)
        else:
            loc_id = f'{location.city}/{location.arg}'
        d = {
            'id': self.id,
            'guild': self.guild_id,
            'location': loc_id,
            'reporter_id': self.reporter_id,
            'kind': self.kind,
            'created': self.created,
            'messages': self.message_ids
        }
        if hasattr(self, 'pokemon'):
            d['pokemon'] = self.pokemon
        return d

    @property
    def _data(self):
        table = self.bot.dbi.table('modifiers')
        query = table.query.where(id=self.id)
        return query

    @property
    def _insert(self):
        table = self.bot.dbi.table('modifiers')
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
    def name(self):
        if self.kind == 'rocket':
            return 'Team GO Rocket Invasion'
        if self.kind == 'glacial':
            return 'Glacial Lure Module'
        if self.kind == 'magnetic':
            return 'Magnetic Lure Module'
        if self.kind == 'mossy':
            return 'Mossy Lure Module'
    
    def img_url(self):
        url = ("https://raw.githubusercontent.com/"
            "FoglyOgly/Meowth/new-core/meowth/images/misc/")
        url += f"{self.kind}.png"
        return url

    async def summary_str(self, tz):
        name = self.name
        if isinstance(self.location, Pokestop):
            locname = await self.location._name()
        else:
            locname = self.location._name
        stamp = self.created
        localzone = timezone(tz)
        reported_dt = datetime.fromtimestamp(stamp, tz=localzone)
        reported_str = reported_dt.strftime('%I:%M %p')
        summary = f'{name} at {locname} reported at {reported_str}'
        return summary

    async def monitor_status(self):
        halfhourdespawn = self.created + 1800
        halfsleep = halfhourdespawn - time.time()
        if halfsleep > 0:
            await asyncio.sleep(halfsleep)
        self.monitor_task = None
        await self.despawn_mod()

    async def users_channels_messages(self):
        channels_users = {}
        message_list = []
        for idstring in self.message_ids:
            chn, msg = await ChannelMessage.from_id_string(self.bot, idstring)
            if not msg:
                continue
            channels_users[chn] = []
            message_list.append(msg)
            for react in msg.reactions:
                if react.emoji == self.react_list['coming']:
                    usrs = await react.users().flatten()
                    channels_users[chn].extend(usrs)
                    channels_users[chn].remove(self.bot.user)
                    break
                continue
        return (channels_users, message_list)

    async def get_wants(self):
        wants = []
        if hasattr(self, 'pokemon'):
            pkmn = [Pokemon(self.bot, x) for x in self.pokemon]
            families = [await x._familyId() for x in pkmn]
            families = list(set(families))
            for f in families:
                wants.append(Want(self.bot, f, self.guild_id))
        wants.append(Want(self.bot, self.kind, self.guild_id))
        return wants

    async def despawned_embed(self):
        name = self.name
        embed = formatters.make_embed(content=f"This {name} has ended!", footer="Ended")
        embed.timestamp = datetime.fromtimestamp(self.end)
        return embed

    async def despawn_mod(self):
        channels_users, message_list = await self.users_channels_messages()
        del Modifier.instances[self.id]
        for idstring in self.message_ids:
            del Modifier.by_message[idstring]
        has_embed = False
        self.expired = True
        self.end = time.time()
        name = self.name
        for message in message_list:
            if not has_embed:
                embed = await self.despawned_embed()
                has_embed = True
            await message.edit(content="", embed=embed)
            try:
                await message.clear_reactions()
            except:
                pass
        for channel in channels_users:
            mentions = [x.mention for x in channels_users[channel]]
            if len(mentions) > 0:
                content = f"{' '.join(mentions)} - The {name} has ended!"
                await channel.send(content)
        mod_table = self.bot.dbi.table('modifiers')
        query = mod_table.query
        query.where(id=self.id)
        await query.delete()
        if self.monitor_task:
            self.monitor_task.cancel()

    async def process_reactions(self, payload):
        user = self.bot.get_user(payload.user_id)
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if payload.guild_id:
            guild = self.bot.get_guild(payload.guild_id)
            user = guild.get_member(user.id)
        if payload.emoji.is_custom_emoji():
            emoji = payload.emoji.id
        else:
            emoji = str(payload.emoji)
        if emoji not in self.react_list.values():
            await message.remove_reaction(emoji, user)
            return
        if emoji == self.react_list['despawn']:
            await message.remove_reaction(emoji, user)
            return await self.despawn_mod()
        elif emoji == self.react_list['coming']:
            pass
        elif self.kind == 'rocket' and emoji == self.react_list['caught']:
            await message.remove_reaction(payload.emoji, user)
            if not hasattr(self, 'pokemon'):
                ask = await channel.send(f'{user.mention} - what three Shadow Pokemon did the Grunt have? Reply below with their names, in the order the Grunt used them.')
                def check(m):
                    return m.channel == channel and m.author == user
                reply = await self.bot.wait_for('message', check=check)
                await ask.delete()
                args = reply.content.split()
                pkmn_ids = []
                if len(args) > 3:
                    args = args[:3]
                for arg in args:
                    try:
                        pkmn = await Pokemon.from_arg(self.bot, 'rocket', channel, user.id, arg)
                        pkmn_ids.append(pkmn.id)
                    except PokemonInvalidContext as e:
                        invalid_name = await e.invalid_mons[0].name()
                        await channel.send(f'{invalid_name} cannot be a Shadow Pokemon!', delete_after=10)
                        await reply.delete()
                        continue
                await reply.delete()
                self.pokemon = pkmn_ids
                await self.upsert()
                embed = (await ModEmbed.from_mod(self)).embed
                for idstring in self.message_ids:
                    try:
                        chn, msg = await ChannelMessage.from_id_string(self.bot, idstring)
                        await msg.edit(embed=embed)
                    except:
                        continue
                    


    @classmethod
    async def from_data(cls, bot, data):
        if data['location'].startswith('gym/'):
            loc_id = data['location'].split('/', maxsplit=1)[1]
            location = Gym(bot, int(loc_id))
        elif data['location'].startswith('pokestop/'):
            loc_id = data['location'].split('/', maxsplit=1)[1]
            location = Pokestop(bot, int(loc_id))
        else:
            city, arg = data['location'].split('/', maxsplit=1)
            location = PartialPOI(bot, city, arg)
        guild_id = data['guild']
        mod_id = data['id']
        reporter_id = data.get('reporter_id')
        name = data['name']
        mod = cls(mod_id, bot, guild_id, reporter_id, location, name)
        mod.message_ids = data['messages']
        for idstring in mod.message_ids:
            Modifier.by_message[idstring] = mod
        mod.created = data['created']
        if data.get('pokemon'):
            mod.pokemon = data['pokemon']
        mod.monitor_task = bot.loop.create_task(mod.monitor_status())
        return mod


class WildCog(Cog):

    def __init__(self, bot):
        bot.wild_info = wild_info
        self.bot = bot
        self.pickup_task = self.bot.loop.create_task(self.pickup_wilddata())
        self.bot.loop.create_task(self.pickup_moddata())
    
    async def pickup_wilddata(self):
        wild_table = self.bot.dbi.table('wilds')
        query = wild_table.query()
        data = await query.get()
        for rcrd in data:
            self.bot.loop.create_task(Wild.from_data(self.bot, rcrd))
    
    async def pickup_moddata(self):
        mod_table = self.bot.dbi.table('modifiers')
        query = mod_table.query
        data = await query.get()
        for rcrd in data:
            self.bot.loop.create_task(Modifier.from_data(self.bot, rcrd))

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return
        idstring = f'{payload.channel_id}/{payload.message_id}'
        wild = Wild.by_message.get(idstring)
        if wild:
            return await wild.process_reactions(payload)
        mod = Modifier.by_message.get(idstring)
        if mod:
            return await mod.process_reactions(payload)
    
    @Cog.listener()
    async def on_command_completion(self, ctx):
        if ctx.command.name == 'list':
            if await wild_checks.is_wild_enabled(ctx):
                tz = await ctx.tz()
                return await self.list_wilds(ctx.channel, tz)
    
    @command(aliases=['w'])
    @wild_checks.wild_enabled()
    @checks.location_set()
    async def wild(self, ctx, pokemon: Pokemon, *, location: POI):
        """Report a wild Pokemon.

        **Arguments**
        *pokemon:* The name of the wild Pokemon plus additional
        information.
        *location:* The location of the wild spawn.

        If the *pokemon* argument is multiple words, wrap it in quotes.
        You may optionally supply additional information.
        If *location* is the name of a known Gym or Pokestop,
        directions will be accurate. Otherwise Meowth just Googles
        the supplied *location* plus the name of the city.
        
        **Example:** `!wild "female combee" city park`"""
        if not await pokemon._wild_available():
            raise
        weather = await location.weather()
        if weather == 'NO_WEATHER':
            weather = None
        pkmn = await pokemon.validate('wild', weather=weather)
        if pkmn.id == 'DITTO':
            disask = await ctx.send('What Pokemon is this Ditto disguised as? Type your response below.')
            def check(m):
                return m.channel == ctx.channel and m.author == ctx.author
            try:
                reply = await ctx.bot.wait_for('message', check=check)
                disguised = await Pokemon.convert(ctx, reply.content)
                await disask.delete()
                try:
                    await reply.delete()
                except:
                    pass
            except:
                disguised = None
        else:
            disguised = None
        wild_table = self.bot.dbi.table('wilds')
        wild_id = next(snowflake.create())
        new_wild = Wild(wild_id, self.bot, ctx.guild.id, ctx.author.id, location, pkmn)
        react_list = list(new_wild.react_list.values())
        name = await pkmn.name()
        family = await pkmn._familyId()
        want = Want(ctx.bot, family, ctx.guild.id)
        mention = await want.mention()
        embed = (await WildEmbed.from_wild(new_wild)).embed
        if mention:
            reportcontent = mention + " - "
        else:
            reportcontent = ""
        coming = '🚗'
        caught_id = new_wild.react_list['caught']
        caught = ctx.bot.get_emoji(caught_id)
        despawned = '💨'
        report_channels = []
        report_channel = ReportChannel(ctx.bot, ctx.channel)
        if isinstance(location, POI):
            loc_name = await self.location._name()
            if isinstance(location, Gym):
                loc_id = 'gym/' + str(location.id)
            elif isinstance(location, Pokestop):
                loc_id = 'pokestop/' + str(location.id)
            channel_list = await location.get_all_channels('wild')
            report_channels.extend(channel_list)
        else:
            loc_name = self.location._name
            loc_id = f'{location.city}/{location.arg}'
        reportcontent += f'Wild {name} reported at {loc_name}! Use {coming} if you are on the way, {str(caught)} if you catch the Pokemon, and {despawned} if the Pokemon despawns.'
        if disguised:
            dis_name = await disguised.name()
            reportcontent += f'\nThis Ditto is disguised as a {dis_name}!'
        if report_channel not in report_channels:
            report_channels.append(report_channel)
        for channel in report_channels:
            try:
                reportmsg = await channel.channel.send(reportcontent, embed=embed)
                for react in react_list:
                    if isinstance(react, int):
                        react = self.bot.get_emoji(react)
                    await reportmsg.add_reaction(react)
                new_wild.message_ids.append(f"{reportmsg.channel.id}/{reportmsg.id}")
            except:
                continue
        d = {
            'id': wild_id,
            'guild': ctx.guild.id,
            'location': loc_id,
            'reporter_id': ctx.author.id,
            'pkmn': pkmn.id,
            'created': new_wild.created,
            'messages': new_wild.message_ids,
            'caught_by': []
        }
        for idstring in new_wild.message_ids:
            Wild.by_message[idstring] = new_wild
        insert = wild_table.insert()
        insert.row(**d)
        self.bot.loop.create_task(new_wild.monitor_status())
        await insert.commit()
    
    async def list_wilds(self, channel, tz):
        report_channel = ReportChannel(self.bot, channel)
        data = await report_channel.get_all_wilds()
        if not data:
            return await channel.send("No wild spawns reported!")
        wild_list = []
        for wild_id in data:
            wild = Wild.instances.get(wild_id)
            if not wild:
                continue
            wild_list.append(await wild.summary_str(tz))
        number = len(wild_list)
        pages = ceil(number/20)
        ins = list(range(0, number, 20))
        color = self.guild.me.color
        for i in range(pages):
            if pages == 1:
                title = "Current Wild Spawns"
            else:
                title = f"Current Wild Spawns (Page {i+1} of {pages})"
            content = "\n\n".join(wild_list[ins[i]:ins[i]+20])
            embed = formatters.make_embed(title=title, content=content, msg_colour=color)
            await channel.send(embed=embed)


    @command(aliases=['tr'])
    @wild_checks.wild_enabled()
    @checks.location_set()
    async def rocket(self, ctx, pokemon: Greedy[Pokemon] = [], *, location: Pokestop):

        """Report a Team GO Rocket Pokestop invasion.

        **Arguments**
        *pokemon (optional):* The names of the Pokemon the Grunt has, in order.
        If you give more than three Pokemon, only the first three will be used.
        *location:* The location of the invasion.

        If *location* is the name of a known Pokestop,
        directions will be accurate. Otherwise Meowth just Googles
        the supplied *location* plus the name of the city.

        **Example:** `!rocket city park`"""

        mod_id = next(snowflake.create())
        name = 'rocket'
        new_mod = Modifier(mod_id, self.bot, ctx.guild.id, ctx.author.id, location, name)
        if pokemon:
            if len(pokemon) > 3:
                pokemon = pokemon[:3]
            new_mod.pokemon = [x.id for x in pokemon]
            pkmn_names = [await x.name() for x in pokemon]
            pkmn_str = f"The Grunt's party: {', '.join(pkmn_names)}! "
        else:
            pkmn_str = ""
        react_list = list(new_mod.react_list.values())
        wants = await new_mod.get_wants()
        mentions = [await x.mention() for x in wants if await x.mention()]
        mention_str = "\u200b".join(mentions)
        embed = (await ModEmbed.from_mod(new_mod)).embed
        if mentions:
            reportcontent = mention_str + " - "
        else:
            reportcontent = ""
        if isinstance(location, POI):
            loc_name = await self.location._name()
        else:
            loc_name = self.location._name
        coming = '🚗'
        caught_id = new_mod.react_list['caught']
        caught = ctx.bot.get_emoji(caught_id)
        despawned = '💨'
        name = new_mod.name
        reportcontent += f'{name} reported at {loc_name}! {pkmn_str}Use {coming} if you are on the way, {str(caught)} if you catch the Shadow Pokemon, and {despawned} if it has ended.'
        report_channels = []
        report_channel = ReportChannel(ctx.bot, ctx.channel)
        if isinstance(location, Pokestop):
            channel_list = await location.get_all_channels('wild')
            report_channels.extend(channel_list)
        if report_channel not in report_channels:
            report_channels.append(report_channel)
        for channel in report_channels:
            try:
                reportmsg = await channel.channel.send(reportcontent, embed=embed)
                for react in react_list:
                    if isinstance(react, int):
                        react = self.bot.get_emoji(react)
                    await reportmsg.add_reaction(react)
                new_mod.message_ids.append(f"{reportmsg.channel.id}/{reportmsg.id}")
            except:
                continue
        for idstring in new_mod.message_ids:
            Modifier.by_message[idstring] = new_mod
        await new_mod.upsert()
        self.bot.loop.create_task(new_mod.monitor_status())

    @command()
    @wild_checks.wild_enabled()
    @checks.location_set()
    async def lure(self, ctx, kind, *, location: Pokestop):

        """Report a lured Pokestop.

        **Arguments**
        *kind:* Glacial, Mossy or Magnetic
        *location:* The location of the lure.

        If *location* is the name of a known Pokestop,
        directions will be accurate. Otherwise Meowth just Googles
        the supplied *location* plus the name of the city.

        **Example:** `!lure glacial city park`"""

        word_list = ["glacial", "mossy", "magnetic"]
        result = fuzzymatch.get_match(word_list, kind)
        kind = result[0]
        if not kind:
            raise commands.BadArgument()
        mod_id = next(snowflake.create())
        new_mod = Modifier(mod_id, self.bot, ctx.guild.id, ctx.author.id, location, kind)
        name = new_mod.name
        react_list = list(new_mod.react_list.values())
        embed = (await ModEmbed.from_mod(new_mod)).embed
        want = Want(ctx.bot, kind, ctx.guild.id)
        mention = await want.mention()
        if mention:
            reportcontent = mention + " - "
        else:
            reportcontent = ""
        if isinstance(location, POI):
            loc_name = await self.location._name()
        else:
            loc_name = self.location._name
        coming = '🚗'
        despawned = '💨'
        reportcontent += f'{name} reported at {loc_name}! Use {coming} if you are on the way and {despawned} if it has ended.'
        report_channels = []
        report_channel = ReportChannel(ctx.bot, ctx.channel)
        if isinstance(location, Pokestop):
            loc_id = 'pokestop/' + str(location.id)
            channel_list = await location.get_all_channels('wild')
            report_channels.extend(channel_list)
        else:
            loc_id = f'{location.city}/{location.arg}'
        if report_channel not in report_channels:
            report_channels.append(report_channel)
        for channel in report_channels:
            try:
                reportmsg = await channel.channel.send(reportcontent, embed=embed)
                for react in react_list:
                    if isinstance(react, int):
                        react = self.bot.get_emoji(react)
                    await reportmsg.add_reaction(react)
                new_mod.message_ids.append(f"{reportmsg.channel.id}/{reportmsg.id}")
            except:
                continue
        for idstring in new_mod.message_ids:
            Modifier.by_message[idstring] = new_mod
        await new_mod.upsert()
        self.bot.loop.create_task(new_mod.monitor_status())
        

class WildEmbed():

    def __init__(self, embed):
        self.embed = embed
    
    pkmn_index = 0
    loc_index = 1
    cp_index = 2
    lvl_iv_index = 3
    moveset_index = 4
    gender_index = 5

    @property
    def cp_str(self):
        return self.embed.fields[WildEmbed.cp_index].value
    
    @cp_str.setter
    def cp_str(self, cp_str):
        self.embed.set_field_at(WildEmbed.cp_index, name="CP", value=cp_str)
    
    @property
    def iv_str(self):
        return self.embed.fields[WildEmbed.lvl_iv_index].value
    
    @iv_str.setter
    def iv_str(self, iv_str):
        self.embed.set_field_at(WildEmbed.lvl_iv_index, name="Level/IVs: Lvl/Atk/Def/Sta", value=iv_str)
    
    @property
    def moveset_str(self):
        return self.embed.fields[WildEmbed.moveset_index].value
    
    @moveset_str.setter
    def moveset_str(self, moveset_str):
        self.embed.set_field_at(WildEmbed.moveset_index, name="Moveset", value=moveset_str)
    
    @property
    def gender_str(self):
        return self.embed.fields[WildEmbed.gender_index].value
    
    @gender_str.setter
    def gender_str(self, gender_str):
        self.embed.set_field_at(WildEmbed.gender_index, name="Gender", value=gender_str)
    
    @classmethod
    async def from_wild(cls, wild: Wild):
        name = await wild.pkmn.name()
        type_emoji = await wild.pkmn.type_emoji()
        shiny_available = await wild.pkmn._shiny_available()
        if shiny_available:
            name += ' :sparkles:'
        quick_move = Move(wild.bot, wild.pkmn.quickMoveid) if wild.pkmn.quickMoveid else None
        charge_move = Move(wild.bot, wild.pkmn.chargeMoveid) if wild.pkmn.chargeMoveid else None
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
        weather = await wild.weather()
        weather = Weather(wild.bot, weather)
        is_boosted = await wild.pkmn.is_boosted(weather.value)
        cp_str = str(wild.pkmn.cp) if wild.pkmn.cp else "Unknown"
        if is_boosted:
            cp_str += " (Boosted)"
        img_url = await wild.pkmn.sprite_url()
        lvlstr = str(wild.pkmn.lvl) if wild.pkmn.lvl else "?"
        attiv = str(wild.pkmn.attiv) if wild.pkmn.attiv is not None else "?"
        defiv = str(wild.pkmn.defiv) if wild.pkmn.defiv is not None else "?"
        staiv = str(wild.pkmn.staiv) if wild.pkmn.staiv is not None else "?"
        iv_str = f'{lvlstr}/{attiv}/{defiv}/{staiv}'
        if isinstance(wild.location, POI):
            directions_url = await wild.location.url()
            directions_text = await wild.location._name()
        else:
            directions_url = wild.location.url
            directions_text = wild.location._name + " (Unknown Location)"
        fields = {
            'Pokemon': f'{name} {type_emoji}',
            'Location': f'[{directions_text}]({directions_url})',
            'CP': cp_str,
            "Level/IVs: Lvl/Atk/Def/Sta": iv_str,
            'Moveset': moveset.strip(),
            'Gender': wild.pkmn.gender.title() if wild.pkmn.gender else "Unknown"
        }
        reporter = wild.guild.get_member(wild.reporter_id).display_name
        footer = f"Reported by {reporter}"
        reportdt = datetime.fromtimestamp(wild.created)
        color = wild.guild.me.color
        embed = formatters.make_embed(title="Wild Spawn Report", msg_colour=color,
            thumbnail=img_url, fields=fields, footer=footer)
        embed.timestamp = reportdt
        return cls(embed)


class ModEmbed():

    def __init__(self, embed):
        self.embed = embed


    @classmethod
    async def from_mod(cls, mod: Modifier):
        name = mod.name
        if isinstance(mod.location, Pokestop):
            directions_url = await mod.location.url()
            directions_text = await mod.location._name()
        else:
            directions_url = mod.location.url
            directions_text = mod.location._name + " (Unknown Location)"
        fields = {}
        if hasattr(mod, 'pokemon'):
            pkmn = [Pokemon(mod.bot, x) for x in mod.pokemon]
            pkmn_names = [await x.name() for x in pkmn]
            fields['Pokemon'] = "\n".join(pkmn_names)
        fields['Location'] = f'[{directions_text}]({directions_url})'
        img_url = mod.img_url()
        reporter = mod.guild.get_member(mod.reporter_id).display_name
        footer = f"Reported by {reporter}"
        reportdt = datetime.fromtimestamp(mod.created)
        color = mod.guild.me.color
        embed = formatters.make_embed(title=f"{name} Report", msg_colour=color,
            thumbnail=img_url, fields=fields, footer=footer)
        embed.timestamp = reportdt
        return cls(embed)

