from meowth.core.data_manager import schema

def setup(bot):
    pokemon_table = bot.dbi.table('pokemon')
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

    return pokemon_table