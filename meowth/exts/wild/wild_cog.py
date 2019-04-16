from meowth import Cog, command, bot, checks
from meowth.exts.map import POI, Gym, Pokestop, ReportChannel, PartialPOI
from meowth.exts.pkmn import Pokemon, Move
from meowth.exts.weather import Weather
from meowth.exts.want import Want
from meowth.exts.users import MeowthUser
from meowth.utils import formatters, snowflake
from meowth.utils.converters import ChannelMessage

import time
from datetime import datetime
import asyncio
from pytz import timezone

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

    def __init__(self, wild_id, bot, guild_id, location, pkmn: Pokemon):
        self.id = wild_id
        self.bot = bot
        self.guild_id = guild_id
        self.location = location
        self.pkmn = pkmn
        self.created = time.time()
        self.message_ids = []
        self.react_list = bot.wild_info.emoji
        self.monitor_task = None

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
        has_embed = False
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
            await message.clear_reactions()
        for channel in channels_users:
            mentions = [x.mention for x in channels_users[channel]]
            if len(mentions) > 0:
                content = f"{' '.join(mentions)} - The {name} has despawned!"
                await channel.send(content)
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
            `$iv##/##/##`
            `$lvl##`
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
            await reply.delete()
            await msg.delete()
            for idstring in self.message_ids:
                chn, msg = await ChannelMessage.from_id_string(self.bot, idstring)
                old_embed = msg.embeds[0]
                old_fields = old_embed.to_dict()['fields']
                new_fields = new_embed.to_dict()['fields']
                if old_fields == new_fields:
                    badmsg = await channel.send('No valid arguments were received!')
                    await asyncio.sleep(10)
                    return await badmsg.delete()
                await msg.edit(embed=new_embed)

    
    async def process_reactions(self, payload):
        id_string = f"{payload.channel_id}/{payload.message_id}"
        user = self.bot.get_user(payload.user_id)
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.get_message(payload.message_id)
        meowthuser = MeowthUser(self.bot, user)
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
    
    @classmethod
    async def from_data(cls, bot, data):
        if data['location'].startswith('gym/'):
            loc_id = data['location'].split('/')[1]
            location = Gym(bot, int(loc_id))
        elif data['location'].startswith('pokestop/'):
            loc_id = data['location'].split('/')[1]
            location = Pokestop(bot, int(loc_id))
        else:
            city, arg = data['location'].split('/')
            location = PartialPOI(bot, city, arg)
        guild_id = data['guild']
        pkmn_id = data['pkmn']
        pkmn = Pokemon(bot, pkmn_id)
        wild_id = data['id']
        wild = cls(wild_id, bot, guild_id, location, pkmn)
        wild.message_ids = data['messages']
        for idstring in wild.message_ids:
            Wild.by_message[idstring] = wild
        wild.created = data['created']
        wild.monitor_task = bot.loop.create_task(wild.monitor_status())
        return wild

        

