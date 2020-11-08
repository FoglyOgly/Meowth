import folium
from aiohttp import web
from meowth import Cog, command, bot
from meowth.exts.map import ReportChannel


class ReportChannelMap:
    def __init__(self, report_channel):
        self.report_channel = report_channel
    
    async def blank_map(self):
        location = await self.report_channel.center_coords()
        loc_list = list(location)
        m = folium.Map(location=loc_list)
        return m
    
    async def gym_map(self):
        m = await self.blank_map()
        gym_list = (await self.report_channel.get_all_gyms()).get()
        for gym in gym_list:
            coords = [gym['lat'], gym['lon']]
            name = gym['name']
            folium.Marker(coords, tooltip=name).add_to(m)
        return m

    @property
    def url(self):
        return f"https://meowthbot.com/map/{self.report_channel.channel.id}"



class WebmapCog(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.run())

    async def serve_map(self, request):
        channel_id = request.match_info['channel_id']
        channel = self.bot.get_channel(channel_id)
        report_channel = ReportChannel(self.bot, channel)
        rc_map = ReportChannelMap(report_channel)
        m = await rc_map.gym_map()
        return m._repr_html_()


    async def run(self):
        app = web.Application()
        app.add_routes([web.get('/map/{channel_id}', self.serve_map)])
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 3000)
        await site.start()

    
    @command(name='showmap')
    async def showmap(self, ctx):
        report_channel = ReportChannel(self.bot, ctx.channel)
        rc_map = ReportChannelMap(report_channel)
        await ctx.send(rc_map.url)