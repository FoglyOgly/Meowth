from discord.ext.commands import CommandError

class InvalidTime(CommandError):
    'Exception raised, raid time invalid'
    pass

class RaidDisabled(CommandError):
    'Exception raised, raid not enabled'
    pass

class TrainDisabled(CommandError):
    'Exception raised, train not enabled'
    pass

class GroupTooBig(CommandError):
    'Exception raised, group too big'
    pass

class NotRaidChannel(CommandError):
    'Exception raised, not raid channel'
    pass

class NotTrainChannel(CommandError):
    'Exception raised, not train channel'
    pass

class RaidNotActive(CommandError):
    'Exception raised, raid not active'
    pass

class MeetupDisabled(CommandError):
    'Exception raised, meetup not enabled'
    pass
