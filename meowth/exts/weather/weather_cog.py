from meowth import Cog, command, bot
from meowth.exts.map import S2_L10
from meowth.utils import fuzzymatch
import aiohttp
import asyncio
from datetime import datetime

class Weather():

    def __init__(self, bot, value):
        self.bot = bot
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
        loop.create_task(self.update_weather())
    
    async def update_weather(self):
        weather_query = self.bot.dbi.table('weather_forecasts').query()
        weather_query.select('cellid')
        cells = await weather_query.get_values()
        for cell in cells:
            s2cell = S2_L10(self.bot, cell)
            place_id = await s2cell.weather_place()
            insert = {'cellid': cell}
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
                    for hour in data:
                        weather = await Weather.from_data(self.bot, hour)
                        time = datetime.utcfromtimestamp(hour['EpochDateTime']).hour % 12
                        col = f"forecast_{time}"
                        insert[col] = weather.value
            forecast_table.insert(**insert)
            await forecast_table.insert.commit(do_update=True)
        

                        



        
    

    

    
