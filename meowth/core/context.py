import asyncio
import textwrap
import gettext

from aiocontextvars import ContextVar

import discord
from discord.abc import Messageable
from discord.ext import commands

from meowth.core import checks
from meowth.utils import convert_to_bool, make_embed, bold

cvar = ContextVar('bot')

def ctx_setup(loop):
    import builtins
    builtins.__dict__['_'] = use_current_gettext
    builtins.__dict__['get_ctx'] = cvar.get
    builtins.__dict__['__cvar__'] = cvar

def use_current_gettext(*args, **kwargs):
    return cvar.get().get_text(*args, **kwargs)

class Context(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dbi = self.bot.dbi
        self.data = self.bot.data
        if self.guild:
            self.guild_dm = self.bot.data.guild(self.guild.id)
            self.setting = self.guild_dm.settings
        self.get = GetTools(self)
        self.language = 'en'

    def get_text(self, content):
        return content

    def language(self):
        try:
            return self.bot.guild_languages[self.guild.id]
        except (AttributeError, KeyError):
            return None

    async def codeblock(self, contents, syntax="py", send=True, title=None):
        paginator = commands.Paginator(prefix=f'```{syntax}', max_size=1900)
        for line in contents.split('\n'):
            for wrapline in textwrap.wrap(line, width=80):
                paginator.add_line(wrapline.rstrip().replace('`', '\u200b`'))
        if not send:
            return paginator.pages
        for page in paginator.pages:
            if page == paginator.pages[0] and title:
                page = bold(title)+"\n"+page
            await self.send(page)

    async def ok(self):
        await self.message.add_reaction('\u2705')

    async def no(self):
        await self.message.add_reaction('\u274e')

    async def is_co_owner(self):
        return await checks.check_is_co_owner(self)

    @property
    def cog_name(self):
        return self.command.instance.__class__.__name__

    async def admin_role(self):
        role_id = await self.setting('AdminRole')
        role = discord.utils.get(self.guild.roles, id=int(role_id))
        return role

    async def mod_role(self):
        role_id = await self.setting('ModRole')
        role = discord.utils.get(self.guild.roles, id=int(role_id))
        return role

    async def cog_enabled(self, value: bool = None, *, clear=False):
        if clear:
            return await self.setting(self.cog_name+'Enabled', delete=True)
        elif value is not None:
            return await self.setting(self.cog_name+'Enabled', value)
        else:
            value = await self.setting(self.cog_name+'Enabled')
            if value is not None:
                value = convert_to_bool(value)
            return value

    async def error(self, title, details=None, log_level='warning',
                    exc: Exception = None, **options):
        """Submit an error to log and reply with error message"""
        msg = await self.embed(
            title=title, description=details, msg_type='error', **options)
        if exc:
            raise exc(details)
        else:
            log = getattr(self.bot.logger, log_level, 'warning')
            log_msg = f"Error in command '{self.command}': {title}"
            if details:
                log_msg += f" - {details}"
            log(log_msg)
        return msg

    async def success(self, title=None, details=None, send=True, **options):
        """Quick send or build an info embed response."""
        if title:
            return await self.embed(
                title, details, msg_type='success', send=send, **options)
        else:
            await self.ok()

    async def info(self, title, details=None, send=True, **options):
        """Quick send or build an info embed response."""
        return await self.embed(
            title, details, msg_type='info', send=send, **options)

    async def warning(self, title, details=None, send=True, **options):
        """Quick send or build an info embed response."""
        return await self.embed(
            title, details, msg_type='warning', send=send, **options)

    async def embed(self, title, description=None, plain_msg='', *,
                    msg_type=None, title_url=None, colour=None,
                    icon=None, thumbnail='', image='', fields: dict = None,
                    footer=None, footer_icon=None, send=True, inline=False):
        """Send or build an embed using context details."""
        embed = make_embed(title=title, content=description, msg_type=msg_type,
                           title_url=title_url, msg_colour=colour, icon=icon,
                           thumbnail=thumbnail, image=image, guild=self.guild)
        if fields:
            for key, value in fields.items():
                ilf = inline
                if not isinstance(value, str):
                    ilf = value[0]
                    value = value[1]
                embed.add_field(name=key, value=value, inline=ilf)
        if footer:
            footer = {'text':footer}
            if footer_icon:
                footer['icon_url'] = footer_icon
            embed.set_footer(**footer)

        if not send:
            return embed

        return await self.send(plain_msg, embed=embed)

    async def ask(self, message, *, timeout: float = 30.0,
                  autodelete: bool = True, options: list = None,
                  author_id: int = None, destination: Messageable = None,
                  react_dict: dict = None):
        """An interactive reaction confirmation dialog.

        Parameters
        -----------
        message: Union[str, discord.Embed]
            The message to show along with the prompt.
        timeout: float
            How long to wait before returning. Default is 30.
        autodelete: bool
            Whether to delete the confirmation message after we're done.
            Default is True.
        options: Optional[list]
            What react options are valid, limited to react_dict keys.
        author_id: Optional[int]
            The member who should respond to the prompt. Defaults to the author of the
            Context's message.
        destination: Optional[discord.abc.Messageable]
            Where the prompt should be sent. Defaults to invoked channel.
        react_dict: Optional[dict]
            Custom react dict. Overrides existing one.

        Returns
        --------
        Optional[Union[bool, str, int]]
            ``1-5`` if selected numbered option,
            ``A-E`` if selected lettered option,
            ``True`` if confirm,
            ``False`` if deny,
            ``None`` if timeout

        If a custom react_dict is provide, it overrides default.
        """
        custom_reacts = bool(react_dict)
        if not custom_reacts:
            cek = '\u20e3'
            react_dict = {
                "1" : {
                    "emoji":"1"+cek,
                    "value":1
                },
                "2" : {
                    "emoji":"2"+cek,
                    "value":2
                },
                "3" : {
                    "emoji":"3"+cek,
                    "value":3
                },
                "4" : {
                    "emoji":"4"+cek,
                    "value":4
                },
                "5" : {
                    "emoji":"5"+cek,
                    "value":5
                },
                "a" : {
                    "emoji":"\U0001f1e6",
                    "value":"a"
                },
                "b" : {
                    "emoji":"\U0001f1e7",
                    "value":"b"
                },
                "c" : {
                    "emoji":"\U0001f1e8",
                    "value":"c"
                },
                "d" : {
                    "emoji":"\U0001f1e9",
                    "value":"d"
                },
                "e" : {
                    "emoji":"\U0001f1ea",
                    "value":"e"
                },
                "true" : {
                    "emoji":"\u2705",
                    "value":True
                },
                "false" : {
                    "emoji":"\u274e",
                    "value":False
                },
                "cancel" : {
                    "emoji":"\U0001f6ab",
                    "value":None
                },
            }

        destination = destination or self.channel

        emoji_list = []
        emoji_lookup = {}
        for key, item in react_dict.items():
            if not options and not custom_reacts:
                options = ['true', 'false']
            if options:
                if key not in options:
                    continue
            emoji_lookup[item['emoji']] = item['value']
            emoji_list.append(item['emoji'])

        is_valid_emoji = frozenset(emoji_list).__contains__

        if isinstance(message, discord.Embed):
            msg = await destination.send(embed=message)
        else:
            msg = await destination.send(message)

        author_id = author_id or self.author.id

        def check(emoji, message_id, channel_id, user_id):
            if message_id != msg.id or user_id != author_id:
                return False
            return is_valid_emoji(str(emoji))

        for emoji in emoji_list:
            # str cast in case of _ProxyEmoji
            if not isinstance(emoji, discord.Emoji):
                emoji = str(emoji)
            await msg.add_reaction(emoji)

        try:
            emoji, *__, = await self.bot.wait_for('raw_reaction_add', check=check, timeout=timeout)
            # str cast in case of _ProxyEmojis
            return emoji_lookup[str(emoji)]
        except asyncio.TimeoutError:
            return None
        finally:
            if autodelete:
                await msg.delete()

class GetTools:
    """Tools to easily get discord objects via Context."""

    def __init__(self, ctx):
        self.ctx = ctx
        self.get = discord.utils.get

    async def user(self, search_term):
        """Get a user by ID or name.

        If an ID is provided, it will return a user even if they don't share a
        guild with the bot.

        Parameters
        -----------
        search_term: :class:`id` or :class:`str`
            The user ID, name or name with discriminator

        Returns
        --------
        :class:`discord.User` or :obj:`None`
            Returns the `User` or `None` if not found.
        """
        bot = self.ctx.bot
        if isinstance(search_term, int):
            user = bot.get_user(search_term)
            if user:
                return user
            try:
                user = await bot.get_user_info(search_term)
            except discord.NotFound:
                return None
            else:
                return user
        if isinstance(search_term, str):
            member = self.get(bot.users, name=search_term)
            if not member:
                members = {str(m) : m for m in bot.users}
                member = members.get(search_term, None)
            return member

    async def message(self, id, channel=None, guild=None, no_cache=False):
        """Get a message from the current or specified channels.

        Parameters
        -----------
        id: :class:`int`
            The message ID
        channel: :class:`discord.TextChannel`, :obj:str or :obj:int, optional
            Specify channel other than the current one. Accepts a discord
            `TextChannel`, channel ID as `int`, or channel name as `str`.

        Returns
        --------
        :class:`discord.Message` or :obj:`None`
            Returns the Message or None if not found.
        """
        if isinstance(channel, (int, str)):
            if isinstance(guild, (int, str)):
                guild = self.guild(guild)
                if not guild:
                    return None
            channel = self.channel(channel, guild=guild)
            if not guild:
                return None
        channel = channel or self.ctx.channel
        if not no_cache:
            msg = self.get(channel._state._messages, id=id)
            if msg:
                return msg
        try:
            return await channel.get_message(id)
        except discord.NotFound:
            return None

    def channel(self, search_term, guild=None):
        """Get a channel from the current or specified guild.

        Parameters
        -----------
        search_term: :class:`id` or :class:`str`
            The channel ID or channel name
        guild: :class:`discord.Guild`, :obj:`int` or :obj:`str`, optional
            Specify guild other than the current one. Accepts a discord
            `Guild`, channel ID as `int`, or channel name as `str`.

        Returns
        --------
        :class:`discord.abc.GuildChannel` or :obj:`None`
            Returns the `Channel` or `None` if not found.
        """
        if isinstance(guild, (int, str)):
            guild = self.guild(guild)
            if not guild:
                return None
        guild = guild or self.ctx.guild
        if not guild:
            return None
        if isinstance(search_term, int):
            return guild.get_channel(search_term)
        if isinstance(search_term, str):
            return self.get(guild.channels, name=search_term)

    def text_channel(self, search_term, guild=None):
        """Get a text channel from the current or specified guild.

        Parameters
        -----------
        search_term: :class:`id` or :class:`str`
            The channel ID or channel name
        guild: :class:`discord.Guild`, :obj:`int` or :obj:`str`, optional
            Specify guild other than the current one. Accepts a discord
            `Guild`, channel ID as `int`, or channel name as `str`.

        Returns
        --------
        :class:`discord.TextChannel` or :obj:`None`
            Returns the `TextChannel` or `None` if not found.
        """
        if isinstance(guild, (int, str)):
            guild = self.guild(guild)
            if not guild:
                return None
        guild = guild or self.ctx.guild
        if not guild:
            return None
        if isinstance(search_term, int):
            channel = guild.get_channel(search_term)
            if isinstance(channel, discord.TextChannel):
                return channel
            return None
        if isinstance(search_term, str):
            return self.get(guild.text_channels, name=search_term)

    def voice_channel(self, search_term, guild=None):
        """Get a voice channel from the current or specified guild.

        Parameters
        -----------
        search_term: :class:`id` or :class:`str`
            The channel ID or channel name
        guild: :class:`discord.Guild`, :obj:`int` or :obj:`str`, optional
            Specify guild other than the current one. Accepts a discord
            `Guild`, channel ID as `int`, or channel name as `str`.

        Returns
        --------
        :class:`discord.VoiceChannel` or :obj:`None`
            Returns the `VoiceChannel` or `None` if not found.
        """
        if isinstance(guild, (int, str)):
            guild = self.guild(guild)
            if not guild:
                return None
        guild = guild or self.ctx.guild
        if not guild:
            return None
        if isinstance(search_term, int):
            return self.get(guild.voice_channels, id=search_term)
        if isinstance(search_term, str):
            return self.get(guild.voice_channels, name=search_term)

    def category(self, search_term, guild=None):
        """Get a channel category from the current or specified guild.

        Parameters
        -----------
        search_term: :class:`id` or :class:`str`
            The category ID or category name
        guild: :class:`discord.Guild`, :obj:`int` or :obj:`str`, optional
            Specify guild other than the current one. Accepts a discord
            `Guild`, channel ID as `int`, or channel name as `str`.

        Returns
        --------
        :class:`discord.CategoryChannel` or :obj:`None`
            Returns the `CategoryChannel` or `None` if not found.
        """
        if isinstance(guild, (int, str)):
            guild = self.guild(guild)
            if not guild:
                return None
        guild = guild or self.ctx.guild
        if not guild:
            return None
        if isinstance(search_term, int):
            return self.get(guild.categories, id=search_term)
        if isinstance(search_term, str):
            return self.get(guild.categories, name=search_term)

    def member(self, search_term, guild=None):
        """Get a member from the current or specified guild.

        Parameters
        -----------
        search_term: :class:`id` or :class:`str`
            The member ID, name, nickname or full name with discriminator
        guild: :class:`discord.Guild`, :obj:`int` or :obj:`str`, optional
            Specify guild other than the current one. Accepts a discord
            `Guild`, channel ID as `int`, or channel name as `str`.

        Returns
        --------
        :class:`discord.Member` or :obj:`None`
            Returns the `Member` or `None` if not found.
        """
        if isinstance(guild, (int, str)):
            guild = self.guild(guild)
            if not guild:
                return None
        guild = guild or self.ctx.guild
        if not guild:
            return None
        if isinstance(search_term, int):
            return guild.get_member(search_term)
        if isinstance(search_term, str):
            member = self.get(guild.members, name=search_term)
            if not member:
                member = self.get(guild.members, nick=search_term)
            if not member:
                members = {str(m) : m for m in guild.members}
                member = members.get(search_term, None)
            return member

    def role(self, search_term, guild=None):
        """Get a role from the current or specified guild.

        Parameters
        -----------
        search_term: :class:`id` or :class:`str`
            The role ID or name
        guild: :class:`discord.Guild`, :obj:`int` or :obj:`str`, optional
            Specify guild other than the current one. Accepts a discord
            `Guild`, channel ID as `int`, or channel name as `str`.

        Returns
        --------
        :class:`discord.Role` or :obj:`None`
            Returns the `Role` or `None` if not found.
        """
        if isinstance(guild, (int, str)):
            guild = self.guild(guild)
            if not guild:
                return None
        guild = guild or self.ctx.guild
        if not guild:
            return None
        if isinstance(search_term, int):
            return self.get(guild.roles, id=search_term)
        if isinstance(search_term, str):
            return self.get(guild.roles, name=search_term)

    def guild(self, search_term):
        """Get a guild by ID or fuzzymatched name.

        Parameters
        -----------
        search_term: :class:`id` or :class:`str`
            The guild ID or name

        Returns
        --------
        :class:`discord.Guild` or :obj:`None`
            Returns the `Guild` or `None` if not found.
        """
        bot = self.ctx.bot
        if isinstance(search_term, int):
            return bot.get_guild(search_term)
        if isinstance(search_term, str):
            return bot.find_guild(name=search_term)

    def emoji(self, search_term):
        """Get an emoji by ID or name.

        Parameters
        -----------
        search_term: :class:`id` or :class:`str`
            The emoji ID or name

        Returns
        --------
        :class:`discord.Emoji` or :obj:`None`
            Returns the `Emoji` or `None` if not found.
        """
        bot = self.ctx.bot
        if isinstance(search_term, int):
            return bot.get_emoji(search_term)
        if isinstance(search_term, str):
            return self.get(bot.emojis, name=search_term)
