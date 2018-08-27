from itertools import zip_longest, chain
from more_itertools import partition

from .errors import PostgresError, SchemaError, ResponseError, QueryError
from . import sqltypes

class SQLOperator:

    default_template = '{column} {operator} {value}'

    def __init__(self, sql_operator, python_operator, str_template):
        self.sql = sql_operator
        self.python = python_operator
        self.template = str_template

    def __str__(self):
        return self.sql

    def format(self, **kwargs):
        return self.template.format(operator=self.sql, **kwargs)

    @classmethod
    def lt(cls):
        return cls('<', '<', cls.default_template)

    @classmethod
    def le(cls):
        return cls('<=', '<=', cls.default_template)

    @classmethod
    def eq(cls):
        return cls('=', '==', cls.default_template)

    @classmethod
    def ne(cls):
        return cls('!=', '!=', cls.default_template)

    @classmethod
    def gt(cls):
        return cls('>', '>', cls.default_template)

    @classmethod
    def ge(cls):
        return cls('>=', '>=', cls.default_template)

    @classmethod
    def like(cls):
        return cls('~~', None, cls.default_template)

    @classmethod
    def ilike(cls):
        return cls('~~*', None, cls.default_template)

    @classmethod
    def not_like(cls):
        return cls('!~~', None, cls.default_template)

    @classmethod
    def not_ilike(cls):
        return cls('!~~*', None, cls.default_template)

    @classmethod
    def between(cls):
        return cls(
            'BETWEEN', None, '{column} {operator} {minvalue} AND {maxvalue}')

    @classmethod
    def in_(cls):
        return cls('=', 'in', '{column} {operator} any({value})')

    @classmethod
    def is_(cls):
        return cls('IS', 'is', cls.default_template)


class SQLComparison:
    def __init__(self, operator, aggregate, column, value=None,
                 minvalue=None, maxvalue=None):
        self.operator = operator
        self.format = operator.format
        self.aggregate = aggregate
        self._column = column
        self.value = value
        self.minvalue = minvalue
        self.maxvalue = maxvalue

    @property
    def column(self):
        if self.aggregate:
            return f"{self.aggregate}({self._column})"
        else:
            return str(self._column)

    def __str__(self):
        return self.operator.format(
            column=self.column, value=self.value,
            minvalue=self.minvalue, maxvalue=self.maxvalue)


