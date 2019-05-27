from meowth import Cog, command, bot, checks
from meowth.exts.map import ReportChannel, Pokestop, PartialPOI, POI
from meowth.exts.pkmn import Pokemon
from meowth.utils import formatters, snowflake
from meowth.utils.fuzzymatch import get_match, get_matches

import time
from pytz import timezone
from datetime import datetime, timedelta



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

    def __init__(self, bot, research_id, guild_id, reporter_id, task, location, reward, tz):
        self.bot = bot
        self.id = research_id
        self.guild_id = guild_id
        self.reporter_id = reporter_id
        self.task = task
        self.reward = reward
        self.location = location
        self.tz = tz
        self.reported_at = time.time()
        self.message_ids = []
    
    def to_dict(self):
        if isinstance(self.location, POI):
            locid = str(self.location.id)
        else:
            locid = f'{self.location.city}/{self.location.arg}'
        d = {
            'id': self.id,
            'guild_id': self.guild_id,
            'reporter_id': self.reporter_id,
            'task': self.task.id,
            'reward': self.reward.id,
            'location': locid,
            'tz': self.tz,
            'reported_at': self.reported_at,
            'message_ids': self.message_ids
        }

        return d
    
    @property
    def expires_at(self):
        tz = timezone(self.tz)
        created_dt = datetime.fromtimestamp(self.reported_at, tz=tz)
        expire_dt = created_dt + timedelta(days=1)
        expire_dt = expire_dt.replace(hour=0,minute=0,second=0)
        return expire_dt.timestamp()
    
    @property
    def guild(self):
        return self.bot.get_guild(self.guild_id)
    
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

    async def possible_rewards(self):
        table = self.bot.dbi.table('research_tasks')
        query = table.query('reward')
        query.where(task=self.id)
        return await query.get_values()

    @classmethod
    async def convert(cls, ctx, arg):
        table = ctx.bot.dbi.table('research_tasks')
        query = table.query('task')
        tasks = await query.get_values()
        tasks = list(set(tasks))
        matches = get_matches(tasks, arg)
        if matches:
            task_matches = [x[0] for x in matches]
        else:
            task_matches = []
        if len(task_matches) > 1:
            react_list = formatters.mc_emoji(len(task_matches))
            display_dict = dict(zip(react_list, task_matches))
            embed = formatters.mc_embed(display_dict)
            multi = await ctx.send('Multiple possible Tasks found! Please select from the following list.',
                embed=embed)
            payload = await formatters.ask(ctx.bot, [multi], user_list=[ctx.author.id],
                react_list=react_list)
            task = display_dict[str(payload.emoji)]
            await multi.delete()
        elif len(task_matches) == 1:
            task = task_matches[0]
        else:
            return PartialTask(ctx.bot, arg)
        return cls(ctx.bot, task)

class PartialTask:

    def __init__(self, bot, arg):
        self.bot = bot
        self.id = f"partial/{arg}"



        

class ItemReward:

    def __init__(self, bot, reward_id):
        self.bot = bot
        self.id = reward_id
    
    @property
    def item(self):
        if self.id.startswith('partial'):
            item_id = self.id.split('/',2)[1]
            return PartialItem(self.bot, item_id)
        item_id = self.id.split('/')[0]
        return Item(self.bot, item_id)
    
    @property
    def amount(self):
        if self.id.startswith('partial'):
            return self.id.split('/', 2)[-1]
        return self.id.split('/', 1)[-1]
    
    async def description(self):
        item = self.item
        if isinstance(item, PartialItem):
            item_name = item.name
        elif isinstance(item, Item):
            item_name = await item.name()
        amount = self.amount
        return f"{amount} {item_name}"
    
    @property
    def img_url(self):
        return self.item.img_url


    @classmethod
    async def convert(cls, ctx, arg):
        args = arg.split()
        item_args = [x for x in args if not x.isdigit()]
        amount = 1
        for arg in args:
            if arg.isdigit():
                amount = arg
        item_name_arg = " ".join(item_args)
        item = await Item.convert(ctx, item_name_arg)
        return cls(ctx.bot, f'{item.id}/{amount}')
        

        

