import asyncio
import inspect
import itertools
import re

import discord

from . import make_embed

async def _can_run(cmd, ctx):
    try:
        return await cmd.can_run(ctx)
    except:
        return False

class CannotPaginate(Exception):
    pass

class Pagination:
    """Implements a paginator that queries the user for the
    pagination interface.

    If the user does not reply within 2 minutes then the pagination
    interface exits automatically.
    """
    def __init__(self, ctx, entries, *, per_page=12, show_entry_count=True,
                 title='Help', msg_type='help'):
        self.bot = ctx.bot
        self.entries = entries
        self.message = ctx.message
        self.channel = ctx.channel
        self.author = ctx.author
        self.per_page = per_page
        pages, left_over = divmod(len(self.entries), self.per_page)
        if left_over:
            pages += 1
        self.maximum_pages = pages
        self._mention = re.compile(r'<@\!?([0-9]{1,19})>')
        self.embed = make_embed(title=title, msg_type=msg_type)
        self.default_icon = self.embed.author.icon_url
        self.paginating = len(entries) > per_page
        self.show_entry_count = show_entry_count
        self.total = len(entries)
        self.reaction_emojis = [
            ('\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}',
             self.first_page),
            ('\N{BLACK LEFT-POINTING TRIANGLE}', self.previous_page),
            ('\N{BLACK RIGHT-POINTING TRIANGLE}', self.next_page),
            ('\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}',
             self.last_page),
            ('\N{BLACK SQUARE FOR STOP}', self.stop_pages),
            ('\N{LEDGER}', self.show_index),
        ]

        if ctx.guild is not None:
            self.permissions = self.channel.permissions_for(ctx.guild.me)
        else:
            self.permissions = self.channel.permissions_for(ctx.bot.user)

        if not self.permissions.embed_links:
            raise CannotPaginate('Bot does not have embed links permission.')

        if not self.permissions.send_messages:
            raise CannotPaginate('Bot cannot send messages.')

        if self.paginating:
            if not self.permissions.add_reactions:
                raise CannotPaginate(
                    'Bot does not have add reactions permission.')
            if not self.permissions.read_message_history:
                raise CannotPaginate(
                    'Bot does not have Read Message History permission.')

    def cleanup_prefix(self, bot, prefix):
        m = self._mention.match(prefix)
        if m:
            user = bot.get_user(int(m.group(1)))
            if user:
                return f'@{user.name} '
        return prefix

    def _command_signature(self, cmd):
        result = [cmd.qualified_name]
        if cmd.usage:
            result.append(cmd.usage)
            return ' '.join(result)

        params = cmd.clean_params
        if not params:
            return ' '.join(result)

        for name, param in params.items():
            if param.default is not param.empty:
                if isinstance(param.default, str):
                    should_print = param.default
                else:
                    should_print = param.default is not None
                if should_print:
                    result.append(f'[{name}={param.default!r}]')
                else:
                    result.append(f'[{name}]')
            elif param.kind == param.VAR_POSITIONAL:
                result.append(f'[{name}...]')
            else:
                result.append(f'<{name}>')

        return ' '.join(result)

    def get_page(self, page):
        self.embed.clear_fields()
        base = (page - 1) * self.per_page
        return self.entries[base:base + self.per_page]

    async def show_page(self, page, *, first=False):
        self.current_page = page
        entries = self.get_page(page)

        self.embed.clear_fields()
        self.embed.title = self.title
        self.embed.description = self.description
        if self.maximum_pages:
            if self.maximum_pages > 1:
                self.embed.set_footer(text=(
                    'Page {0}/{1} ({2} commands) | '
                    'Use {3}help <command> for more details.'
                ).format(page, self.maximum_pages, self.total, self.prefix))
            else:
                self.embed.set_footer(text=(
                    'Use {}help <command> for more details.').format(
                        self.prefix))
        else:
            self.embed.set_footer(text=(
                'Use {}help <command> for more details.').format(self.prefix))

        signature = self._command_signature

        requirements = getattr(self, 'requirements', [])
        if requirements:
            cmd_msg = ""
            for req in requirements:
                cmd_msg += (
                    "{}\n"
                ).format(req)
            self.embed.add_field(
                name="Requirements", value=f"{cmd_msg}", inline=False)

        if entries:
            cmd_msg = ""
            for entry in entries:
                cmd_msg += (
                    "{}\n"
                ).format(signature(entry))
            self.embed.add_field(
                name="Commands", value=f"{cmd_msg}", inline=False)

        if self.maximum_pages:
            self.embed.set_author(
                icon_url=self.default_icon,
                name=f'Help')

        if not self.paginating:
            return await self.channel.send(embed=self.embed)

        if not first:
            await self.message.edit(embed=self.embed)
            return

        self.message = await self.channel.send(embed=self.embed)
        for (reaction, __) in self.reaction_emojis:
            if self.maximum_pages == 2 and reaction in ('\u23ed', '\u23ee'):
                continue

            await self.message.add_reaction(reaction)

    async def checked_show_page(self, page):
        if page != 0 and page <= self.maximum_pages:
            await self.show_page(page)

    async def first_page(self):
        """goes to the first page"""
        await self.show_page(1)

    async def last_page(self):
        """goes to the last page"""
        await self.show_page(self.maximum_pages)

    async def next_page(self):
        """goes to the next page"""
        await self.checked_show_page(self.current_page + 1)

    async def previous_page(self):
        """goes to the previous page"""
        await self.checked_show_page(self.current_page - 1)

    async def show_current_page(self):
        if self.paginating:
            await self.show_page(self.current_page)

    async def numbered_page(self):
        """lets you type a page number to go to"""
        to_delete = []
        to_delete.append(
            await self.channel.send('What page do you want to go to?'))

        def message_check(m):
            return m.author == self.author and \
                   self.channel == m.channel and \
                   m.content.isdigit()

        try:
            msg = await self.bot.wait_for(
                'message', check=message_check, timeout=30.0)
        except asyncio.TimeoutError:
            to_delete.append(await self.channel.send('Took too long.'))
            await asyncio.sleep(5)
        else:
            page = int(msg.content)
            to_delete.append(msg)
            if page != 0 and page <= self.maximum_pages:
                await self.show_page(page)
            else:
                to_delete.append(
                    await self.channel.send(
                        f'Invalid page given. ({page}/{self.maximum_pages})'))
                await asyncio.sleep(5)

        try:
            await self.channel.delete_messages(to_delete)
        except Exception:
            pass

    async def show_index(self):
        """Shows Page Index"""

        self.embed.title = 'Page Index'
        self.embed.description = ''
        self.embed.clear_fields()

        pages = {}
        for i in range(1, self.maximum_pages + 1):
            base = (i - 1) * self.per_page
            page_entries = self.entries[base:base + self.per_page]
            page_title = f"{page_entries[0][0]} Commands"
            page_cmd_count = len(page_entries[0][2])
            pages_entry = pages.get(page_title)
            if pages_entry:
                pages[page_title]['end_page'] = i
                pages[page_title]['cmd_count'] = (
                    pages[page_title]['cmd_count']+page_cmd_count)
            else:
                pages[page_title] = {
                    'start_page' : i,
                    'cmd_count'  : page_cmd_count
                }

        for group, data in pages.items():
            cmd_count = data['cmd_count']
            start_page = data['start_page']
            end_page = data.get('end_page')
            if end_page:
                page_range = f"Pages {start_page} to {end_page}"
            else:
                page_range = f"Page {start_page}"
            self.embed.add_field(
                name=group,
                value=f"{page_range} ({cmd_count} Commands)")

        self.embed.set_footer(text=f'We were on page {self.current_page}.')
        await self.message.edit(embed=self.embed)

        self.reaction_emojis.append(
            ('\N{INPUT SYMBOL FOR NUMBERS}', self.numbered_page))
        await self.message.add_reaction('\N{INPUT SYMBOL FOR NUMBERS}')

        async def go_back_to_current_page():
            await asyncio.sleep(30.0)
            await self.show_current_page()
        self.bot.loop.create_task(go_back_to_current_page())

    async def stop_pages(self):
        """stops the interactive pagination session"""
        await self.message.delete()
        self.paginating = False

    def react_check(self, reaction, user):
        if user is None or user.id != self.author.id:
            return False

        if reaction.message.id != self.message.id:
            return False

        for (emoji, func) in self.reaction_emojis:
            if reaction.emoji == emoji:
                self.match = func
                return True
        return False

    async def paginate(self):
        """Actually paginate the entries and run the interactive loop if
        necessary."""
        first_page = self.show_page(1, first=True)
        if not self.paginating:
            await first_page
        else:
            self.bot.loop.create_task(first_page)

        while self.paginating:
            try:
                reaction, user = await self.bot.wait_for(
                    'reaction_add',
                    check=self.react_check,
                    timeout=120.0)
            except asyncio.TimeoutError:
                self.paginating = False
                try:
                    await self.message.clear_reactions()
                except:
                    pass
                finally:
                    break

            try:
                await self.message.remove_reaction(reaction, user)
            except:
                pass # can't remove it so don't bother doing so

            try:
                self.reaction_emojis.remove(
                    ('\N{INPUT SYMBOL FOR NUMBERS}', self.numbered_page))
                await self.message.remove_reaction(
                    '\N{INPUT SYMBOL FOR NUMBERS}', self.bot.user)
            except:
                pass # can't remove it so don't bother doing so

            await self.match()

    def get_bot_page(self, page):
        cog, description, commands = self.entries[page - 1]
        self.title = f'{cog} Commands'
        self.description = description
        return commands

    @staticmethod
    def _command_requirements(cmd):
        requirements = []
        for check in cmd.checks:
            name = getattr(check, '__qualname__', '')

            if name[:9] == "check_is_":
                name = name.replace("check_is_", "").replace("_", " ")
                name = f"{name} Only".title()
                requirements.append(name)
            elif '<locals>' in name:
                print('yes')
                name = name.split('.',1)[0]
                name = name.replace("_", " ").title()
                requirements.append(name)
            else:
                requirements.append(name)

        return requirements

    @classmethod
    async def from_category(cls, ctx, category):
        # get the commands
        entries = sorted(ctx.bot.commands, key=lambda c: c.name)

        # get only commands with categories
        entries = [
            cmd for cmd in entries if (
                getattr(cmd.callback, 'command_category', False))]
        entries = [
            cmd for cmd in entries if (
                cmd.callback.command_category == category)]

        # remove the ones we can't run
        entries = [cmd for cmd in entries if (
            await _can_run(cmd, ctx)) and not cmd.hidden]

        self = cls(ctx, entries)
        self.title = f'{category} Commands'

        categories = ctx.bot.config.command_categories
        cat_cfg = categories.get(category)

        self.description = cat_cfg.get("description")
        self.prefix = self.cleanup_prefix(ctx.bot, ctx.prefix)

        return self

    @classmethod
    async def from_cog(cls, ctx, cog):
        cog_name = cog.__class__.__name__

        # get the commands
        entries = sorted(
            ctx.bot.get_cog_commands(cog_name), key=lambda c: c.name)

        # remove the ones we can't run
        entries = [cmd for cmd in entries if (
            await _can_run(cmd, ctx)) and not cmd.hidden]

        self = cls(ctx, entries)
        self.title = f'{cog_name} Commands'
        self.description = inspect.getdoc(cog)
        self.prefix = self.cleanup_prefix(ctx.bot, ctx.prefix)

        return self

    @classmethod
    async def from_command(cls, ctx, command, **kwargs):
        try:
            entries = sorted(command.commands, key=lambda c: c.name)
        except AttributeError:
            entries = []
        else:
            entries = [cmd for cmd in entries if (
                await _can_run(cmd, ctx)) and not cmd.hidden]

        self = cls(ctx, entries, **kwargs)
        self.title = command.signature

        if command.description:
            self.description = f'{command.description}\n\n{command.help}'
        else:
            self.description = command.help or 'No help given.'

        if command.checks:
            self.requirements = self._command_requirements(command)

        self.prefix = self.cleanup_prefix(ctx.bot, ctx.prefix)
        return self

    @classmethod
    async def from_bot(cls, ctx):

        categories = ctx.bot.config.command_categories

        def sortkey(cmd):
            category = getattr(cmd.callback, 'command_category', None)
            cat_cfg = categories.get(category)
            category = cat_cfg["index"] if cat_cfg else category
            return category or cmd.cog_name or '\u200bMisc'

        def groupkey(cmd):
            category = getattr(cmd.callback, 'command_category', None)
            return category or cmd.cog_name or '\u200bMisc'

        entries = sorted(ctx.bot.commands, key=sortkey)
        nested_pages = []
        per_page = 15

        for cog, commands in itertools.groupby(entries, key=groupkey):
            plausible = [cmd for cmd in commands if (
                await _can_run(cmd, ctx)) and not cmd.hidden]
            if len(plausible) == 0:
                continue
            plausible = sorted(plausible, key=lambda x: x.name)
            description = ctx.bot.get_cog(cog)
            if description is None:
                cat_cfg = categories.get(cog)
                if cat_cfg:
                    description = cat_cfg.get("description")
                else:
                    description = discord.Embed.Empty
            else:
                description = (
                    inspect.getdoc(description) or discord.Embed.Empty)

            nested_pages.extend(
                (cog, description, plausible[i:i + per_page]) for i in range(
                    0, len(plausible), per_page))

        # this forces the pagination session
        self = cls(ctx, nested_pages, per_page=1)
        self.prefix = self.cleanup_prefix(ctx.bot, ctx.prefix)

        # swap the get_page implementation
        self.get_page = self.get_bot_page
        self._is_bot = True

        # replace the actual total
        self.total = sum(len(o) for __, __, o in nested_pages)
        return self

        cls.reaction_emojis.append(
            ('\N{INPUT SYMBOL FOR NUMBERS}', self.numbered_page))
        await self.message.add_reaction('\N{INPUT SYMBOL FOR NUMBERS}')
