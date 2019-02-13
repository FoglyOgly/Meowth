from meowth import Cog, command, bot, checks
from meowth.exts.map import Gym, ReportChannel, PartialPOI
from meowth.exts.pkmn import Pokemon, Move
from meowth.exts.weather import Weather
from meowth.exts.want import Want
from meowth.exts.users import MeowthUser
from meowth.utils import formatters
from meowth.utils.converters import ChannelMessage

import time

class Wild():

    def __init__(self, bot, guild_id, location, pkmn: Pokemon, created: float=time.time()):
        self.bot = bot
        self.guild_id = guild_id
        self.location = location
        self.pkmn = pkmn
        self.created = created