from meowth import group, Cog


class GuildLanguages:
    def __init__(self, dbi):
        self.data = dict()
        self.dbi = dbi

    def __getitem__(self, key):
        return self.data[key]

    async def get(self, guild_id):
        try:
            return self.data[guild_id]
        except KeyError:
            query = self.dbi.table('guild_config').query('config_value')
            query.where(guild_id=guild_id, config_name='language')
            result = await query.get_value()
            return int(result) if result else None

    async def assign(self, guild_id, language_id):
        table = self.dbi.table('guild_config').insert('config_value')
        table.insert(
            guild_id=guild_id,
            config_name='language',
            config_value=str(language_id))
        await table.insert.commit(do_update=True)
        self.data[guild_id] = language_id

    async def build_cache(self):
        table = self.dbi.table('guild_config')
        query = table.query('guild_id', 'config_value')
        query.where(config_name='language')
        result = await query.get()
        if not result:
            raise OSError
        new_data = {r['guild_id']:int(r['config_value']) for r in result}
        self.data = new_data
        return self.data

class I18n(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.cache_guild_languages())
        self._lang_data = None

    @property
    def lang_table(self):
        return self.bot.dbi.table('languages')

    async def get_language_data(self, language_id=None, refresh=False):
        if not self._lang_data or refresh:
            query = self.lang_table.query
            results = await query.get()
            data = dict()

            for r in results:
                data[r['language_id']] = {
                    'iso639':r['iso639'],
                    'iso3166':r['iso3166'],
                    'identifier':r['identifier'],
                    'official':r['official']
                }

            self._lang_data = data

        if language_id:
            try:
                return self._lang_data[language_id]
            except KeyError:
                return None

        return self._lang_data

    async def cache_guild_languages(self):
        if not hasattr(self.bot, 'guild_languages'):
            self.bot.guild_languages = GuildLanguages(self.bot.dbi)
        return await self.bot.guild_languages.build_cache()

    @group(invoke_without_command=True, alias=['lang'])
    async def language(self, ctx):
        """Returns the current language setting."""
        if not ctx.language:
            await ctx.error("Context attribute 'language' missing.")

        # test with ID only first
        await ctx.info("Your current language is ID{ctx.language}")
