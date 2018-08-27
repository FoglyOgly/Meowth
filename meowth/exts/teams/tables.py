from meowth.core.data_manager import schema

def setup(bot):
    team_table = bot.dbi.table('teams')
    # color_table = bot.dbi.table('colors')
    team_table.new_columns = [
        schema.IDColumn('team_id', primary_key=True),
        schema.IDColumn('color_id', unique=True,
            # foreign_key=colors['color_id']
            ),
        schema.StringColumn('identifier', unique=True),
        schema.StringColumn('emoji', unique=True)
    ]

    team_names_table = bot.dbi.table('team_names')
    languages = bot.dbi.table('languages')
    team_names_table.new_columns = [
        schema.IDColumn('team_id', primary_key=True),
        schema.IDColumn('language_id', primary_key=True,
            foreign_key=languages['language_id']),
        schema.StringColumn('team_name')
    ]

    team_table.initial_data = [
        {
            "team_id": 1,
            "color_id": 2,
            "identifier": "mystic",
            "emoji": ':mystic:'
        },
        {
            "team_id": 2,
            "color_id": 10,
            "identifier": "instinct",
            "emoji": ':instinct:'
        },
        {
            "team_id": 3,
            "color_id": 8,
            "identifier": "valor",
            "emoji": ':valor:'
        }
    ]

    team_names_table.initial_data = [
        {
            "team_id": 1,
            "language_id": 9,
            "team_name": "mystic"
        },
        {
            "team_id": 1,
            "language_id": 12,
            "team_name": "mystic",
        },
        {
            "team_id": 1,
            "language_id": 1,
            "team_name": "ミスティック",
        },
        {
            "team_id": 1,
            "language_id": 2,
            "team_name": "misutikku",
        },
        {
            "team_id": 1,
            "language_id": 5,
            "team_name": "sagesse",
        },
        {
            "team_id": 1,
            "language_id": 6,
            "team_name": "weisheit",
        },
        {
            "team_id": 1,
            "language_id": 7,
            "team_name": "sabiduría",
        },
        {
            "team_id": 1,
            "language_id": 8,
            "team_name": "saggezza",
        },
        {
            "team_id": 2,
            "language_id": 9,
            "team_name": "instinct",
        },
        {
            "team_id": 2,
            "language_id": 12,
            "team_name": "instinct",
        },
        {
            "team_id": 2,
            "language_id": 1,
            "team_name": "インスティンクト",
        },
        {
            "team_id": 2,
            "language_id": 2,
            "team_name": "insutinkuto",
        },
        {
            "team_id": 2,
            "language_id": 5,
            "team_name": "intuition",
        },
        {
            "team_id": 2,
            "language_id": 6,
            "team_name": "intuition",
        },
        {
            "team_id": 2,
            "language_id": 7,
            "team_name": "instinto",
        },
        {
            "team_id": 2,
            "language_id": 8,
            "team_name": "istinto",
        },
        {
            "team_id": 3,
            "language_id": 9,
            "team_name": "valor",
        },
        {
            "team_id": 3,
            "language_id": 12,
            "team_name": "valour",
        },
        {
            "team_id": 3,
            "language_id": 1,
            "team_name": "ヴァーラー",
        },
        {
            "team_id": 3,
            "language_id": 2,
            "team_name": "ba-ra",
        },
        {
            "team_id": 3,
            "language_id": 5,
            "team_name": "bravoure",
        },
        {
            "team_id": 3,
            "language_id": 6,
            "team_name": "wagemut",
        },
        {
            "team_id": 3,
            "language_id": 7,
            "team_name": "valor",
        },
        {
            "team_id": 3,
            "language_id": 8,
            "team_name": "coraggio",
        }
    ]




    return [
        team_table,
        team_names_table,
    ]
