import discord
from discord import app_commands

from .research_cog import ResearchCog, Research
from .research_commands import ResearchCommands

def setup(bot):
    bot.add_cog(ResearchCog(bot))
    tree = getattr(bot, 'tree', None) or app_commands.CommandTree(bot)
    research_command_group = ResearchCommands()
    try:
        tree.remove_command(research_command_group.name)
    except:
        pass
    tree.add_command(research_command_group)
    bot.loop.create_task(tree.sync())
    bot.tree = tree