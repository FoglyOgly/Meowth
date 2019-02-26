from meowth import Cog, command, bot, checks
from meowth.exts.map import POI, Gym, Pokestop, ReportChannel, PartialPOI
from meowth.exts.pkmn import Pokemon, Move
from meowth.exts.weather import Weather
from meowth.exts.want import Want
from meowth.exts.users import MeowthUser
from meowth.utils import formatters
from meowth.utils.converters import ChannelMessage

import time
from datetime import datetime
import asyncio

from . import wild_info
from . import wild_checks

class Wild():

    def __init__(self, bot, guild_id, location, pkmn: Pokemon):
        self.bot = bot
        self.guild_id = guild_id
        self.location = location
        self.pkmn = pkmn
        self.created = time.time()
        self.message_ids = []
        self.react_list = bot.wild_info.emoji
        self.expired = False
    
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
    
    async def despawned_embed(self):
        name = await self.pkmn.name()
        embed = formatters.make_embed(content=f"This {name} has despawned!", footer="Despawned")
        embed.timestamp = datetime.fromtimestamp(self.end)
        return embed

    async def despawn_wild(self):
        channels_users, message_list = await self.users_channels_messages()
        has_embed = False
        self.expired = True
        self.end = time.time()
        name = await self.pkmn.name()
        for message in message_list:
            if not has_embed:
                embed = await self.despawned_embed()
                has_embed = True
            await message.edit(embed=embed)
        for channel in channels_users:
            mentions = [x.mention for x in channels_users[channel]]
            if len(mentions) > 0:
                content = f"{' '.join(mentions)} - The {name} has despawned!"
                await channel.send(content)
        wild_table = self.bot.dbi.table('wilds')
        query = wild_table.query
        query.where(id=self.id)
        await query.delete()

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
                await msg.edit(embed=new_embed)

    
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
        if payload.emoji.is_custom_emoji():
            emoji = payload.emoji.id
        else:
            emoji = str(payload.emoji)
        if emoji not in self.react_list.values():
            return
        await message.remove_reaction(emoji, user)
        if emoji == self.react_list['despawn']:
            return await self.despawn_wild()
        elif emoji == self.react_list['info']:
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
        wild = cls(bot, guild_id, location, pkmn)
        wild.message_ids = data['messages']
        wild.created = data['created']
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
    
    @command(aliases=['w'])
    @wild_checks.wild_enabled()
    async def wild(self, ctx, pkmn: Pokemon, *, location: POI):
        if not await pkmn._wild_available():
            raise
        weather = await location.weather()
        if weather == 'NO_WEATHER':
            weather = None
        pkmn = await pkmn.validate('wild', weather=weather)
        wild_table = self.bot.dbi.table('wilds')
        new_wild = Wild(self.bot, ctx.guild.id, location, pkmn)
        react_list = list(new_wild.react_list.values())
        name = await pkmn.name()
        want = Want(ctx.bot, new_wild.pkmn.id, ctx.guild.id)
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
            'guild': ctx.guild.id,
            'location': loc_id,
            'pkmn': pkmn.id,
            'created': new_wild.created,
            'messages': new_wild.message_ids
        }
        insert = wild_table.insert()
        insert.row(**d)
        insert.returning('id')
        rcrd = await insert.commit()
        new_wild.id = rcrd[0][0]
        self.bot.add_listener(new_wild.on_raw_reaction_add)
        await asyncio.sleep(3600)
        if not new_wild.expired:
            return await new_wild.despawn_wild()

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
            'Weather': f'{weather_name} {weather_emoji}',
            'CP': cp_str,
            "IVs: Atk/Def/Sta": iv_str,
            'Moveset': moveset,
            'Gender': wild.pkmn.gender.title() if wild.pkmn.gender else "Unknown"
        }
        reportdt = datetime.fromtimestamp(wild.created)
        embed = formatters.make_embed(title=directions_text, # msg_colour=color,
            title_url=directions_url, thumbnail=img_url, fields=fields, footer="Reported")
        embed.timestamp = reportdt
        return cls(embed)

    