class Column:
    __slots__ = ('name', 'data_type', 'primary_key', 'required',
                 'default', 'unique', 'table', 'aggregate', 'foreign_key')

    def __init__(self, name, data_type=None, *, primary_key=False,
                 required=False, default=None, unique=False, table=None,
                 foreign_key=None):
        self.name = name
        if data_type:
            if not isinstance(data_type, sqltypes.SQLType):
                raise TypeError('Data types must be SQLType.')
        self.data_type = data_type
        self.primary_key = primary_key
        self.required = required
        self.default = default
        self.unique = unique
        if sum(map(bool, [primary_key, default is not None, unique])) > 1:
            raise SchemaError('Set only one of either primary_key, default or '
                              'unique')
        if table:
            if not isinstance(table, Table):
                raise SchemaError('Table must be Table object')
        self.table = table
        self.aggregate = None
        if foreign_key:
            if not isinstance(foreign_key, Column):
                raise SchemaError('Foreign key must be Column object')
        self.foreign_key = foreign_key

    @property
    def full_name(self):
        return f"{self.table}.{self.name}" if self.table else self.name

    def __str__(self):
        if self.aggregate:
            return f"{self.aggregate} ({self.full_name})"
        else:
            return self.full_name

    def __lt__(self, value):
        return SQLComparison(
            SQLOperator.lt(), self.aggregate, self.full_name, value)

    def __le__(self, value):
        return SQLComparison(
            SQLOperator.le(), self.aggregate, self.full_name, value)

    def __eq__(self, value):
        return SQLComparison(
            SQLOperator.eq(), self.aggregate, self.full_name, value)

    def __ne__(self, value):
        return SQLComparison(
            SQLOperator.ne(), self.aggregate, self.full_name, value)

    def __gt__(self, value):
        return SQLComparison(
            SQLOperator.gt(), self.aggregate, self.full_name, value)

    def __ge__(self, value):
        return SQLComparison(
            SQLOperator.ge(), self.aggregate, self.full_name, value)

    def like(self, value):
        return SQLComparison(
            SQLOperator.like(), self.aggregate, self.full_name, value)

    def ilike(self, value):
        return SQLComparison(
            SQLOperator.ilike(), self.aggregate, self.full_name, value)

    def not_like(self, value):
        return SQLComparison(
            SQLOperator.not_like(), self.aggregate, self.full_name, value)

    def not_ilike(self, value):
        return SQLComparison(
            SQLOperator.not_ilike(), self.aggregate, self.full_name, value)

    def between(self, minvalue, maxvalue):
        return SQLComparison(
            SQLOperator.between(), self.aggregate, self.full_name,
            minvalue=minvalue, maxvalue=maxvalue)

    def in_(self, value):
        return SQLComparison(
            SQLOperator.in_(), self.aggregate, self.full_name, value)

    @classmethod
    def from_dict(cls, data):
        name = data.pop('name')
        data_type = data.pop('data_type')
        data_type = sqltypes.SQLType.from_dict(data_type)
        return cls(name, data_type, **data)

    @property
    def to_sql(self):
        sql = []
        sql.append(self.full_name)
        sql.append(self.data_type.to_sql())
        if self.default is not None:
            if isinstance(self.default, str) and isinstance(self.data_type, str):
                default = f"'{self.default}'"
            elif isinstance(self.default, bool):
                default = str(self.default).upper()
            else:
                default = f"{self.default}"
            sql.append(f"DEFAULT {default}")
        elif self.unique:
            sql.append('UNIQUE')
        if self.required:
            sql.append('NOT NULL')
        return ' '.join(sql)

    @property
    def count(self):
        self.aggregate = 'COUNT'
        return self

    @property
    def sum(self):
        self.aggregate = 'SUM'
        return self

    @property
    def avg(self):
        self.aggregate = 'AVG'
        return self

    @property
    def min(self):
        self.aggregate = 'MIN'
        return self

    @property
    def max(self):
        self.aggregate = 'MAX'
        return self

    async def set(self, value):
        if not self.table:
            return None
        data = dict(self.table.current_filter)
        data[self.full_name] = value
        return await self.table.upsert(**data)

    async def get(self, **filters):
        return await self.table.get(columns=self.name, **filters)

    async def get_first(self, **filters):
        return await self.table.get_first(column=self.name, **filters)


class IDColumn(Column):
    def __init__(self, name, **kwargs):
        super().__init__(name, sqltypes.IntegerSQL(big=True), **kwargs)

class StringColumn(Column):
    def __init__(self, name, **kwargs):
        super().__init__(name, sqltypes.StringSQL(), **kwargs)

class IntColumn(Column):
    def __init__(self, name, big=False, small=False, **kwargs):
        super().__init__(name, sqltypes.IntegerSQL(big=big, small=small), **kwargs)

class BoolColumn(Column):
    def __init__(self, name, **kwargs):
        super().__init__(name, sqltypes.BooleanSQL(), **kwargs)

class DatetimeColumn(Column):
    def __init__(self, name, *, timezone=False, **kwargs):
        super().__init__(name, sqltypes.DatetimeSQL(timezone=timezone), **kwargs)

class DecimalColumn(Column):
    def __init__(self, name, *, precision=None, scale=None, **kwargs):
        super().__init__(
            name, sqltypes.DecimalSQL(precision=precision, scale=scale), **kwargs)

class IntervalColumn(Column):
    def __init__(self, name, field=False, **kwargs):
        super().__init__(name, sqltypes.IntervalSQL(field), **kwargs)

class Schema:
    """Represents a database schema."""

    __slots__ = ('name', 'dbi')

    def __init__(self, dbi, name: str):
        self.dbi = dbi
        self.name = name

    async def exists(self):
        schemata_table = self.dbi.table('information_schema.schemata')
        query = schemata_table.query('schema_name')
        result = await query.where(schema_name=self.name).get_value()
        return bool(result)

    async def drop(self, cascade=False):
        sql = "DROP SCHEMA $1"
        if cascade:
            sql += " CASCADE"
        return await self.dbi.execute_transaction(sql, self.name)

    async def create(self, skip_if_exists=True):
        if skip_if_exists:
            sql = "CREATE SCHEMA IF NOT EXISTS $1"
        else:
            sql = "CREATE SCHEMA $1"
        await self.dbi.execute_transaction(sql, self.name)
        return self

