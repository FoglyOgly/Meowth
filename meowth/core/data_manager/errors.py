from asyncpg import PostgresError

class SchemaError(PostgresError):
    pass

class ResponseError(PostgresError):
    pass

class QueryError(PostgresError):
    pass
