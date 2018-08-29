import csv
from meowth.core.data_manager import schema

def setup(bot):
    pokemon_table = bot.dbi.table('pkmn.pokemon')
    pokemon_table.new_columns = [
        schema.StringColumn('pokemonId', primary_key=True),
        schema.IntColumn('Num'),
        schema.IntColumn('Gen'),
        schema.StringColumn('type'),
        schema.StringColumn('type2'),
        schema.IntColumn('form_type_id'),
        schema.StringColumn('gender'),
        schema.BoolColumn('mythical'),
        schema.BoolColumn('legendary'),
        schema.BoolColumn('wild'),
        schema.BoolColumn('shiny'),
        schema.IntColumn('baseStamina'),
        schema.IntColumn('baseAttack'),
        schema.IntColumn('baseDefense'),
        schema.DecimalColumn('HeightM'),
        schema.DecimalColumn('WeightKg'),
        schema.DecimalColumn('heightStdDev'),
        schema.DecimalColumn('weightStdDev'),
        schema.StringColumn('familyId'),
        schema.IntColumn('stageID'),
        schema.StringColumn('evolves_from'),
        schema.IntColumn('evo_cost_candy'),
        schema.StringColumn('evo_cost_item'),
        schema.StringColumn('evo_condition')
    ]

    color_table = bot.dbi.table('pkmn.colors')
    color_table.new_columns = [
        schema.IDColumn('color_id', primary_key=True),
        schema.StringColumn('identifier')
    ]
    color_table.initial_data = [
        {
            "color_id": 1,
            "identifier": "black"
        },
        {
            "color_id": 2,
            "identifier": "blue"
        },
        {
            "color_id": 3,
            "identifier": "brown"
        },
        {
            "color_id": 4,
            "identifier": "gray"
        },
        {
            "color_id": 5,
            "identifier": "green"
        },
        {
            "color_id": 6,
            "identifier": "pink"
        },
        {
            "color_id": 7,
            "identifier": "purple"
        },
        {
            "color_id": 8,
            "identifier": "red"
        },
        {
            "color_id": 9,
            "identifier": "white"
        },
        {
            "color_id": 10,
            "identifier": "yellow"
        }
    ]

    gen_table = bot.dbi.table('generations')
    gen_table.new_columns = [
        schema.IDColumn('GenID', primary_key=True),
        schema.StringColumn('identifier')
    ]
    gen_table.initial_data = [
        {
            "GenID": 1,
            "identifier": "kanto"
        },
        {
            "GenID": 2,
            "identifier": "johto"
        },
        {
            "GenID": 3,
            "identifier": "hoenn"
        }
    ]

    

    return [
        pokemon_table,
        color_table,
        gen_table
    ]