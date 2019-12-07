from discord.ext.commands import CommandError

class RocketNotFound(CommandError):
    'Exception raised, Rocket Type not found'
    pass