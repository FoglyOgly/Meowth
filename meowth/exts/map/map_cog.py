from meowth import Cog, command, bot
from meowth.utils.fuzzymatch import get_match
import pywraps2 as s2
import aiohttp
import asyncio
import datetime
from discord import TextChannel
from math import radians, degrees	


class ReportChannel(TextChannel):
    def __init__(self):
        super().__init__()

    def _data(self, bot):
        channel_query = bot.dbi.table('report_channels').query()
        _data = channel_query.where(channelid=self.id)
        return _data
    
    async def center_coords(self, bot):
        data = self._data(bot)
        record = await data.get()
        return (record['lat'], record['lon'])
    
    async def radius(self, bot):
        data = self._data(bot)
        radius = await data.select('radius').get_value()
        return radius
    
    async def raid_report(self, bot):
        data = self._data(bot)
        raid = await data.select('raid').get_value()
        return raid
    
    async def wild_report(self, bot):
        data = self._data(bot)
        wild = await data.select('wild').get_value()
        return wild
    
    async def research_report(self, bot):
        data = self._data(bot)
        research = await data.select('research').get_value()
        return research
    
    async def raidparty_report(self, bot):
        data = self._data(bot)
        raidparty = await data.select('raidparty').get_value()
        return raidparty
    
    async def user_report(self, bot):
        data = self._data(bot)
        user = await data.select('user').get_value()
        return user
    
    async def clean_mode(self, bot):
        data = self._data(bot)
        clean = await data.select('clean').get_value()
        return clean
    
    async def s2_cap(self, bot):
        coords = await self.center_coords(bot)
        point = s2.S2LatLng.FromDegrees(*coords).ToPoint()
        radius = await self.radius(bot)
        angle = radius/6371.0
        cap = s2.S2Cap(point, s2.S1Angle.Radians(angle))
        return cap

    async def point_in_channel(self, bot, coords):
        cell = S2_L10.from_coords(bot, coords)
        covering = await self.level_10_covering(bot)
        return cell.cellid in covering

    
    async def level_10_covering(self, bot):
        cap = await self.s2_cap(bot)
        coverer = s2.S2RegionCoverer()
        coverer.set_fixed_level(10)
        covering = coverer.GetCovering(cap)
        return covering

    async def get_all_gyms(self, bot):
        covering = await self.level_10_covering(bot)
        gyms = bot.dbi.table('gyms')
        gyms_query = gyms.query().where(gyms['l10'] in covering)
        return gyms_query


        


class S2_L10():

    def __init__(self, bot, cellid):
        self.bot = bot
        self.cellid = cellid
        
    @classmethod
    def from_coords(cls, bot, coords):
        cellid = s2.S2CellId(
            s2.S2LatLng.FromDegrees(*coords)
        ).parent(10)
        return cls(bot, cellid)
    
    @property
    def center_coords(self):
        cellid = int(self.cellid, base=16)
        center_coords = s2.S2LatLng(s2.S2CellId(cellid).ToPoint())
        return center_coords
    
    async def weather_place(self):
        center_coords = self.center_coords
        url = 'http://dataservice.accuweather.com/locations/v1/geoposition/search.json'
        params = {
            'q': f"{center_coords.lat()},{center_coords.lng()}",
            'apikey': self.bot.config.weatherapikey,
            'toplevel': 'true'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params) as resp:
                data = await resp.json()
                place_id = data[0]['Key']
                return place_id


    async def weather(self):
        weather_query = self.bot.dbi.table('weather_forecasts')
        current_hour = datetime.datetime.utcnow().hour % 12
        weather_query.select(str(current_hour)).where(cellid=self.cellid)
        weather = await weather_query.get_value()
        return weather

    async def get_all_gyms(self):
        gyms_query = self.bot.dbi.table('gyms').query()
        gyms_query.select('gym_id').where(l10=self.cellid)
        gyms = await gyms_query.get_values()
        return gyms



class POI():

    def __init__(self, bot, poi_id):
        self.bot = bot
        self.id = poi_id
    
    async def _coords(self):
        data = self._data
        record = await data.get()
        return (record['lat'], record['lon'])

    async def _L10(self):
        data = self._data
        L10 = await data.select('l10').get_value()
        return L10
    
    async def _name(self):
        data = self._data
        name = await data.select('name').get_value()
        return name
    
    async def url(self):
        lat, lon = await self._coords()
        prefix = "https://www.google.com/maps/dir/?api=1&"
        prefix += f"destination={lat},{lon}"
        prefix += "&dir_action=navigate"
        return prefix
    
    async def weather(self):
        L10id = await self._L10()
        L10 = S2_L10(self.bot, L10id)
        weather = await L10.weather()
    


class Gym(POI):

    @property 
    def _data(self):
        data = self.bot.dbi.table('gyms').query()
        data = data.where(gym_id=self.id)
        return data
    
    async def _exraid(self):
        data = self._data
        exraid = await data.select('exraid').get_value()
        return exraid

    @classmethod
    async def convert(cls, ctx, arg):
        report_channel = ctx.channel.ReportChannel()
        gyms_query = await report_channel.get_all_gyms(ctx.bot)
        gyms_query.select('gym_id', 'name')
        data = await gyms_query.get()
        data_dict = {x['name'] : x['gym_id'] for x in data}
        gymname_list = data_dict.keys()
        match = get_match(gymname_list, arg)
        if match:
            return cls(ctx.bot, data_dict[match])

    


class Pokestop(POI):

    @property
    def _data(self):
        data = self.bot.dbi.table('stops').query()
        data = data.where(stop_id=self.id)
        return data

class Mapper(Cog):

    def __init__(self, bot):
        self.bot = bot

    