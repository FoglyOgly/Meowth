import discord
from discord import app_commands

from .raid_cog import RaidCog, Raid, Meetup
from .raid_commands import RaidCommands

def setup(bot):
    bot.add_cog(RaidCog(bot))
    tree = bot.tree or app_commands.CommandTree(bot)
    tree.add_command(RaidCommands())
    bot.loop.create_task(tree.sync())
    bot.tree = tree