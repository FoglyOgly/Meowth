from meowth import Cog, command, bot, checks
from meowth.exts.map import POI, Pokestop, ReportChannel, PartialPOI
from meowth.exts.pkmn import Pokemon, Move
from meowth.exts.pkmn.errors import PokemonInvalidContext
from meowth.exts.want import Want
from meowth.exts.users import MeowthUser
from meowth.utils import formatters, snowflake, fuzzymatch
from meowth.utils.converters import ChannelMessage

import time
from datetime import datetime, timedelta
import asyncio
import pytz
from pytz import timezone
from math import ceil
from discord.ext import commands
from discord.ext.commands import Greedy
from typing import Optional
from enum import Enum, auto

from . import rocket_checks
from .errors import *

class RocketType(Enum):
    GRUNT = 0
    ARLO = 1
    CLIFF = 2
    SIERRA = 3
    GIOVANNI = 4

    @classmethod
    async def convert(cls, ctx, arg):
        arg = arg.lower()
        choices = ['grunt', 'arlo', 'cliff', 'sierra', 'giovanni']
        name = fuzzymatch.get_match(choices, arg)
        if name[0]:
            index = choices.index(name[0])
            return cls(index)
        else:
            raise RocketNotFound



class Rocket():
    instances = dict()
    by_message = dict()

    def __new__(cls, mod_id, *args, **kwargs):
        if mod_id in cls.instances:
            return cls.instances[mod_id]
        instance = super().__new__(cls)
        cls.instances[mod_id] = instance
        return instance

    def __init__(self, mod_id, bot, guild_id, reporter_id, location, kind, tz):
        self.id = mod_id
        self.bot = bot
        self.guild_id = guild_id
        self.reporter_id = reporter_id
        self.location = location
        self.kind = kind
        self.created = time.time()
        self.tz = tz
        self.message_ids = []
        emoji = {
            'coming': '🚗',
            'despawn': '💨',
            'caught': 581146003177078784
        }
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
            'kind': self.kind.value,
            'created': self.created,
            'messages': self.message_ids
        }
        if hasattr(self, 'pokemon'):
            d['pokemon'] = self.pokemon
        return d

    @property
    def _data(self):
        table = self.bot.dbi.table('rockets')
        query = table.query.where(id=self.id)
        return query

    @property
    def _insert(self):
        table = self.bot.dbi.table('rockets')
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
        if self.kind == RocketType.GRUNT:
            return 'Team GO Rocket Grunt'
        if self.kind == RocketType.ARLO:
            return 'Team GO Rocket Leader Arlo'
        if self.kind == RocketType.CLIFF:
            return 'Team GO Rocket Leader Cliff'
        if self.kind == RocketType.SIERRA:
            return 'Team GO Rocket Leader Sierra'
        if self.kind == RocketType.GIOVANNI:
            return 'Team GO Rocket Boss Giovanni'
    
    def img_url(self):
        url = ("https://raw.githubusercontent.com/"
            "FoglyOgly/Meowth/new-core/meowth/images/misc/")
        url += f"{self.kind.name.lower()}.png"
        return url

    async def summary_str(self, tz):
        name = self.name
        if isinstance(self.location, Pokestop):
            directions_url = await self.location.url()
            directions_text = await self.location._name()
            if len(directions_text) > 28:
                directions_text = directions_text[:25] + "..."
        else:
            directions_url = self.location.url
            directions_text = self.location._name
            if len(directions_text) > 23:
                directions_text = directions_text[:20] + "..."
            directions_text = directions_text + " (Unknown Pokestop)"
        stamp = self.created
        localzone = timezone(tz)
        reported_dt = datetime.fromtimestamp(stamp, tz=localzone)
        reported_str = reported_dt.strftime('%I:%M %p')
        summary = f'{name} at [{directions_text}]({directions_url}) reported at {reported_str}'
        return summary
    
    @property
    def expires_at(self):
        if self.kind == RocketType.GRUNT:
            return self.created + 1800
        tz = timezone(self.tz)
        created_dt = datetime.fromtimestamp(self.created, tz=tz)
        expire_dt = created_dt + timedelta(days=1)
        expire_dt = expire_dt.replace(hour=0,minute=0,second=0)
        expire_dt = expire_dt.astimezone(pytz.utc)
        return expire_dt.timestamp()

    async def monitor_status(self):
        despawn = self.expires_at
        sleep = despawn - time.time()
        if sleep > 0:
            await asyncio.sleep(sleep)
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
        wants.append(Want(self.bot, self.kind.name.lower(), self.guild_id))
        wants.append(Want(self.bot, 'rocket', self.guild_id))
        return wants

    async def despawned_embed(self):
        name = self.name
        embed = formatters.make_embed(content=f"This {name} has ended!", footer="Ended")
        embed.timestamp = datetime.fromtimestamp(self.end)
        return embed

    async def despawn_mod(self):
        channels_users, message_list = await self.users_channels_messages()
        del Rocket.instances[self.id]
        for idstring in self.message_ids:
            del Rocket.by_message[idstring]
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
        mod_table = self.bot.dbi.table('rockets')
        query = mod_table.query
        query.where(id=self.id)
        await query.delete()
        if self.monitor_task:
            self.monitor_task.cancel()

    async def process_reactions(self, payload):
        if payload.guild_id:
            user = payload.member
        else:
            return
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
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
        elif emoji == self.react_list['caught']:
            await message.remove_reaction(payload.emoji, user)
            if not hasattr(self, 'pokemon'):
                ask = await channel.send(f'{user.mention} - what three Shadow Pokemon did the enemy have? Reply below with their names, in the order the enemy used them.')
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
                embed = (await RocketEmbed.from_mod(self)).embed
                for idstring in self.message_ids:
                    try:
                        chn, msg = await ChannelMessage.from_id_string(self.bot, idstring)
                        await msg.edit(embed=embed)
                    except:
                        continue
                    


    @classmethod
    async def from_data(cls, bot, data):
        if data['location'].startswith('pokestop/'):
            loc_id = data['location'].split('/', maxsplit=1)[1]
            location = Pokestop(bot, int(loc_id))
        else:
            city, arg = data['location'].split('/', maxsplit=1)
            location = PartialPOI(bot, city, arg)
        guild_id = data['guild']
        mod_id = data['id']
        reporter_id = data.get('reporter_id')
        kind = data['kind']
        kind = RocketType(kind)
        tz = data['tz']
        mod = cls(mod_id, bot, guild_id, reporter_id, location, kind, tz)
        mod.message_ids = data['messages']
        for idstring in mod.message_ids:
            Rocket.by_message[idstring] = mod
        mod.created = data['created']
        if data.get('pokemon'):
            mod.pokemon = data['pokemon']
        mod.monitor_task = bot.loop.create_task(mod.monitor_status())
        return mod


