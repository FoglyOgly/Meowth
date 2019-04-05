from discord.ext.commands import CommandError

class InvalidWeather(CommandError):
    'Exception raised, invalid weather'
    pass

class InvalidAPIKey(CommandError):
    'Exception raised, invalid Accuweather API Key'
    pass