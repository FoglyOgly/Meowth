import pydoc
import datetime
import decimal
from .errors import SchemaError


class SQLType:
    python = None

    def to_dict(self):
        dic = self.__dict__.copy()
        cls = self.__class__
        dic['__meta__'] = cls.__module__ + '.' + cls.__qualname__
        return dic

    @classmethod
    def from_dict(cls, data):
        meta = data.pop('__meta__')
        given = cls.__module__ + '.' + cls.__qualname__
        if given != meta:
            cls = pydoc.locate(meta)
            if cls is None:
                raise RuntimeError(f'Could not locate "{meta}".')
        self = cls.__new__(cls)
        self.__dict__.update(data)
        return self

    def __eq__(self, other):
        return isinstance(
            other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    def to_sql(self):
        raise NotImplementedError()

    def is_real_type(self):
        return True


class BooleanSQL(SQLType):
    python = bool

    def to_sql(self):
        return 'BOOLEAN'


class DateSQL(SQLType):
    python = datetime.date

    def to_sql(self):
        return 'DATE'


class DatetimeSQL(SQLType):
    python = datetime.datetime

    def __init__(self, *, timezone=False):
        self.timezone = timezone

    def to_sql(self):
        if self.timezone:
            return 'TIMESTAMP WITH TIMEZONE'
        return 'TIMESTAMP'


class DoubleSQL(SQLType):
    python = float

    def to_sql(self):
        return 'REAL'


class FloatSQL(SQLType):
    python = float

    def to_sql(self):
        return 'FLOAT'


class IntegerSQL(SQLType):
    python = int

    def __init__(self, *, big=False, small=False, auto_increment=False):
        self.big = big
        self.small = small
        self.auto_increment = auto_increment

        if big and small:
            raise SchemaError('Integer column type cannot be both big and small.')

    def to_sql(self):
        if self.auto_increment:
            if self.big:
                return 'BIGSERIAL'
            if self.small:
                return 'SMALLSERIAL'
            return 'SERIAL'
        if self.big:
            return 'BIGINT'
        if self.small:
            return 'SMALLINT'
        return 'INTEGER'

    def is_real_type(self):
        return not self.auto_increment


class IntervalSQL(SQLType):
    python = datetime.timedelta
    valid_fields = (
        'YEAR', 'MONTH', 'DAY', 'HOUR', 'MINUTE', 'SECOND', 'YEAR TO MONTH',
        'DAY TO HOUR', 'DAY TO MINUTE', 'DAY TO SECOND', 'HOUR TO MINUTE',
        'HOUR TO SECOND', 'MINUTE TO SECOND')

    def __init__(self, field=None):
        if field:
            field = field.upper()
            if field not in self.valid_fields:
                raise SchemaError('invalid interval specified')
            self.field = field
        else:
            self.field = None

    def to_sql(self):
        if self.field:
            return 'INTERVAL ' + self.field
        return 'INTERVAL'


class DecimalSQL(SQLType):
    python = decimal.Decimal

    def __init__(self, *, precision=None, scale=None):
        if precision is not None:
            if precision < 0 or precision > 1000:
                raise SchemaError(
                    'precision must be greater than 0 and below 1000')
            if scale is None:
                scale = 0

        self.precision = precision
        self.scale = scale

    def to_sql(self):
        if self.precision is not None:
            return f'NUMERIC({self.precision}, {self.scale})'
        return 'NUMERIC'


class StringSQL(SQLType):
    python = str

    def to_sql(self):
        return 'TEXT'


class TimeSQL(SQLType):
    python = datetime.time

    def __init__(self, *, timezone=False):
        self.timezone = timezone

    def to_sql(self):
        if self.timezone:
            return 'TIME WITH TIME ZONE'
        return 'TIME'


class JSONSQL(SQLType):
    python = None

    def to_sql(self):
        return 'JSONB'

class ArraySQL(SQLType):
    def __init__(self, inner_type, size: int = None):
        if not isinstance(inner_type, SQLType):
            raise SchemaError('Array inner type must be an SQLType')
        self.type = inner_type
        self.size = size

    def to_sql(self):
        if self.size:
            return f"{self.type.to_sql()}[{self.size}]"
        return f"{self.type.to_sql()}[]"
