'''Configuration values for Meowth - Rename to config.py'''

# bot token from discord developers
bot_token = 'your_token_here'

# default bot settings
bot_prefix = '!'
bot_master = 12345678903216549878
bot_coowners = [132314336914833409, 263607303096369152]
preload_extensions = []

# minimum required permissions for bot user
bot_permissions = 268822608

# postgresql database credentials
db_details = {
    # 'username' : 'meowth',
    # 'database' : 'meowth',
    # 'hostname' : 'localhost',
    'password' : 'password'
}

emoji = {
    'coming': '\u1f697',
    'here': '<:here:350686955316445185>',
    'maybe': '\u1f914'
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
    "instinct" : "<:instinct:351758298627702786>"
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
    "here_id" : ":here:"
}

type_emoji = {
    "normal"   : "<:normal:351758296409178112>",
    "fire"     : "<:fire1:351758296044142624>",
    "water"    : "<:water:351758295142498325>",
    "electric" : "<:electric:351758295414865921>",
    "grass"    : "<:grass:351758295729700868>",
    "ice"      : "<:ice:351758296111120384>",
    "fighting" : "<:fighting:351758296090148864>",
    "poison"   : "<:poison:351758295976902679>",
    "ground"   : "<:ground:351758295968776194>",
    "flying"   : "<:flying:351758295033446400>",
    "psychic"  : "<:psychic:351758294744039426>",
    "bug"      : "<:bug1:351758295196893185>",
    "rock"     : "<:rock:351758296077697024>",
    "ghost"    : "<:ghost1:351758295683432449>",
    "dragon"   : "<:dragon:351758295612129280>",
    "dark"     : "<:dark:351758294316089356>",
    "steel"    : "<:steel:351758296425955328>",
    "fairy"    : "<:fairy:351758295070932992>"
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
