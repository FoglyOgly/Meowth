from meowth import Cog, command, bot
from discord.ext import commands
from meowth.utils.fuzzymatch import get_match
import pywraps2 as s2
import aiohttp
import asyncio
import datetime
import io
import codecs
from math import radians, degrees
import csv


class ReportChannel():
    def __init__(self, bot, channel):
        self.bot = bot
        self.channel = channel

    @property
    def _data(self):
        channel_query = self.bot.dbi.table('report_channels').query()
        _data = channel_query.where(channelid=self.channel.id)
        return _data
    
    async def center_coords(self):
        data = self._data
        record = (await data.get())[0]
        return (record['lat'], record['lon'])
    
    async def radius(self):
        data = self._data
        radius = await data.select('radius').get_value()
        return radius
    
    async def raid_report(self):
        data = self._data
        raid = await data.select('raid').get_value()
        return raid
    
    async def wild_report(self):
        data = self._data
        wild = await data.select('wild').get_value()
        return wild
    
    async def research_report(self):
        data = self._data
        research = await data.select('research').get_value()
        return research
    
    async def raidparty_report(self):
        data = self._data
        raidparty = await data.select('raidparty').get_value()
        return raidparty
    
    async def user_report(self):
        data = self._data
        user = await data.select('user').get_value()
        return user
    
    async def clean_mode(self):
        data = self._data
        clean = await data.select('clean').get_value()
        return clean
    
    async def s2_cap(self):
        coords = await self.center_coords()
        point = s2.S2LatLng.FromDegrees(*coords).ToPoint()
        radius = await self.radius()
        angle = radius/6371.0
        cap = s2.S2Cap(point, s2.S1Angle.Radians(angle))
        return cap

    async def point_in_channel(self, coords):
        cell = S2_L10.from_coords(self.bot, coords)
        covering = await self.level_10_covering()
        return cell.cellid in covering

    
    async def level_10_covering(self):
        cap = await self.s2_cap()
        coverer = s2.S2RegionCoverer()
        coverer.set_fixed_level(10)
        covering = coverer.GetCovering(cap)
        id_list = [hex(x.id()) for x in covering]
        return id_list

    async def get_all_gyms(self):
        covering = await self.level_10_covering()
        gyms = self.bot.dbi.table('gyms')
        gyms_query = gyms.query().where(gyms['l10'].in_(covering))
        gyms_query.where(guild=self.channel.guild.id)
        return gyms_query


        


class S2_L10():

    def __init__(self, bot, cellid):
        self.bot = bot
        self.cellid = cellid
        
    @classmethod
    def from_coords(cls, bot, coords):
        cellid = hex(s2.S2CellId(
            s2.S2LatLng.FromDegrees(*coords)
        ).parent(10).id())
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
            async with session.get(url, params=params) as resp:
                data = await resp.json()
                place_id = data[0]['Key']
                return place_id


    async def weather(self):
        weather_query = self.bot.dbi.table('weather_forecasts').query()
        current_hour = datetime.datetime.utcnow().hour % 12
        col = f"forecast_{current_hour}"
        weather_query.select(col).where(cellid=self.cellid)
        weather = await weather_query.get_value()
        return weather

    async def get_all_gyms(self):
        gyms_table = self.bot.dbi.table('gyms')
        gyms_query.select('id').where(l10=self.cellid)
        gyms = await gyms_query.get_values()
        return gyms



class POI():

    def __init__(self, bot, poi_id):
        self.bot = bot
        self.id = poi_id
    
    async def _coords(self):
        data = self._data
        record = (await data.get())[0]
        return (record['lat'], record['lon'])

    async def _L10(self):
        data = self._data
        L10 = await data.select('l10').get_value()
        return L10
    
    async def _name(self):
        data = self._data
        name = await data.select('name').get_value()
        return name
    
    async def _nick(self):
        data = self._data
        nick = await data.select('nickname').get_value()
        return nick
    
    async def _guildid(self):
        data = self._data
        guildid = await data.select('guild').get_value()
        return guildid
    
    async def guild(self):
        guildid = await self._guildid()
        guild = bot.get_guild(guildid)
        return guild
    
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
        return weather
    


class Gym(POI):

    @property 
    def _data(self):
        data = self.bot.dbi.table('gyms').query()
        data = data.where(id=self.id)
        return data
    
    async def _exraid(self):
        data = self._data
        exraid = await data.select('exraid').get_value()
        return exraid

    @classmethod
    async def convert(cls, ctx, arg):
        report_channel = ReportChannel(ctx.bot, ctx.channel)
        gyms_query = await report_channel.get_all_gyms()
        gyms_query.select('id', 'name', 'nickname')
        data = await gyms_query.get()
        nick_dict = {}
        for x in data:
            if x.get('nickname'):
                nick_dict[x['nickname']] = x['id']
            else:
                continue
        name_dict = {x['name'] : x['id'] for x in data}
        match = get_match(nick_dict.keys(), arg)
        if match:
            return cls(ctx.bot, nick_dict[match[0]])
        match = get_match(name_dict.keys(), arg)
        if match:
            return cls(ctx.bot, data_dict[match[0]])
    
    @classmethod
    async def insert_from_data(cls, bot, guildid, data):
        gyms_table = bot.dbi.table('gyms')
        insert = gyms_table.insert()
        data['guild'] = guildid
        insert.row(**data)
        rcrdlist = await insert.commit(do_update=True)
        rcrd = rcrdlist[0]
        return cls(bot, rcrd['id'])


    


class Pokestop(POI):

    @property
    def _data(self):
        data = self.bot.dbi.table('stops').query()
        data = data.where(stop_id=self.id)
        return data

class Mapper(Cog):

    def __init__(self, bot):
        self.bot = bot
    
    async def gyms_from_csv(self, guildid, file):
        bot = self.bot
        gyms_table = bot.dbi.table('gyms')
        insert = gyms_table.insert()
        reader = csv.DictReader(codecs.iterdecode(file.readlines(), 'utf-8'))
        rows = []
        for row in reader:
            valid_data = {}
            valid_data['guild'] = guildid
            if isinstance(row.get('name'), str):
                valid_data['name'] = row['name']
            else:
                continue
            if isinstance(row.get('nickname'), str):
                valid_data['nickname'] = row.get('nickname')
            else:
                pass
            try:
                lat = float(row.get('lat'))
                lon = float(row.get('lon'))
            except:
                continue
            l10 = S2_L10.from_coords(bot, (lat, lon))
            valid_data['lat'] = lat
            valid_data['lon'] = lon
            valid_data['l10'] = l10.cellid
            if isinstance(row.get('exraid'), str):
                if row['exraid'].lower() == 'false':
                    valid_data['exraid'] = False
                elif row['exraid'].lower() == 'true':
                    valid_data['exraid'] = True
            rows.append(valid_data)
        insert.rows(rows)
        await insert.commit(do_update=True)
    
    @command()
    @commands.has_permissions(manage_guild=True)
    async def importgyms(self, ctx):
        attachment = ctx.message.attachments[0]
        guildid = ctx.guild.id
        bot = ctx.bot
        f = io.BytesIO()
        await attachment.save(f)
        await self.gyms_from_csv(guildid, f)

    
    

    