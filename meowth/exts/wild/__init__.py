import discord
from discord import app_commands

from .wild_cog import WildCog
from .wild_commands import WildCommands

def setup(bot):
    bot.add_cog(WildCog(bot))
    tree = getattr(bot, 'tree', None) or app_commands.CommandTree(bot)
    tree.add_command(WildCommands())
    bot.loop.create_task(tree.sync())
    bot.tree = tree