class WildCog(Cog):

    def __init__(self, bot):
        bot.wild_info = wild_info
        self.bot = bot
        self.pickup_task = self.bot.loop.create_task(self.pickup_wilddata())
    
    async def pickup_wilddata(self):
        wild_table = self.bot.dbi.table('wilds')
        query = wild_table.query()
        data = await query.get()
        for rcrd in data:
            self.bot.loop.create_task(Wild.from_data(self.bot, rcrd))

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return
        idstring = f'{payload.channel_id}/{payload.message_id}'
        wild = Wild.by_message.get(idstring)
        if wild:
            return await wild.process_reactions(payload)
    
    @Cog.listener()
    async def on_command_completion(self, ctx):
        if ctx.command.name == 'list':
            if await wild_checks.is_wild_enabled(ctx):
                tz = await ctx.tz()
                return await self.list_wilds(ctx.channel, tz)
    
    @command(aliases=['w'])
    @wild_checks.wild_enabled()
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
        wild_table = self.bot.dbi.table('wilds')
        wild_id = next(snowflake.create())
        new_wild = Wild(wild_id, self.bot, ctx.guild.id, location, pkmn)
        react_list = list(new_wild.react_list.values())
        name = await pkmn.name()
        family = await pkmn._familyId()
        want = Want(ctx.bot, family, ctx.guild.id)
        role = await want.role()
        embed = (await WildEmbed.from_wild(new_wild)).embed
        if role:
            reportcontent = role.mention + " - "
        else:
            reportcontent = ""
        reportcontent += f'Wild {name} reported!'
        report_channels = []
        report_channel = ReportChannel(ctx.bot, ctx.channel)
        if isinstance(location, POI):
            if isinstance(location, Gym):
                loc_id = 'gym/' + str(location.id)
            elif isinstance(location, Pokestop):
                loc_id = 'pokestop/' + str(location.id)
            channel_list = await gym.get_all_channels()
            report_channels.extend(channel_list)
        else:
            loc_id = f'{location.city}/{location.arg}'
            report_channels.append(report_channel)
        for channel in report_channels:
            if not role:
                dm_content = f"Wild {name} reported in {ctx.channel.name}!"
                dms = await want.notify_users(dm_content, embed)
                new_wild.message_ids.extend(dms)
            reportmsg = await channel.channel.send(reportcontent, embed=embed)
            for react in react_list:
                if isinstance(react, int):
                    react = self.bot.get_emoji(react)
                await reportmsg.add_reaction(react)
            new_wild.message_ids.append(f"{reportmsg.channel.id}/{reportmsg.id}")
        d = {
            'id': wild_id,
            'guild': ctx.guild.id,
            'location': loc_id,
            'pkmn': pkmn.id,
            'created': new_wild.created,
            'messages': new_wild.message_ids
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
        title = "Current Wild Spawns"
        content = "\n\n".join(wild_list)
        embed = formatters.make_embed(title=title, content=content)
        await channel.send(embed=embed)
        

class WildEmbed():

    def __init__(self, embed):
        self.embed = embed
    
    pkmn_index = 0
    weather_index = 1
    cp_index = 2
    iv_index = 3
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
        return self.embed.fields[WildEmbed.iv_index].value
    
    @iv_str.setter
    def iv_str(self, iv_str):
        self.embed.set_field_at(WildEmbed.iv_index, name="IVs: Atk/Def/Sta", value=iv_str)
    
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
        weather_name = await weather.name()
        weather_emoji = await weather.boosted_emoji_str()
        is_boosted = await wild.pkmn.is_boosted(weather.value)
        cp_str = str(wild.pkmn.cp) if wild.pkmn.cp else "Unknown"
        if is_boosted:
            cp_str += " (Boosted)"
        img_url = await wild.pkmn.sprite_url()
        attiv = str(wild.pkmn.attiv) if wild.pkmn.attiv else "?"
        defiv = str(wild.pkmn.defiv) if wild.pkmn.defiv else "?"
        staiv = str(wild.pkmn.staiv) if wild.pkmn.staiv else "?"
        iv_str = f'{attiv}/{defiv}/{staiv}'
        if isinstance(wild.location, POI):
            directions_url = await wild.location.url()
            directions_text = await wild.location._name()
        else:
            directions_url = wild.location.url
            directions_text = wild.location._name + " (Unknown Location)"
        fields = {
            'Pokemon': f'{name} {type_emoji}',
            'Weather': f'{weather_name} {weather_emoji}'.strip(),
            'CP': cp_str,
            "IVs: Atk/Def/Sta": iv_str,
            'Moveset': moveset.strip(),
            'Gender': wild.pkmn.gender.title() if wild.pkmn.gender else "Unknown"
        }
        reportdt = datetime.fromtimestamp(wild.created)
        embed = formatters.make_embed(title=directions_text, # msg_colour=color,
            title_url=directions_url, thumbnail=img_url, fields=fields, footer="Reported")
        embed.timestamp = reportdt
        return cls(embed)

    