class TableColumns:
    """Inteface to get and return table columns."""
    def __init__(self, table):
        self._table = table
        self._dbi = table.dbi

    def get_column(self, name):
        return Column(name, table=self._table)

    async def info(self, *names):
        metatable = Table('information_schema.columns', self._dbi)
        metatable.query.where(TABLE_NAME=self._table.name)
        if names:
            metatable.query.where(metatable['COLUMN_NAME'].in_(names))
        print(metatable.query.sql())
        return await metatable.query.get()

    async def get_names(self):
        metatable = Table('information_schema.columns', self._dbi)
        metatable.query('column_name')
        metatable.query.where(TABLE_NAME=self._table.name)
        return await metatable.query.get_values()

    async def get_primaries(self):
        kcu = Table('information_schema.key_column_usage', self._dbi)
        query = kcu.query('column_name').where(TABLE_NAME=self._table.name)
        return await query.get_values()

class Table:
    """Represents a database table."""

    __slots__ = ('name', 'dbi', 'columns', 'where', 'new_columns',
                 'query', 'insert', 'update', 'initial_data', 'schema')

    def __init__(self, name: str, dbi, *, schema=None):
        if '.' in name and not schema:
            schema, name = name.split('.', 1)
            schema = Schema(dbi, schema)
        self.name = name
        if schema:
            if isinstance(schema, str):
                schema = Schema(dbi, schema)
        self.schema = schema
        self.dbi = dbi
        self.where = SQLConditions(parent=self)
        self.columns = TableColumns(table=self)
        self.new_columns = []
        self.initial_data = []
        self.query = Query(dbi, self)
        self.insert = Insert(dbi, self)
        self.update = Update(dbi, self)

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(str(self))

    def __getitem__(self, key):
        return self.columns.get_column(key)

    def __eq__(self, other):
        if isinstance(other, Table):
            return self.name == other.name
        return False

    @classmethod
    def create_sql(cls, name, *columns, primaries=None):
        """Generate SQL for creating the table."""
        sql = f"CREATE TABLE {name} ("
        sql += ', '.join(col.to_sql for col in columns)
        if not primaries:
            primaries = [col.name for col in columns if col.primary_key]
        if primaries:
            if isinstance(primaries, str):
                sql += f", CONSTRAINT {name}_pkey PRIMARY KEY ({primaries})"
            elif isinstance(primaries, (list, tuple, set)):
                sql += (f", CONSTRAINT {name}_pkey"
                        f" PRIMARY KEY ({', '.join(primaries)})")
        sql += ")"
        return sql

    async def create(self, *columns, primaries=None):
        """Create table and return the object representing it."""
        if self.schema:
            await self.schema.create()
            sql = f"CREATE TABLE {self.schema}.{self.name} ("
        else:
            sql = f"CREATE TABLE {self.name} ("
        if not columns:
            if not self.new_columns:
                raise SchemaError("No columns for created table.")
            columns = self.new_columns
        sql += ', '.join(col.to_sql for col in columns)
        if not primaries:
            primaries = [col.name for col in columns if col.primary_key]
        if primaries:
            if isinstance(primaries, str):
                sql += f", CONSTRAINT {self.name}_pkey PRIMARY KEY ({primaries})"
            elif isinstance(primaries, (list, tuple, set)):
                sql += (f", CONSTRAINT {self.name}_pkey"
                        f" PRIMARY KEY ({', '.join(primaries)})")
        sql += ")"
        await self.dbi.execute_transaction(sql)
        if self.new_columns:
            await self.insert.rows(self.new_columns).commit(do_update=False)
        return self

    async def exists(self):
        """Create table and return the object representing it."""
        sql = f"SELECT to_regclass('{self.name}')"
        result = await self.dbi.execute_query(sql)
        return bool(list(result[0])[0])

    async def drop(self):
        """Drop table from database."""
        sql = f"DROP TABLE $1"
        return await self.dbi.execute_transaction(sql, (self.name,))

    async def get_constraints(self):
        """Get column from table."""
        table = Table('information_schema.table_constraints', self.dbi)
        table.query('constrain_name').where(
            TABLE_NAME=table,
            CONSTRAINT_TYPE='PRIMARY KEY')
        return await table.query.get_values()

