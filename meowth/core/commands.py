import asyncio
import json
import os
import textwrap
import functools

import aiohttp
import psutil

import discord
from discord.ext import commands

from meowth import command, group, checks, errors
from meowth.utils import snowflake, url_color, make_embed, convert_to_bool
from meowth.utils.pagination import Pagination

class Core:
    """General bot functions."""

    def __init__(self, bot):
        self.bot = bot
        bot.remove_command('help')

    @command(name="shutdown", aliases=["exit"], category='Owner')
    @checks.is_owner()
    async def _shutdown(self, ctx):
        """Shuts down the bot"""
        embed = make_embed(
            title='Shutting down.',
            msg_colour='red',
            icon="https://i.imgur.com/uBYS8DR.png")
        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            pass
        await ctx.bot.shutdown()

    @command(name="break", category='Owner')
    @checks.is_owner()
    async def _break(self, ctx):
        """Simulates a sudden disconnection."""
        embed = make_embed(msg_type='warning', title='Faking a crash...')
        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            pass
        await ctx.bot.logout()

    @command(name="restart", category='Owner')
    @checks.is_owner()
    async def _restart(self, ctx):
        """Restarts the bot"""
        embed = make_embed(
            title='Restarting...',
            msg_colour='red',
            icon="https://i.imgur.com/uBYS8DR.png")
        try:
            restart_msg = await ctx.send(embed=embed)
        except discord.HTTPException:
            restart_msg = None
        data = {
            'restart_snowflake': next(snowflake.create()),
            'restart_by':ctx.author.id,
            'restart_channel':ctx.channel.id,
            'restart_guild':ctx.guild.id
        }
        if restart_msg:
            data['restart_message'] = restart_msg.id
        table = ctx.bot.dbi.table('restart_savedata')
        table.insert(**data)
        await table.insert.commit()
        await ctx.bot.shutdown(restart=True)

    @group(name="set", category='Owner')
    @checks.is_co_owner()
    async def _set(self, ctx):
        """Changes bot settings"""
        if ctx.invoked_subcommand is None:
            await ctx.bot.send_cmd_help(ctx)

    @_set.command(name="game")
    @checks.is_co_owner()
    async def _game(self, ctx, *, game: str):
        """Sets the bot's activity"""
        status = ctx.me.status
        game = discord.Game(name=game)
        await ctx.bot.change_presence(status=status, activity=game)
        embed = make_embed(msg_type='success', title='Game set.')
        await ctx.send(embed=embed)

    @_set.command()
    @checks.is_co_owner()
    async def status(self, ctx, *, status: str):
        """Sets the bot's online status

        Available statuses:
            online
            idle
            dnd
        """

        statuses = {
            "online"    : discord.Status.online,
            "idle"      : discord.Status.idle,
            "dnd"       : discord.Status.dnd,
            "invisible" : discord.Status.invisible
            }

        game = ctx.me.activity

        try:
            status = statuses[status.lower()]
        except KeyError:
            await ctx.bot.send_cmd_help(ctx)
        else:
            await ctx.bot.change_presence(status=status,
                                          activity=game)
            embed = make_embed(
                msg_type='success',
                title="Status changed to {}.".format(status))
            await ctx.send(embed=embed)

    @_set.command(name="username", aliases=["name"])
    @checks.is_owner()
    async def _username(self, ctx, *, username: str):
        """Sets bot's username"""
        try:
            await ctx.bot.user.edit(username=username)
        except discord.HTTPException:
            embed = make_embed(
                msg_type='error',
                title="Failed to change name",
                content=("Remember that you can only do it up to 2 times an "
                         "hour. Use nicknames if you need frequent changes. "
                         "**{}set nickname**").format(ctx.prefix))
            await ctx.send(embed=embed)
        else:
            embed = make_embed(msg_type='success', title="Username set.")
            await ctx.send(embed=embed)

    @_set.command(name="avatar")
    @checks.is_co_owner()
    async def _avatar(self, ctx, *, avatar_url: str):
        """Sets bot's avatar"""
        session = aiohttp.ClientSession()
        async with session.get(avatar_url) as req:
            data = await req.read()
        await session.close()
        try:
            await ctx.bot.user.edit(avatar=data)
        except discord.HTTPException:
            await ctx.error('Failed to set avatar.')
        else:
            await ctx.success('Avatar set.')

    @_set.command(name="nickname")
    @checks.is_admin()
    @commands.guild_only()
    async def _nickname(self, ctx, *, nickname: str):
        """Sets bot's nickname"""
        try:
            await ctx.guild.me.edit(nick=nickname)
        except discord.Forbidden:
            embed = make_embed(
                msg_type='error',
                title="Failed to set nickname",
                content=("I'm missing permissions to change my nickname. "
                         "Use **{}get guildperms** to check permissions."
                         "").format(ctx.prefix))
            await ctx.send()
        else:
            embed = make_embed(msg_type='success', title="Nickname set.")
            await ctx.send(embed=embed)

    @command(name="uptime", category='Bot Info')
    async def _uptime(self, ctx):
        """Shows bot's uptime"""
        uptime_str = ctx.bot.uptime_str
        try:
            await ctx.embed('Uptime', uptime_str, colour='blue',
                            icon="https://i.imgur.com/82Cqf1x.png")
        except discord.errors.Forbidden:
            await ctx.send("Uptime: {}".format(uptime_str))

    @command(name="botinvite", category='Bot Info')
    async def _bot_invite(self, ctx, plain_url: bool = False):
        """Shows bot's invite url"""
        invite_url = ctx.bot.invite_url
        if plain_url:
            await ctx.send("Invite URL: <{}>".format(invite_url))
            return
        else:
            embed = make_embed(
                title='Click to invite me to your server!',
                title_url=invite_url,
                msg_colour='blue',
                icon="https://i.imgur.com/DtPWJPG.png")
        try:
            await ctx.send(embed=embed)
        except discord.errors.Forbidden:
            await ctx.send("Invite URL: <{}>".format(invite_url))

    @command(name="about", category='Bot Info')
    async def _about(self, ctx):
        """Shows info about the bot"""
        bot = ctx.bot
        author_repo = "https://github.com/FoglyOgly"
        bot_repo = author_repo + "/Meowth"
        uptime_str = bot.uptime_str
        owner = await ctx.get.user(ctx.bot.owner)
        invite_str = "[Invite Me!]({})".format(bot.invite_url)

        if ctx.guild:
            prefix = await ctx.bot.dbi.prefix_stmt.fetchval(ctx.guild.id)
        if not prefix:
            prefix = ctx.bot.default_prefix

        member_count = 0
        server_count = 0

        server_count = len(bot.guilds)
        member_count = sum([g.member_count for g in bot.guilds])

        about = [
            "A Bot for Pokemon Go Communities!",
            f"**[Docs & Source!]({bot_repo})** | **{invite_str}**\n\n",
            f"Guild Prefix: `{prefix}`\n",
            f"Help: `{prefix}help`\n\n",
            f"**Owner:** {owner}",
            f"**Uptime:** {uptime_str}",
            f"**Servers:** {server_count}",
            f"**Members:** {member_count}"]

        embed_colour = await url_color(bot.avatar_small)
        embed = make_embed(
            icon=bot.avatar_small, title=f"{bot.user}",
            content='\n'.join(about), msg_colour=embed_colour)
        embed.set_thumbnail(url=bot.avatar)

        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("I need the `Embed links` permission to send this")

    def get_cpu(self):
        return psutil.cpu_percent(interval=1)

    @command(name="stats", category='Owner', aliases=['statistics'])
    @checks.is_co_owner()
    async def _stats(self, ctx):
        """Shows stats about bot"""
        bot = ctx.bot
        owner = await bot.get_user_info(ctx.bot.owner)
        uptime_str = bot.uptime_str
        cpu_p = await ctx.bot.loop.run_in_executor(None, self.get_cpu)
        mem = psutil.virtual_memory()
        mem_p = round((mem.available / mem.total) * 100, 2)
        bot_process = psutil.Process()
        ppid = bot_process.ppid()
        p_mem = bot_process.memory_info().rss
        swapped = psutil.swap_memory().used

        data_sizes = {
            'B':1,
            'KB':1024,
            'MB':1048576,
            'GB':1073741824
        }
        for size, value in data_sizes.items():
            if (p_mem / value) > 1 < 1024:
                p_mem_str = "{} {}".format(
                    round(p_mem / value, 2), size)
            if (swapped / value) > 1 < 1024:
                swap_str = "{} {}".format(
                    round(swapped / value, 2), size)

        member_count = 0
        server_count = 0
        for guild in bot.guilds:
            server_count += 1
            member_count += guild.member_count

        msg_table = bot.dbi.table('discord_messages')
        msg_table.query(msg_table['*'].count)
        message_count = await msg_table.query.get_value()

        cmd_table = bot.dbi.table('command_log')
        cmd_table.query(cmd_table['*'].count)
        command_count = await cmd_table.query.get_value()

        embed = make_embed(
            msg_type='info', title="Bot Statistics")
        instance_msg = (
            f"**Owner:** {owner}\n**Uptime:** {uptime_str}\n"
            f"**Version:** {bot.version}\n"
            f"**D.Py Ver:** {bot.dpy_version}\n"
            f"**Python:** {bot.py_version}")
        session_msg = (
            f"**Servers:** {server_count}\n**Members:** {member_count}\n"
            f"**Messages:** {message_count}\n"
            f"**Commands:** {command_count}\n"
            f"**Reconnections:** {bot.resumed_count}")
        process_msg = (
            f"**PID:** {ppid}\n**Process RAM:** {p_mem_str}\n"
            f"**Swap File:** {swap_str}\n**System RAM:** {mem_p}\n"
            f"**System CPU:** {cpu_p}\n")
        embed.add_field(name="ACTIVITY", value=session_msg)
        embed.add_field(name="PROCESS", value=process_msg)
        embed.add_field(name="INSTANCE", value=instance_msg)

        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("I need the `Embed links` permission to send this")

    @group(name="get", category="Owner", invoke_without_command=True)
    async def _get(self, ctx):
        """Gets information on settings, guilds, channels and users"""
        await ctx.bot.send_cmd_help(ctx)

    @group(category="Bot Info", name='permissions',
           aliases=['perms'], invoke_without_command='True')
    @checks.is_mod()
    async def bot_perms(self, ctx, *, channel_id: int = None):
        """Show bot's permissions for the guild and channel."""
        if not await ctx.is_co_owner() and channel_id is not None:
            return await ctx.error(
                'Only co-owners of the bot can specify channel')
        channel = ctx.bot.get(ctx.bot.get_all_channels(), id=channel_id)
        guild = channel.guild if channel else ctx.guild
        channel = channel or ctx.channel
        guild_perms = guild.me.guild_permissions
        chan_perms = channel.permissions_for(guild.me)
        req_perms = ctx.bot.req_perms

        embed = await ctx.info('Bot Permissions', send=False)

        wrap = functools.partial(textwrap.wrap, width=20)
        names = [wrap(channel.name), wrap(guild.name)]
        if channel.category:
            names.append(wrap(channel.category.name))
        name_len = max(len(n) for n in names)
        def same_len(txt):
            return '\n'.join(txt + ([' '] * (name_len-len(txt))))
        names = [same_len(n) for n in names]
        chan_msg = [f"**{names[0]}** \n{channel.id} \n"]
        guild_msg = [f"**{names[1]}** \n{guild.id} \n"]
        def perms_result(perms):
            data = []
            meet_req = perms >= req_perms
            result = "**PASS**" if meet_req else "**FAIL**"
            data.append(f"{result} - {perms.value} \n")
            true_perms = [k for k, v in dict(perms).items() if v is True]
            false_perms = [k for k, v in dict(perms).items() if v is False]
            req_perms_list = [k for k, v in dict(req_perms).items() if v is True]
            true_perms_str = '\n'.join(true_perms)
            if not meet_req:
                missing = '\n'.join([p for p in false_perms if p in req_perms_list])
                data.append(f"**MISSING** \n{missing} \n")
            if true_perms_str:
                data.append(f"**ENABLED** \n{true_perms_str} \n")
            return '\n'.join(data)
        guild_msg.append(perms_result(guild_perms))
        chan_msg.append(perms_result(chan_perms))
        embed.add_field(name='GUILD', value='\n'.join(guild_msg))
        if channel.category:
            cat_perms = channel.category.permissions_for(guild.me)
            cat_msg = [f"**{names[2]}** \n{channel.category.id} \n"]
            cat_msg.append(perms_result(cat_perms))
            embed.add_field(name='CATEGORY', value='\n'.join(cat_msg))
        embed.add_field(name='CHANNEL', value='\n'.join(chan_msg))

        try:
            await ctx.send(embed=embed)
        except discord.errors.Forbidden:
            # didn't have permissions to send a message with an embed
            try:
                msg = "I couldn't send an embed here, so I've sent you a DM"
                await ctx.send(msg)
            except discord.errors.Forbidden:
                # didn't have permissions to send a message at all
                pass
            await ctx.author.send(embed=embed)

    @bot_perms.command(name='guild')
    @checks.is_mod()
    async def guild_perms(self, ctx, guild_id=None):
        """Gets bot's permissions for the guild."""
        if not ctx.guild and not guild_id:
            await ctx.send(embed=make_embed(
                msg_type='error', title="This is a DM. Please provide ID."))
            return
        if guild_id:
            guild = ctx.bot.get_guild(int(guild_id))
            if not guild:
                await ctx.send(embed=make_embed(
                    msg_type='error', title="Guild not found"))
                return
        else:
            guild = ctx.guild

        guild_perms = guild.me.guild_permissions
        req_perms = ctx.bot.req_perms
        perms_compare = guild_perms >= req_perms
        core_dir = ctx.bot.core_dir
        data_dir = os.path.join(core_dir, '..', 'data')
        data_file = 'permissions.json'
        msg = f"{guild}\nID {guild.id}\n"
        msg += f"```py\n{guild_perms.value}\n"
        msg += f"{perms_compare}```"

        with open(os.path.join(data_dir, data_file), "r") as perm_json:
            perm_dict = json.load(perm_json)

        for perm, bitshift in perm_dict.items():
            if bool((req_perms.value >> bitshift) & 1):
                if bool((guild_perms.value >> bitshift) & 1):
                    msg += ":white_small_square:  {}\n".format(perm)
                else:
                    msg += ":black_small_square:  {}\n".format(perm)

        try:
            if not isinstance(ctx.channel, discord.DMChannel):
                if not ctx.channel.permissions_for(ctx.guild.me).embed_links:
                    await ctx.send(msg)
                    return
            embed = make_embed(
                msg_type='info',
                title='Guild Permissions',
                content=msg)
            await ctx.send(embed=embed)
        except discord.errors.Forbidden:
            embed = make_embed(
                msg_type='info',
                title='Guild Permissions',
                content=msg)
            await ctx.author.send(embed=embed)

    @bot_perms.command(name='channel', aliases=['chan'])
    @checks.is_mod()
    async def channel_perms(self, ctx, channel_id=None):
        """Gets bot's permissions for the channel."""
        if channel_id:
            channel = ctx.bot.get_channel(int(channel_id))
            if not channel:
                await ctx.send(embed=make_embed(
                    msg_type='error', title="Channel not found"))
                return
        else:
            channel = ctx.channel

        dm_channel = isinstance(channel, discord.DMChannel)
        me = ctx.bot.user if dm_channel else channel.guild.me
        chan_perms = channel.permissions_for(me)
        req_perms = ctx.bot.req_perms
        perms_compare = chan_perms >= req_perms
        core_dir = ctx.bot.core_dir
        data_dir = os.path.join(core_dir, '..', 'data')
        data_file = 'permissions.json'
        msg = ""
        if not dm_channel:
            msg += f"{channel.guild}\nID {channel.guild.id}\n"
        msg += f"{channel}\nID {channel.id}\n"
        msg += f"```py\n{chan_perms.value}\n"
        msg += f"{perms_compare}```"

        with open(os.path.join(data_dir, data_file), "r") as perm_json:
            perm_dict = json.load(perm_json)

        for perm, bitshift in perm_dict.items():
            if bool((req_perms.value >> bitshift) & 1):
                if bool((chan_perms.value >> bitshift) & 1):
                    msg += f":white_small_square:  {perm}\n"
                else:
                    msg += f":black_small_square:  {perm}\n"
        try:
            if not isinstance(ctx.channel, discord.DMChannel):
                if not ctx.channel.permissions_for(ctx.guild.me).embed_links:
                    await ctx.send(msg)
                    return
            embed = make_embed(
                msg_type='info',
                title='Channel Permissions',
                content=msg)
            await ctx.send(embed=embed)
        except discord.errors.Forbidden:
            embed = make_embed(
                msg_type='info',
                title='Channel Permissions',
                content=msg)
            await ctx.author.send(embed=embed)

    @command(name="resumed", category='Bot Info')
    async def _resumed(self, ctx):
        """Gets the number of websocket reconnections."""
        r_c = ctx.bot.resumed_count
        embed = make_embed(msg_type='info',
                           title=f"Connections Resumed: {r_c}")
        await ctx.send(embed=embed)

    @command(name="ping", category='Bot Info')
    async def _ping(self, ctx):
        msg = ''
        for shard, latency in ctx.bot.latencies:
            here = '  🡸' if shard == ctx.guild.shard_id else ''
            msg += ("**Shard {0}:** {1:.2f} ms{2}"
                    "\n").format(shard, latency * 1000, here)
        await ctx.embed('Latency', msg, msg_type='info')

    @command(category='Owner')
    @checks.is_admin()
    async def purge(self, ctx, msg_number: int = 10):
        """Delete a number of messages from the channel.

        Default is 10. Max 100."""
        if msg_number > 100:
            embed = make_embed(
                msg_type='info',
                title="ERROR",
                content="No more than 100 messages can be purged at a time.",
                guild=ctx.guild)
            await ctx.send(embed=embed)
            return
        deleted = await ctx.channel.purge(limit=msg_number)
        embed = make_embed(
            msg_type='success',
            title='Deleted {} message{}'.format(
                len(deleted), "s" if len(deleted) > 1 else ""))
        result_msg = await ctx.send(embed=embed)
        await asyncio.sleep(3)
        await result_msg.delete()

    @command(category='Owner')
    @checks.is_co_owner()
    async def reload_cm(self, ctx):
        """Reload Cog Manager."""
        bot = ctx.bot
        try:
            bot.unload_extension('meowth.core.cog_manager')
            bot.load_extension('meowth.core.cog_manager')
            embed = make_embed(msg_type='success',
                               title='Cog Manager reloaded.')
            await ctx.send(embed=embed)
        except Exception as e:
            msg = "{}: {}".format(type(e).__name__, e)
            embed = make_embed(msg_type='error',
                               title='Error loading Cog Manager',
                               content=msg)
            await ctx.send(embed=embed)

    @command(name="prefix", category='Bot Info')
    async def _prefix(self, ctx, *, new_prefix: str = None):
        """Get prefix and set server prefix.
        Use the argument 'reset' to reset the guild prefix to default.
        """
        bot = ctx.bot
        default_prefix = bot.default_prefix
        if not ctx.guild:
            if new_prefix:
                embed = make_embed(
                    msg_type='error',
                    title=f"Prefix can only be changed in guilds.")
                await ctx.send(embed=embed)
            else:
                embed = make_embed(
                    msg_type='info', title=f"Prefix is {default_prefix}")
                await ctx.send(embed=embed)
        else:
            if await ctx.is_co_owner():
                if new_prefix:
                    await ctx.guild_dm.prefix(new_prefix)
                    if new_prefix.lower() == 'reset':
                        new_prefix = bot.default_prefix
                    embed = make_embed(
                        msg_type='success', title=f"Prefix set to {new_prefix}")
                    return await ctx.send(embed=embed)

            guild_prefix = await ctx.guild_dm.prefix()
            prefix = guild_prefix if guild_prefix else default_prefix
            embed = make_embed(
                msg_type='info', title=f"Prefix is {prefix}")
            await ctx.send(embed=embed)

    @command(name='help', category='Bot Info')
    async def _help(self, ctx, *, command_name: str = None):
        """Shows help on available commands."""
        try:
            if command_name is None:
                p = await Pagination.from_bot(ctx)
            else:
                entity = (self.bot.get_category(command_name) or
                          self.bot.get_cog(command_name) or
                          self.bot.get_command(command_name))
                if entity is None:
                    clean = command_name.replace('@', '@\u200b')
                    return await ctx.send(f'Command or category "{clean}" not found.')
                elif isinstance(entity, commands.Command):
                    p = await Pagination.from_command(ctx, entity)
                elif isinstance(entity, str):
                    p = await Pagination.from_category(ctx, entity)
                else:
                    p = await Pagination.from_cog(ctx, entity)

            await p.paginate()
        except Exception as e:
            await ctx.send(e)

    @group(category='Server Config', name='enable', aliases=['disable'],
           invoke_without_command=True, hidden=True)
    @commands.guild_only()
    @checks.is_admin()
    async def _enable(self, ctx, cog):
        """Enable/Disable bot features within your guild."""
        if ctx.invoked_with == 'disable':
            value = False
        else:
            value = True
        try:
            if cog in {*ctx.bot.cogs}:
                await ctx.setting(cog+'Enabled', value)
                action = 'enabled' if value else 'disabled'
                embed = make_embed(msg_type='success', title=f'{cog} {action}.')
                await ctx.send(embed=embed)
                return
            else:
                embed = make_embed(msg_type='error', title=f'{cog} not found.')
                await ctx.send(embed=embed)
                return
        except errors.PostgresError as e:
            msg = "{}: {}".format(type(e).__name__, e)
            embed = make_embed(
                msg_type='error', title=f'Error enabling {cog}', content=msg)
            await ctx.send(embed=embed)
            raise

    @_enable.command(name='list')
    @checks.is_admin()
    async def _list(self, ctx):
        """List all loaded cogs."""
        cog_list = []
        for cog in ctx.bot.cogs:
            value = await ctx.setting(f'{cog}Enabled')
            if value is not None:
                value = convert_to_bool(value)
            if value is None:
                status = ":black_small_square:"
            elif value is True:
                status = ":white_small_square:"
            elif value is False:
                status = ":small_orange_diamond:"
            cog_list.append(f"{status} {cog}")
        cog_msg = '\n'.join(cog_list)
        embed = make_embed(
            msg_type='info', title='Available Cogs', content=cog_msg)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Core(bot))
