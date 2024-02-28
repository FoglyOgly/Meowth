import discord
from discord import app_commands

from .raid_cog import RaidCog, Raid, Meetup
from .raid_commands import RaidCommands

def setup(bot):
    bot.add_cog(RaidCog(bot))
    tree = getattr(bot, 'tree', None) or app_commands.CommandTree(bot)
    raid_command_group = RaidCommands()
    try:
        tree.remove_command(raid_command_group.name)
    except:
        pass
    tree.add_command(raid_command_group)
    bot.loop.create_task(tree.sync())
    bot.tree = tree
