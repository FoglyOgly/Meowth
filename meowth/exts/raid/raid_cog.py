from meowth import Cog, command, bot
from meowth.exts.map import Gym, ReportChannel
from meowth.exts.pkmn import Pokemon, Move, RaidBoss
from meowth.utils import formatters
from . import raid_info

import discord
import time
from datetime import timezone, datetime

class Raid():

    def __init__(self, bot, gym: Gym, level=None, #fix level
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
    
    async def weather(self):
        gym = self.gym
        weather = await gym.weather()
        return weather

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
        level = self.level
        boss = self.pkmn
        boss_name = await boss.name()
        boss_type = await boss.type_emoji()
        title = f"{boss_name} Raid"
        weather = await self.gym.weather()
        is_boosted = await boss.is_boosted(weather)
        end = self.end
        enddt = datetime.fromtimestamp(end, tzinfo=timezone.utc)
        title = f"{boss_name} {boss_type} Raid (Level {level})"
        img_url = await boss.sprite_url()
        gym = self.gym
        directions_url = await gym.url()
        directions_text = "Click here for directions to this raid!"
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
    async def raid(self, ctx, level_or_boss, gym: Gym, time: int):
        if level_or_boss.isdigit():
            level = level_or_boss
            boss = None
            hatch = time.time() + 60*time
            end = None
        else:
            boss = await Pokemon.convert(ctx, level_or_boss)
            # level = boss.raid_level
            end = time.time() + 60*time
            hatch = None
        new_raid = Raid(ctx.bot, gym, pkmn = boss, hatch=hatch, end=end)
        if new_raid.hatch:
            embed = await new_raid.egg_embed()
        else:
            embed = await new_raid.raid_embed()
        await ctx.send(embed=embed)
