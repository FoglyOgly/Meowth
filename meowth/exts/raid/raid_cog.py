from meowth import Cog, command, bot, checks
from meowth.exts.map import Gym, ReportChannel
from meowth.exts.pkmn import Pokemon, Move
from meowth.exts.weather import Weather
from meowth.exts.want import Want
from meowth.utils import formatters
from . import raid_info
from . import raid_checks

import discord
import asyncio
import aiohttp
import time
from datetime import timezone, datetime

class RaidBoss(Pokemon):

    def __init__(self, pkmn):
        self.bot = pkmn.bot
        self.id = pkmn.id
        self.form = pkmn.form
        self.shiny = False
        self.gender = None
        self.quickMoveid = pkmn.quickMoveid
        self.chargeMoveid = pkmn.chargeMoveid

    

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

    def __init__(self, bot, gym: Gym=None, level=None,
        pkmn: RaidBoss=None, hatch: float=None, end: float=None):

        self.bot = bot
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
    
    def update_time(self, new_time: int):
        if new_time < 0:
            raise
        level = self.level
        max_times = self.bot.raid_info.raid_times[level]
        max_hatch = max_times[0]
        max_active = max_times[1]
        if self.hatch >= time.time():
            if new_time > max_hatch:
                raise
            else:
                self.hatch = time.time() + new_time*60
                self.end = self.hatch + max_active*60
        else:
            self.end = time.time() + new_time*60
    
    @property
    def boss_list(self):
        level = self.level
        boss_list = self.bot.raid_info.raid_lists[level]
        return boss_list
    
    @property
    def pokebattler_url(self):
        pkmnid = self.pkmn.id
        url = f"https://www.pokebattler.com/raids/{pkmnid}"
        return url
    
    @staticmethod
    def pokebattler_data_url(pkmnid, level, weather):
        json_url = 'https://fight.pokebattler.com/raids/defenders/'
        json_url += f"{pkmnid}/levels/RAID_LEVEL_{level}/attackers/levels/"
        json_url += "30/strategies/CINEMATIC_ATTACK_WHEN_POSSIBLE/"
        json_url += f"DEFENSE_RANDOM_MC"
        json_url += f"?sort=OVERALL&weatherCondition={weather}"
        json_url += "&dodgeStrategy=DODGE_REACTION_TIME"
        json_url += "&aggregation=AVERAGE&randomAssistants=-1"
        return json_url
    
    
    async def channel_name(self):
        gym_name = await self.gym._name()
        if self.pkmn:
            boss_name = await self.pkmn.name()
            return f"{boss_name}-{gym_name}"
        else:
            return f"{self.level}-{gym_name}"
    
    async def on_raw_reaction_add(self, payload):
        if payload.message_id not in self.message_ids:
            return
        

    
    async def weather(self):
        gym = self.gym
        weather = await gym.weather()
        return weather
    
    async def is_boosted(self):
        weather = await self.weather()
        pkmn = self.pkmn
        return await pkmn.is_boosted(weather)
    
    async def cp_range(self):
        boost = await self.is_boosted()
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
    
    async def generic_counters_data(self):
        data_table = self.bot.dbi.table('counters_data')
        weather = await self.weather()
        boss = self.pkmn
        boss_id = boss.id
        level = self.level
        if boss.quickMoveid:
            fast_move_id = boss.quickMoveid
        else:
            fast_move_id = 'random'
        if boss.chargeMoveid:
            charge_move_id = boss.chargeMoveid
        else:
            charge_move_id = 'random'
        query = data_table.query().select().where(
            boss_id=boss_id, weather=weather, level=level,
            fast_move=fast_move_id, charge_move=charge_move_id)
        query_dict = (await query.get())[0]
        ctrs_list = []
        for x in range(1,7):
            ctrid = query_dict[f'counter_{x}_id']
            ctrfast = query_dict[f'counter_{x}_fast']
            ctrcharge = query_dict[f'counter_{x}_charge']
            ctr = Pokemon(self.bot, ctrid, quickMoveid=ctrfast, chargeMoveid=ctrcharge)
            ctrs_list.append(ctr)
        return ctrs_list
        


    async def egg_embed(self):
        raid_icon = 'https://media.discordapp.net/attachments/423492585542385664/512682888236367872/imageedit_1_9330029197.png'
        footer_icon = 'https://media.discordapp.net/attachments/346766728132427777/512699022822080512/imageedit_10_6071805149.png'
        level = self.level
        egg_img_url = self.bot.raid_info.egg_images[level]
        boss_list = self.boss_list
        hatch = self.hatch
        hatchdt = datetime.fromtimestamp(hatch)
        gym = self.gym
        directions_url = await gym.url()
        directions_text = await gym._name()
        exraid = await gym._exraid()
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
            name = f'{i+1}\u20e3'
            name += await boss.name()
            type_emoji = await boss.type_emoji()
            shiny_available = await boss._shiny_available()
            if shiny_available:
                name += ':sparkles:'
            boss_names.append(f"{name} {type_emoji}")
        half_length = -len(boss_names)//2
        bosses_left = boss_names[0:half_length]
        bosses_right = boss_names[half_length:]
        fields = {
            "Weather": (False, f"{weather_name} {weather_emoji}"),
            "Possible Bosses:": "\n".join(bosses_left),
            "\u200b": "\n".join(bosses_right)
        }
        footer_text = "Hatching"
        embed = formatters.make_embed(icon=raid_icon, title=directions_text,
            thumbnail=egg_img_url, title_url = directions_url,
            fields=fields, footer=footer_text, footer_icon=footer_icon)
        embed.timestamp = hatchdt
        return embed

    async def raid_embed(self):
        raid_icon = 'https://media.discordapp.net/attachments/423492585542385664/512682888236367872/imageedit_1_9330029197.png' #TODO
        footer_icon = 'https://media.discordapp.net/attachments/346766728132427777/512699022822080512/imageedit_10_6071805149.png'
        boss = self.pkmn
        level = boss.raid_level
        if level == 6:
            display_level = 5
        else:
            display_level = level
        boss_name = await boss.name()
        type_emoji = await boss.type_emoji()
        shiny_available = await boss._shiny_available()
        if shiny_available:
            boss_name += ':sparkles:'
        boss_type = await boss.type_emoji()
        quick_move = Move(self.bot, boss.quickMoveid) if boss.quickMoveid else None
        charge_move = Move(self.bot, boss.chargeMoveid) if boss.chargeMoveid else None
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
        moveset = f"{quick_name} {quick_emoji} | {charge_name} {charge_emoji}"
        weather = await self.weather()
        weather = Weather(self.bot, weather)
        weather_name = await weather.name()
        weather_emoji = await weather.boosted_emoji_str()
        is_boosted = await boss.is_boosted(weather.value)
        cp_range = await self.cp_range()
        cp_str = f"{cp_range[0]}-{cp_range[1]}"
        end = self.end
        enddt = datetime.fromtimestamp(end)
        if is_boosted:
            cp_str += " (Boosted)"
        img_url = await boss.sprite_url()
        color = await boss.color()
        gym = self.gym
        directions_url = await gym.url()
        gym_name = await gym._name()
        exraid = await gym._exraid()
        directions_text = gym_name
        if exraid:
            directions_text += " (EX Raid Gym)"
        resists = await boss.resistances_emoji()
        weaks = await boss.weaknesses_emoji()
        ctrs_list = await self.generic_counters_data()
        fields = {
            "Boss": f"{boss_name} {type_emoji}",
            "Weather": f"{weather_name} {weather_emoji}",
            "Weaknesses": weaks,
            "Resistances": resists,
            "CP Range": f"{cp_range[0]}-{cp_range[1]}",
            "Moveset": moveset
        }
        i = 1
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
            i += 1
        ctrs_str.append(f'[Results courtesy of Pokebattler](https://www.pokebattler.com/raids/{boss.id})')
        fields['<:pkbtlr:512707623812857871> Counters'] = "\n".join(ctrs_str)
        embed = formatters.make_embed(icon=raid_icon, title=directions_text, msg_colour=color,
            title_url=directions_url, thumbnail=img_url, fields=fields, footer="Ending",
            footer_icon=footer_icon)
        embed.timestamp = enddt
        return embed
    
    async def hatch_egg(self, message):
        boss_list = self.boss_list
        for i in range(len(boss_list)):
            await message.add_reaction(f'{i+1}\u20e3')

    async def report_hatch(self, pkmn):
        self.pkmn = pkmn
        return await self.raid_embed()

    # async def update_weather(self, weather):
    
    # async def expire_raid(self):
    
    # async def update_gym(self, gym):     
        