class SQLConditions:
    def __init__(self, parent=None, allow_having=True):
        self.allow_having = allow_having
        self._parent = parent
        self.where_conditions = []
        self.having_conditions = []
        self.values = []
        self.add = self.add_having if allow_having else self.add_conditions
        self._count_token = 0

    def clear(self):
        self.where_conditions = []
        self.having_conditions = []
        self.values = []
        return self

    def sort_conditions(self, *conditions, allow_having=True):
        having_list = []
        where_list = []
        not_comps, comps = partition(
            lambda c: isinstance(c, SQLComparison), conditions)
        where, having = partition(lambda c: c.aggregate, comps)
        if not self.allow_having and having:
            raise SchemaError("'HAVING' can't be in an UPDATE statement.")
        if not allow_having and having:
            raise SchemaError("'HAVING' can't be an 'OR' condition.")
        where_list.extend(where)
        having_list.extend(having)
        for c in not_comps:
            where_list.append(self.sort_conditions(*c)[0])
        if allow_having:
            return (tuple(where_list), tuple(having_list))
        return tuple(where_list)

    @staticmethod
    def process_dict_conditions(conditions):
        eq = SQLOperator.eq()
        c_list = [SQLComparison(eq, None, k, v) for k, v in conditions.items()]
        return c_list

    @property
    def _count(self):
        self._count_token += 1
        return self._count_token

    def submit_conditions(self, *conditions, having=False):
        if having:
            cond_list = self.having_conditions
        else:
            cond_list = self.where_conditions
        def make_string(*conditions):
            condition_strings = []
            for condition in conditions:
                if isinstance(condition, tuple):
                    c = make_string(*condition)
                    con_str = f"({' OR '.join(c)})"
                    condition_strings.append(con_str)
                    continue
                data = dict(column=condition.column)
                if condition.value is not None:
                    if isinstance(condition.value, Column):
                        data.update(value=str(condition.value))
                    else:
                        data.update(value=f"${self._count}")
                        self.values.append(condition.value)
                else:
                    data.update(minvalue=f"${self._count}")
                    self.values.append(condition.minvalue)
                    data.update(maxvalue=f"${self._count}")
                    self.values.append(condition.maxvalue)
                condition_strings.append(condition.format(**data))
            return condition_strings
        cond_list.extend(make_string(*conditions))

    def add_conditions(self, *conditions, **kwarg_conditions):
        if kwarg_conditions:
            k_conds = self.process_dict_conditions(kwarg_conditions)
            k_conds.extend(conditions)
            conditions = k_conds
        where, having = self.sort_conditions(*conditions)
        self.submit_conditions(*where)
        self.submit_conditions(*having, having=True)
        return self._parent

    def add_having(self, *conditions):
        self.having_conditions.extend(conditions)
        return self._parent

    def or_(self, *conditions, **kwarg_conditions):
        if kwarg_conditions:
            k_conds = self.process_dict_conditions(kwarg_conditions)
            k_conds.extend(conditions)
            conditions = tuple(k_conds)
        return self.add_conditions(conditions)

