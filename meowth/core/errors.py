from discord.ext.commands import CommandError
import meowth.core.data_manager.errors

class LocationNotSet(CommandError):
    'Exception raised checks.location_set fails'

class MissingSubcommand(CommandError):
    pass

class TeamSetCheckFail(CommandError):
    'Exception raised checks.teamset fails'

class WantSetCheckFail(CommandError):
    'Exception raised checks.wantset fails'

class WildSetCheckFail(CommandError):
    'Exception raised checks.wildset fails'

class ReportCheckFail(CommandError):
    'Exception raised checks.allowreport fails'

class RaidSetCheckFail(CommandError):
    'Exception raised checks.raidset fails'

class EXRaidSetCheckFail(CommandError):
    'Exception raised checks.exraidset fails'

class ResearchSetCheckFail(CommandError):
    'Exception raised checks.researchset fails'

class MeetupSetCheckFail(CommandError):
    'Exception raised checks.meetupset fails'

class ArchiveSetCheckFail(CommandError):
    'Exception raised checks.archiveset fails'

class InviteSetCheckFail(CommandError):
    'Exception raised checks.inviteset fails'

class CityChannelCheckFail(CommandError):
    'Exception raised checks.citychannel fails'

class WantChannelCheckFail(CommandError):
    'Exception raised checks.wantchannel fails'

class RaidChannelCheckFail(CommandError):
    'Exception raised checks.raidchannel fails'

class EggChannelCheckFail(CommandError):
    'Exception raised checks.eggchannel fails'

class NonRaidChannelCheckFail(CommandError):
    'Exception raised checks.nonraidchannel fails'

class ActiveRaidChannelCheckFail(CommandError):
    'Exception raised checks.activeraidchannel fails'

class ActiveChannelCheckFail(CommandError):
    'Exception raised checks.activechannel fails'

class CityRaidChannelCheckFail(CommandError):
    'Exception raised checks.cityraidchannel fails'

class RegionEggChannelCheckFail(CommandError):
    'Exception raised checks.cityeggchannel fails'

class RegionExRaidChannelCheckFail(CommandError):
    'Exception raised checks.allowexraidreport fails'

class ExRaidChannelCheckFail(CommandError):
    'Exception raised checks.cityeggchannel fails'

class ResearchReportChannelCheckFail(CommandError):
    'Exception raised checks.researchreport fails'

class MeetupReportChannelCheckFail(CommandError):
    'Exception raised checks.researchreport fails'

class WildReportChannelCheckFail(CommandError):
    'Exception raised checks.researchreport fails'

class TradeChannelCheckFail(CommandError):
    'Exception raised checks.tradereport fails'

class TradeSetCheckFail(CommandError):
    'Exception raised checks.tradeset fails'
