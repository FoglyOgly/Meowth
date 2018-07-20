"""Core contains all the required modules for getting the bot online and
running.

Extension management, basic error handling, statistics, commands for the bot
and other inbuilt features are defined here.
"""

from .bot import command, group, Bot
from .cog_base import Cog
