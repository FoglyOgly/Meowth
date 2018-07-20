from discord.ext.commands import CommandError
from meowth.core.data_manager.errors import *

class MissingSubcommand(CommandError):
    pass

class TeamSetCheckFail(CommandError):
    'Exception raised checks.teamset fails'
    pass

class WantSetCheckFail(CommandError):
    'Exception raised checks.wantset fails'
    pass

class WildSetCheckFail(CommandError):
    'Exception raised checks.wildset fails'
    pass

class ReportCheckFail(CommandError):
    'Exception raised checks.allowreport fails'
    pass

class RaidSetCheckFail(CommandError):
    'Exception raised checks.raidset fails'
    pass

class EXRaidSetCheckFail(CommandError):
    'Exception raised checks.exraidset fails'
    pass

class ResearchSetCheckFail(CommandError):
    'Exception raised checks.researchset fails'
    pass

class MeetupSetCheckFail(CommandError):
    'Exception raised checks.meetupset fails'
    pass

class ArchiveSetCheckFail(CommandError):
    'Exception raised checks.archiveset fails'
    pass

class InviteSetCheckFail(CommandError):
    'Exception raised checks.inviteset fails'
    pass

class CityChannelCheckFail(CommandError):
    'Exception raised checks.citychannel fails'
    pass

class WantChannelCheckFail(CommandError):
    'Exception raised checks.wantchannel fails'
    pass

class RaidChannelCheckFail(CommandError):
    'Exception raised checks.raidchannel fails'
    pass

class EggChannelCheckFail(CommandError):
    'Exception raised checks.eggchannel fails'
    pass

class NonRaidChannelCheckFail(CommandError):
    'Exception raised checks.nonraidchannel fails'
    pass

class ActiveRaidChannelCheckFail(CommandError):
    'Exception raised checks.activeraidchannel fails'
    pass

class ActiveChannelCheckFail(CommandError):
    'Exception raised checks.activechannel fails'
    pass

class CityRaidChannelCheckFail(CommandError):
    'Exception raised checks.cityraidchannel fails'
    pass

class RegionEggChannelCheckFail(CommandError):
    'Exception raised checks.cityeggchannel fails'
    pass

class RegionExRaidChannelCheckFail(CommandError):
    'Exception raised checks.allowexraidreport fails'
    pass

class ExRaidChannelCheckFail(CommandError):
    'Exception raised checks.cityeggchannel fails'
    pass

class ResearchReportChannelCheckFail(CommandError):
    'Exception raised checks.researchreport fails'
    pass

class MeetupReportChannelCheckFail(CommandError):
    'Exception raised checks.researchreport fails'
    pass

class WildReportChannelCheckFail(CommandError):
    'Exception raised checks.researchreport fails'
    pass

class TradeChannelCheckFail(CommandError):
    'Exception raised checks.tradereport fails'
    pass

class TradeSetCheckFail(CommandError):
    'Exception raised checks.tradeset fails'
    pass
