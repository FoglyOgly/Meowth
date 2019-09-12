from meowth import Cog, command, bot
from meowth.exts.map import S2_L10, ReportChannel
from meowth.utils import fuzzymatch
import aiohttp
import asyncio
from datetime import datetime, timedelta
import os
from staticmap import IconMarker
from copy import deepcopy
import io
import discord

class Weather():

    def __init__(self, bot, value):
        self.bot = bot
        if not value:
            value = "NO_WEATHER"
        self.value = value

    async def name(self):
        weather_names_query = self.bot.dbi.table('weather_names').query().select('name')
        weather_names_query.where(weather=self.value).where(language_id=9)
        name = await weather_names_query.get_value()
        return name
    
    async def types_boosted(self):
        types_table = self.bot.dbi.table('types')
        query = types_table.select('typeid').where(weather=self.value)
        type_list = await query.get_values()
        return type_list
    
    async def boosted_emoji_str(self):
        types_table = self.bot.dbi.table('types')
        query = types_table.query('emoji').where(weather=self.value)
        emoji_list = await query.get_values()
        return "".join(emoji_list)
    
    @property
    def icon_url(self):
        url = f'https://github.com/FoglyOgly/Meowth/blob/new-core/meowth/images/weather/{self.value}.png?raw=true'
        return url
    
    @property
    def icon_path(self):
        bot_dir = self.bot.bot_dir
        path = os.path.join(bot_dir, "images", "weather", f"{self.value}.png")
        return path


    @classmethod
    async def from_data(cls, bot, data):
        phrase = data['IconPhrase'].lower()
        accuweather = bot.dbi.table('accuweather')
        phrase_query = accuweather.query()
        phrase_query.where(phrase=phrase)
        wind_speed = data['Wind']['Speed']['Value']
        wind_gust = data['WindGust']['Speed']['Value']
        if wind_speed + wind_gust > 55:
            phrase_query.select('precipitation')
            precip = await phrase_query.get_value()
            if not precip:
                return cls(bot, 'WINDY')
        phrase_query.select('weather')
        weather = await phrase_query.get_value()
        return cls(bot, weather)
    
    @classmethod
    async def convert(cls, ctx, arg):
        weather_names = ctx.bot.dbi.table('weather_names')
        day_names = await weather_names.query('name').get_values()
        night_names = await weather_names.query('night_name').get_values()
        names = day_names + night_names
        names = [x for x in names if x]
        match = fuzzymatch.get_match(names, arg)
        if match[0]:
            if match[0] in day_names:
                match_query = weather_names.query('weather').where(name=match[0])
            elif match[0] in night_names:
                match_query = weather_names.query('weather').where(night_name=match[0])
            matched_weather = await match_query.get_value()
            return cls(ctx.bot, matched_weather)
        else:
            raise



class WeatherCog(Cog):

    def __init__(self, bot):
        self.bot = bot
        loop = asyncio.get_event_loop()
        # loop.create_task(self.update_weather())
    
    async def update_weather(self):
        channel = self.bot.get_channel(428016400368402442)
        while True:
            now = datetime.utcnow()
            if now.minute < 30:
                then = now.replace(minute=30)
            else:
                then = (now + timedelta(hours=1)).replace(minute=30)
            sleeptime = (then - now).total_seconds()
            await channel.send(f'Sleeping until {str(then)}')
            await asyncio.sleep(sleeptime)
            weather_query = self.bot.dbi.table('current_weather').query()
            weather_query.select('cellid')
            weather_query.where(forecast=True)
            cells = await weather_query.get_values()
            cells = list(set(cells))
            pull_hour = then.hour % 8
            await channel.send(f'Pulling: pull hour is {str(pull_hour)}')
            forecast_table = self.bot.dbi.table('weather_forecasts')
            rows = []
            for cell in cells:
                s2cell = S2_L10(self.bot, cell)
                place_id = await s2cell.weather_place()
                if not place_id:
                    continue
                insert = {'cellid': cell}
                insert['pull_hour'] = pull_hour
                forecast_table = self.bot.dbi.table('weather_forecasts')
                async with aiohttp.ClientSession() as session:
                    url = f"http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/{place_id}"
                    params = {
                        'apikey' : self.bot.config.weatherapikey,
                        'details': 'true',
                        'metric': 'true'
                    }
                    async with session.get(url, params=params) as resp:
                        data = await resp.json()
                        try:
                            data = data[:8]
                        except TypeError:
                            await channel.send(f'```{data}```')
                            return
                        for hour in data:
                            weather = await Weather.from_data(self.bot, hour)
                            time = (datetime.utcfromtimestamp(hour['EpochDateTime']).hour) % 8
                            col = f"forecast_{time}"
                            insert[col] = weather.value
                rows.append(insert)
            insert = forecast_table.insert
            insert.rows(rows)
            await insert.commit(do_update=True)
    
    async def forecast(self, ctx):
        channel = ReportChannel(ctx.bot, ctx.channel)
        base_map, cells = await channel.get_map()
        markers = []
        for cell in cells:
            forecast = await cell.forecast(ctx.guild.id)
            if not forecast:
                continue
            coords = cell.center_coords
            coords = (coords.lng().degrees(), coords.lat().degrees())
            for hour in forecast:
                weather = Weather(ctx.bot, forecast[hour])
                icon_path = weather.icon_path
                m = {
                    'hour': hour,
                    'icon_path': icon_path,
                    'coords': coords
                }
                markers.append(m)
        max_hour = max([x['hour'] for x in markers])
        maps = {}
        for i in range(max_hour+1):
            maps[i] = deepcopy(base_map)
        for m in markers:
            hour = m['hour']
            frame = maps[hour]
            coords = m['coords']
            icon_path = m['icon_path']
            marker = IconMarker(coords, icon_path, 15, 15)
            marker.img = marker.img.resize((30, 30))
            frame.add_marker(marker)
        f = io.BytesIO()
        images = [m.render() for m in maps]
        await ctx.send(str(images))
        images[0].save(f, format='GIF', save_all=True, append_images=images[1:], duration=1)
        to_send = discord.File(io.BytesIO(f.getvalue()), filename='forecast.gif')
        await ctx.send(file=to_send)


            
        

                        



        
    

    

    
