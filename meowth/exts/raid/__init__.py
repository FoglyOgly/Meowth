import discord
from discord import app_commands

from .raid_cog import RaidCog, Raid, Meetup
from .raid_commands import RaidCommands

def setup(bot):
    bot.add_cog(RaidCog(bot))
    tree = app_commands.CommandTree(bot)
    tree.add_command(RaidCommands(), guild=discord.Object(id=344960572649111552))
    bot.loop.create_task(tree.sync(guild=discord.Object(id=344960572649111552)))