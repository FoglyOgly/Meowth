import textwrap

import discord
from discord.ext import commands

from meowth.utils import convert_to_bool, make_embed, bold
from meowth import settings

class Context(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.get = GetTools(self)
        if self.guild:
            guild_data = self.bot.guild_dict[self.guild.id]
            self.data = settings.GuildData(self, guild_data)

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

    async def error(self, title, details=None):
        """Quick send or build an error embed response"""
        return await self.embed(
            title=title, description=details, msg_type='error')

    async def success(self, title=None, details=None, send=True):
        """Quick send or build an info embed response."""
        if title:
            return await self.embed(title, details, msg_type='success', send=send)
        else:
            await self.ok()

    async def info(self, title, details=None, send=True):
        """Quick send or build an info embed response."""
        return await self.embed(title, details, msg_type='info', send=send)

    async def warning(self, title, details=None, send=True):
        """Quick send or build an info embed response."""
        return await self.embed(title, details, msg_type='warning', send=send)

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

    async def message(self, id, channel=None, guild=None):
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
        try:
            return await channel.fetch_message(id)
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
