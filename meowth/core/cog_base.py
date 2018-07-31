import importlib
import logging

from meowth.utils import Map


class Cog:
    """Base Class for Cogs to inherit in order to automate Cog setup.

    Defined ``__new__`` method ensures the Cog class is initialised
    without explicitly calling ``super``. Works with multiple
    inheritances.

    Base __init__ automatically assigns ``self.bot`` attribute, sets up the
    logger while assigning it to ``self.logger`` attribute, and detects,
    creates if necessary and assigns the cog packages database tables to
    the ``self.tables`` attribute.
    """

    _is_base = True

    def __new__(cls, bot, *args, **kwargs):
        instance = super().__new__(cls, *args, **kwargs)
        def run_cog_init(klass):
            for base in klass.__bases__:
                if base is object:
                    return
                elif base._is_base:
                    base.__init__(instance, bot)
                else:
                    run_cog_init(base)
        run_cog_init(instance.__class__)
        return instance

    def __init_subclass__(cls):
        cls._is_base = False

    def __init__(self, bot):
        self.bot = bot
        self.tables = None
        module = self.__class__.__module__
        cog = self.__class__.__name__
        log_name = f"{module}.{cog}"
        self.logger = logging.getLogger(log_name)
        self._check_tables_module()

    def _check_tables_module(self):
        this_module = self.__class__.__module__
        try:
            tbl_mod = importlib.import_module('..tables', this_module)
        except ModuleNotFoundError:
            pass
        else:
            if not hasattr(tbl_mod, 'setup'):
                del tbl_mod
            else:
                self.bot.loop.create_task(self._table_setup(tbl_mod))

    async def _table_setup(self, table_module):
        cog_name = self.__class__.__name__
        cog_tables = table_module.setup(self.bot)
        if not isinstance(cog_tables, (list, tuple)):
            cog_tables = [cog_tables]
        self.tables = Map({t.name:t for t in cog_tables})
        for table in self.tables.values():
            if await table.exists():
                self.logger.info(
                    f'Cog table {table.name} for {cog_name} found.')
                table.new_columns = []
                table.initial_data = []
                continue
            await table.create()
            self.logger.info(f'Cog table {table.name} for {cog_name} created.')
        del table_module
