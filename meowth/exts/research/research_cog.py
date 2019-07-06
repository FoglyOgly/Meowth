from meowth import Cog, command, bot, checks
from meowth.exts.map import ReportChannel, Pokestop, PartialPOI, POI
from meowth.exts.pkmn import Pokemon
from meowth.exts.want import Want, Item, PartialItem
from meowth.utils import formatters, snowflake
from meowth.utils.fuzzymatch import get_match, get_matches
from meowth.utils.converters import ChannelMessage

import time
import pytz
from pytz import timezone
from datetime import datetime, timedelta
from dateparser import parse
from math import ceil
from typing import Optional

from discord.ext import commands

import asyncio



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

    def __init__(self, research_id, bot, guild_id, reporter_id, task, location, reward, tz, reported_at):
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
    
    async def summary_str(self):
        task = self.task
        reward = self.reward
        location = self.location
        if '/' in reward:
            reward = ItemReward(self.bot, reward)
            desc = await reward.description()
        elif reward == 'unknown_encounter':
            desc = "Unknown Encounter"
        else:
            pkmn = Pokemon(self.bot, reward)
            desc = await pkmn.name()
            if await pkmn._shiny_available():
                desc += " :sparkles:"
            type_emoji = await pkmn.type_emoji()
            desc += f" {type_emoji}"
        
        if isinstance(task, Task):
            task = task.id
        else:
            task = task.id.split('/', 1)[1]
        
        if isinstance(location, POI):
            directions_url = await location.url()
            directions_text = await location._name()
        else:
            directions_url = location.url
            directions_text = location._name + " (Unknown Pokestop)"

        summary_str = f"• Reward: {desc} • Task: {task} • Location: [{directions_text}]({directions_url})"
        return summary_str

        
        
    
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
            try:
                await msg.edit(embed=expire_embed)
                await msg.clear_reactions()
            except:
                pass
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
    
    async def get_wants(self):
        wants = []
        reward = self.reward
        if reward.startswith('partial'):
            return wants
        elif '/' in reward:
            reward = ItemReward(self.bot, reward)
            item = reward.item
            wants.append(item.id)
        elif reward == 'unknown_encounter':
            return wants
        else:
            pkmn = Pokemon(self.bot, reward)
            family = await pkmn._familyId()
            wants.append(family)
        wants = [Want(self.bot, x, self.guild_id) for x in wants]
        want_dict = {x: await x.mention() for x in wants}
        return want_dict

    
    @classmethod
    async def from_data(cls, bot, data):
        d = dict(data)
        locid = d.pop('location')
        task_id = d.pop('task')
        if task_id.startswith('partial'):
            task_id = task_id.split('/',1)[1]
            task = PartialTask(bot, task_id)
        else:
            task = Task(bot, task_id)
        if locid.isdigit():
            location = Pokestop(bot, int(locid))
        else:
            city, arg = locid.split('/', 1)
            location = PartialPOI(bot, city, arg)
        research_id = d['id']
        guild_id = d['guild_id']
        reporter_id = d['reporter_id']
        reward = d['reward']
        tz = d['tz']
        reported_at = d['reported_at']
        message_ids = d['message_ids']
        completed_by = d['completed_by']
        res = cls(research_id, bot, guild_id, reporter_id, task, location, reward, tz, reported_at)
        res.completed_by = completed_by
        res.message_ids = message_ids
        for msgid in message_ids:
            cls.by_message[msgid] = res
        return res

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
        arg = arg.lower()
        argsplit = arg.split()
        table = ctx.bot.dbi.table('task_names')
        query = table.query('task_desc', 'category')
        data = await query.get()
        categories = [x.get('category') for x in data]
        if len(argsplit) == 1:
            if arg in categories:
                query = table.query('task_desc')
                query.where(category=arg)
                task_matches = await query.get_values()
            else:
                raise ValueError
        else:
            tasks = [x.get('task_desc') for x in data]
            matches = get_matches(tasks, arg)
            if matches:
                task_matches = [x[0] for x in matches]
            else:
                task_matches = []
        if len(task_matches) > 1:
            react_list = formatters.mc_emoji(len(task_matches))
            display_dict = dict(zip(react_list, task_matches))
            display_dict["\u2754"] = "Other"
            react_list.append("\u2754")
            embed = formatters.mc_embed(display_dict)
            multi = await ctx.send('Multiple possible Tasks found! Please select from the following list.',
                embed=embed)
            payload = await formatters.ask(ctx.bot, [multi], user_list=[ctx.author.id],
                react_list=react_list)
            task = display_dict[str(payload.emoji)]
            if task == 'Other':
                if arg in categories:
                    taskask = await ctx.send('What is the Task for this Research? Please type your answer below.')
                    def check(m):
                        return m.author == ctx.author and m.channel == ctx.channel
                    reply = await ctx.bot.wait_for('message', check=check)
                    arg = reply.content
                return PartialTask(ctx.bot, arg)
            try:
                await multi.delete()
            except:
                pass
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
    