class Query:
    """Builds a database query."""
    def __init__(self, dbi, *tables):
        self._dbi = dbi
        self._select = ['*']
        self._distinct = False
        self._group_by = []
        self._order_by = []
        self._sort = ''
        self._from = set()
        if tables:
            self.table(*tables)
        self._limit = None
        self._offset = None
        self.conditions = SQLConditions(parent=self)
        self.where = self.conditions.add_conditions
        self.having = self.conditions.add_having

    def select(self, *columns, distinct=False):
        self._select = []
        self._distinct = distinct
        for col in columns:
            if isinstance(col, Column):
                self._select.append(str(col))
                if not self._from and col.table:
                    self._from.add(col.table)
            elif isinstance(col, str):
                self._select.append(col)
        return self

    __call__ = select

    def distinct(self, distinct_select=True):
        self._distinct = distinct_select
        return self

    def table(self, *tables):
        self._from = set()
        for table in tables:
            if isinstance(table, Table):
                self._from.add(table)
            elif isinstance(table, str):
                self._from.add(Table(table, self._dbi))
            else:
                type_given = type(table).__name__
                raise SyntaxError(
                    f"Unexpected data type encountered: {type_given}")
        return self

    def group_by(self, *columns):
        for col in columns:
            if isinstance(col, Column):
                self._group_by.append(col.full_name)
            elif isinstance(col, str):
                self._group_by.append(col)
        return self

    def order_by(self, *columns, asc: bool = None):
        if asc is False:
            sort = ' DESC'
        if asc is True:
            sort = ' ASC'
        if asc is None:
            sort = ''
        for col in columns:
            if isinstance(col, Column):
                self._order_by.append(f"{col.full_name}{sort}")
            elif isinstance(col, str):
                self._order_by.append(f"{col}{sort}")
        return self

    def limit(self, number=None):
        if not isinstance(number, (int, type(None))):
            raise TypeError("Method 'limit' only accepts an int argument.")
        self._limit = number
        return self

    def offset(self, number=None):
        if not isinstance(number, (int, type(None))):
            raise TypeError("Method 'limit' only accepts an int argument.")
        self._offset = number
        return self

    def sql(self, delete=False):
        sql = []
        if delete:
            sql.append("DELETE")
        else:
            select_str = "SELECT DISTINCT" if self._distinct else "SELECT"
            if not self._select:
                sql.append(f"{select_str} *")
            else:
                select_names = [str(c) for c in self._select]
                sql.append(f"{select_str} {', '.join(select_names)}")
        table_names = [t.name for t in self._from]
        sql.append(f"FROM {', '.join(table_names)}")
        if self.conditions.where_conditions:
            con_sql = self.conditions.where_conditions
            sql.append(f"WHERE {' AND '.join(con_sql)}")
        if self._group_by:
            sql.append(f"GROUP BY {', '.join(self._group_by)}")
        if self.conditions.having_conditions:
            con_sql = self.conditions.having_conditions
            sql.append(f"HAVING {' AND '.join(con_sql)}")
        if self._order_by:
            sql.append(f"ORDER BY {', '.join(self._order_by)}")
        if self._limit:
            sql.append(f"LIMIT {self._limit}")
        if self._offset:
            sql.append(f"OFFSET {self._offset}")
        return (f"{' '.join(sql)};", self.conditions.values)

    async def delete(self, **conditions):
        if conditions:
            self.conditions.add_conditions(**conditions)
        query, args = self.sql(delete=True)
        return await self._dbi.execute_query(query, *args)

    async def get(self):
        query, args = self.sql()
        return await self._dbi.execute_query(query, *args)

    async def get_one(self):
        old_limit = self._limit
        self.limit(2)
        data = await self.get()
        self.limit(old_limit)
        if len(data) > 1:
            raise ResponseError('More than one result returned.')
        if not data:
            return None
        return data[0]

    async def get_first(self):
        old_limit = self._limit
        self.limit(1)
        data = await self.get()
        self.limit(old_limit)
        if not data:
            return None
        return data[0]

    async def get_value(self, *cols_selected):
        if cols_selected:
            self.select(*cols_selected)
        if len(self._select) == 1 or self._select == '*':
            data = await self.get_first()
            if not data:
                return None
            return next(data.values())
        else:
            raise QueryError("Query doesn't have a single column selected.")

    async def get_values(self):
        if len(self._select) == 1 or self._select == '*':
            data = await self.get()
            return [next(row.values()) for row in data]
        else:
            raise QueryError("Query doesn't have a single column selected.")

