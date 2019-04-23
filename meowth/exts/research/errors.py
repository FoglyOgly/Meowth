from discord.ext.commands import CommandError

class ResearchDisabled(CommandError):
    'Exception raised, research not enabled'
    pass