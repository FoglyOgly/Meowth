from meowth import Cog, command, bot, checks
from meowth.exts.raid import Raid

import asyncio
import time

import discord
from discord.ext import commands


from meowth.utils import formatters

class Tutorial(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.add_listeners())

    async def add_listeners(self):
        if self.bot.dbi.tutorial_listener:
            await self.bot.dbi.pool.release(self.bot.dbi.tutorial_listener)
        self.bot.dbi.tutorial_listener = await self.bot.dbi.pool.acquire()
        rsvp_listener = ('rsvp', self._rsvp)
        await self.bot.dbi.tutorial_listener.add_listener(*rsvp_listener)

    
    def _rsvp(self, connection, pid, channel, payload):
        if channel != 'rsvp':
            return
        payload_args = payload.split('/')
        if len(payload_args) != 3:
            return
        raid_id = int(payload_args[0])
        if not payload_args[1].isdigit():
            return
        user_id = int(payload_args[1])
        status = payload_args[2]
        self.bot.dispatch('tutorial_rsvp', raid_id, user_id, status)
    
    async def wait_for_rsvp(self, raid, newbie, status):

        def check(raid_id, user_id, status_str):
            if not raid_id == raid.id:
                return False
            if not user_id == newbie.id:
                return False
            if not status_str == status:
                return False
            return True
        
        rsvp_args = await self.bot.wait_for('tutorial_rsvp', check=check, timeout=300)

        return rsvp_args

    async def wait_for_cmd(self, tutorial_channel, newbie, command_name):

        # build check relevant to command
        def check(c):
            if not c.channel == tutorial_channel:
                return False
            if not c.author == newbie:
                return False
            if c.command.name == command_name:
                return True
            return False

        # wait for the command to complete
        cmd_ctx = await self.bot.wait_for(
            'command_completion', check=check, timeout=300)

        return cmd_ctx

    def get_overwrites(self, guild, member):
        return {
            guild.default_role: discord.PermissionOverwrite(
                read_messages=False),
            member: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                manage_channels=True),
            guild.me: discord.PermissionOverwrite(
                read_messages=True)
            }

    async def guild_tutorial_settings(self, guild):
        guild_id = guild.id
        report_channel_table = self.bot.dbi.table('report_channels')
        query = report_channel_table.query
        query.where(guild_id=guild_id)
        data = await query.get()
        d = {}
        for row in data:
            for key in row.keys():
                if row[key]:
                    d[key] = row[key]
        return d

    async def want_tutorial(self, ctx):

        await ctx.tutorial_channel.send(
            f"This server utilizes the **{ctx.prefix}want** command to help "
            "members receive push notifications about Pokemon they want! "
            "I create Discord roles for each Pokemon that people want, "
            "and @mentioning these roles will send a notification to "
            f"anyone who **{ctx.prefix}want**-ed that Pokemon!\n"
            f"Try the {ctx.prefix}want command!\n"
            f"Ex: `{ctx.prefix}want unown`")

        try:
            await self.wait_for_cmd(ctx.tutorial_channel, ctx.author, 'want')

            # acknowledge and wait a second before continuing
            await ctx.tutorial_channel.send("Great job!")
            await asyncio.sleep(1)

        # if no response for 5 minutes, close tutorial
        except asyncio.TimeoutError:
            await ctx.tutorial_channel.send(
                f"You took too long to complete the **{ctx.prefix}want** "
                "command! This channel will be deleted in ten seconds.")
            await asyncio.sleep(10)
            await ctx.tutorial_channel.delete()

            return False


        return True

    async def wild_tutorial(self, ctx):

        await ctx.tutorial_channel.send(
            f"This server utilizes the **{ctx.prefix}wild** command to "
            "report wild spawns! When you use it, I will send a message "
            "summarizing the report and containing a link to my best "
            "guess of the spawn location. If the reported Pokemon has "
            "an associated role on the server, I will @mention the role "
            "in my message! Your report must contain the name of the "
            "Pokemon followed by its location. "
            "Try reporting a wild spawn!\n"
            f"Ex: `{ctx.prefix}wild magikarp some park`")

        try:
            await self.wait_for_cmd(ctx.tutorial_channel, ctx.author, 'wild')

            # acknowledge and wait a second before continuing
            await ctx.tutorial_channel.send("Great job!")
            await asyncio.sleep(1)

        # if no response for 5 minutes, close tutorial
        except asyncio.TimeoutError:
            await ctx.tutorial_channel.send(
                f"You took too long to complete the **{ctx.prefix}wild** "
                "command! This channel will be deleted in ten seconds.")
            await asyncio.sleep(10)
            await ctx.tutorial_channel.delete()
            return False


        return True

    async def raid_tutorial(self, ctx):
        tutorial_channel = ctx.tutorial_channel
        prefix = ctx.prefix
        raid = None

        async def timeout_raid(cmd, raid=None):
            await tutorial_channel.send(
                f"You took too long to complete the **{prefix}{cmd}** "
                "command! This channel will be deleted in one minute.")
            if raid:
                await raid.expire_raid()
            else:
                await asyncio.sleep(60)
                await tutorial_channel.delete()
            return

        await tutorial_channel.send(
            f"This server utilizes the **{prefix}raid** command to "
            "report raids! When you use it, I will send a message "
            "summarizing the report and create a text channel for "
            "coordination. \n"
            "The report must contain, in this order: The Pokemon (if an "
            "active raid) or raid level (if an egg), and the location; "
            " and the "
            "minutes remaining until hatch or expiry (at the end of the "
            "report) \n\n"
            "Try reporting a raid!\n"
            f"Ex: `{prefix}raid magikarp local church 42`\n"
            f"`{prefix}raid 3 local church 27`")

        try:
            while True:
                raid_ctx = await self.wait_for_cmd(
                    tutorial_channel, ctx.author, 'raid')

                raid = raid_ctx.raid

                if raid:
                    break

                # acknowledge failure and redo wait_for
                await tutorial_channel.send(
                    "Doesn't look like it worked. Make sure you're not "
                    "missing any arguments from your raid command and "
                    "try again.")

            # acknowledge and redirect to new raid channel
            raid.channel_ids.append(str(tutorial_channel.id))
            Raid.by_channel[str(tutorial_channel.id)] = raid
            await raid.upsert()
            await tutorial_channel.send("Great job!")
            await asyncio.sleep(1)

        # if no response for 5 minutes, close tutorial
        except asyncio.TimeoutError:
            await timeout_raid('raid')
            return False

        # post raid help info prefix, avatar, user
        helpembed = await formatters.get_raid_help(
            ctx.prefix, ctx.bot.user.avatar_url)

        await tutorial_channel.send(
            f"This channel will now be treated as a raid channel. Here is a list of "
            "commands that can be used in here:", embed=helpembed)

        await tutorial_channel.send(
            f"Try expressing interest in this raid!\n\n"
            f"Ex: `{prefix}interested 5 m3 i1 v1` would mean 5 trainers: "
            "3 Mystic, 1 Instinct, 1 Valor\n"
            "Alternatively, you may use the :thinking: reaction to express interest. "
            "I will automatically use the party totals from your last RSVP if you use the reaction.")

        # wait for interested status update
        try:
            await self.wait_for_rsvp(
                raid, ctx.author, 'maybe')

        # if no response for 5 minutes, close tutorial
        except asyncio.TimeoutError:
            await timeout_raid('interested', raid=raid)
            return False

        # acknowledge and continue with pauses between
        await asyncio.sleep(1)
        await tutorial_channel.send(
            f"Great job! To save time, you can also use **{prefix}i** "
            f"as an alias for **{prefix}interested**.")

        await asyncio.sleep(1)
        await tutorial_channel.send(
            "Now try letting people know that you are on your way!\n\n"
            f"Ex: `{prefix}coming`\n"
            "You can also use the :red_car: reaction.")

        # wait for coming status update
        try:
            await self.wait_for_rsvp(
                raid, ctx.author, 'coming')

        # if no response for 5 minutes, close tutorial
        except asyncio.TimeoutError:
            await timeout_raid('coming', raid=raid)
            return False

        # acknowledge and continue with pauses between
        await asyncio.sleep(1)
        await tutorial_channel.send(
            "Great! Note that if you have already specified your party "
            "in a previous command, you do not have to again for the "
            "current raid unless you are changing it. Also, "
            f"**{prefix}c** is an alias for **{prefix}coming**.")

        await asyncio.sleep(1)
        await tutorial_channel.send(
            "Now try letting people know that you have arrived at the "
            "raid!\n\n"
            f"Ex: `{prefix}here`\n"
            "You can also use the <:here:350686955316445185> reaction.")

        # wait for here status update
        try:
            await self.wait_for_rsvp(
                raid, ctx.author, 'here')

        # if no response for 5 minutes, close tutorial
        except asyncio.TimeoutError:
            await timeout_raid('here', raid=raid)
            return False

        # acknowledge and continue with pauses between
        await asyncio.sleep(1)
        await tutorial_channel.send(
            f"Good! Please note that **{prefix}h** is an alias for "
            f"**{prefix}here**")

        await asyncio.sleep(1)
        await tutorial_channel.send(
            "Now try checking to see everyone's RSVP status for this "
            f"raid!\n\nEx: `{prefix}list`")

        # wait for list command completion
        try:
            await self.wait_for_cmd(
                tutorial_channel, ctx.author, 'list')

        # if no response for 5 minutes, close tutorial
        except asyncio.TimeoutError:
            await timeout_raid('list', raid=raid)
            return False

        # acknowledge and continue with pauses between
        await asyncio.sleep(1)
        while True:
            if raid.status == 'egg':
                await tutorial_channel.send(
                    "Excellent. For the next command, we need the raid to be active, "
                    "so I'm going to go ahead and set the hatch time to right now. "
                    "I'll wait a bit for you to report a boss."
                )
                raid.update_time(time.time())
                await asyncio.sleep(10)
                continue
            elif raid.status == 'hatched':
                await tutorial_channel.send(
                    "Use the reactions on the message above to report a boss!"
                )
                await asyncio.sleep(10)
                continue
            else:
                break
        await tutorial_channel.send(
            "Awesome! Since no one else is on their way, try using the "
            f"**{prefix}starting** command to move everyone on the "
            "'here' list to a lobby!\n"
            "You can also use the :arrow_forward: reaction.\n"
            "Also, if you happen to start a raid with a group that is smaller "
            "than the recommended group size for the boss, or if your group is larger "
            "than 20 trainers, or if you are starting the raid when the trainers "
            "who are still on the way to the raid won't be able to take the boss on "
            "their own, I will alert you to those circumstances and ask you to confirm "
            "that you want to begin the raid. You can use a reaction to either cancel "
            "the raid start or to go ahead.")

        # wait for starting command completion
        try:
            await self.wait_for_rsvp(
                raid, ctx.author, 'lobby')

        # if no response for 5 minutes, close tutorial
        except asyncio.TimeoutError:
            await timeout_raid('starting', raid=raid)
            return False

        # acknowledge and continue with pauses between
        await asyncio.sleep(1)
        await tutorial_channel.send(
            "Great! You are now listed as being 'in the lobby', where "
            "you will remain for two minutes until the raid begins. In "
            "that time, anyone can request a backout with the "
            "reaction to the above message. If the person requesting is "
            "in the lobby, the backout is automatic. If it is someone "
            "who arrived at the raid afterward, confirmation will be "
            "requested from a lobby member. When a backout is confirmed, "
            "all members will be returned to the 'here' list.")

        await asyncio.sleep(1)
        await tutorial_channel.send(
            "A couple of notes about raid channels. Meowth has "
            "partnered with Pokebattler to give you the best counters "
            "for each raid boss in every situation. You can set the "
            "weather with the "
            f"**{prefix}weather** command. You can select the moveset "
            f"using the **{prefix}moveset** command. If "
            f"you have a Pokebattler account, you can use **{prefix}"
            "pokebattler <id>** to link them! After that, the "
            f"**{prefix}counters**  command will DM you your own counters "
            "pulled from your Pokebox.")

        await asyncio.sleep(15)

        return True

    async def research_tutorial(self, ctx):

        await ctx.tutorial_channel.send(
            f"This server utilizes the **{ctx.prefix}research** command to "
            "report field research tasks! There are three ways to use this "
            f"command: **{ctx.prefix}research <location>** will start an interactive "
            "session where I will prompt you for the task category, specific task, and "
            "reward of the research task. You can also use "
            f"**{ctx.prefix}research <task_category> <location>** to "
            "skip the first prompt. Finally, you can use "
            f"**{ctx.prefix}research <task> <location> to skip to the reward prompt. "
            "At each step, I will try to match your task and reward input with known "
            "Field Research tasks, Pokemon, or items. To input the task category as "
            "a shortcut, use single words like `raid` or `catch`.\n\n"
            f"Try it out by typing `{ctx.prefix}research starbucks`")

        # wait for research command completion
        try:
            await self.wait_for_cmd(
                ctx.tutorial_channel, ctx.author, 'research')

            # acknowledge and wait a second before continuing
            await ctx.tutorial_channel.send("Great job!")
            await asyncio.sleep(1)
            return True

        # if no response for 5 minutes, close tutorial
        except asyncio.TimeoutError:
            await ctx.tutorial_channel.send(
                f"You took too long to use the **{ctx.prefix}research** "
                "command! This channel will be deleted in ten seconds.")
            await asyncio.sleep(10)
            await ctx.tutorial_channel.delete()
            return False


    async def team_tutorial(self, ctx):
        await ctx.tutorial_channel.send(
            f"This server utilizes the **{ctx.prefix}team** command to "
            "allow members to select which Pokemon Go team they belong "
            f"to! Type `{ctx.prefix}team mystic` for example if you are in "
            "Team Mystic.")

        # wait for team command completion
        try:
            await self.wait_for_cmd(
                ctx.tutorial_channel, ctx.author, 'team')

            # acknowledge and wait a second before continuing
            await ctx.tutorial_channel.send("Great job!")
            await asyncio.sleep(1)

        # if no response for 5 minutes, close tutorial
        except asyncio.TimeoutError:
            await ctx.tutorial_channel.send(
                f"You took too long to use the **{ctx.prefix}team** command! "
                "This channel will be deleted in ten seconds.")
            await asyncio.sleep(10)
            await ctx.tutorial_channel.delete()
            return False

        return True

    @commands.group(invoke_without_command=True)
    async def tutorial(self, ctx):
        """Launches an interactive tutorial session for Meowth.
        Meowth will create a private channel and initiate a
        conversation that walks you through the various commands
        that are enabled on the current server."""

        newbie = ctx.author
        guild = ctx.guild
        prefix = ctx.prefix

        # get channel overwrites
        ows = self.get_overwrites(guild, newbie)

        # create tutorial channel
        name = newbie.display_name+"-tutorial"
        ctx.tutorial_channel = await guild.create_text_channel(
            name, overwrites=ows)
        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.send(
            ("Meowth! I've created a private tutorial channel for "
             f"you! Continue in {ctx.tutorial_channel.mention}"),
            delete_after=20.0)

        # get tutorial settings
        d = await self.guild_tutorial_settings(guild)
        d['channelid'] = ctx.tutorial_channel.id
        d['clean'] = False
        d['meetup'] = False
        d['category_1'] = 'message'
        d['category_2'] = 'message'
        d['category_3'] = 'message'
        d['category_4'] = 'message'
        d['category_5'] = 'message'
        d['category_ex'] = 'message'
        d['lat'] = -90
        d['lon'] = 0
        d['radius'] = 1
        enabled = [x for x in d if d[x] is True]
        report_channel_table = ctx.bot.dbi.table('report_channels')
        insert = report_channel_table.insert
        insert.row(**d)
        await insert.commit()

        await ctx.tutorial_channel.send(
            f"Hi {ctx.author.mention}! I'm Meowth, a Discord helper bot for "
            "Pokemon Go communities! I created this channel to teach you all "
            "about the things I can do to help you on this server! You can "
            "abandon this tutorial at any time and I'll delete this channel "
            "after five minutes. Let's get started!")

        try:

            # start want tutorial
            if 'users' in enabled:
                completed = await self.want_tutorial(ctx)
                if not completed:
                    return

            # start wild tutorial
            if 'wild' in enabled:
                completed = await self.wild_tutorial(ctx)
                if not completed:
                    return

            # start raid
            if 'raid' in enabled:
                completed = await self.raid_tutorial(ctx)
                if not completed:
                    return

            # start research
            if 'research' in enabled:
                completed = await self.research_tutorial(ctx)
                if not completed:
                    return

            # start team
            if 'users' in enabled:
                completed = await self.team_tutorial(ctx)
                if not completed:
                    return

            # finish tutorial
            await ctx.tutorial_channel.send(
                f"This concludes the Meowth tutorial! "
                "This channel will be deleted in 30 seconds.")
            await asyncio.sleep(30)

        finally:
            query = report_channel_table.query
            query.where(channelid=ctx.tutorial_channel.id)
            await query.delete()
            try:
                await ctx.tutorial_channel.delete()
            except:
                pass

    @tutorial.command()
    async def want(self, ctx):
        """Launches a tutorial session for the want feature.
        Meowth will create a private channel and initiate a
        conversation that walks you through the various commands
        that are enabled on the current server."""

        newbie = ctx.author
        guild = ctx.guild

        # get channel overwrites
        ows = self.get_overwrites(guild, newbie)

        # create tutorial channel
        name = newbie.display_name+"-tutorial"
        ctx.tutorial_channel = await guild.create_text_channel(
            name, overwrites=ows)
        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.send(
            ("Meowth! I've created a private tutorial channel for "
             f"you! Continue in {ctx.tutorial_channel.mention}"),
            delete_after=20.0)

        # set tutorial settings
        d = {
            'channelid': ctx.tutorial_channel.id,
            'users': True
        }
        report_channel_table = ctx.bot.dbi.table('report_channels')
        insert = report_channel_table.insert
        insert.row(**d)
        await insert.commit()

        await ctx.tutorial_channel.send(
            f"Hi {ctx.author.mention}! I'm Meowth, a Discord helper bot for "
            "Pokemon Go communities! I created this channel to teach you "
            "about the want command! You can abandon this tutorial at any time "
            "and I'll delete this channel after five minutes. "
            "Let's get started!")

        try:
            await self.want_tutorial(ctx)
            await ctx.tutorial_channel.send(
                f"This concludes the Meowth tutorial! "
                "This channel will be deleted in ten seconds.")
            await asyncio.sleep(10)
        finally:
            query = report_channel_table.query
            query.where(channelid=ctx.tutorial_channel.id)
            await query.delete()
            await ctx.tutorial_channel.delete()

    @tutorial.command()
    async def wild(self, ctx):
        """Launches an tutorial session for the wild feature.
        Meowth will create a private channel and initiate a
        conversation that walks you through wild command."""

        newbie = ctx.author
        guild = ctx.guild

        # get channel overwrites
        ows = self.get_overwrites(guild, newbie)

        # create tutorial channel
        name = newbie.display_name+"-tutorial"
        ctx.tutorial_channel = await guild.create_text_channel(
            name, overwrites=ows)
        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.send(
            ("Meowth! I've created a private tutorial channel for "
             f"you! Continue in {ctx.tutorial_channel.mention}"),
            delete_after=20.0)

        # set tutorial settings
        d = {
            'channelid': ctx.tutorial_channel.id,
            'wild': True,
            'city': 'Lapland',
            'lat': 90,
            'lon': 0,
            'radius': 1
        }
        report_channel_table = ctx.bot.dbi.table('report_channels')
        insert = report_channel_table.insert
        insert.row(**d)
        await insert.commit()

        await ctx.tutorial_channel.send(
            f"Hi {ctx.author.mention}! I'm Meowth, a Discord helper bot for "
            "Pokemon Go communities! I created this channel to teach you "
            "about the wild command! You can abandon this tutorial at any time "
            "and I'll delete this channel after five minutes. "
            "Let's get started!")

        try:
            await self.wild_tutorial(ctx)
            await ctx.tutorial_channel.send(
                f"This concludes the Meowth tutorial! "
                "This channel will be deleted in ten seconds.")
            await asyncio.sleep(10)
        finally:
            query = report_channel_table.query
            query.where(channelid=ctx.tutorial_channel.id)
            await query.delete()
            await ctx.tutorial_channel.delete()

    @tutorial.command()
    async def raid(self, ctx):
        """Launches an tutorial session for the raid feature.
        Meowth will create a private channel and initiate a
        conversation that walks you through the raid commands."""

        newbie = ctx.author
        guild = ctx.guild

        # get channel overwrites
        ows = self.get_overwrites(guild, newbie)

        # create tutorial channel
        name = newbie.display_name+"-tutorial"
        ctx.tutorial_channel = await guild.create_text_channel(
            name, overwrites=ows)
        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.send(
            ("Meowth! I've created a private tutorial channel for "
             f"you! Continue in {ctx.tutorial_channel.mention}"),
            delete_after=20.0)

        # set tutorial settings
        d = {
            'channelid': ctx.tutorial_channel.id,
            'raid': True,
            'city': 'Lapland',
            'lat': 90,
            'lon': 0,
            'radius': 1,
            'category_1': 'message',
            'category_2': 'message',
            'category_3': 'message',
            'category_4': 'message',
            'category_5': 'message',
            'category_ex': 'message'
        }
        report_channel_table = ctx.bot.dbi.table('report_channels')
        insert = report_channel_table.insert
        insert.row(**d)
        await insert.commit()

        await ctx.tutorial_channel.send(
            f"Hi {ctx.author.mention}! I'm Meowth, a Discord helper bot for "
            "Pokemon Go communities! I created this channel to teach you "
            "about the raid command! You can abandon this tutorial at any time "
            "and I'll delete this channel after five minutes. "
            "Let's get started!")

        try:
            await self.raid_tutorial(ctx)
            await ctx.tutorial_channel.send(
                f"This concludes the Meowth tutorial! "
                "This channel will be deleted in ten seconds.")
            await asyncio.sleep(10)
        finally:
            query = report_channel_table.query
            query.where(channelid=ctx.tutorial_channel.id)
            await query.delete()
            await ctx.tutorial_channel.delete()

    @tutorial.command()
    async def research(self, ctx):
        """Launches an tutorial session for the research feature.
        Meowth will create a private channel and initiate a
        conversation that walks you through the research command."""

        newbie = ctx.author
        guild = ctx.guild

        # get channel overwrites
        ows = self.get_overwrites(guild, newbie)

        # create tutorial channel
        name = newbie.display_name+"-tutorial"
        ctx.tutorial_channel = await guild.create_text_channel(
            name, overwrites=ows)
        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.send(
            ("Meowth! I've created a private tutorial channel for "
             f"you! Continue in {ctx.tutorial_channel.mention}"),
            delete_after=20.0)

        # set tutorial settings
        d = {
            'channelid': ctx.tutorial_channel.id,
            'research': True,
            'city': 'Lapland',
            'lat': 90,
            'lon': 0,
            'radius': 1
        }
        report_channel_table = ctx.bot.dbi.table('report_channels')
        insert = report_channel_table.insert
        insert.row(**d)
        await insert.commit()

        await ctx.tutorial_channel.send(
            f"Hi {ctx.author.mention}! I'm Meowth, a Discord helper bot for "
            "Pokemon Go communities! I created this channel to teach you "
            "about the research command! You can abandon this tutorial at "
            "any time and I'll delete this channel after five minutes. "
            "Let's get started!")

        try:
            await self.research_tutorial(ctx)
            await ctx.tutorial_channel.send(
                f"This concludes the Meowth tutorial! "
                "This channel will be deleted in ten seconds.")
            await asyncio.sleep(10)
        finally:
            query = report_channel_table.query
            query.where(channelid=ctx.tutorial_channel.id)
            await query.delete()
            await ctx.tutorial_channel.delete()

    @tutorial.command()
    async def team(self, ctx):
        """Launches an tutorial session for the team feature.
        Meowth will create a private channel and initiate a
        conversation that walks you through the team command."""

        newbie = ctx.author
        guild = ctx.guild

        # get channel overwrites
        ows = self.get_overwrites(guild, newbie)

        # create tutorial channel
        name = newbie.display_name+"-tutorial"
        ctx.tutorial_channel = await guild.create_text_channel(
            name, overwrites=ows)
        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.send(
            ("Meowth! I've created a private tutorial channel for "
             f"you! Continue in {ctx.tutorial_channel.mention}"),
            delete_after=20.0)

        # set tutorial settings
        d = {
            'channelid': ctx.tutorial_channel.id,
            'users': True
        }
        report_channel_table = ctx.bot.dbi.table('report_channels')
        insert = report_channel_table.insert
        insert.row(**d)
        await insert.commit()

        await ctx.tutorial_channel.send(
            f"Hi {ctx.author.mention}! I'm Meowth, a Discord helper bot for "
            "Pokemon Go communities! I created this channel to teach you "
            "about the team command! You can abandon this tutorial at any time "
            "and I'll delete this channel after five minutes. "
            "Let's get started!")

        try:
            await self.team_tutorial(ctx)
            await ctx.tutorial_channel.send(
                f"This concludes the Meowth tutorial! "
                "This channel will be deleted in ten seconds.")
            await asyncio.sleep(10)
        finally:
            query = report_channel_table.query
            query.where(channelid=ctx.tutorial_channel.id)
            await query.delete()
            await ctx.tutorial_channel.delete()