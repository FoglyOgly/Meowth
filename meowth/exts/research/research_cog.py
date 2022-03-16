from meowth import Cog, command, bot, checks
from meowth.core.context import Context
from meowth.exts.map import ReportChannel, Pokestop, PartialPOI, POI
from meowth.exts.pkmn import Pokemon
from meowth.exts.want import Want, Item, PartialItem
from meowth.utils import formatters, snowflake
from meowth.utils.fuzzymatch import get_match, get_matches
from meowth.utils.converters import ChannelMessage

import discord
import time
import pytz
from pytz import timezone
from datetime import datetime, timedelta
from dateparser import parse
from math import ceil
from typing import Optional, Union
import re

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
            if len(directions_text) > 25:
                directions_text = directions_text[:25] + "..."
        else:
            directions_url = location.url
            name = location._name
            if len(name) > 25:
                name = name[:25] + "..."
            directions_text = name + " (Unknown Pokestop)"

        summary_str = f"• Reward: {desc} • Task: {task} • Location: [{directions_text}]({directions_url})"
        return summary_str

    async def update_url(self, url):
        location = self.location
        if isinstance(location, POI):
            directions_text = await location._name()
        else:
            directions_text = location._name + " (Unknown Pokestop)"
        dir_str = f"[{directions_text}]({url})"
        embed = await ResearchEmbed.from_research(self)
        embed = embed.embed.set_field_at(0, name="Pokestop", value=dir_str)
        for msgid in self.message_ids:
            chn, msg = await ChannelMessage.from_id_string(self.bot, msgid)
            try:
                await msg.edit(embed=embed)
            except:
                pass

    
    async def monitor_status(self):
        expires_at = self.expires_at
        sleeptime = expires_at - time.time()
        await asyncio.sleep(sleeptime)
        await self.expire_research()
    
    async def delete(self):
        for msgid in self.message_ids:
            chn, msg = await ChannelMessage.from_id_string(self.bot, msgid)
            try:
                await msg.delete()
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
    async def convert(cls, ctx, arg, require_task=False):
        arg = arg.lower()
        table = ctx.bot.dbi.table('research_tasks')
        query = table.query('task')
        tasks = await query.get_values()
        tasks = list(set(tasks))
        matches = get_matches(tasks, arg, limit=19)
        if matches:
            task_matches = [x[0] for x in matches]
        else:
            task_matches = []

        async def ask_partial_task():
            other_ask = await ctx.send('What is the Task for this Research? Please type your answer below.')

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                other_reply = await ctx.bot.wait_for('message', check=check, timeout=300)
            except asyncio.TimeoutError:
                return PartialTask(ctx.bot, arg)
            else:
                try:
                    await other_reply.delete()
                except (discord.Forbidden, discord.NotFound):
                    pass
                return PartialTask(ctx.bot, other_reply.content)
            finally:
                try:
                    await other_ask.delete()
                except discord.NotFound:
                    pass

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
            try:
                await multi.delete()
            except discord.NotFound:
                pass
            if task == 'Other':
                return await ask_partial_task()
        elif len(task_matches) == 1:
            task = task_matches[0]
        elif require_task:
            return await ask_partial_task()
        else:
            raise ValueError
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
        if not item:
            raise ValueError
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
    async def on_raw_message_delete(self, payload):
        idstring = f"{payload.channel_id}/{payload.message_id}"
        chn, msg = await ChannelMessage.from_id_string(self.bot, idstring)
        research = Research.by_message.get(idstring)
        if not research:
            return
        return await research.delete()
        
    
    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        idstring = f"{payload.channel_id}/{payload.message_id}"
        chn, msg = await ChannelMessage.from_id_string(self.bot, idstring)
        research = Research.by_message.get(idstring)
        if not research or payload.user_id == self.bot.user.id:
            return
        user = payload.member
        if payload.emoji.is_custom_emoji():
            emoji = payload.emoji.id
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
            elif emoji.id == 597185467217346602:
                askmsg = await chn.send(f"{user.mention}: Where is this Research located? Please type your response below. If you send a plain text response, I will check it against the Pokestops I know about. You can also send a Google Maps link!")

                def check(m):
                    return m.author == user and m.channel == chn
                reply = await self.bot.wait_for('message', check=check)
                try:
                    await askmsg.delete()
                    await reply.delete()
                except discord.HTTPException:
                    pass
                url_re = '(http(s?)://)?((maps\.google\./)|((www\.)?google\.com/maps/)|(goo.gl/maps/))\S*'
                match = re.search(url_re, reply.content)
                if match:
                    url = match.group()
                    return await research.update_url(url)
                else:
                    ctx = await self.bot.get_context(reply, cls=Context)
                    stop = await Pokestop.convert(ctx, reply.content)
                    research.location = stop
        else:
            emoji = str(payload.emoji)
            await msg.remove_reaction(emoji, user)
            if emoji == '\U0001F4DD':
                askmsg = await chn.send(f"{user.mention}: What Research task is located here? Please type your response below.")

                def check(m):
                    return m.author == user and m.channel == chn
                try:
                    reply = await self.bot.wait_for('message', check=check, timeout=300)
                except asyncio.TimeoutError:
                    return
                try:
                    await askmsg.delete()
                    await reply.delete()
                except discord.HTTPException:
                    pass
                ctx = await self.bot.get_context(reply, cls=Context)
                task = await Task.convert(ctx, reply.content, require_task=True)
                research.task = task

        embed = await ResearchEmbed.from_research(research)
        for msgid in research.message_ids:
            try:
                chn, msg = await ChannelMessage.from_id_string(self.bot, msgid)
                await msg.edit(embed=embed.embed)
            except discord.HTTPException:
                pass
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

    async def possible_tasks(self, reward):
        if reward.startswith('partial'):
            return []
        table = self.bot.dbi.table('research_tasks')
        query = table.query('task')
        try:
            query.where(reward=reward)
        except:
            return []
        return await query.get_values()
    
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
    async def research(self, ctx, reward: Optional[Union[Pokemon, ItemReward]], task: Optional[Task], *, location: Pokestop):
        """Report a Field Research task.
        
        **Arguments**
        *reward (optional):* Description of the reward for the research. Either
            a Pokemon or an item.
        *task (optional):* Either the text of the research task itself or
            the research category (e.g. `raid`). If a conversion to a Task cannot
            be made, Meowth asks you to select a category, then to select the
            specific task.
        *location:* Name of the Pokestop where the Field Research can be found.
        
        Meowth will automatically expire the research at midnight local time.
        The reporter will be awarded points for the number of users that obtain
        the task."""
        tz = await ctx.tz()
        if reward and not task:
            task_matches = await self.possible_tasks(reward.id)
            if len(task_matches) == 1:
                task = Task(ctx.bot, task_matches[0])
            elif len(task_matches) > 1:
                react_list = formatters.mc_emoji(len(task_matches))
                display_dict = dict(zip(react_list, task_matches))
                display_dict["\u2754"] = "Other"
                react_list.append("\u2754")
                embed = formatters.mc_embed(display_dict)
                multi = await ctx.send('Multiple possible Tasks found! Please select from the following list.',
                    embed=embed)
                payload = await formatters.ask(ctx.bot, [multi], user_list=[ctx.author.id],
                    react_list=react_list)
                if not payload:
                    try:
                        return await multi.delete()
                    except:
                        return
                task = display_dict[str(payload.emoji)]
                if task == 'Other':
                    otherask = await ctx.send('What is the Task for this Research? Please type your answer below.')
                    def check(m):
                        return m.author == ctx.author and m.channel == ctx.channel
                    reply = await ctx.bot.wait_for('message', check=check)
                    arg = reply.content
                    try:
                        await reply.delete()
                        await otherask.delete()
                    except:
                        pass
                    task = PartialTask(ctx.bot, arg)
                else:
                    task = Task(ctx.bot, task)
                try:
                    await multi.delete()
                except:
                    pass
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
            task = await Task.convert(ctx, cat, require_task=True)
        if isinstance(task, Task) and not reward:
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
        elif not reward:
            msg = await ctx.send('What is the reward for this Research? Please type your response below.')
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            reply = await ctx.bot.wait_for('message', check=check)
            try:
                reward = await Pokemon.convert(ctx, reply.content)
            except:
                reward = None
            if not reward:
                try:
                    reward = await ItemReward.convert(ctx, reply.content)
                except:
                    reward = ItemReward(ctx.bot, f'partial/{reply.content}/1')
            try:
                await reply.delete()
                await msg.delete()
            except:
                pass
        if not isinstance(reward, str):
            reward = reward.id
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
        map_icon = ctx.bot.get_emoji(597185467217346602)
        reportcontent += f"Field Research reported! Use {str(stamp)} to indicate that you picked up this task!"
        report_channels = []
        report_channel = ReportChannel(ctx.bot, ctx.channel)
        msgs = []
        if isinstance(location, Pokestop):
            research_table = ctx.bot.dbi.table('research')
            query = research_table.query()
            query.where(location=str(location.id), guild_id=ctx.guild.id)
            old_research = await query.get()
            if old_research:
                return await ctx.send("There is already a research task reported at this pokéstop!", delete_after=20)
            channel_list = await location.get_all_channels('research')
            report_channels.extend(channel_list)
        if report_channel not in report_channels:
            report_channels.append(report_channel)
        stamp = ctx.bot.get_emoji(583375171847585823)
        for channel in report_channels:
            try:
                msg = await channel.channel.send(reportcontent, embed=embed)
                await msg.add_reaction("\U0001F4DD")  # Task emoji
                await msg.add_reaction(map_icon)
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
        research_list_embeds = make_research_list_embeds(research_list, color)
        for embed in research_list_embeds:
            await channel.send(embed=embed)
            await asyncio.sleep(0.25)


