from discord.ext.commands import CommandError

class WantDisabled(CommandError):
    'Exception raised, want not enabled'
    pass

class InvalidWant(CommandError):
    'Exception raised, invalid want'
    pass

class DMBlocked(CommandError):
    'Exception raised, cannot DM user'
    pass