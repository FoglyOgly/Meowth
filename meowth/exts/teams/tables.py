from meowth.core.data_manager import schema

def setup(bot):
    team_table = bot.dbi.table('teams')
    team_table.new_columns = [
        schema.IDColumn('team_id', primary_key=True),
        schema.StringColumn('identifier', unique=True),
        schema.IntColumn('color_id', unique=True)
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
            "color_id": 1
        },
        {
            "team_id": 2,
            "identifier": "instinct",
            "color_id": 2
        },
        {
            "team_id": 3,
            "identifier": "valor",
            "color_id": 3
        }
    ]

    team_names_table.initial_data = [
        {
            "team_id": 1,
            "language_id": 1,
            "name": "mystic"
        },
        {
            "team_id": 1,
            "language_id": 2,
            "name": "mystic"
        },
        {
            "team_id": 1,
            "language_id": 3,
            "name": "ミスティック"
        },
        {
            "team_id": 1,
            "language_id": 5,
            "name": "misutikku"
        },
        {
            "team_id": 1,
            "language_id": 8,
            "name": "sagesse" 
        },
        {
            "team_id": 1,
            "language_id": 9,
            "name": "weisheit"
        },
        {
            "team_id": 1,
            "language_id": 10,
            "name": "sabiduría"
        },
        {
            "team_id": 1,
            "language_id": 11,
            "name": "saggezza"
        },
        {
            "team_id": 2,
            "language_id": 1,
            "name": "instinct"
        },
        {
            "team_id": 2,
            "language_id": 2,
            "name": "instinct"
        },
        {
            "team_id": 2,
            "language_id": 3,
            "name": "インスティンクト"
        },
        {
            "team_id": 2,
            "language_id": 5,
            "name": "insutinkuto"
        },
        {
            "team_id": 2,
            "language_id": 8,
            "name": "intuition"
        },
        {
            "team_id": 2,
            "language_id": 9,
            "name": "intuition"
        },
        {
            "team_id": 2,
            "language_id": 10,
            "name": "instinto"
        },
        {
            "team_id": 2,
            "language_id": 11,
            "name": "istinto"
        },
        {
            "team_id": 3,
            "language_id": 1,
            "name": "valor"
        },
        {
            "team_id": 3,
            "language_id": 2,
            "name": "valour"
        },
        {
            "team_id": 3,
            "language_id": 3,
            "name": "ヴァーラー"
        },
        {
            "team_id": 3,
            "language_id": 5,
            "name": "ba-ra"
        },
        {
            "team_id": 3,
            "language_id": 8,
            "name": "bravoure"
        },
        {
            "team_id": 3,
            "language_id": 9,
            "name": "wagemut"
        },
        {
            "team_id": 3,
            "language_id": 10,
            "name": "valor"
        },
        {
            "team_id": 3,
            "language_id": 11,
            "name": "coraggio"
        }
    ]

    color_names_table.initial_data = [
        {
            "color_id": 1,
            "language_id": 1,
            "name": "blue"
        },
        {
            "color_id": 2,
            "language_id": 1,
            "name": "yellow"
        },
        {
            "color_id": 3,
            "language_id": 1,
            "name": "red"
        },
        {
            "color_id": 1,
            "language_id": 2,
            "name": "blue"
        },
        {
            "color_id": 2,
            "language_id": 2,
            "name": "yellow"
        },
        {
            "color_id": 3,
            "language_id": 2,
            "name": "red"
        },
        {
            "color_id": 1,
            "language_id": 3,
            "name": "あお"
        },
        {
            "color_id": 1,
            "language_id": 4,
            "name": "青"
        },
        {
            "color_id": 1,
            "language_id": 5, 
            "name": "ao"
        },
        {
            "color_id": 2,
            "language_id": 3,
            "name": "きいろ"
        },
        {
            "color_id": 2,
            "language_id": 4,
            "name": "黄色"
        },
        {
            "color_id": 2,
            "language_id": 5,
            "name": "ki iro"
        },
        {
            "color_id": 3,
            "language_id": 3,
            "name": "あか"
        },
        {
            "color_id": 3,
            "language_id": 4,
            "name": "赤"
        },
        {
            "color_id": 3,
            "language_id": 5,
            "name": "aka"
        },
        {
            "color_id": 1,
            "language_id": 8,
            "name": "bleu"
        },
        {
            "color_id": 2,
            "language_id": 8,
            "name": "jaune"
        },
        {
            "color_id": 3,
            "language_id": 8,
            "name": "rouge"
        },
        {
            "color_id": 1,
            "language_id": 9,
            "name": "blau"
        },
        {
            "color_id": 2,
            "language_id": 9,
            "name": "gelb"
        },
        {
            "color_id": 3,
            "language_id": 9,
            "name": "rot"
        },
        {
            "color_id": 1,
            "language_id": 10,
            "name": "azul"
        },
        {
            "color_id": 2,
            "language_id": 10,
            "name": "amarillo"
        },
        {
            "color_id": 3,
            "language_id": 10,
            "name": "rojo"
        },
        {
            "color_id": 1,
            "language_id": 11,
            "name": "azzurro"
        },
        {
            "color_id": 2,
            "language_id": 11,
            "name": "giallo"
        },
        {
            "color_id": 3,
            "language_id": 11,
            "name": "rosso"
        }
    ]



    return [
        team_table,
        team_names_table,
        color_names_table
    ]