def make_research_list_embeds(research_list, color, page_size=8):
    number = len(research_list)
    pages = ceil(number/page_size)
    embeds = []
    for i in range(pages):
        if pages == 1:
            title = "Current Research"
        else:
            title = f'Current Research (Page {i+1} of {pages})'
        if len(research_list) > page_size:
            content = "\n\n".join(research_list[:page_size])
            research_list = research_list[page_size:]
        else:
            content = "\n\n".join(research_list)
        embed = formatters.make_embed(title=title, content=content, msg_colour=color)
        embeds.append(embed)
    if len(max(embeds, key=len)) > 2048 and page_size > 2:
        embeds = make_research_list_embeds(research_list, color, page_size=page_size-2)
    return embeds


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
        if not reporter:
            reporter = await research.guild.fetch_member(research.reporter_id)
        color = research.guild.me.color
        reporter_name = reporter.display_name
        reporter_avy = reporter.avatar.url
        footer = f"Reported by {reporter_name} • Expires"
        icon_url = ("https://raw.githubusercontent.com/"
                "FoglyOgly/Meowth/new-core/meowth/images/misc/field-research.png")
        embed = formatters.make_embed(title=title, thumbnail=thumbnail,
            fields=fields, footer=footer, footer_icon=reporter_avy, icon=icon_url, msg_colour=color)
        embed.timestamp = datetime.utcfromtimestamp(research.expires_at)
        return cls(embed)