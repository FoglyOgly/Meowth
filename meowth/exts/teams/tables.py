from meowth.core.data_manager import schema

def setup(bot):
    team_table = bot.dbi.table('teams')
    team_table.new_columns = [
        schema.IDColumn('team_id', primary_key=True),
        schema.StringColumn('identifier', unique=True),
        schema.StringColumn('emoji', unique=True)
    ]

    teamcolor_names_table = bot.dbi.table('teamcolor_names')
    teamcolor_names_table.new_columns = [
        schema.IDColumn('team_id', primary_key=True),
        schema.IDColumn('language_id', primary_key=True),
        schema.StringColumn('team_name'),
        schema.StringColumn('color_name')
    ]

    team_table.initial_data = [
        {
            "team_id": 1,
            "identifier": "mystic",
            "emoji": ':mystic:'
        },
        {
            "team_id": 2,
            "identifier": "instinct",
            "emoji": ':instinct:'
        },
        {
            "team_id": 3,
            "identifier": "valor",
            "emoji": ':valor:'
        }
    ]

    teamcolor_names_table.initial_data = [
        {
            "team_id": 1,
            "language_id": 9,
            "team_name": "mystic",
            "color_name": "blue"
        },
        {
            "team_id": 1,
            "language_id": 12,
            "team_name": "mystic",
            "color_name": "blue"
        },
        {
            "team_id": 1,
            "language_id": 1,
            "team_name": "ミスティック",
            "color_name": "あお"
        },
        {
            "team_id": 1,
            "language_id": 2,
            "team_name": "misutikku",
            "color_name": "ao"
        },
        {
            "team_id": 1,
            "language_id": 5,
            "team_name": "sagesse",
            "color_name": "bleu"
        },
        {
            "team_id": 1,
            "language_id": 6,
            "team_name": "weisheit",
            "color_name": "blau"
        },
        {
            "team_id": 1,
            "language_id": 7,
            "team_name": "sabiduría",
            "color_name": "azul"
        },
        {
            "team_id": 1,
            "language_id": 8,
            "team_name": "saggezza",
            "color_name": "azzurro"
        },
        {
            "team_id": 2,
            "language_id": 9,
            "team_name": "instinct",
            "color_name": "yellow"
        },
        {
            "team_id": 2,
            "language_id": 12,
            "team_name": "instinct",
            "color_name": "yellow"
        },
        {
            "team_id": 2,
            "language_id": 1,
            "team_name": "インスティンクト",
            "color_name": "きいろ"
        },
        {
            "team_id": 2,
            "language_id": 2,
            "team_name": "insutinkuto",
            "color_name": "ki iro"
        },
        {
            "team_id": 2,
            "language_id": 5,
            "team_name": "intuition",
            "color_name": "jaune"
        },
        {
            "team_id": 2,
            "language_id": 6,
            "team_name": "intuition",
            "color_name": "gelb"
        },
        {
            "team_id": 2,
            "language_id": 7,
            "team_name": "instinto",
            "color_name": "amarillo"
        },
        {
            "team_id": 2,
            "language_id": 8,
            "team_name": "istinto",
            "color_name": "giallo"
        },
        {
            "team_id": 3,
            "language_id": 9,
            "team_name": "valor",
            "color_name": "red"
        },
        {
            "team_id": 3,
            "language_id": 12,
            "team_name": "valour",
            "color_name": "red"
        },
        {
            "team_id": 3,
            "language_id": 1,
            "team_name": "ヴァーラー",
            "color_name": "あか"
        },
        {
            "team_id": 3,
            "language_id": 2,
            "team_name": "ba-ra",
            "color_name": "aka"
        },
        {
            "team_id": 3,
            "language_id": 5,
            "team_name": "bravoure",
            "color_name": "rouge"
        },
        {
            "team_id": 3,
            "language_id": 6,
            "team_name": "wagemut",
            "color_name": "rot"
        },
        {
            "team_id": 3,
            "language_id": 7,
            "team_name": "valor",
            "color_name": "rojo"
        },
        {
            "team_id": 3,
            "language_id": 8,
            "team_name": "coraggio",
            "color_name": "rosso"
        }
    ]




    return [
        team_table,
        teamcolor_names_table,
    ]
