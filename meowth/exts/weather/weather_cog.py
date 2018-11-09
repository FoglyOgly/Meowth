from meowth import Cog, command, bot
from meowth.exts.map import S2_L10
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
    
    @classmethod
    async def from_data(cls, bot, data):
        phrase = data['IconPhrase']
        phrase_query = bot.dbi.table('accuweather').query()
        phrase_query.where(phrase=phrase)
        wind_speed = data['Wind']['Speed']['Value']
        if wind_speed > 24:
            phrase_query.select('precipitation')
            precip = await phrase_query.get_value()
            if not precip:
                return cls(bot, 'WINDY')
        phrase_query.select('weather')
        weather = await phrase_query.get_value()
        return cls(bot, weather)



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
            print(cell)
            s2cell = S2_L10(self.bot, cell)
            place_id = await s2cell.weather_place()
            update = {}
            weather_update = self.bot.dbi.table('weather_forecasts').update()
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
                        update[time] = weather.value
            weather_update.where(cellid=cell)
            weather_update.values(**update)
            await weather_update.commit()
        

                        



        
    

    

    
