from meowth import Cog, command, bot, checks

import asyncio
import aiohttp
import time
from datetime import datetime
from dateparser import parse

from . import silph_info

class SilphCog(Cog):

    def __init__(self, bot):
        self.bot = bot

    def parse_info_from_silph(self, data):
        raid_lists = self.bot.raid_info.raid_lists
        for level in data:
            if level == 'LEVEL_6':
                new_level = 'EX'
            else:
                new_level = level[-1]
            for boss in data[level]['boss']:
                silphid = data[level]['boss']['id']
                meowthid = silphid.upper().replace('-', '_')
                forms = ['ALOLA', 'ATTACK', 'DEFENSE', 'SPEED', 'RAINY', 'SNOWY', 'SUNNY']
                for form in forms:
                    if meowthid.endswith(form):
                        meowthid += "_FORM"
                if meowthid not in raid_lists[new_level]:
                    raid_lists[new_level].append(meowthid)
    
    @command()
    @checks.is_co_owner()
    async def shakeup(self, ctx, shaketime=None):
        if shaketime:
            newdt = parse(shaketime, settings={'TIMEZONE': 'America/Chicago', 'RETURN_AS_TIMEZONE_AWARE': True})
            stamp = newdt.timestamp()
            sleeptime = time.time() - stamp
        else:
            sleeptime = 0
        await asyncio.sleep(sleeptime)
        url = 'https://api.thesilphroad.com/v0/raids'
        headers = {'Authorization': f'Silph {silph_info.api_key}'}
        async with aiohttp.ClientSession() as sess:
            async with sess.get(url, headers=headers) as resp:
                data = await resp.json()
                data = data['data']
                print(self.bot.raid_info.raid_lists)
                self.parse_info_from_silph(data)
                print(self.bot.raid_info.raid_lists)
