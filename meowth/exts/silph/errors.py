from discord.ext.commands import CommandError

class InvalidAPIKey(CommandError):
    'Exception raised, invalid Silph API Key'
    pass

class SilphCardNotFound(CommandError):
    'Exception raised, Silph Card not found'
    pass

class SilphCardPrivate(CommandError):
    'Exception raised, Silph Card private'
    pass

class SilphCardAlreadyLinked(CommandError):
    'Exception raised, Silph Card linked to different user'
    pass

