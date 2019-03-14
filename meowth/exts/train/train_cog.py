from meowth import Cog, command, bot, checks
from meowth.exts.map import Gym

class Train:

    def __init__(self, bot, guild_id, channel_id):
        self.bot = bot
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.current_raid = None
    
    @property
    def guild(self):
        return self.bot.get_guild(self.guild_id)
    
    @property
    def channel(self):
        return self.bot.get_channel(self.channel_id)
    
    async def route_url(self, next_raid):
        if isinstance(next_raid.gym, Gym):
            lat2, lon2 = await next_raid.gym._coords()
            dest_str = f"&destination={lat2},{lon2}"
        else:
            return next_raid.gym.url
        prefix = "https://www.google.com/maps/dir/?api=1"
        if isinstance(self.current_raid.gym, Gym):
            lat1, lon1 = await self.current_raid.gym._coords()
            origin_str = f"&origin={lat1},{lon1}"
            prefix += origin_str
        prefix += dest_str
        prefix += "&dir_action=navigate"

    

