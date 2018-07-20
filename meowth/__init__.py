#!/usr/bin/python3
"""Meowth - A Discord helper bot for Pokemon Go communities.

Meowth is a Discord bot written in Python 3.6 using version 1.0.0a (rewrite)
of the discord.py library. It assists with the organisation of local
Pokemon Go Discord servers and their members."""

__version__ = "3.0.0"

__author__ = "FoglyOgly and Scragly"
__credits__ = ["FoglyOgly", "6_lasers", "Scragly"]
__license__ = "GNU General Public License v3.0"
__maintainer__ = "FoglyOgly"
__status__ = "Production"

from .core import bot, checks, Cog, command, context, errors, group
from .core.data_manager import dbi, schema, sqltypes
