import asyncio
import os
import sys
import json
from datetime import timezone
import logging
from logging import handlers

import asyncpg
import discord

from meowth.utils import snowflake

get_id = snowflake.create()

LOGGERS = ('meowth_logs', 'discord_logs')

module_logger = logging.getLogger('meowth.logger')

def init_logger(bot, debug_flag=False):

    # set root logger level
    logging.getLogger().setLevel(logging.DEBUG)

    # setup discord logger
    discord_log = logging.getLogger("discord")
    discord_log.setLevel(logging.INFO)

    # setup bot logger
    meowth_log = logging.getLogger("meowth")

    # setup log directory
    log_path = os.path.join(bot.data_dir, 'logs')
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    # file handler factory
    def create_fh(file_name):
        fh_path = os.path.join(log_path, file_name)
        return handlers.RotatingFileHandler(
            filename=fh_path, encoding='utf-8', mode='a',
            maxBytes=400000, backupCount=20)

    # set bot log formatting
    log_format = logging.Formatter(
        '%(asctime)s %(name)s %(levelname)s %(module)s %(funcName)s %(lineno)d: '
        '%(message)s',
        datefmt="[%d/%m/%Y %H:%M]")

    # create file handlers
    meowth_fh = create_fh('meowth.log')
    meowth_fh.setLevel(logging.INFO)
    meowth_fh.setFormatter(log_format)
    meowth_log.addHandler(meowth_fh)
    discord_fh = create_fh('discord.log')
    discord_fh.setLevel(logging.INFO)
    discord_fh.setFormatter(log_format)
    discord_log.addHandler(discord_fh)

    # create console handler
    console_std = sys.stdout if debug_flag else sys.stderr
    meowth_console = logging.StreamHandler(console_std)
    meowth_console.setLevel(logging.INFO if debug_flag else logging.ERROR)
    meowth_console.setFormatter(log_format)
    meowth_log.addHandler(meowth_console)
    discord_console = logging.StreamHandler(console_std)
    discord_console.setLevel(logging.ERROR)
    discord_console.setFormatter(log_format)
    discord_log.addHandler(discord_console)

    # create db handler
    meowth_db = DBLogHandler(bot, 'meowth_logs')
    bot.log_meowth_db = meowth_db
    meowth_log.addHandler(meowth_db)
    discord_db = DBLogHandler(bot, 'discord_logs')
    discord_log.addHandler(discord_db)

    bot.add_cog(ActivityLogging(bot))

    return meowth_log

class DBLogHandler(logging.Handler):
    def __init__(self, bot, log_name: str, level=logging.INFO):
        if log_name not in LOGGERS:
            raise RuntimeError(f'Unknown Log Name: {log_name}')
        self.bot = bot
        self.log_name = log_name
        self.logger = module_logger.getChild('DBLogHandler')
        super().__init__(level=level)

    def emit(self, record):
        record_id = next(get_id)
        asyncio.run_coroutine_threadsafe(
            self.submit_log(record_id, record), self.bot.loop)

    async def submit_log(self, log_id, record):
        data = dict(log_id=log_id,
                    created=record.created,
                    logger_name=str(record.name),
                    level_name=str(record.levelname),
                    file_path=str(record.pathname),
                    module=str(record.module),
                    func_name=str(record.funcName),
                    line_no=record.lineno,
                    message=str(record.message),
                    traceback=str(record.exc_info))
        try:
            table = self.bot.dbi.table(self.log_name)
            table.insert(**data)
            await table.insert.commit()
        except asyncpg.PostgresError as e:
            self.logger.exception(type(e).__name__, exc_info=e)

class ActivityLogging:
    def __init__(self, bot):
        self.bot = bot
        self.logger = module_logger.getChild('ActivityLogging')

    async def on_message(self, msg):
        sent = int(msg.created_at.replace(tzinfo=timezone.utc).timestamp())
        guild_id = msg.guild.id if msg.guild else None
        embeds = [json.dumps(e.to_dict()) for e in msg.embeds]
        attachments = [a.url for a in msg.attachments]
        data = dict(message_id=msg.id, sent=sent, is_edit=False, deleted=False,
                    author_id=msg.author.id, channel_id=msg.channel.id,
                    guild_id=guild_id, content=msg.content,
                    clean_content=msg.clean_content, embeds=embeds,
                    webhook_id=msg.webhook_id, attachments=attachments)
        try:
            table = self.bot.dbi.table('discord_messages')
            table.insert(**data)
            await table.insert.commit()
        except asyncpg.PostgresError as e:
            self.logger.exception(type(e).__name__, exc_info=e)

    async def on_raw_message_delete(self, payload):
        try:
            table = self.bot.dbi.table('discord_messages')
            table.update(deleted=True)
            table.update.where(message_id=payload.message_id)
            await table.update.commit()
        except asyncpg.PostgresError as e:
            self.logger.exception(type(e).__name__, exc_info=e)

    async def on_raw_bulk_message_delete(self, payload):
        try:
            table = self.bot.dbi.table('discord_messages')
            table.update(deleted=True)
            m_ids = payload.message_ids
            conditions = [table['message_id'] == m_id for m_id in m_ids]
            table.update.where(conditions)
            await table.update.commit()
        except asyncpg.PostgresError as e:
            self.logger.exception(type(e).__name__, exc_info=e)

    async def on_message_edit(self, before, after):
        if before.type == discord.MessageType.call:
            return
        if before.content == after.content:
            return
        msg = after
        sent = int(msg.edited_at.replace(tzinfo=timezone.utc).timestamp())
        guild_id = msg.guild.id if msg.guild else None
        embeds = [json.dumps(e.to_dict()) for e in msg.embeds]
        attachments = [a.url for a in msg.attachments]
        data = dict(message_id=msg.id, sent=sent, is_edit=True, deleted=False,
                    author_id=msg.author.id, channel_id=msg.channel.id,
                    guild_id=guild_id, content=msg.content,
                    clean_content=msg.clean_content, embeds=embeds,
                    webhook_id=msg.webhook_id, attachments=attachments)
        try:
            table = self.bot.dbi.table('discord_messages')
            table.insert(**data)
            # update existing data
            table.insert.primaries('message_id', 'sent')
            await table.insert.commit(do_update=True)
        except asyncpg.PostgresError as e:
            self.logger.exception(type(e).__name__, exc_info=e)

    async def on_command(self, ctx):
        created = ctx.message.created_at
        sent = int(created.replace(tzinfo=timezone.utc).timestamp())
        guild = ctx.guild.id if ctx.guild else None
        cog = ctx.cog.__class__.__name__ if ctx.cog else None
        isc = ctx.invoked_subcommand.name if ctx.invoked_subcommand else None
        cmd = ctx.command.name if ctx.command else None
        data = dict(message_id=ctx.message.id, sent=sent,
                    author_id=ctx.author.id, channel_id=ctx.channel.id,
                    guild_id=guild, prefix=ctx.prefix,
                    command=cmd, invoked_with=ctx.invoked_with,
                    invoked_subcommand=isc,
                    subcommand_passed=ctx.subcommand_passed,
                    command_failed=ctx.command_failed, cog=cog)
        try:
            table = self.bot.dbi.table('command_log')
            table.insert(**data)
            table.insert.primaries('message_id', 'sent')
            # ignore conflicts
            await table.insert.commit(do_update=False)
        except asyncpg.PostgresError as e:
            self.logger.exception(type(e).__name__, exc_info=e)
