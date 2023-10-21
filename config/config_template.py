'''Configuration values for Meowth - Rename to config.py'''

# bot token from discord developers
bot_token = 'your_token_here'

# default bot settings
bot_prefix = '!'
bot_master = 12345678903216549878
bot_coowners = [132314336914833409, 263607303096369152]
preload_extensions = ['raid','map','pkmn','research','rocket','wild','users','admin']
version = '3'

# minimum required permissions for bot user
bot_permissions = 18135768366161

# postgresql database credentials
db_details = {
    # 'username' : 'meowth',
    # 'database' : 'meowth',
    # 'hostname' : 'localhost',
    'password' : 'password'
}

dbdocid = 'google_sheet_id_here'

emoji = {
    'maybe': '🙋',
    'coming': '🚗',
    'here': '<:here:350686955316445185>',
    'remote': '🛰',
    'invite': '✉',
    'cancel': '❌'
}

# default language
lang_bot = 'en'
lang_pkmn = 'en'

# team settings
team_list = ['mystic', 'valor', 'instinct']
team_colours = {
    "mystic"   : "0x3498db",
    "valor"    : "0xe74c3c",
    "instinct" : "0xf1c40f"
}

team_emoji = {
    "mystic"   : "<:mystic:351758303912656896>",
    "valor"    : "<:valor:351758298975830016>",
    "instinct" : "<:instinct:351758298627702786>",
    "unknown" : "\u2754"
}

pkbtlr_emoji = {
    'pkbtlr' : '<:pkbtlr:1150901168176894113>'
}

form_emoji = {
    'shadow' : '<:shadow:1165329645496788434>',
    'purified' : '<:purified:1163456644170522706>'
}

# raid settings
allow_assume = {
    "5" : "False",
    "4" : "False",
    "3" : "False",
    "2" : "False",
    "1" : "False"
}

status_emoji = {
    "omw"     : ":omw:",
    "here" : ":here:"
}

type_emoji = {
    "bug"      : { "typeid" : "POKEMON_TYPE_BUG",      "emoji" : "<:bug1:351758295196893185>",     "weather" : "RAINY" },
    "dark"     : { "typeid" : "POKEMON_TYPE_DARK",     "emoji" : "<:dark:351758294316089356>",     "weather" : "FOG" },
    "dragon"   : { "typeid" : "POKEMON_TYPE_DRAGON",   "emoji" : "<:dragon1:351758295612129280>",   "weather" : "WINDY" },
    "electric" : { "typeid" : "POKEMON_TYPE_ELECTRIC", "emoji" : "<:electric:351758295414865921>", "weather" : "RAINY" },
    "fairy"    : { "typeid" : "POKEMON_TYPE_FAIRY",    "emoji" : "<:fairy1:351758295070932992>",    "weather" : "OVERCAST" },
    "fighting" : { "typeid" : "POKEMON_TYPE_FIGHTING", "emoji" : "<:fighting:351758296090148864>", "weather" : "OVERCAST" },
    "fire"     : { "typeid" : "POKEMON_TYPE_FIRE",     "emoji" : "<:fire1:351758296044142624>",    "weather" : "CLEAR" },
    "flying"   : { "typeid" : "POKEMON_TYPE_FLYING",   "emoji" : "<:flying:351758295033446400>",   "weather" : "WINDY" },
    "ghost"    : { "typeid" : "POKEMON_TYPE_GHOST",    "emoji" : "<:ghost1:351758295683432449>",   "weather" : "FOG" },
    "grass"    : { "typeid" : "POKEMON_TYPE_GRASS",    "emoji" : "<:grass:351758295729700868>",    "weather" : "CLEAR" },
    "ground"   : { "typeid" : "POKEMON_TYPE_GROUND",   "emoji" : "<:ground:351758295968776194>",   "weather" : "CLEAR" },
    "ice"     : { "typeid" : "POKEMON_TYPE_ICE",      "emoji" : "<:ice:351758296111120384>",      "weather" : "SNOW" },
    "normal"   : { "typeid" : "POKEMON_TYPE_NORMAL",   "emoji" : "<:normal:351758296409178112>",   "weather" : "PARTLY_CLOUDY" },
    "poison"   : { "typeid" : "POKEMON_TYPE_POISON",   "emoji" : "<:poison:351758295976902679>",   "weather" : "OVERCAST" },
    "psychic"  : { "typeid" : "POKEMON_TYPE_PSYCHIC",  "emoji" : "<:psychic:351758294744039426>",  "weather" : "WINDY" },
    "rock"     : { "typeid" : "POKEMON_TYPE_ROCK",     "emoji" : "<:rock1:351758296077697024>",     "weather" : "PARTLY_CLOUDY" },
    "steel"    : { "typeid" : "POKEMON_TYPE_STEEL",    "emoji" : "<:steel:351758296425955328>",    "weather" : "SNOW" },
    "water"   : { "typeid" : "POKEMON_TYPE_WATER",    "emoji" : "<:water:351758295142498325>",    "weather" : "RAINY" }
}

raid_times = {
    1: (60, 45),
    2: (60, 45),
    3: (60, 45),
    4: (60, 45),
    5: (60, 45),
    "EX": (None, 45)
}

# weatherapikey = 
# gmapsapikey = 

max_report_distance = 20

# help command categories
command_categories = {
    "Owner" : {
        "index"       : "5",
        "description" : "Owner-only commands for bot config or info."
    },
    "Server Config" : {
        "index"       : "10",
        "description" : "Server configuration commands."
    },
    "Bot Info" : {
        "index"       : "15",
        "description" : "Commands for finding out information on the bot."
    },
}

# analytics/statistics
pokebattler_tracker = "MeowthSelfHoster"
