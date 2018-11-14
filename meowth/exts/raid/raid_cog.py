from meowth import Cog, command, bot
from meowth.exts.map import Gym, ReportChannel
from meowth.exts.pkmn import Pokemon, Move
from meowth.utils import formatters
from . import raid_info

import discord
import aiohttp
import time
from datetime import timezone, datetime

class RaidBoss(Pokemon):

    def __init__(self, pkmn):
        self = pkmn

    

    @property
    def raid_level(self):
        for level in self.bot.raid_info.raid_lists:
            if self.id in self.bot.raid_info.raid_lists[level]:
                return level
        
    
    @classmethod
    async def convert(cls, ctx, arg):
        pkmn = await super().convert(ctx, arg)
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
            active_time = bot.config.raid_times[level[1]]
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
    
    # async def generic_counters_data(self):
        


    async def egg_embed(self):
        raid_icon = '' #TODO
        level = self.level
        title = f"Level {level} Raid Egg"
        egg_img_url = self.bot.raid_info.egg_images[level]
        boss_list = self.boss_list
        hatch = self.hatch
        hatchdt = datetime.fromtimestamp(hatch, tzinfo=timezone.utc)
        gym = self.gym
        directions_url = await gym.url()
        directions_text = "Click here for directions to this raid!"
        boss_names = []
        for x in boss_list:
            boss = RaidBoss(x)
            name = await boss.name()
            type_emoji = await boss.type_emoji()
            boss_names.append(f"{name} {type_emoji}")
        half_length = -len(boss_names)//2
        bosses_left = boss_names[0:half_length]
        bosses_right = boss_names[half_length:]
        fields = {
            "Possible Bosses:": "\n".join(bosses_left),
            "\u200b": "\n".join(bosses_right)
        }
        footer_text = "Hatches at"
        embed = formatters.make_embed(icon=raid_icon, title=title, thumbnail=egg_img_url,
            fields=fields, footer=footer_text)
        embed.timestamp = hatchdt
        embed.title = directions_text
        embed.url = directions_url
        return embed

    async def raid_embed(self):
        raid_icon = '' #TODO
        boss = self.pkmn
        level = boss.raid_level
        if level == 6:
            display_level = 5
        else:
            display_level = level
        boss_name = await boss.name()
        boss_type = await boss.type_emoji()
        weather = await self.weather()
        is_boosted = await boss.is_boosted(weather)
        end = self.end
        enddt = datetime.fromtimestamp(end)
        title = f"{boss_name} Raid (Level {display_level})"
        img_url = await boss.sprite_url()
        gym = self.gym
        directions_url = await gym.url()
        gym_name = await gym._name()
        exraid = await gym._exraid()
        directions_text = f"{gym_name}"
        if exraid:
            directions_text += " (EX RAID GYM)"
        resists = await boss.resistances_emoji()
        weaks = await boss.weaknesses_emoji()
        fields = {
            "Weaknesses": weaks,
            "Resistances": resists
        }
        embed = formatters.make_embed(icon=raid_icon, title=title,
            thumbnail=img_url, fields=fields, footer="Ends at")
        embed.timestamp = enddt
        embed.title = directions_text
        embed.url = directions_url
        return embed
    
    # async def hatch_egg(self):

    # async def report_hatch(self, pkmn):

    # async def update_weather(self, weather):
    
    # async def expire_raid(self):
    
    # async def update_gym(self, gym):     
        

class RaidCog(Cog):
    
    def __init__(self, bot):
        bot.raid_info = raid_info
        self.bot = bot
    
    @command()
    async def raid(self, ctx, level_or_boss, gym: Gym, endtime: int):
        if level_or_boss.isdigit():
            level = level_or_boss
            boss = None
            hatch = time.time() + 60*endtime
            end = None
        else:
            boss = await RaidBoss.convert(ctx, level_or_boss)
            level = boss.raid_level
            end = time.time() + 60*endtime
            hatch = None
        new_raid = Raid(ctx.bot, gym, level=level, pkmn = boss, hatch=hatch, end=end)
        if new_raid.hatch:
            embed = await new_raid.egg_embed()
        else:
            embed = await new_raid.raid_embed()
        await ctx.send(embed=embed)
    
    @command()
    async def countersupdate(self, ctx):
        data_table = ctx.bot.dbi.table('counters_data')
        raid_lists = ctx.bot.raid_info.raid_lists
        weather_list = ['CLEAR', 'PARTLY_CLOUDY', 'OVERCAST', 'RAINY', 'SNOW', 'FOG', 'WINDY']
        ctrs_data_list = []
        for level in raid_lists:
            for pkmnid in raid_lists[level]:
                for weather in weather_list:
                    data_url = Raid.pokebattler_data_url(
                        pkmnid, level, weather
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
        return await insert.commit()



