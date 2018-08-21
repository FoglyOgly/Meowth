import logging
import json

import asyncpg

from discord.ext.commands import when_mentioned_or

from .schema import Table, Query, Insert, Update, Schema
from .tables import core_table_sqls
from . import sqltypes

logger = logging.getLogger('meowth.dbi')

async def init_conn(conn):
    await conn.set_type_codec("jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog")
    await conn.set_type_codec("json", encoder=json.dumps, decoder=json.loads, schema="pg_catalog")

class DatabaseInterface:
    """Get, Create and Edit data in the connected database."""

    def __init__(self,
                 password,
                 hostname='localhost',
                 username='meowth',
                 database="meowth",
                 port=5432):
        self.loop = None
        self.dsn = "postgres://{}:{}@{}:{}/{}".format(
            username, password, hostname, port, database)
        self.pool = None
        self.prefix_conn = None
        self.prefix_stmt = None
        self.settings_conn = None
        self.settings_stmt = None
        self.types = sqltypes

    async def start(self, loop=None):
        if loop:
            self.loop = loop
        self.pool = await asyncpg.create_pool(
            self.dsn, loop=loop, init=init_conn)
        await self.prepare()

    async def recreate_pool(self):
        logger.warning(f'Re-creating closed database pool.')
        self.pool = await asyncpg.create_pool(
            self.dsn, loop=self.loop, init=init_conn)

    async def prepare(self):
        # ensure tables exists
        await self.core_tables_exist()

        # guild prefix callable statement
        self.prefix_conn = await self.pool.acquire()
        prefix_sql = 'SELECT prefix FROM prefix WHERE guild_id=$1;'
        self.prefix_stmt = await self.prefix_conn.prepare(prefix_sql)

        # guild settings statement
        self.settings_conn = await self.pool.acquire()
        settings_sql = ('SELECT config_value FROM guild_config '
                        'WHERE guild_id=$1 AND config_name=$2;')
        self.settings_stmt = await self.settings_conn.prepare(settings_sql)

    async def core_tables_exist(self):
        core_sql = core_table_sqls()
        for k, v in core_sql.items():
            table_exists = await self.table(k).exists()
            if not table_exists:
                logger.warning(f'Core table {k} not found. Creating...')
                await self.execute_transaction(v)
                logger.warning(f'Core table {k} created.')

    async def stop(self):
        conns = (self.prefix_conn, self.settings_conn)
        for c in conns:
            if c:
                await self.pool.release(c)
        if self.pool:
            await self.pool.close()
            self.pool.terminate()

    async def prefix_manager(self, bot, message):
        """Returns the bot prefixes by context.

        Returns a guild-specific prefix if it has been set. If not,
        returns the default prefix.

        Uses a prepared statement to ensure caching.
        """
        default_prefix = bot.default_prefix
        if message.guild:
            g_prefix = await self.prefix_stmt.fetchval(message.guild.id)
            prefix = g_prefix if g_prefix else default_prefix
        else:
            prefix = default_prefix

        return when_mentioned_or(prefix)(bot, message)

    async def execute_query(self, query, *query_args):
        result = []
        try:
            async with self.pool.acquire() as conn:
                stmt = await conn.prepare(query)
                rcrds = await stmt.fetch(*query_args)
                for rcrd in rcrds:
                    result.append(rcrd)
            return result
        except asyncpg.exceptions.InterfaceError as e:
            logger.error(f'Exception {type(e)}: {e}')
            await self.recreate_pool()
            return await self.execute_query(query, *query_args)

    async def execute_transaction(self, query, *query_args):
        result = []
        try:
            async with self.pool.acquire() as conn:
                stmt = await conn.prepare(query)

                if any(isinstance(x, (set, tuple)) for x in query_args):
                    async with conn.transaction():
                        for query_arg in query_args:
                            async for rcrd in stmt.cursor(*query_arg):
                                result.append(rcrd)
                else:
                    async with conn.transaction():
                        async for rcrd in stmt.cursor(*query_args):
                            result.append(rcrd)
                return result
        except asyncpg.exceptions.InterfaceError:
            await self.recreate_pool()
            return await self.execute_query(query, *query_args)

    async def create_table(self, name, columns: list, *, primaries=None):
        """Create table."""
        return await Table(self, name).create(columns, primaries=primaries)

    def table(self, name):
        return Table(name, self)

    def query(self, *tables):
        tables = [Table(self, name) for name in tables]
        return Query(self, tables)

    def insert(self, table):
        return Insert(self, table)

    def update(self, table):
        return Update(self, table)

    async def tables(self):
        table = self.table('information_schema.tables')
        table.query('table_name')
        table.query.where(table_schema='public')
        table.query.order_by('table_name')
        return await table.query.get()
    
    def schema(self, name):
        return Schema(self, name)
