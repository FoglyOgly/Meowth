import asyncio
import functools

import discord
from discord.ext import commands

from meowth import utils, checks

from meowth.exts import pokemon


class Wild:

    icon_url = ("")


    __slots__ = [
        'bot', '_data', 'reporter_id',
        'report_id', 'report_channel_id',
        'guild_id'
    ]

    def __init__(self, bot, reporter_id,
    message_id, channel_id, guild_id, pokemon):
        self.bot = bot
        wild_dict = 