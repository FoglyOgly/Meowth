class GuildConfig:
    def __init__(self, data):
        self._data = data
        self.prefix = self.settings['prefix']
        self.offset = self.settings['offset']
        self.regional_pkmn = self.settings['regional']
        self.has_configured = self.settings['done']

    @property
    def settings(self):
        return self._data['prefix']

class RaidData:
    def __init__(self, data):
        self._data = data

class WildData:
    def __init__(self, data):
        self._data = data

class QuestData:
    def __init__(self, data):
        self._data = data

class EventData:
    def __init__(self, data):
        self._data = data

class TrainerData:
    def __init__(self, bot, data):
        self._bot = bot
        self._data = data
        self.raid_reports = data.get('raid_reports')
        self.ex_reports = data.get('ex_reports')
        self.wild_reports = data.get('wild_reports')
        self.egg_reports = data.get('egg_reports')
        self.research_reports = data.get('research_reports')
        self.silph_id = data.get('silphid')
        self.silph = self.silph_profile

    @property
    def silph_card(self):
        if not self.silph_id:
            return None
        silph_cog = self._bot.cogs.get('Silph')
        if not silph_cog:
            return None
        return silph_cog.get_silph_card(self.silph_id)

    @property
    def silph_profile(self):
        if not self.silph_id:
            return None
        silph_cog = self._bot.cogs.get('Silph')
        if not silph_cog:
            return None
        return silph_cog.get_silph_profile_lazy(self.silph_id)

class GuildData:
    def __init__(self, ctx, data):
        self.ctx = ctx
        self._data = data

    @property
    def config(self):
        return GuildConfig(self._data['configure_dict'])

    @property
    def raids(self):
        return self._data['raidchannel_dict']

    def raid(self, channel_id=None):
        channel_id = channel_id or self.ctx.channel.id
        data = self.raids.get(channel_id)
        return RaidData(data) if data else None

    @property
    def trainers(self):
        return self._data['trainers']

    def trainer(self, member_id=None):
        member_id = member_id or self.ctx.author.id
        trainer_data = self.trainers.get(member_id)
        if not trainer_data:
            return None
        return TrainerData(self.ctx.bot, trainer_data)
