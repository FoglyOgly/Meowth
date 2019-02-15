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

from . import wild_info

class Wild():

    def __init__(self, bot, guild_id, location, pkmn: Pokemon, created: float=time.time()):
        self.bot = bot
        self.guild_id = guild_id
        self.location = location
        self.pkmn = pkmn
        self.created = created
        self.message_ids = []
        self.react_list = bot.wild_info.emoji
        self.expired = False
    
    async def weather(self):
        if isinstance(self.location, POI):
            return await self.location.weather()
        else:
            return "NO_WEATHER"
    
    async def set_cp(self, cp: int):
        has_embed = False
        for idstring in self.message_ids:
            chn, msg = await ChannelMessage.from_id_string(self.bot, idstring)
            if not has_embed:
                embed = WildEmbed(msg.embeds[0])
                embed.cp_str = str(cp)
                has_embed = True
            await msg.edit(embed=embed)
    
    async def set_gender(self, gender: str):
        has_embed = False
        gender_type = await self.pkmn._gender_type()
        if gender_type in ('NONE', 'MALE', 'FEMALE'):
            return
        if self.pkmn.gender == gender.upper():
            return
        self.pkmn.gender = gender.upper()
        for idstring in self.message_ids:
            chn, msg = await ChannelMessage.from_id_string(self.bot, idstring)
            if not has_embed:
                embed = WildEmbed(msg.embeds[0])
                embed.gender_str = gender.title()
                if gender_type == 'DIMORPH':
                    sprite_url = await self.pkmn.sprite_url()
                    self.embed.set_thumbnail(url=sprite_url)
                has_embed = True
            await msg.edit(embed=embed)
    
    async def set_moveset(self, move1, move2=None):
        has_embed = False
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
        for idstring in self.message_ids:
            chn, msg = await ChannelMessage.from_id_string(self.bot, idstring)
            if not has_embed:
                embed = WildEmbed(msg.embeds[0])
                embed.moveset_str = moveset_str
                has_embed = True
            await msg.edit(embed=embed)
    
    async def set_ivs(self, attiv, defiv, staiv):
        iv_str = f'{attiv}/{defiv}/{staiv}'
        for idstring in self.message_ids:
            chn, msg = await ChannelMessage.from_id_string(self.bot, idstring)
            if not has_embed:
                embed = WildEmbed(msg.embeds[0])
                embed.iv_str = iv_str
                has_embed = True
            await msg.edit(embed=embed)

    
    async def users_channels_messages(self):
        channels_users = {}
        message_list = []
        for idstring in self.message_ids:
            chn, msg = await ChannelMessage.from_id_string(self.bot, idstring)
            channels_users[chn] = []
            message_list.append(msg)
            for react in msg.reactions:
                if react.emoji == self.react_list['coming']:
                    usrs = await reaction.users().flatten()
                    channels_users[chn].extend(usrs)
                    break
                continue
        return (channels_users, message_list)
    
    async def despawned_embed(self):
        name = await self.pkmn.name()
        embed = formatters.make_embed(content=f"This {name} has despawned!", footer="Despawned")
        embed.timestamp = datetime.fromtimestamp(self.end)

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
            await msg.edit(embed=embed)
        for channel in channels_users:
            mentions = [x.mention for x in channels_users[channel]]
            if len(mentions) > 0:
                content = f"{' '.join(mentions)} - The {name} has despawned!"
            else:
                content = f"The {name} has despawned!"
            await channel.send(content)


    
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
        if emoji == self.react_list['despawn']:
            return await self.despawn_wild()
        

class WildCog(Cog):

    def __init__(self, bot):
        bot.wild_info = wild_info
        self.bot = bot
    
    @command(aliases=['w'])
    async def wild(self, ctx, pkmn: Pokemon, *, location: POI):
        wild_table = self.bot.dbi.table('wilds')
        new_wild = Wild(self.bot, ctx.guild.id, location, pkmn)
        name = await pkmn.name()
        want = Want(ctx.bot, boss.id, ctx.guild.id)
        role = await want.role()
        embed = WildEmbed.from_wild(new_wild)
        if role:
            reportcontent = role.mention + " - "
        else:
            reportcontent = ""
        reportcontent += f'Wild {name} reported!'
        report_channels = []
        report_channel = ReportChannel(ctx.bot, ctx.channel)
        if isinstance(location, POI):
            loc_id = str(location.id)
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
            'guild_id': ctx.guild.id,
            'location': loc_id,
            'pkmn': pkmn.id,
            'created': new_wild.created
        }
        insert = wild_table.insert()
        insert.row(**d)
        insert.returning('id')
        rcrd = await insert.commit()
        new_wild.id = rcrd[0][0]
        self.bot.add_listener(new_wild.on_raw_reaction_add)
        await asyncio.sleep(3600)
        if not self.expired:
            return await self.despawn_wild()

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
            directions_text = wild.location._name + " (Unknown Gym)"
        fields = {
            'Pokemon': f'{name} {type_emoji}',
            'Weather': f'{weather_name} {weather_emoji}',
            'CP': cp_str,
            "IVs: Atk/Def/Sta": iv_str,
            'Moveset': moveset,
            'Gender': wild.pkmn.gender.title()
        }
        reportdt = datetime.fromtimestamp(wild.created)
        embed = formatters.make_embed(title=directions_text, # msg_colour=color,
            title_url=directions_url, thumbnail=img_url, fields=fields, footer="Reported")
        embed.timestamp = reportdt
        return cls(embed)

    