class RocketCog(Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.pickup_rocketdata())
    
    
    async def pickup_rocketdata(self):
        mod_table = self.bot.dbi.table('rockets')
        query = mod_table.query
        data = await query.get()
        for rcrd in data:
            self.bot.loop.create_task(Rocket.from_data(self.bot, rcrd))

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return
        idstring = f'{payload.channel_id}/{payload.message_id}'
        mod = Rocket.by_message.get(idstring)
        if mod:
            return await mod.process_reactions(payload)
    
    @Cog.listener()
    async def on_command_completion(self, ctx):
        if ctx.command.name == 'list':
            if await rocket_checks.is_rocket_enabled(ctx):
                if len(ctx.args) == 2 or 'rockets' in ctx.args:
                    tz = await ctx.tz()
                    return await self.list_rockets(ctx.channel, tz)
    
    @Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, RocketNotFound):
            await ctx.error('Invalid Rocket Type')

    async def list_rockets(self, channel, tz):
        report_channel = ReportChannel(self.bot, channel)
        data = await report_channel.get_all_rockets()
        if not data:
            return await channel.send("No Team GO Rocket Invasions reported!")
        wild_list = []
        for wild_id in data:
            wild = Rocket.instances.get(wild_id)
            if not wild:
                continue
            wild_list.append(await wild.summary_str(tz))
        number = len(wild_list)
        page_size = 10
        pages = ceil(number/page_size)
        ins = list(range(0, number, page_size))
        color = channel.guild.me.color
        for i in range(pages):
            if pages == 1:
                title = "Current Team GO Rocket Invasions"
            else:
                title = f"Current Team GO Rocket Invasions (Page {i+1} of {pages})"
            content = "\n\n".join(wild_list[ins[i]:ins[i]+page_size])
            embed = formatters.make_embed(title=title, content=content, msg_colour=color)
            await channel.send(embed=embed)
    
    @command(aliases=['tr'])
    @rocket_checks.rocket_enabled()
    @checks.location_set()
    async def rocket(self, ctx, rocket_type: Optional[RocketType] = RocketType.GRUNT, pokemon: Greedy[Pokemon] = [], *, location: Pokestop):

        """Report a Team GO Rocket Pokestop invasion.

        **Arguments**
        *rocket_type (optional):* The type of Invasion. One of 'grunt', 'arlo',
        'cliff', 'sierra', or 'giovanni'. Defaults to 'grunt'.
        *pokemon (optional):* The names of the Pokemon the enemy has, in order.
        If you give more than three Pokemon, only the first three will be used.
        *location:* The location of the invasion.

        If *location* is the name of a known Pokestop,
        directions will be accurate. Otherwise Meowth just Googles
        the supplied *location* plus the name of the city.

        **Example:** `!rocket city park`"""

        mod_id = next(snowflake.create())
        name = rocket_type.name.lower()
        tz = await ctx.tz()
        new_mod = Rocket(mod_id, self.bot, ctx.guild.id, ctx.author.id, location, rocket_type, tz)
        if pokemon:
            if len(pokemon) > 3:
                pokemon = pokemon[:3]
            new_mod.pokemon = [x.id for x in pokemon]
            pkmn_names = [await x.name() for x in pokemon]
            pkmn_str = f"The enemy's party: {', '.join(pkmn_names)}! "
        else:
            pkmn_str = ""
        react_list = list(new_mod.react_list.values())
        wants = await new_mod.get_wants()
        mentions = [await x.mention() for x in wants if await x.mention()]
        mention_str = "\u200b".join(mentions)
        embed = (await RocketEmbed.from_mod(new_mod)).embed
        if mentions:
            reportcontent = mention_str + " - "
        else:
            reportcontent = ""
        coming = '🚗'
        caught_id = new_mod.react_list['caught']
        caught = ctx.bot.get_emoji(caught_id)
        despawned = '💨'
        name = new_mod.name
        report_channels = []
        report_channel = ReportChannel(ctx.bot, ctx.channel)
        if isinstance(location, Pokestop):
            loc_name = await location._name()
            channel_list = await location.get_all_channels('rocket')
            report_channels.extend(channel_list)
        else:
            loc_name = location._name
        reportcontent += f'{name} reported at {loc_name}! {pkmn_str}Use {coming} if you are on the way, {str(caught)} if you catch the Shadow Pokemon, and {despawned} if it has ended.'
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
            Rocket.by_message[idstring] = new_mod
        await new_mod.upsert()
        self.bot.loop.create_task(new_mod.monitor_status())


class RocketEmbed():

    def __init__(self, embed):
        self.embed = embed


    @classmethod
    async def from_mod(cls, mod: Rocket):
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
        reporter = mod.guild.get_member(mod.reporter_id)
        if not reporter:
            reporter = await mod.guild.fetch_member(mod.reporter_id)
        reporter = reporter.display_name
        footer = f"Reported by {reporter}"
        reportdt = datetime.fromtimestamp(mod.created)
        color = mod.guild.me.color
        embed = formatters.make_embed(title=f"{name} Report", msg_colour=color,
            thumbnail=img_url, fields=fields, footer=footer)
        embed.timestamp = reportdt
        return cls(embed)
