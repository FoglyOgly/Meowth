from meowth import Cog, command, bot, checks
from meowth.exts.map import ReportChannel, Pokestop, PartialPOI, POI
from meowth.exts.pkmn import Pokemon
from meowth.utils import formatters, snowflake


from . import research_checks

class Research:

    instances = dict()
    by_message = dict()

    def __new__(cls, research_id, *args, **kwargs):
        if research_id in cls.instances:
            return cls.instances[research_id]
        instance = super().__new__(cls)
        cls.instances[research_id] = instance
        return instance

    def __init__(self, bot, research_id, task, location, reward, tz):
        self.bot = bot
        self.id = research_id
        self.task = task
        self.reward = reward
        self.location = location
        self.tz = tz
        self.message_ids = []
    
    def to_dict(self):
        if isinstance(self.location, POI):
            locid = str(self.location.id)
        else:
            locid = f'{self.location.city}/{self.location.arg}'
        d = {
            'id': self.id,
            'task': self.task.id,
            'reward': self.reward.id,
            'location': locid,
            'tz': self.tz,
            'message_ids': self.message_ids
        }

        return d
    
    @property
    def _data(self):
        table = self.bot.dbi.table('research')
        query = table.query
        query.where(id=self.id)
        return query
    
    @property
    def _insert(self):
        table = self.bot.dbi.table('research')
        insert = table.insert
        d = self.to_dict()
        insert.row(**d)
        return insert
    
    async def upsert(self):
        insert = self._insert
        await insert.commit(do_update=True)
    
    async def expire_research(self):
        data = self._data
        await data.delete()

class Task:

    def __init__(self, bot, task_id):
        self.bot = bot
        self.id = task_id
    
    # async def description(self):

    # async def possible_rewards(self):

class Item:

    def __init__(self, bot, item_id):
        self.bot = bot
        self.id = item_id
    
    # async def name(self):


class ResearchCog(Cog):

    def __init__(self, bot):
        self.bot = bot

    @command(aliases=['res'])
    @research_checks.research_enabled()
    async def research(self, ctx, task, *, location: Pokestop):
        tz = await ctx.tz()
        research_id = next(snowflake.create())
        research = Research(ctx.bot, research_id, task, location, reward, tz)



class ResearchEmbed:

    def __init__(self, embed):
        self.embed = embed
        
    
    loc_index = 0
    task_index = 1
    reward_index = 2

    @classmethod
    async def from_research(cls, research):
        task = research.task
        location = research.location
        reward = research.reward

        task_desc = await task.description()
        if isinstance(location, POI):
            

    