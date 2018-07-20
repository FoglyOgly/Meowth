from .guild import GuildDM

class DataManager:
    """Query and data handling"""

    def __init__(self, db):
        self._db = db

    def guild(self, guild_id):
        """Guild Data Manager"""
        return GuildDM(self._db, guild_id)
