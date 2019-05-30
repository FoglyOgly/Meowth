from meowth import Cog, command, bot, checks
from meowth.exts.map import ReportChannel, Pokestop, PartialPOI, POI
from meowth.exts.pkmn import Pokemon
from meowth.utils import formatters, snowflake
from meowth.utils.fuzzymatch import get_match, get_matches
from meowth.utils.converters import ChannelMessage

import time
import pytz
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

    def __init__(self, bot, research_id, guild_id, reporter_id, task, location, reward, tz, reported_at):
        self.bot = bot
        self.id = research_id
        self.guild_id = guild_id
        self.reporter_id = reporter_id
        self.task = task
        self.reward = reward
        self.location = location
        self.tz = tz
        self.reported_at = reported_at
        self.completed_by = []
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
            'reward': self.reward,
            'location': locid,
            'tz': self.tz,
            'reported_at': self.reported_at,
            'message_ids': self.message_ids,
            'completed_by': self.completed_by
        }

        return d
    
    @property
    def expires_at(self):
        tz = timezone(self.tz)
        created_dt = datetime.fromtimestamp(self.reported_at, tz=tz)
        expire_dt = created_dt + timedelta(days=1)
        expire_dt = expire_dt.replace(hour=0,minute=0,second=0)
        expire_dt = expire_dt.astimezone(pytz.utc)
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
    
    async def monitor_status(self):
        expires_at = self.expires_at
        sleeptime = expires_at - time.time()
        await asyncio.sleep(sleeptime)
        await self.expire_research()
    
    async def expire_research(self):
        if self.completed_by:
            research_score = 1 + len(self.completed_by)
        else:
            research_score = 1
        score_table = self.bot.dbi.table('scoreboard')
        query = score_table.query
        query.where(guild_id=self.guild_id)
        query.where(user_id=self.reporter_id)
        old_data = await query.get()
        if not old_data:
            d = {
                'guild_id': self.guild_id,
                'user_id': self.reporter_id,
                'raid': 0,
                'wild': 0,
                'trade': 0,
                'research': 0,
                'service': 0
            }
        else:
            d = dict(old_data[0])
        d['research'] += research_score
        insert = score_table.insert
        insert.row(**d)
        await insert.commit(do_update=True)
        expire_embed = formatters.make_embed(title='This Research Task has expired!')
        for msgid in self.message_ids:
            chn, msg = await ChannelMessage.from_id_string(self.bot, msgid)
            await msg.edit(embed=expire_embed)
            try:
                del Research.by_message[msgid]
            except:
                pass
        data = self._data
        await data.delete()
        try:
            del Research.instances[self.id]
        except:
            pass
    
    @classmethod
    async def from_data(cls, bot, data):
        d = {
            'id': self.id,
            'guild_id': self.guild_id,
            'reporter_id': self.reporter_id,
            'task': self.task.id,
            'reward': self.reward.id,
            'location': locid,
            'tz': self.tz,
            'reported_at': self.reported_at,
            'message_ids': self.message_ids,
            'completed_by': self.completed_by
        }
        d = dict(data)
        locid = d.pop('location')
        if locid.isdigit():
            location = Pokestop(bot, int(locid))
        else:
            city, arg = locid.split('/', 1)
            location = PartialPOI(bot, city, arg)
        
        return cls(bot, location=location, **d)

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
    
    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        idstring = f"{payload.channel_id}/{payload.message_id}"
        chn, msg = await ChannelMessage.from_id_string(self.bot, idstring)
        research = Research.by_message.get(idstring)
        if not research:
            return
        user = chn.guild.get_member(payload.user_id)
        if payload.emoji.is_custom_emoji():
            emoji = payload.emoji.id
        else:
            emoji = str(payload.emoji)
        await msg.remove_reaction(emoji, user)
        if emoji == 583375171847585823:
            if payload.user_id not in research.completed_by:
                research.completed_by.append(payload.user_id)
            if research.reward == 'unknown_encounter':
                if isinstance(research.task, Task):
                    possible_rewards = await research.task.possible_rewards()
                    pkmn_rewards = [x for x in possible_rewards if '/' not in x]
                    pkmn = [Pokemon(self.bot, x) for x in pkmn_rewards]
                    pkmn_dict = {await x.name(): x.id for x in pkmn}
                    react_list = formatters.mc_emoji(len(pkmn))
                    choice_dict = dict(zip(react_list, pkmn_dict.values()))
                    display_dict = dict(zip(react_list, pkmn_dict.keys()))
                    embed = formatters.mc_embed(display_dict)
                    embed.fields[0].value = embed.fields[0].value + "\n<:silph:548259248442703895>Research tasks and rewards provided by [The Silph Road](https://thesilphroad.com/research-tasks)"
                    multi = await chn.send(f"{user.mention}: What is the reward for this task? Please select from the options below. If you don't know, just ignore this!",
                        embed=embed)
                    payload = await formatters.ask(self.bot, [multi], user_list=[user.id],
                        react_list=react_list)
                    if not payload:
                        return await multi.delete()
                    reward = choice_dict[str(payload.emoji)]
                    await multi.delete()
                    research.reward = reward
            return await research.upsert()
    
    async def pickup_researchdata(self):
        research_table = self.bot.dbi.table('research')
        query = research_table.query()
        data = await query.get()
        for rcrd in data:
            self.bot.loop.create_task(self.pickup_research(rcrd))
    
    async def pickup_research(self, rcrd):
        research = await Research.from_data(self.bot, rcrd)
        self.bot.loop.create_task(research.monitor_status())

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
                if len(pkmn_dict) > 1:
                    react_list = formatters.mc_emoji(len(possible_rewards)+1)
                    reward_dict['Unknown Encounter'] = 'unknown_encounter'
                choice_dict = dict(zip(react_list, reward_dict.values()))
                display_dict = dict(zip(react_list, reward_dict.keys()))
                embed = formatters.mc_embed(display_dict)
                embed.fields[0].value = embed.fields[0].value + "\n<:silph:548259248442703895>Research tasks and rewards provided by [The Silph Road](https://thesilphroad.com/research-tasks)"
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
        research = Research(ctx.bot, research_id, ctx.guild.id, ctx.author.id, task, location, reward, tz, time.time())
        embed = await ResearchEmbed.from_research(research)
        embed = embed.embed
        report_channels = []
        report_channel = ReportChannel(ctx.bot, ctx.channel)
        if isinstance(location, Pokestop):
            channel_list = await location.get_all_channels('research')
            report_channels.extend(channel_list)
        if report_channel not in report_channels:
            report_channels.append(report_channel)
        msgs = []
        for channel in report_channels:
            msg = await channel.channel.send(embed=embed)
            idstring = f'{msg.channel.id}/{msg.id}'
            msgs.append(idstring)
            Research.by_message[idstring] = research
        research.message_ids = msgs
        await research.upsert()




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
        elif reward == 'unknown_encounter':
            desc = "Unknown Encounter"
            thumbnail = ("https://raw.githubusercontent.com/"
                "FoglyOgly/Meowth/new-core/meowth/images/misc/unknown_encounter.png")
        else:
            pkmn = Pokemon(bot, reward)
            desc = await pkmn.name()
            if await pkmn._shiny_available():
                desc += " :sparkles:"
            type_emoji = await pkmn.type_emoji()
            desc += f" {type_emoji}"
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
            'Reward': desc + "\n<:silph:548259248442703895>Research tasks and rewards provided by [The Silph Road](https://thesilphroad.com/research-tasks)"
        }
        reporter = research.guild.get_member(research.reporter_id).display_name
        footer = f"Reported by {reporter} • Expires"
        embed = formatters.make_embed(title=title, thumbnail=thumbnail,
            fields=fields, footer=footer)
        embed.timestamp = datetime.utcfromtimestamp(research.expires_at)
        return cls(embed)