from meowth.core.data_manager import schema

def setup(bot):
    team_table = bot.dbi.table('teams')
    team_table.new_columns = [
        schema.IDColumn('team_id', primary_key=True),
        schema.StringColumn('identifier', unique=True),
        schema.IntColumn('color_id', unique=True),
        schema.StringColumn('emoji', unique=True)
    ]

    team_names_table = bot.dbi.table('team_names')
    team_names_table.new_columns = [
        schema.IDColumn('team_id'),
        schema.IDColumn('language_id'),
        schema.StringColumn('name')
    ]

    color_names_table = bot.dbi.table('color_names')
    color_names_table.new_columns = [
        schema.IDColumn('color_id'),
        schema.IDColumn('language_id'),
        schema.StringColumn('name')
    ]

    team_table.initial_data = [
        {
            "team_id": 1,
            "identifier": "mystic",
            "color_id": 1,
            "emoji": ':mystic:'
        },
        {
            "team_id": 2,
            "identifier": "instinct",
            "color_id": 2,
            "emoji": ':instinct:'
        },
        {
            "team_id": 3,
            "identifier": "valor",
            "color_id": 3,
            "emoji": ':valor:'
        }
    ]

    team_names_table.initial_data = [
        {
            "team_id": 1,
            "language_id": 9,
            "name": "mystic"
        },
        {
            "team_id": 1,
            "language_id": 12,
            "name": "mystic"
        },
        {
            "team_id": 1,
            "language_id": 1,
            "name": "ミスティック"
        },
        {
            "team_id": 1,
            "language_id": 2,
            "name": "misutikku"
        },
        {
            "team_id": 1,
            "language_id": 5,
            "name": "sagesse" 
        },
        {
            "team_id": 1,
            "language_id": 6,
            "name": "weisheit"
        },
        {
            "team_id": 1,
            "language_id": 7,
            "name": "sabiduría"
        },
        {
            "team_id": 1,
            "language_id": 8,
            "name": "saggezza"
        },
        {
            "team_id": 2,
            "language_id": 9,
            "name": "instinct"
        },
        {
            "team_id": 2,
            "language_id": 12,
            "name": "instinct"
        },
        {
            "team_id": 2,
            "language_id": 1,
            "name": "インスティンクト"
        },
        {
            "team_id": 2,
            "language_id": 2,
            "name": "insutinkuto"
        },
        {
            "team_id": 2,
            "language_id": 5,
            "name": "intuition"
        },
        {
            "team_id": 2,
            "language_id": 6,
            "name": "intuition"
        },
        {
            "team_id": 2,
            "language_id": 7,
            "name": "instinto"
        },
        {
            "team_id": 2,
            "language_id": 8,
            "name": "istinto"
        },
        {
            "team_id": 3,
            "language_id": 9,
            "name": "valor"
        },
        {
            "team_id": 3,
            "language_id": 12,
            "name": "valour"
        },
        {
            "team_id": 3,
            "language_id": 1,
            "name": "ヴァーラー"
        },
        {
            "team_id": 3,
            "language_id": 2,
            "name": "ba-ra"
        },
        {
            "team_id": 3,
            "language_id": 5,
            "name": "bravoure"
        },
        {
            "team_id": 3,
            "language_id": 6,
            "name": "wagemut"
        },
        {
            "team_id": 3,
            "language_id": 7,
            "name": "valor"
        },
        {
            "team_id": 3,
            "language_id": 8,
            "name": "coraggio"
        }
    ]

    color_names_table.initial_data = [
        {
            "color_id": 1,
            "language_id": 9,
            "name": "blue"
        },
        {
            "color_id": 2,
            "language_id": 9,
            "name": "yellow"
        },
        {
            "color_id": 3,
            "language_id": 9,
            "name": "red"
        },
        {
            "color_id": 1,
            "language_id": 12,
            "name": "blue"
        },
        {
            "color_id": 2,
            "language_id": 12,
            "name": "yellow"
        },
        {
            "color_id": 3,
            "language_id": 12,
            "name": "red"
        },
        {
            "color_id": 1,
            "language_id": 1,
            "name": "あお"
        },
        {
            "color_id": 1,
            "language_id": 11,
            "name": "青"
        },
        {
            "color_id": 1,
            "language_id": 2, 
            "name": "ao"
        },
        {
            "color_id": 2,
            "language_id": 1,
            "name": "きいろ"
        },
        {
            "color_id": 2,
            "language_id": 11,
            "name": "黄色"
        },
        {
            "color_id": 2,
            "language_id": 2,
            "name": "ki iro"
        },
        {
            "color_id": 3,
            "language_id": 1,
            "name": "あか"
        },
        {
            "color_id": 3,
            "language_id": 11,
            "name": "赤"
        },
        {
            "color_id": 3,
            "language_id": 2,
            "name": "aka"
        },
        {
            "color_id": 1,
            "language_id": 5,
            "name": "bleu"
        },
        {
            "color_id": 2,
            "language_id": 5,
            "name": "jaune"
        },
        {
            "color_id": 3,
            "language_id": 5,
            "name": "rouge"
        },
        {
            "color_id": 1,
            "language_id": 6,
            "name": "blau"
        },
        {
            "color_id": 2,
            "language_id": 6,
            "name": "gelb"
        },
        {
            "color_id": 3,
            "language_id": 6,
            "name": "rot"
        },
        {
            "color_id": 1,
            "language_id": 7,
            "name": "azul"
        },
        {
            "color_id": 2,
            "language_id": 7,
            "name": "amarillo"
        },
        {
            "color_id": 3,
            "language_id": 7,
            "name": "rojo"
        },
        {
            "color_id": 1,
            "language_id": 8,
            "name": "azzurro"
        },
        {
            "color_id": 2,
            "language_id": 8,
            "name": "giallo"
        },
        {
            "color_id": 3,
            "language_id": 8,
            "name": "rosso"
        }
    ]



    return [
        team_table,
        team_names_table,
        color_names_table
    ]
