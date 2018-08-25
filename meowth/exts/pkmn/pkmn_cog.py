from meowth import Cog, command
from meowth.utils import get_match

import discord

class Pokemon:

    def __init__(self, bot, pokemonId, gender=None, shiny=False):