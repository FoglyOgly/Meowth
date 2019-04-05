from discord.ext.commands import CommandError

class MapCSVImportFailure(CommandError):
    'Exception raised, CSV import failed'
    pass

class InvalidLocation(CommandError):
    'Exception raised, invalid location'
    pass

class InvalidGMapsKey(CommandError):
    'Exception raised, invalid Google Maps API Key'
    pass