class Insert:
    """Insert data into database table."""

    def __init__(self, dbi, table=None):
        self._dbi = dbi
        self._from = None
        if table:
            self.table(table)
        self._data = []
        self._columns = None
        self._returning = None
        self._primaries = None

    def table(self, table):
        if isinstance(table, Table):
            self._from = table
        elif isinstance(table, str):
            self._from = Table(table, self._dbi)
        else:
            type_given = type(table).__name__
            raise SyntaxError(
                f"Unexpected data type encountered: {type_given}.")
        return self

    def returning(self, *columns):
        self._returning = columns
        return self

    def sql(self, do_update=None):
        """Build the SQL and sort data ready for dbi processing.

        Parameters:
        -----------
        do_update: :class:`bool`
            `None` is default, which raises a `UniqueViolationError` exception
            when the primary keys are found to be a duplicate.
            `True` allows it to update the existing data if found to exist
            already.
            `False` suppresses the exception and just does nothing when a
            duplicate is encountered.
        """

        # get columns
        cols = self._columns or set(chain.from_iterable(self._data))

        # ensure all data entries have no missing keys
        if not self._columns:
            for entry in self._data:
                entry.update((k, None) for k in cols - entry.keys())

        # order columns and build column indexes
        col_idx, cols = zip(*[(f"${i+1}", c) for i, c in enumerate(cols)])

        # sort all data entries into in same order of columns
        data = []
        for entry in self._data:
            entry_values = tuple(entry[d] for d in cols)
            data.append(entry_values)

        # build the insert statement
        col_str, idx_str = (', '.join(cols), ', '.join(col_idx))
        sql = f"INSERT INTO {self._from} ({col_str}) VALUES ({idx_str})"

        # handle conflict if required
        if do_update:
            const_str = ', '.join(self._primaries)
            sql += f" ON CONFLICT ({const_str}) DO UPDATE SET "
            excluded = [f'{c} = excluded.{c}' for c in cols]
            sql += ', '.join(excluded)

        if do_update is False:
            const_str = ', '.join(self._primaries)
            sql += f" ON CONFLICT ({const_str}) DO NOTHING"

        # add the returning statement if specified
        if self._returning:
            sql += f" RETURNING {', '.join(self._returning)}"

        return (sql, tuple(data))

    def sql_test(self, do_update=None):
        """SQL test output"""
        sql, data = self.sql(do_update)
        data_str = '\n'.join(str(d) for d in data)
        msg = f" ```\n**SQL**```sql\n{sql}\n```\n**Data**```py\n{data_str}\n"
        return msg

    async def commit(self, do_update=None):
        """Commit the data in the current insert session to the database.

        Parameters:
        -----------
        do_update: :class:`bool`
            `None` is default, which raises a `UniqueViolationError` exception
            when the primary keys are found to be a duplicate.
            `True` allows it to update the existing data if found to exist
            already.
            `False` suppresses the exception and just does nothing when a
            duplicate is encountered.
        """
        if not self._from:
            raise SchemaError('A table must be declared.')
        if not do_update is None and not self._primaries:
            self._primaries = await self._from.columns.get_primaries()
        sql, data = self.sql(do_update)
        return await self._dbi.execute_transaction(sql, *data)

    def set_columns(self, *columns):
        """Declares the columns for positional arg data entry."""
        if not columns:
            return self._columns
        if self._data:
            raise SchemaError(
                'Columns must be declared before data has been added.')
        self._columns = columns
        return self

    def primaries(self, *primaries):
        if not primaries:
            return self._primaries
        self._primaries = primaries
        return self

    def row(self, *values, **dict_values):
        """Add row data to insert.

        Pass data with column name as keyword and the data as their values.
        If insert column names has been set with ``insert.columns()``,
        positional args may be passed in the same order of declaration.
        """

        if values and dict_values:
            raise SyntaxError(
                'Unable to mix positional args and kwargs when adding row '
                'data. Use only positional args if columns are set or all '
                'columns will be specified. Use only kwargs if adding row '
                'data to specify relevant columns.')

        if values and not self._columns:
            raise SyntaxError(
                'Columns must be declared before being able to use '
                'positional args for this method.')

        if values:
            dict_values = dict(zip_longest(self._columns, values))
            if None in dict_values:
                raise SyntaxError(
                    'Too many values given '
                    f'({len(values)}/{len(self._columns)})')

        if dict_values:
            self._data.append(dict_values)

        return self

    def rows(self, data_iterable):
        """Add row data in bulk to insert."""
        if not hasattr(data_iterable, '__iter__'):
            raise SyntaxError(
                'Non-iterable encountered in rows method. Can only accept '
                'an iterable of data for adding row data in bulk.')

        for row in data_iterable:
            if isinstance(row, dict):
                self.row(**row)
            else:
                self.row(*row)

        return self

    def __call__(self, *args, **kwargs):
        if args and kwargs:
            raise SyntaxError(
                'Unable to mix positional args and kwargs in base call '
                'for Insert. Use only positional args if setting the columns '
                'or use kwargs if adding a row as a shortcut.')

        if args:
            self.set_columns(*args)
        if kwargs:
            self.row(**kwargs)

        return self