class ResearchCog(Cog):

    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.pickup_researchdata())
    
    @Cog.listener()
    async def on_command_completion(self, ctx):
        if ctx.command.name == 'list':
            try:
                if await research_checks.is_research_enabled(ctx):
                    if len(ctx.args) == 2 or 'research' in ctx.args:
                        return await self.list_research(ctx.channel)
            except:
                pass
    
    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        idstring = f"{payload.channel_id}/{payload.message_id}"
        chn, msg = await ChannelMessage.from_id_string(self.bot, idstring)
        research = Research.by_message.get(idstring)
        if not research or payload.user_id == self.bot.user.id:
            return
        user = chn.guild.get_member(payload.user_id)
        if payload.emoji.is_custom_emoji():
            emoji = payload.emoji.id
        else:
            emoji = str(payload.emoji)
        if isinstance(emoji, int):
            emoji = self.bot.get_emoji(emoji)
        await msg.remove_reaction(emoji, user)
        if emoji.id == 583375171847585823:
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
                    try:
                        await multi.delete()
                    except:
                        pass
                    research.reward = reward
                    embed = await ResearchEmbed.from_research(research)
                    for msgid in research.message_ids:
                        chn, msg = await ChannelMessage.from_id_string(self.bot, msgid)
                        await msg.edit(embed=embed.embed)
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
    
    async def task_categories(self):
        table = self.bot.dbi.table('task_names')
        query = table.query('category')
        cats = await query.get_values()
        cats = list(set(cats))
        return cats
    
    @command()
    @checks.is_co_owner()
    async def cleartasks(self, ctx, *, cleartime=None):
        if cleartime:
            cleardt = parse(cleartime, settings={'TIMEZONE': 'America/Chicago', 'RETURN_AS_TIMEZONE_AWARE': True})
            cleardt = cleardt.astimezone(pytz.utc)
            stamp = cleardt.timestamp()
            if stamp > time.time():
                sleeptime = stamp - time.time()
                await asyncio.sleep(sleeptime)
        else:
            stamp = time.time()
        active_research = list(Research.instances.values())
        for research in active_research:
            if research.reported_at < stamp:
                await research.expire_research()

    @command(aliases=['res'])
    @research_checks.research_enabled()
    @checks.location_set()
    async def research(self, ctx, task: Optional[Task], *, location: Pokestop):
        """Report a Field Research task.
        
        **Arguments**
        *task (optional):* Either the text of the research task itself or
            the research category (e.g. `raid`). If a conversion to a Task cannot
            be made, Meowth asks you to select a category, then to select the
            specific task.
        *location:* Name of the Pokestop where the Field Research can be found.
        
        Meowth will automatically expire the research at midnight local time.
        The reporter will be awarded points for the number of users that obtain
        the task."""
        tz = await ctx.tz()
        if not task:
            cats = await self.task_categories()
            content = "What category of Research Task is this? Select from the options below."
            react_list = formatters.mc_emoji(len(cats))
            cat_dict = dict(zip(react_list, cats))
            embed = formatters.mc_embed(cat_dict)
            multi = await ctx.send(content, embed=embed)
            payload = await formatters.ask(ctx.bot, [multi], user_list=[ctx.author.id], react_list=react_list)
            if not payload:
                try:
                    return await multi.delete()
                except:
                    return
            cat = cat_dict[str(payload.emoji)]
            try:
                await multi.delete()
            except:
                pass
            task = await Task.convert(ctx, cat)
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
                    try:
                        return await multi.delete()
                    except:
                        return
                reward = choice_dict[str(payload.emoji)]
                try:
                    await multi.delete()
                except:
                    pass
        else:
            msg = await ctx.send('What is the reward for this Research? Please type your response below.')
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
            try:
                await reply.delete()
                await msg.delete()
            except:
                pass
        research_id = next(snowflake.create())
        research = Research(research_id, ctx.bot, ctx.guild.id, ctx.author.id, task, location, reward, tz, time.time())
        embed = await ResearchEmbed.from_research(research)
        embed = embed.embed
        wants = await research.get_wants()
        mentions = [wants.get(x) for x in wants if wants.get(x)]
        mention_str = "\u200b".join(mentions)
        if mention_str:
            reportcontent = mention_str + " - "
        else:
            reportcontent = ""
        stamp = ctx.bot.get_emoji(583375171847585823)
        reportcontent += f"Field Research reported! Use {str(stamp)} to indicate that you picked up this task!"
        report_channels = []
        report_channel = ReportChannel(ctx.bot, ctx.channel)
        msgs = []
        if isinstance(location, Pokestop):
            channel_list = await location.get_all_channels('research')
            report_channels.extend(channel_list)
        if report_channel not in report_channels:
            report_channels.append(report_channel)
        stamp = ctx.bot.get_emoji(583375171847585823)
        for channel in report_channels:
            try:
                msg = await channel.channel.send(reportcontent, embed=embed)
                await msg.add_reaction(stamp)
            except:
                continue
            idstring = f'{msg.channel.id}/{msg.id}'
            msgs.append(idstring)
            Research.by_message[idstring] = research
        research.message_ids = msgs
        await research.upsert()
        ctx.bot.loop.create_task(research.monitor_status())
    
    async def list_research(self, channel):
        color = channel.guild.me.color
        report_channel = ReportChannel(self.bot, channel)
        data = await report_channel.get_all_research()
        research_list = []
        if not data:
            return await channel.send('No research reported!')
        for research_id in data:
            research = Research.instances.get(research_id)
            if not research:
                continue
            research_list.append(await research.summary_str())
        number = len(research_list)
        pages = ceil(number/8)
        for i in range(pages):
            if pages == 1:
                title = "Current Research"
            else:
                title = f'Current Research (Page {i+1} of {pages})'
            if len(research_list) > 8:
                content = "\n\n".join(research_list[:8])
                research_list = research_list[8:]
            else:
                content = "\n\n".join(research_list)
            embed = formatters.make_embed(title=title, content=content, msg_colour=color)
            await channel.send(embed=embed)




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
        reporter = research.guild.get_member(research.reporter_id)
        color = research.guild.me.color
        reporter_name = reporter.display_name
        reporter_avy = reporter.avatar_url
        footer = f"Reported by {reporter_name} • Expires"
        icon_url = ("https://raw.githubusercontent.com/"
                "FoglyOgly/Meowth/new-core/meowth/images/misc/field-research.png")
        embed = formatters.make_embed(title=title, thumbnail=thumbnail,
            fields=fields, footer=footer, footer_icon=reporter_avy, icon=icon_url, msg_colour=color)
        embed.timestamp = datetime.utcfromtimestamp(research.expires_at)
        return cls(embed)