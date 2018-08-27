import inspect
import io
import os
import textwrap
import traceback
import unicodedata
import json
import logging
from datetime import datetime
from contextlib import redirect_stdout
from subprocess import Popen, PIPE

import pathlib

import discord
from discord.ext import commands

from meowth import checks, command, group
from meowth.utils import make_embed, get_match
from meowth.utils.formatters import ilcode
from meowth.utils.converters import BotCommand, Guild, Multi

logger = logging.getLogger('meowth.cogs.dev')

class Dev:
    """Developer Tools"""

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    def __local_check(self, ctx):
        return checks.check_is_co_owner(ctx)

    @command()
    async def linecount(self, ctx):
        root = pathlib.Path(ctx.bot.core_dir, "..", "..")
        py_files = tuple(root.glob('**/*.py'))
        json_files = tuple(root.glob('**/*.json'))
        py_count = len(py_files)
        json_count = len(json_files)
        total_files = py_count + json_count
        py_pc = round(py_count/total_files*100)
        json_pc = round(json_count/total_files*100)
        ln_count = tuple(len(list(p.open(encoding='utf-8'))) for p in py_files)
        max_count = max(ln_count)
        total_count = sum(ln_count)
        await ctx.info(
            f"Project Statistics",
            f"{total_count} Lines Total\n"
            f"{max_count} Most Lines\n\n"
            f"**{total_files} Files Total**\n"
            f"{py_count} **\*.py** files ({py_pc}%)\n"
            f"{json_count} **\*.json** files ({json_pc}%)")

    @command()
    async def charinfo(self, ctx, *, characters: str):
        """Shows you information about a number of characters.
        Only up to 25 characters at a time.
        """
        if len(characters) > 25:
            return await ctx.send(f'Too many characters ({len(characters)}/25)')
        charlist = []
        rawlist = []
        for char in characters:
            digit = f'{ord(char):x}'
            url = f"http://www.fileformat.info/info/unicode/char/{digit}"
            name = f"[{unicodedata.name(char, '')}]({url})"
            u_code = f'\\U{digit:>08}'
            if len(f'{digit}') <= 4:
                u_code = f'\\u{digit:>04}'
            charlist.append(' '.join([ilcode(u_code.ljust(10)+':'), name, '-', char]))
            rawlist.append(u_code)

        embed = await ctx.info('Character Info', '\n'.join(charlist), send=False)
        if len(characters) > 1:
            embed.add_field(name='Raw', value=ilcode(''.join(rawlist)), inline=False)
        await ctx.send(embed=embed)

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    @command(name='eval')
    @checks.is_co_owner()
    async def _eval(self, ctx, *, body: str):
        """Evaluates provided python code"""

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '__': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = (f'async def func():\n{textwrap.indent(body, "  ")}')

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()

            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except Exception: 
                pass

            if ret is None:
                if value:
                    await ctx.codeblock(value)
            else:
                self._last_result = ret
                await ctx.codeblock(f"{value}{ret}")

    @command(name='print')
    @checks.is_co_owner()
    async def _print(self, ctx, *, body: str):
        """Prints code snippets"""
        ctx.message.content = f'!eval print({body})'
        await ctx.bot.process_commands(ctx.message)

    @command()
    @checks.is_co_owner()
    async def runas(self, ctx, member: discord.Member, *, new_cmd):
        """Run a command as a different member."""
        if await ctx.bot.is_owner(member):
            await ctx.send(embed=make_embed(
                msg_type='error', title='No, you may not run as owner.'))
            return
        ctx.message.content = new_cmd
        ctx.message.author = member
        await ctx.bot.process_commands(ctx.message)

    @command(aliases=['src'])
    @commands.cooldown(rate=2, per=5, type=commands.BucketType.user)
    @checks.is_co_owner()
    async def source(self, ctx, *, command: BotCommand):
        """Displays the source code for a particular command.
        There is a per-user, 2 times per 5 seconds cooldown in order to prevent spam.
        """
        paginator = commands.Paginator(prefix='```py')
        for line in inspect.getsourcelines(command.callback)[0]:
            paginator.add_line(line.rstrip().replace('`', '\u200b`'))

        for p in paginator.pages:
            await ctx.send(p)

    @command()
    @checks.is_owner()
    async def clear_console(self, ctx):
        """Clear the console"""
        os.system('cls')
        await ctx.ok()

    @command()
    @checks.is_co_owner()
    async def guild(self, ctx, *, guild: Guild):
        """Lookup Guild info"""
        if guild:
            if guild.unavailable:
                embed = make_embed(
                    msg_type='error', title='Guild found, but unavailable!')
            else:
                embed = make_embed(
                    msg_type='info', thumbnail=guild.icon_url_as(format='png'))
                date_created = datetime.strftime(
                    guild.created_at, "UTC %Y/%m/%d %H:%M")
                basic_info = (
                    f"ID: {guild.id}\n"
                    f"Owner: {guild.owner}\n"
                    f"Created: {date_created}\n"
                    f"Region: {guild.region}\n")
                embed.add_field(
                    name=guild.name, value=basic_info, inline=False)
                stats_info = (
                    f"Members: {guild.member_count}\n"
                    f"Roles: {len(guild.roles)}\n"
                    f"Text Channels: {len(guild.text_channels)}\n"
                    f"Channel Categories: {len(guild.categories)}")
                embed.add_field(name='Stats', value=stats_info, inline=False)

                guild_perms = guild.me.guild_permissions
                req_perms = ctx.bot.req_perms
                perms_compare = guild_perms >= req_perms
                core_dir = ctx.bot.core_dir
                data_dir = os.path.join(core_dir, '..', 'data')
                data_file = 'permissions.json'
                perms_info = f"Value: {guild_perms.value}\n"
                perms_info += f"Meets Requirements: {perms_compare}\n"
                with open(os.path.join(data_dir, data_file), "r") as perm_json:
                    perm_dict = json.load(perm_json)

                for perm, bitshift in perm_dict.items():
                    if bool((req_perms.value >> bitshift) & 1):
                        if bool((guild_perms.value >> bitshift) & 1):
                            perms_info += ":white_small_square:  {}\n".format(perm)
                        else:
                            perms_info += ":black_small_square:  {}\n".format(perm)
                embed.add_field(name='Permissions', value=perms_info, inline=False)

                bot_list = [m for m in guild.members if m.bot]
                bot_info = f"Bots: {len(bot_list)}\n"
                if 1 <= len(bot_list) <= 20:
                    for bot in bot_list:
                        online = bot.status == discord.Status.online
                        status = "\U000025ab" if online else "\U000025aa"
                        bot_info += f"{status} {bot}\n"
                embed.add_field(name='Bots', value=bot_info, inline=False)

        else:
            embed = make_embed(msg_type='error', title='Guild not found')
        await ctx.send(embed=embed)

    @command(name='say')
    @checks.is_co_owner()
    async def _say(self, ctx, *, msg):
        """Repeat the given message."""
        await ctx.send(msg)

    @command()
    @checks.is_co_owner()
    async def emoji(self, ctx, emoji):
        emoji_obj = ctx.get.emoji(emoji)
        if not emoji_obj:
            emojis = {e.name:e for e in ctx.bot.emojis}
            match = get_match(list(emojis.keys()), emoji, score_cutoff=80)[0]
            emoji_obj = emojis[match] if match else None
        if not emoji_obj:
            return await ctx.error('Emoji not found.')
        await ctx.send(f"{emoji_obj}")
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

    @command()
    @checks.is_co_owner()
    async def check_perms(
            self, ctx, member_or_role: Multi(discord.Member, discord.Role),
            guild_or_channel: Multi(
                discord.Guild, discord.TextChannel, discord.VoiceChannel)=None):
        """Show permissions of a member or role for the guild and channel."""
        if guild_or_channel:
            if isinstance(guild_or_channel, discord.Guild):
                guild_perms = ctx.guild.me.guild_permissions
        else:
            guild_perms = ctx.guild.me.guild_permissions
            if isinstance(member_or_role, discord.Member):
                chan_perms = ctx.channel.permissions_for(member_or_role)
            else:
                return await ctx.send("Role Permissions aren't done yet.")

        req_perms = ctx.bot.req_perms
        g_perms_compare = guild_perms >= req_perms
        c_perms_compare = chan_perms >= req_perms
        core_dir = ctx.bot.core_dir
        data_dir = os.path.join(core_dir, '..', 'data')
        data_file = 'permissions.json'
        msg = f"**Guild:**\n{ctx.guild}\nID {ctx.guild.id}\n"
        msg += f"**Channel:**\n{ctx.channel}\nID {ctx.channel.id}\n"
        msg += "```py\nGuild     | Channel\n"
        msg += "----------|----------\n"
        msg += "{} | {}\n".format(guild_perms.value, chan_perms.value)
        msg += "{0:9} | {1}```".format(str(g_perms_compare), str(c_perms_compare))
        y_emj = ":white_small_square:"
        n_emj = ":black_small_square:"

        with open(os.path.join(data_dir, data_file), "r") as perm_json:
            perm_dict = json.load(perm_json)

        for perm, bitshift in perm_dict.items():
            if bool((req_perms.value >> bitshift) & 1):
                guild_bool = bool((guild_perms.value >> bitshift) & 1)
                channel_bool = bool((chan_perms.value >> bitshift) & 1)
                guild_e = y_emj if guild_bool else n_emj
                channel_e = y_emj if channel_bool else n_emj
                msg += f"{guild_e} {channel_e}  {perm}\n"

        try:
            if chan_perms.embed_links:
                embed = make_embed(
                    msg_type='info',
                    title=f'Permissions for {member_or_role}',
                    content=msg)
                await ctx.send(embed=embed)
            else:
                await ctx.send(msg)
        except discord.errors.Forbidden:
            embed = make_embed(
                msg_type='info',
                title=f'Permissions for {member_or_role}',
                content=msg)
            await ctx.author.send(embed=embed)

    @command()
    @checks.is_co_owner()
    async def msg(self, ctx, message_id: int, channel=None, guild=None):
        """Returns the raw content, embed and attachment data of a message."""
        if channel and channel.isdigit():
            channel = int(channel)
        if guild and guild.isdigit():
            guild = int(guild)
        msg = await ctx.get.message(message_id, channel=channel, guild=guild)

        if not msg:
            return await ctx.error("Message not found")

        details = [f"**Author:** {msg.author}"]
        if msg.author.bot:
            details.append("**Is Bot:** True")
        if msg.type != discord.MessageType.default:
            details.append(f"**Type:** {msg.type.name.title()}")
        if msg.guild:
            details.append(f"**Guild:** {msg.guild}")
        else:
            details.append(f"**DM User:** {msg.channel.recipient}")
        details.append(f"**Channel:** {msg.channel}")
        created = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
        details.append(f"**Created:** {created}")
        if msg.edited_at:
            edited = msg.edited_at.strftime("%Y-%m-%d %H:%M:%S")
            details.append(f"**Edited:** {edited}")
        mentions = []
        if msg.raw_mentions:
            mentions.append(
                f"**User Mentions:** {len(msg.raw_mentions)}")
        if msg.raw_role_mentions:
            mentions.append(
                f"**Role Mentions:** {len(msg.raw_role_mentions)}")
        if msg.raw_channel_mentions:
            mentions.append(
                f"**Channel Mentions:** {len(msg.raw_channel_mentions)}")
        reactions = []
        if msg.reactions:
            react_total = sum([r.count for r in msg.reactions])
            react_users = 0
            for reaction in msg.reactions:
                react_users += len(await reaction.users().flatten())
            reactions.append(
                f"**Total:** {react_total}"
            )
            reactions.append(
                f"**Unique:** {len(msg.reactions)}"
            )
            reactions.append(
                f"**Members:** {react_users}"
            )
        fields = {"DETAILS":'\n'.join(details)}
        if reactions:
            fields['REACTIONS'] = '\n'.join(reactions)
        if mentions:
            fields['MENTIONS'] = '\n'.join(mentions)
        await ctx.embed(f"Message {message_id}", fields=fields, inline=True)
        if msg.reactions:
            reaction_list = [f'{r} x {r.count}' for r in msg.reactions]
            await ctx.send(f"**Reactions:** {', '.join(reaction_list)}")
        if msg.content:
            await ctx.codeblock(msg.content, '', title='Content')
        for embed in msg.embeds:
            embed_json = json.dumps(embed.to_dict(), indent=4)
            await ctx.codeblock(embed_json, 'json', title='Embed')
        for att in msg.attachments:
            data = {a: getattr(att, a) for a in att.__slots__ if a[0] != '_'}
            att_json = json.dumps(data, indent=4)
            await ctx.codeblock(att_json, 'json', 'Attachment')

    @command()
    @checks.is_co_owner()
    async def sql(self, ctx, *, query):
        results = await ctx.bot.dbi.execute_transaction(query)
        if len(results) == 1:
            results = results[0]
        await ctx.codeblock(str(results), "")

    @group()
    @checks.is_owner()
    async def git(self, ctx):
        ctx.git_path = os.path.dirname(ctx.bot.eevee_dir)
        ctx.git_cmd = ['git']

    @git.command()
    async def pull(self, ctx):
        ctx.git_cmd.append('pull')

        p = Popen(ctx.git_cmd, stdout=PIPE, cwd=ctx.git_path)
        await ctx.codeblock(p.stdout.read().decode("utf-8"), syntax="")
