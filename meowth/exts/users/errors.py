from discord.ext.commands import CommandError

class TeamDisabled(CommandError):
    'Exception raised, team not enabled'
    pass

class TeamNotFound(CommandError):
    'Exception raised, team not found'
    pass

class TeamAlreadySet(CommandError):
    'Exception raised, team already set'
    pass