class Update:
    """Update data in a database table."""

    def __init__(self, dbi, table=None):
        self._dbi = dbi
        self._from = None
        if table:
            self.table(table)
        self._data = []
        self._columns = None
        self._returning = None
        self.conditions = SQLConditions(parent=self)
        self.where = self.conditions.add_conditions

    def table(self, table):
        if isinstance(table, Table):
            self._from = table
        elif isinstance(table, str):
            self._from = Table(table, self._dbi)
        else:
            type_given = type(table).__name__
            raise SyntaxError(
                f"Unexpected data type encountered: {type_given}.")
        return self

    def returning(self, *columns):
        self._returning = columns
        return self

    def sql(self, allow_no_condition=False):
        """Build the SQL and sort data ready for dbi processing."""

        # get columns
        cols = self._columns or set(chain.from_iterable(self._data))

        # ensure all data entries have no missing keys
        if not self._columns:
            for entry in self._data:
                entry.update((k, None) for k in cols - entry.keys())

        # order columns and build column indexes
        offset = 1
        if self.conditions.where_conditions:
            offset = self.conditions._count_token + 1
        col_idx, cols = zip(*[(f"${i+offset}", c) for i, c in enumerate(cols)])

        # build conditions
        if self.conditions.where_conditions:
            conditions = self.conditions.where_conditions
            cond_sql = f"WHERE {' AND '.join(conditions)}"
            cond_values = self.conditions.values
        else:
            if not allow_no_condition:
                raise SchemaError(
                    "No condition provided for Update. If this is "
                    "intentional, use the 'allow_no_condition' kwarg.")
            else:
                cond_values = []

        # sort all data entries into in same order of columns
        data = []
        for entry in self._data:
            entry_values = tuple(cond_values + [entry[d] for d in cols])
            data.append(entry_values)

        # build the insert statement
        col_str, idx_str = (', '.join(cols), ', '.join(col_idx))
        if len(cols) > 1:
            sql = [f"UPDATE {self._from} SET ({col_str}) = ({idx_str})"]
        else:
            sql = [f"UPDATE {self._from} SET {col_str} = {idx_str}"]

        # add conditions
        if self.conditions.where_conditions:
            sql.append(cond_sql)

        # add the returning statement if specified
        if self._returning:
            sql.append(f"RETURNING {', '.join(self._returning)}")

        return (' '.join(sql), tuple(data))

    def sql_test(self, allow_no_condition=False):
        """SQL test output"""
        sql, data = self.sql(allow_no_condition)
        data_str = '\n'.join(str(d) for d in data)
        msg = f" ```\n**SQL**```sql\n{sql}\n```\n**Data**```py\n{data_str}\n"
        return msg

    async def commit(self, allow_no_condition=False):
        """Commit the data in the current update session to the database."""
        sql, data = self.sql(allow_no_condition)
        await self._dbi.execute_transaction(sql, *data)

    def columns(self, *columns):
        if not columns:
            return self._columns
        if self._data:
            raise SchemaError(
                'Columns must be declared before values are defined.')
        self._columns = columns
        return self

    def values(self, *values, **dict_values):
        """Add values to update rows that match the update conditions.

        Pass data with column name as keyword and the data as their values.
        If update column names has been set with ``update.columns()``,
        positional args may be passed in the same order of declaration.
        """

        if values and dict_values:
            raise SyntaxError(
                'Unable to mix positional args and kwargs when adding row '
                'data. Use only positional args if columns are set or all '
                'columns will be specified. Use only kwargs if adding row '
                'data to specify relevant columns.')

        if values and not self._columns:
            raise SyntaxError(
                'Columns must be declared before being able to use '
                'positional args for this method.')

        if values:
            dict_values = dict(zip_longest(self._columns, values))
            if None in dict_values:
                raise SyntaxError(
                    'Too many values given '
                    f'({len(values)}/{len(self._columns)})')

        if dict_values:
            self._data.append(dict_values)

        return self

    def __call__(self, *args, **kwargs):
        if args and kwargs:
            raise SyntaxError(
                'Unable to mix positional args and kwargs in base call '
                'for Update. Use only positional args if setting the columns '
                'or use kwargs if adding a row as a shortcut.')

        if args:
            self.columns(*args)
        if kwargs:
            self.values(**kwargs)

        return self
