from meowth.core.data_manager import schema

def setup(bot):
    team_table = bot.dbi.table('teams')
    team_table.new_columns = [
        schema.IDColumn('team_id', primary_key=True),
        schema.StringColumn('identifier', unique=True)
    ]

    team_table.initial_data = [
        {}
    ]

    return team_table