class RaidCog(Cog):
    
    def __init__(self, bot):
        bot.raid_info = raid_info
        self.bot = bot

    
    @command()
    @raid_checks.raid_enabled()
    async def raid(self, ctx, level_or_boss, gym: Gym, endtime: int):
        raid_table = ctx.bot.dbi.table('raids')
        query = raid_table.query()
        query.where(gym=gym.id, guild=ctx.guild.id)
        old_raid = await query.get()
        if old_raid:
            #handle duplicate?
        if level_or_boss.isdigit():
            level = level_or_boss
            want = Want(ctx.bot, level, ctx.guild.id)
            role = await want.role()
            boss = None
            hatch = time.time() + 60*endtime
            end = None
        else:
            boss = await RaidBoss.convert(ctx, level_or_boss)
            want = Want(ctx.bot, boss.id, ctx.guild.id)
            role = await want.role()
            level = boss.raid_level
            end = time.time() + 60*endtime
            hatch = None
        new_raid = Raid(ctx.bot, gym, level=level, pkmn=boss, hatch=hatch, end=end)
        new_raid.channel_ids = []
        new_raid.message_ids = []
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
            new_raid.message_ids.append(reportmsg.id)
        elif raid_mode.isdigit():
            catid = int(raid_mode)
            category = ctx.guild.get_channel(catid)
            raid_channel_name = await new_raid.channel_name()
            raid_channel = await ctx.guild.create_text_channel(raid_channel_name,
                category=category)
            new_raid.channel_ids.append(raid_channel.id)
            reportcontent += f"Coordinate this raid in {raid_channel.mention}!"
            if not role:
                dm_content = f"Coordinate this raid in {raid_channel.name}!"
                dms = await want.notify_users(dm_content, embed)
                new_raid.message_ids.extend(dms)
            reportmsg = await ctx.send(reportcontent, embed=embed)
            new_raid.message_ids.extend(reportmsg.id)
        insert = raid_table.insert()
        data = {
            'gym': gym.id,
            'guild': ctx.guild.id,
            'level': level,
            'pkmn': boss.id,
            'hatch': hatch,
            'end': end
        }
        insert.row(**data)
        await insert.commit()
        
        
        
        
    
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
                        pkmnid, url_level, weather
                    )
                    async with aiohttp.ClientSession() as session:
                        async with session.get(data_url) as resp:
                            try:
                                data = await resp.json()
                                data = data['attackers'][0]
                            except KeyError:
                                print(data_url)
                    random_move_ctrs = data['randomMove']['defenders'][-6:]
                    estimator = data['randomMove']['total']['estimator']
                    random_move_dict = {
                        'boss_id': pkmnid,
                        'level': level,
                        'weather': weather,
                        'fast_move': 'random',
                        'charge_move': 'random',
                        'estimator': estimator
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
                    for moveset in data['byMove']:
                        ctrs = moveset['defenders'][-6:]
                        boss_fast = moveset['move1']
                        boss_charge = moveset['move2']
                        estimator = moveset['total']['estimator']
                        moveset_dict = {
                            'boss_id': pkmnid,
                            'level': level,
                            'weather': weather,
                            'fast_move': boss_fast,
                            'charge_move': boss_charge,
                            'estimator': estimator
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
        return await insert.commit(do_update=True)