class Item:

    def __init__(self, bot, item_id):
        self.bot = bot
        self.id = item_id
    
    async def name(self):
        table = self.bot.dbi.table('item_names')
        query = table.query('name')
        query.where(language_id=9)
        query.where(item_id=self.id)
        return await query.get_value()
    
    @property
    def img_url(self):
        url = ("https://raw.githubusercontent.com/"
            "FoglyOgly/Meowth/new-core/meowth/images/misc/")
        url += self.id
        url += '.png'
        return url
    
    @classmethod
    async def convert(cls, ctx, arg):
        table = ctx.bot.dbi.table('item_names')
        query = table.query
        data = await query.get()
        name_dict = {x['name']: x['item_id'] for x in data}
        matches = get_matches(name_dict.keys(), arg)
        if matches:
            item_matches = [name_dict[x[0]] for x in matches]
            name_matches = [x[0] for x in matches]
        else:
            item_matches = []
            name_matches = []
        if len(item_matches) > 1:
            react_list = formatters.mc_emoji(len(item_matches))
            choice_dict = dict(zip(react_list, item_matches))
            display_dict = dict(zip(react_list, name_matches))
            embed = formatters.mc_embed(display_dict)
            multi = await ctx.send('Multiple possible Items found! Please select from the following list.',
                embed=embed)
            payload = await formatters.ask(ctx.bot, [multi], user_list=[ctx.author.id],
                react_list=react_list)
            item = choice_dict[str(payload.emoji)]
            await multi.delete()
        elif len(item_matches) == 1:
            item = item_matches[0]
        else:
            return PartialItem(ctx.bot, arg)
        return cls(ctx.bot, item)

class PartialItem:

    def __init__(self, bot, arg):
        self.bot = bot
        self.id = f"partial/{arg}"
    
    @property
    def item(self):
        return self.id.split('/', 1)[1]
    
    @property
    def name(self):
        return self.item.title()
    
    @property
    def img_url(self):
        return ""


class ResearchCog(Cog):

    def __init__(self, bot):
        self.bot = bot

    @command(aliases=['res'])
    @research_checks.research_enabled()
    async def research(self, ctx, task: Task, *, location: Pokestop):
        tz = await ctx.tz()
        if isinstance(task, Task):
            possible_rewards = await task.possible_rewards()
            if len(possible_rewards) == 1:
                reward = possible_rewards[0]
            else:
                react_list = formatters.mc_emoji(len(possible_rewards))
                item_dict = {}
                pkmn_dict = {}
                for reward in possible_rewards:
                    if '/' in reward:
                        obj = ItemReward(ctx.bot, reward)
                        desc = await obj.description()
                        item_dict[desc] = reward
                    else:
                        pkmn = Pokemon(ctx.bot, reward)
                        name = await pkmn.name()
                        pkmn_dict[name] = reward
                reward_dict = dict(pkmn_dict, **item_dict)
                choice_dict = dict(zip(react_list, reward_dict.values()))
                display_dict = dict(zip(react_list, reward_dict.keys()))
                embed = formatters.mc_embed(display_dict)
                multi = await ctx.send('What is the reward for this task? Please select from the options below.',
                    embed=embed)
                payload = await formatters.ask(ctx.bot, [multi], user_list=[ctx.author.id],
                    react_list=react_list)
                if not payload:
                    return await multi.delete()
                reward = choice_dict[str(payload.emoji)]
                await multi.delete()
        else:
            msg = await ctx.send('What is the reward for this task? Please type your response below.')
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            reply = await ctx.bot.wait_for('message', check=check)
            try:
                reward = await Pokemon.convert(ctx, reply.content)
            except:
                reward = None
            if not reward:
                reward = await ItemReward.convert(ctx, reply.content)
            reward = reward.id
            await reply.delete()
            await msg.delete()
        research_id = next(snowflake.create())
        research = Research(ctx.bot, research_id, ctx.guild.id, ctx.author.id, task, location, reward, tz)
        embed = await ResearchEmbed.from_research(research)
        embed = embed.embed
        await ctx.send(embed=embed)



class ResearchEmbed:

    def __init__(self, embed):
        self.embed = embed
        
    
    loc_index = 0
    task_index = 1
    reward_index = 2

    @classmethod
    async def from_research(cls, research):
        bot = research.bot
        task = research.task
        location = research.location
        reward = research.reward

        if isinstance(task, Task):
            task = task.id
        else:
            task = task.id.split('/', 1)[1]

        if '/' in reward:
            reward = ItemReward(research.bot, reward)
            desc = await reward.description()
            thumbnail = reward.img_url
        else:
            pkmn = Pokemon(bot, reward)
            desc = await pkmn.name()
            thumbnail = await pkmn.sprite_url()

        if isinstance(location, POI):
            directions_url = await location.url()
            directions_text = await location._name()
        else:
            directions_url = location.url
            directions_text = location._name + " (Unknown Pokestop)"
        
        title = "Field Research Report"
        fields = {
            'Pokestop': f"[{directions_text}]({directions_url})",
            'Task': task,
            'Reward': desc
        }
        reporter = research.guild.get_member(research.reporter_id).display_name
        footer = f"Reported by {reporter} • Expires"
        embed = formatters.make_embed(title=title, thumbnail=thumbnail,
            fields=fields, footer=footer)
        embed.timestamp = datetime.utcfromtimestamp(research.expires_at)
        return cls(embed)