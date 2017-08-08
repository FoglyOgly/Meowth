import discord
import asyncio
from discord.ext.commands import Bot
import time
from time import strftime

Meowth = Bot(command_prefix="!")


"""

======================

Configuration

======================

"""

"""

Server information

"""
# Bot token ID, needed for authentication.
# This is found on the app page when you click to reveal the bot user's token
bot_token = "mytokenhere"

# IDs for team roles.
# Find this ID information by doing \@role, which will
# return a string like this: <@&123456789123456789>.
# Just grab the numbers out of the string.
roles = [
    "mysticid",
    "valorid",
    "instinctid"
]

# Your town and state. These are pasted
# verbatim into the Google Maps query.
yourtown = ""
yourstate = ""

"""

Define your server's special strings here.

To use emoji, obtain the ID with \:emoji_name:
and format the string as <emoji_name:id>

The default values are custom emoji and will need to have
their IDs changed to match your server.

You can also use plain strings, if you want.
However, don't use strings that contains the bot's
command prefix (at the top of the file)

"""

# Emoji for team assignments
team_dict = {"mystic": "<:mystic:id>", "valor": "<:valor:id>", "instinct": "<:instinct:id>"}

# Emoji for raid organization
omw_id = "<:omw:id>"
unomw_id = "<:unomw:id>"
here_id = "<:here:id>"
unhere_id = "<:unhere:id>"

# Emoji for Pokemon types.
type_id_dict = {
    'fire'     : "<:fire1:id>",
    'water'    : "<:water:id>",
    'electric' : "<:electric:id>",
    'grass'    : "<:grass:id>",
    'ice'      : "<:ice:id>",
    'fighting' : "<:fighting:id>",
    'poison'   : "<:poison:id>",
    'ground'   : "<:ground:id>",
    'flying'   : "<:flying:id>",
    'psychic'  : "<:psychic:id>",
    'bug'      : "<:bug1:id>",
    'rock'     : "<:rock:id>",
    'ghost'    : "<:ghost1:id>",
    'dragon'   : "<:dragon:id>",
    'dark'     : "<:dark:id>",
    'steel'    : "<:steel:id>",
    'fairy'    : "<:fairy:id>"
}

"""

======================

End configuration

======================

"""



"""Below is a dict of raid bosses with their type weaknesses. These become part of the raid report message."""

raid_dict = {
    "lugia": ["rock", "ghost", "electric", "ice", "dark"],
    "moltres": ["rockx2", "water", "electric"],
    "zapdos": ["rock", "ice"],
    "articuno": ["rockx2", "steel", "fire", "electric"],
    "tyranitar": ["fightingx2", "ground", "bug", "steel", "water", "grass", "fairy"],
    "snorlax": ["fighting"],
    "lapras": ["fighting", "rock", "grass", "electric"],
    "rhydon": ["waterx2", "grassx2", "ice", "steel", "ground", "fighting"],
    "blastoise": ["electric", "grass"],
    "charizard": ["rockx2", "water", "electric"],
    "venusaur": ["flying", "fire", "psychic", "ice"],
    "flareon": ["water", "ground", "rock"],
    "jolteon": ["ground"],
    "vaporeon": ["electric", "grass"],
    "gengar": ["ground", "ghost", "psychic", "dark"],
    "machamp": ["flying", "psychic", "fairy"],
    "alakazam": ["bug", "ghost", "dark"],
    "arcanine": ["water", "ground", "rock"],
    "magmar": ["water", "ground", "rock"],
    "electabuzz": ["ground"],
    "weezing": ["ground", "psychic"],
    "exeggutor": ["bugx2", "flying", "poison", "ghost", "fire", "ice", "dark"],
    "muk": ["ground", "psychic"],
    "croconaw": ["electric", "grass"],
    "quilava": ["water", "ground", "rock"],
    "bayleef": ["flying", "poison", "bug", "fire", "ice"],
    "magikarp": ["electric", "grass"],
}

"""Given a list of weaknesses, return a
space-separated string of their type IDs,
as defined in the type_id_dict"""
def weakness_to_str(weak_list):
    ret = ""
    for weakness in weak_list:
        # Handle an "x2" postfix defining a double weakness
        x2 = ""
        if weakness[-2:] == "x2":
            weakness = weakness[:-2]
            x2 = "x2"
        
        # Append to string
        ret += type_id_dict[weakness] + x2 + " "
    
    return ret


"""A list of all Pokemon up to Gen VII. This helps partially futureproof"""


pokemon_list = [
    "bulbasaur",
    "ivysaur",
    "venusaur",
    "charmander",
    "charmeleon",
    "charizard",
    "squirtle",
    "wartortle",
    "blastoise",
    "caterpie",
    "metapod",
    "butterfree",
    "weedle",
    "kakuna",
    "beedrill",
    "pidgey",
    "pidgeotto",
    "pidgeot",
    "rattata",
    "raticate",
    "spearow",
    "fearow",
    "ekans",
    "arbok",
    "pikachu",
    "raichu",
    "sandshrew",
    "sandslash",
    "nidoran♀",
    "nidorina",
    "nidoqueen",
    "nidoran♂",
    "nidorino",
    "nidoking",
    "clefairy",
    "clefable",
    "vulpix",
    "ninetales",
    "jigglypuff",
    "wigglytuff",
    "zubat",
    "golbat",
    "oddish",
    "gloom",
    "vileplume",
    "paras",
    "parasect",
    "venonat",
    "venomoth",
    "diglett",
    "dugtrio",
    "meowth",
    "persian",
    "psyduck",
    "golduck",
    "mankey",
    "primeape",
    "growlithe",
    "arcanine",
    "poliwag",
    "poliwhirl",
    "poliwrath",
    "abra",
    "kadabra",
    "alakazam",
    "machop",
    "machoke",
    "machamp",
    "bellsprout",
    "weepinbell",
    "victreebel",
    "tentacool",
    "tentacruel",
    "geodude",
    "graveler",
    "golem",
    "ponyta",
    "rapidash",
    "slowpoke",
    "slowbro",
    "magnemite",
    "magneton",
    "farfetch'd",
    "doduo",
    "dodrio",
    "seel",
    "dewgong",
    "grimer",
    "muk",
    "shellder",
    "cloyster",
    "gastly",
    "haunter",
    "gengar",
    "onix",
    "drowzee",
    "hypno",
    "krabby",
    "kingler",
    "voltorb",
    "electrode",
    "exeggcute",
    "exeggutor",
    "cubone",
    "marowak",
    "hitmonlee",
    "hitmonchan",
    "lickitung",
    "koffing",
    "weezing",
    "rhyhorn",
    "rhydon",
    "chansey",
    "tangela",
    "kangaskhan",
    "horsea",
    "seadra",
    "goldeen",
    "seaking",
    "staryu",
    "starmie",
    "mr. mime",
    "scyther",
    "jynx",
    "electabuzz",
    "magmar",
    "pinsir",
    "tauros",
    "magikarp",
    "gyarados",
    "lapras",
    "ditto",
    "eevee",
    "vaporeon",
    "jolteon",
    "flareon",
    "porygon",
    "omanyte",
    "omastar",
    "kabuto",
    "kabutops",
    "aerodactyl",
    "snorlax",
    "articuno",
    "zapdos",
    "moltres",
    "dratini",
    "dragonair",
    "dragonite",
    "mewtwo",
    "mew",
    "chikorita",
    "bayleef",
    "meganium",
    "cyndaquil",
    "quilava",
    "typhlosion",
    "totodile",
    "croconaw",
    "feraligatr",
    "sentret",
    "furret",
    "hoothoot",
    "noctowl",
    "ledyba",
    "ledian",
    "spinarak",
    "ariados",
    "crobat",
    "chinchou",
    "lanturn",
    "pichu",
    "cleffa",
    "igglybuff",
    "togepi",
    "togetic",
    "natu",
    "xatu",
    "mareep",
    "flaaffy",
    "ampharos",
    "bellossom",
    "marill",
    "azumarill",
    "sudowoodo",
    "politoed",
    "hoppip",
    "skiploom",
    "jumpluff",
    "aipom",
    "sunkern",
    "sunflora",
    "yanma",
    "wooper",
    "quagsire",
    "espeon",
    "umbreon",
    "murkrow",
    "slowking",
    "misdreavus",
    "unown",
    "wobbuffet",
    "girafarig",
    "pineco",
    "forretress",
    "dunsparce",
    "gligar",
    "steelix",
    "snubbull",
    "granbull",
    "qwilfish",
    "scizor",
    "shuckle",
    "heracross",
    "sneasel",
    "teddiursa",
    "ursaring",
    "slugma",
    "magcargo",
    "swinub",
    "piloswine",
    "corsola",
    "remoraid",
    "octillery",
    "delibird",
    "mantine",
    "skarmory",
    "houndour",
    "houndoom",
    "kingdra",
    "phanpy",
    "donphan",
    "porygon2",
    "stantler",
    "smeargle",
    "tyrogue",
    "hitmontop",
    "smoochum",
    "elekid",
    "magby",
    "miltank",
    "blissey",
    "raikou",
    "entei",
    "suicune",
    "larvitar",
    "pupitar",
    "tyranitar",
    "lugia",
    "ho-oh",
    "celebi",
    "treecko",
    "grovyle",
    "sceptile",
    "torchic",
    "combusken",
    "blaziken",
    "mudkip",
    "marshtomp",
    "swampert",
    "poochyena",
    "mightyena",
    "zigzagoon",
    "linoone",
    "wurmple",
    "silcoon",
    "beautifly",
    "cascoon",
    "dustox",
    "lotad",
    "lombre",
    "ludicolo",
    "seedot",
    "nuzleaf",
    "shiftry",
    "taillow",
    "swellow",
    "wingull",
    "pelipper",
    "ralts",
    "kirlia",
    "gardevoir",
    "surskit",
    "masquerain",
    "shroomish",
    "breloom",
    "slakoth",
    "vigoroth",
    "slaking",
    "nincada",
    "ninjask",
    "shedinja",
    "whismur",
    "loudred",
    "exploud",
    "makuhita",
    "hariyama",
    "azurill",
    "nosepass",
    "skitty",
    "delcatty",
    "sableye",
    "mawile",
    "aron",
    "lairon",
    "aggron",
    "meditite",
    "medicham",
    "electrike",
    "manectric",
    "plusle",
    "minun",
    "volbeat",
    "illumise",
    "roselia",
    "gulpin",
    "swalot",
    "carvanha",
    "sharpedo",
    "wailmer",
    "wailord",
    "numel",
    "camerupt",
    "torkoal",
    "spoink",
    "grumpig",
    "spinda",
    "trapinch",
    "vibrava",
    "flygon",
    "cacnea",
    "cacturne",
    "swablu",
    "altaria",
    "zangoose",
    "seviper",
    "lunatone",
    "solrock",
    "barboach",
    "whiscash",
    "corphish",
    "crawdaunt",
    "baltoy",
    "claydol",
    "lileep",
    "cradily",
    "anorith",
    "armaldo",
    "feebas",
    "milotic",
    "castform",
    "kecleon",
    "shuppet",
    "banette",
    "duskull",
    "dusclops",
    "tropius",
    "chimecho",
    "absol",
    "wynaut",
    "snorunt",
    "glalie",
    "spheal",
    "sealeo",
    "walrein",
    "clamperl",
    "huntail",
    "gorebyss",
    "relicanth",
    "luvdisc",
    "bagon",
    "shelgon",
    "salamence",
    "beldum",
    "metang",
    "metagross",
    "regirock",
    "regice",
    "registeel",
    "latias",
    "latios",
    "kyogre",
    "groudon",
    "rayquaza",
    "jirachi",
    "deoxys",
    "turtwig",
    "grotle",
    "torterra",
    "chimchar",
    "monferno",
    "infernape",
    "piplup",
    "prinplup",
    "empoleon",
    "starly",
    "staravia",
    "staraptor",
    "bidoof",
    "bibarel",
    "kricketot",
    "kricketune",
    "shinx",
    "luxio",
    "luxray",
    "budew",
    "roserade",
    "cranidos",
    "rampardos",
    "shieldon",
    "bastiodon",
    "burmy",
    "wormadam",
    "mothim",
    "combee",
    "vespiquen",
    "pachirisu",
    "buizel",
    "floatzel",
    "cherubi",
    "cherrim",
    "shellos",
    "gastrodon",
    "ambipom",
    "drifloon",
    "drifblim",
    "buneary",
    "lopunny",
    "mismagius",
    "honchkrow",
    "glameow",
    "purugly",
    "chingling",
    "stunky",
    "skuntank",
    "bronzor",
    "bronzong",
    "bonsly",
    "mime jr.",
    "happiny",
    "chatot",
    "spiritomb",
    "gible",
    "gabite",
    "garchomp",
    "munchlax",
    "riolu",
    "lucario",
    "hippopotas",
    "hippowdon",
    "skorupi",
    "drapion",
    "croagunk",
    "toxicroak",
    "carnivine",
    "finneon",
    "lumineon",
    "mantyke",
    "snover",
    "abomasnow",
    "weavile",
    "magnezone",
    "lickilicky",
    "rhyperior",
    "tangrowth",
    "electivire",
    "magmortar",
    "togekiss",
    "yanmega",
    "leafeon",
    "glaceon",
    "gliscor",
    "mamoswine",
    "porygon-z",
    "gallade",
    "probopass",
    "dusknoir",
    "froslass",
    "rotom",
    "uxie",
    "mesprit",
    "azelf",
    "dialga",
    "palkia",
    "heatran",
    "regigigas",
    "giratina",
    "cresselia",
    "phione",
    "manaphy",
    "darkrai",
    "shaymin",
    "arceus",
    "victini",
    "snivy",
    "servine",
    "serperior",
    "tepig",
    "pignite",
    "emboar",
    "oshawott",
    "dewott",
    "samurott",
    "patrat",
    "watchog",
    "lillipup",
    "herdier",
    "stoutland",
    "purrloin",
    "liepard",
    "pansage",
    "simisage",
    "pansear",
    "simisear",
    "panpour",
    "simipour",
    "munna",
    "musharna",
    "pidove",
    "tranquill",
    "unfezant",
    "blitzle",
    "zebstrika",
    "roggenrola",
    "boldore",
    "gigalith",
    "woobat",
    "swoobat",
    "drilbur",
    "excadrill",
    "audino",
    "timburr",
    "gurdurr",
    "conkeldurr",
    "tympole",
    "palpitoad",
    "seismitoad",
    "throh",
    "sawk",
    "sewaddle",
    "swadloon",
    "leavanny",
    "venipede",
    "whirlipede",
    "scolipede",
    "cottonee",
    "whimsicott",
    "petilil",
    "lilligant",
    "basculin",
    "sandile",
    "krokorok",
    "krookodile",
    "darumaka",
    "darmanitan",
    "maractus",
    "dwebble",
    "crustle",
    "scraggy",
    "scrafty",
    "sigilyph",
    "yamask",
    "cofagrigus",
    "tirtouga",
    "carracosta",
    "archen",
    "archeops",
    "trubbish",
    "garbodor",
    "zorua",
    "zoroark",
    "minccino",
    "cinccino",
    "gothita",
    "gothorita",
    "gothitelle",
    "solosis",
    "duosion",
    "reuniclus",
    "ducklett",
    "swanna",
    "vanillite",
    "vanillish",
    "vanilluxe",
    "deerling",
    "sawsbuck",
    "emolga",
    "karrablast",
    "escavalier",
    "foongus",
    "amoonguss",
    "frillish",
    "jellicent",
    "alomomola",
    "joltik",
    "galvantula",
    "ferroseed",
    "ferrothorn",
    "klink",
    "klang",
    "klinklang",
    "tynamo",
    "eelektrik",
    "eelektross",
    "elgyem",
    "beheeyem",
    "litwick",
    "lampent",
    "chandelure",
    "axew",
    "fraxure",
    "haxorus",
    "cubchoo",
    "beartic",
    "cryogonal",
    "shelmet",
    "accelgor",
    "stunfisk",
    "mienfoo",
    "mienshao",
    "druddigon",
    "golett",
    "golurk",
    "pawniard",
    "bisharp",
    "bouffalant",
    "rufflet",
    "braviary",
    "vullaby",
    "mandibuzz",
    "heatmor",
    "durant",
    "deino",
    "zweilous",
    "hydreigon",
    "larvesta",
    "volcarona",
    "cobalion",
    "terrakion",
    "virizion",
    "tornadus",
    "thundurus",
    "reshiram",
    "zekrom",
    "landorus",
    "kyurem",
    "keldeo",
    "meloetta",
    "genesect",
    "chespin",
    "quilladin",
    "chesnaught",
    "fennekin",
    "braixen",
    "delphox",
    "froakie",
    "frogadier",
    "greninja",
    "bunnelby",
    "diggersby",
    "fletchling",
    "fletchinder",
    "talonflame",
    "scatterbug",
    "spewpa",
    "vivillon",
    "litleo",
    "pyroar",
    "flabébé",
    "floette",
    "florges",
    "skiddo",
    "gogoat",
    "pancham",
    "pangoro",
    "furfrou",
    "espurr",
    "meowstic",
    "honedge",
    "doublade",
    "aegislash",
    "spritzee",
    "aromatisse",
    "swirlix",
    "slurpuff",
    "inkay",
    "malamar",
    "binacle",
    "barbaracle",
    "skrelp",
    "dragalge",
    "clauncher",
    "clawitzer",
    "helioptile",
    "heliolisk",
    "tyrunt",
    "tyrantrum",
    "amaura",
    "aurorus",
    "sylveon",
    "hawlucha",
    "dedenne",
    "carbink",
    "goomy",
    "sliggoo",
    "goodra",
    "klefki",
    "phantump",
    "trevenant",
    "pumpkaboo",
    "gourgeist",
    "bergmite",
    "avalugg",
    "noibat",
    "noivern",
    "xerneas",
    "yveltal",
    "zygarde",
    "diancie",
    "hoopa",
    "volcanion",
    "rowlet",
    "dartrix",
    "decidueye",
    "litten",
    "torracat",
    "incineroar",
    "popplio",
    "brionne",
    "primarina",
    "pikipek",
    "trumbeak",
    "toucannon",
    "yungoos",
    "gumshoos",
    "grubbin",
    "charjabug",
    "vikavolt",
    "crabrawler",
    "crabominable",
    "oricorio",
    "cutiefly",
    "ribombee",
    "rockruff",
    "lycanroc",
    "wishiwashi",
    "mareanie",
    "toxapex",
    "mudbray",
    "mudsdale",
    "dewpider",
    "araquanid",
    "fomantis",
    "lurantis",
    "morelull",
    "shiinotic",
    "salandit",
    "salazzle",
    "stufful",
    "bewear",
    "bounsweet",
    "steenee",
    "tsareena",
    "comfey",
    "oranguru",
    "passimian",
    "wimpod",
    "golisopod",
    "sandygast",
    "palossand",
    "pyukumuku",
    "type: null",
    "silvally",
    "minior",
    "komala",
    "turtonator",
    "togedemaru",
    "mimikyu",
    "bruxish",
    "drampa",
    "dhelmise",
    "jangmo-o",
    "hakamo-o",
    "kommo-o",
    "tapu koko",
    "tapu lele",
    "tapu bulu",
    "tapu fini",
    "cosmog",
    "cosmoem",
    "solgaleo",
    "lunala",
    "nihilego",
    "buzzwole",
    "pheromosa",
    "xurkitree",
    "celesteela",
    "kartana",
    "guzzlord",
    "necrozma",
    "magearna",
    "marshadow"
    ]

"""The empty lists Meowth will populate for keeping track of active raids, people who are on the way to a raid or waiting at 
a raid, and a list of messages saying when the raids will expire. These all become lists of tuples."""

raidchannel_list = []
omw_list = []
waiting_list = []
raidexpmsg_list=[]

@Meowth.event
async def on_ready():
    print("Meowth! That's right!") #prints to the terminal or cmd prompt window upon successful connection to Discord

"""Welcome message to the server and some basic instructions."""

@Meowth.event
async def on_member_join(member):
    server = member.server
    announcements = discord.utils.get(server.channels, name='announcements')
    admin = discord.utils.get(server.roles, name='admin')                
    message = "Meowth! Welcome to {0.name}, {1.mention}! Set your team by typing '!team mystic', '!team valor', or '!team instinct' without quotations. Then head over to {2.mention} to get caught up on what's happening! If you have any questions just ask an {3.mention}."
    await Meowth.send_message(server, message.format(server, member, announcements, admin))


"""A command for setting a team role. These roles have to be created manually beforehand."""

@Meowth.command(pass_context = True)
async def team(ctx):
    role = None
    entered_team = ctx.message.content[6:].lower()
    role = discord.utils.get(ctx.message.server.roles, name=entered_team)
    for r in ctx.message.author.roles:
        if r.id in roles:
            await Meowth.send_message(ctx.message.channel, "Meowth! You already have a team role!") #checks if user already has a team
            return
    if role is None or role.name not in list(team_dict.keys()):
        await Meowth.send_message(ctx.message.channel, "Meowth! Invalid team!") #checks if team is one of the three
        return
    else:
        try:
            await Meowth.add_roles(ctx.message.author, role)
            await Meowth.send_message(ctx.message.channel, "Meowth! Added {0} to Team {1}! {2}".format(ctx.message.author.mention, role.name.capitalize(), team_dict[entered_team]))
        except discord.Forbidden:
            await Meowth.send_message(ctx.message.channel, "Meowth! I can't add roles!")
            
"""A command for setting a role for a Pokemon species the user wants. 
Meowth creates a role if one does not exist for the species."""
@Meowth.command(pass_context = True)                
async def want(ctx):
    entered_want = ctx.message.content[6:].lower()
    role = discord.utils.get(ctx.message.server.roles, name=entered_want)
    if role is None and entered_want in pokemon_list:
        newrole = await Meowth.create_role(server = ctx.message.server, name = entered_want, hoist = False, mentionable = True)
        await asyncio.sleep(0.5)
        await Meowth.add_roles(ctx.message.author, newrole)
        want_number = pokemon_list.index(entered_want) + 1
        want_img_url = "http://floatzel.net/pokemon/black-white/sprites/images/{0}.png".format(str(want_number))
        want_embed = discord.Embed(colour=discord.Colour(0x2ecc71))
        want_embed.set_thumbnail(url=want_img_url)
        await Meowth.send_message(ctx.message.channel, content="Meowth! Got it! {0} wants {1}".format(ctx.message.author.mention, entered_want.capitalize()),embed=want_embed)
        return
    if role is None and entered_want not in pokemon_list:
        await Meowth.send_message(ctx.message.channel, "Meowth! {0} is not a Pokemon! Check your spelling!".format(entered_want.capitalize()))
        return
    else:
        await Meowth.add_roles(ctx.message.author, role)
        want_number = pokemon_list.index(entered_want) + 1
        want_img_url = "http://floatzel.net/pokemon/black-white/sprites/images/{0}.png".format(str(want_number)) #This part embeds the sprite
        want_embed = discord.Embed(colour=discord.Colour(0x2ecc71))
        want_embed.set_thumbnail(url=want_img_url)
        await Meowth.send_message(ctx.message.channel, content="Meowth! Got it! {0} wants {1}".format(ctx.message.author.mention, entered_want.capitalize()),embed=want_embed)

"""A command for reporting a wild Pokemon spawn location. Meowth will insert the details (really just everything after
the species name) into a Google maps link and post the link to the same channel the report was made in."""
@Meowth.command(pass_context = True)
async def wild(ctx):
    space1 = ctx.message.content.find(" ",6)
    if space1 == -1:
        await Meowth.send_message(ctx.message.channel, "Meowth! Give more details when reporting!")
        return
    else:
        entered_wild = ctx.message.content[6:space1].lower()
        wild_details = ctx.message.content[space1:]
        wild_details_list = wild_details.split()
        wild_gmaps_link = "https://www.google.com/maps/search/?api=1&query={0}+{1}+{2}".format('+'.join(wild_details_list), yourtown, yourstate)
        if entered_wild not in pokemon_list:
            await Meowth.send_message(ctx.message.channel, "Meowth! That's not a Pokemon! Check your spelling!")
            return
        else:
            wild = discord.utils.get(ctx.message.server.roles, name = entered_wild)
<<<<<<< HEAD
            if wild is None and entered_wild in pokemon_list:
=======
            if wild is None:
>>>>>>> abf1a131728c3de218fa98d0349209f76cacf31b
                wild = await Meowth.create_role(server = ctx.message.server, name = entered_wild, hoist = False, mentionable = True)
                await asyncio.sleep(0.5)
            wild_number = pokemon_list.index(entered_wild) + 1
            wild_img_url = "http://floatzel.net/pokemon/black-white/sprites/images/{0}.png".format(str(wild_number))
            wild_embed = discord.Embed(title="Meowth! Click here for directions to the wild {0}!".format(entered_wild.capitalize()),url=wild_gmaps_link,description="This is just my best guess!",colour=discord.Colour(0x2ecc71))
            wild_embed.set_thumbnail(url=wild_img_url)
            await Meowth.send_message(ctx.message.channel, content="Meowth! Wild {0} reported by {1}! Details: {2}".format(wild.mention, ctx.message.author.mention, wild_details),embed=wild_embed)

"""A command for reporting a raid. This works the same way as the wild command but embeds the
icons of the boss's type weaknesses as custom emoji."""
@Meowth.command(pass_context=True)
async def raid(ctx):
    space1 = ctx.message.content.find(" ",6)
    if space1 == -1:
        await Meowth.send_message(ctx.message.channel, "Meowth! Give more details when reporting!")
        return
    else:
        entered_raid = ctx.message.content[6:space1].lower()
        raid_details = ctx.message.content[space1:]
        raid_details_list = raid_details.split()
        raid_gmaps_link = "https://www.google.com/maps/search/?api=1&query={0}+{1}+{2}".format('+'.join(raid_details_list), yourtown, yourstate)
        if entered_raid not in pokemon_list:
            await Meowth.send_message(ctx.message.channel, "Meowth! That's not a Pokemon! Check your spelling!")
            return
        if entered_raid not in list(raid_dict.keys()) and entered_raid in pokemon_list:
            await Meowth.send_message(ctx.message.channel, "Meowth! That Pokemon does not appear in raids!")
            return
        else:
            raid_details_list = raid_details.split(" ", 10)
            raid_channel_name = "{0}{1}".format(entered_raid, "-".join(raid_details_list))
            raid_channel = await Meowth.create_channel(ctx.message.server, raid_channel_name)
            raid = discord.utils.get(ctx.message.server.roles, name = entered_raid)
<<<<<<< HEAD
            if raid is None and entered_raid in pokemon_list:
=======
            if raid is None:
>>>>>>> abf1a131728c3de218fa98d0349209f76cacf31b
                raid = await Meowth.create_role(server = ctx.message.server, name = entered_raid, hoist = False, mentionable = True)
                await asyncio.sleep(0.5)
            raid_number = pokemon_list.index(entered_raid) + 1
            raid_img_url = "http://floatzel.net/pokemon/black-white/sprites/images/{0}.png".format(str(raid_number))
            raid_embed = discord.Embed(title="Meowth! Click here for directions to the raid!",url=raid_gmaps_link,description="Weaknesses: {0}".format(weakness_to_str(raid_dict[entered_raid])),colour=discord.Colour(0x2ecc71))
            raid_embed.set_thumbnail(url=raid_img_url)
            await Meowth.send_message(ctx.message.channel, content = "Meowth! {0} raid reported by {1}! Coordinate in {2}".format(raid.mention, ctx.message.author.mention, raid_channel.mention),embed=raid_embed)
            await asyncio.sleep(1) #Wait for the channel to be created.
            raidmsg = await Meowth.send_message(raid_channel, content = "Meowth! {0} raid reported by {1}! Coordinate here! Reply (not react) to this message with {2} to say you are on your way, or {3} if you are at the raid already!".format(raid.mention, ctx.message.author.mention, omw_id, here_id),embed=raid_embed)
            raidchannel_list.append(raid_channel)
                
"""Deletes any raid channel that is created after two hours and removes corresponding entries in waiting, omw, and
raidexpmsg lists.""" 
@Meowth.event
async def on_channel_create(channel):
    await asyncio.sleep(7200)
    if channel in raidchannel_list:
        raidchannel_list.remove(channel)
        for i in omw_list:
            if i[0] == channel:
                omw_list.remove(i)
        for j in waiting_list:
            if j[0] == channel:
                waiting_list.remove(j)
        await Meowth.delete_channel(channel)
    
"""A command for removing the role for wanting a Pokemon."""
@Meowth.command(pass_context=True)
async def unwant(ctx):
    entered_unwant = ctx.message.content[8:].lower()
    role = discord.utils.get(ctx.message.server.roles, name=entered_unwant)
    if role is None and entered_unwant not in pokemon_list:
        await Meowth.send_message(ctx.message.channel, "Meowth! {0} is not a Pokemon! Check your spelling!".format(entered_unwant))
        return
    else:    
        await Meowth.remove_roles(ctx.message.author, role)
        unwant_number = pokemon_list.index(entered_unwant) + 1
        unwant_img_url = "http://floatzel.net/pokemon/black-white/sprites/images/{0}.png".format(str(unwant_number))
        unwant_embed = discord.Embed(colour=discord.Colour(0x2ecc71))
        unwant_embed.set_thumbnail(url=unwant_img_url)
        await Meowth.send_message(ctx.message.channel, content="Meowth! Got it! {0} no longer wants {1}".format(ctx.message.author.mention, entered_unwant.capitalize()),embed=unwant_embed)

"""Meowth watches for messages that start with the omw, here, unomw, unhere emoji. For omw and here, Meowth
counts the number of emoji and adds that user and the number to the omw and waiting lists. For unomw and unhere,
Meowth removes that user and their number from the list regardless of emoji count. The emoji here will have to be
changed to fit the emoji ids in your server."""
@Meowth.event
async def on_message(message):
    if message.channel in raidchannel_list and message.content.startswith(omw_id):
        # TODO: handle case where a user sends :omw:
        # after they've already sent :here:
        await Meowth.send_message(message.channel, "Meowth! {0} is on the way with {1} trainers!".format(message.author.mention,message.content.count(omw_id)))
        # Check if trainer is already in the list.
        # Specifically, look for a matching entry of [channel, author.mention]
        already_listed = False
        for a in range(len(omw_list)):
            # If already listed, replace previous count with the new one
            if omw_list[a][0] == message.channel and omw_list[a][1] == message.author.mention:
                already_listed = True
                omw_list[a] = (message.channel,message.author.mention,message.content.count(omw_id))
        # If not already listed, create a new entry
        if not already_listed:
            omw_list.append((message.channel,message.author.mention,message.content.count(omw_id)))
        return
    # TODO: there's no relation between the :here: count and the :omw: count.
    # For example, if a user is :omw: with 4, they have to send 4x :here:
    # or else they only count as 1 person waiting
    if message.channel in raidchannel_list and message.content.startswith(here_id):
        await Meowth.send_message(message.channel, "Meowth! {0} is at the raid with {1} trainers!".format(message.author.mention, message.content.count(here_id)))
        # Check if trainer is already in the list.
        # Specifically, look for a matching entry of [channel, author.mention]
        already_listed = False
        for a in range(len(waiting_list)):
            # If already listed, replace previous count with the new one
            if waiting_list[a][0] == message.channel and waiting_list[a][1] == message.author.mention:
                already_listed = True
                waiting_list[a] = (message.channel,message.author.mention,message.content.count(here_id))
        # If not already listed, create a new entry
        if not already_listed:
            waiting_list.append((message.channel,message.author.mention,message.content.count(here_id)))
        for b in omw_list:
            if b[0] == message.channel and b[1] == message.author.mention:
                omw_list.remove(b)
                break
        return
    if message.channel in raidchannel_list and message.content.startswith(unhere_id):
        for c in waiting_list:
            if c[0] == message.channel and c[1] == message.author.mention:
                await Meowth.send_message(message.channel, "Meowth! {0} and the trainers with them have left the raid!".format(message.author.mention))
                waiting_list.remove(c)
                break
        return
    if message.channel in raidchannel_list and message.content.startswith(unomw_id):
        for d in omw_list:
            if d[0] == message.channel and d[1] == message.author.mention:
                await Meowth.send_message(message.channel, "Meowth! {0} and the trainers with them are no longer on their way!".format(message.author.mention))
                omw_list.remove(d)
                break
        return
    await Meowth.process_commands(message)
    
"""A command to set an end time for a raid. Works only in raid channels, can be set or overridden by anyone.
Meowth displays the end time in HH:MM local time and saves that message in raidexpmsg_list."""
@Meowth.command(pass_context = True)
async def timerset(ctx):
    if ctx.message.channel in raidchannel_list:
        for d in raidexpmsg_list:
            if d[0] == ctx.message.channel:
                raidexpmsg_list.remove(d)
        ticks = time.time()
        h, m = ctx.message.content[10:].split(':')
        s = int(h) * 3600 + int(m) * 60
        expire = ticks + s
        localexpire = time.localtime(expire)
        raidexpmsg = await Meowth.send_message(ctx.message.channel, "Meowth! This raid will end at {0}!".format(strftime("%I:%M", localexpire)))
        raidexpmsg_list.append((ctx.message.channel, raidexpmsg))
        
"""A command to retrieve and resend previously set expire time for a raid."""
@Meowth.command(pass_context=True)
async def timer(ctx):
    if ctx.message.channel in raidchannel_list:
        for e in raidexpmsg_list:
            if e[0] == ctx.message.channel:
                await Meowth.send_message(ctx.message.channel, e[1].content)
                return

"""A command to list the number and users who are on the way to the raid."""
@Meowth.command(pass_context=True)
async def otw(ctx):
    if ctx.message.channel in raidchannel_list:
        ctx_omwcount = 0
        ctx_omwlist = []
        for (channel, mention, count) in omw_list:
            if channel == ctx.message.channel:
                ctx_omwcount += count
                ctx_omwlist.append(mention)
        await asyncio.sleep(1)
        
        # If at least 1 person is on the way,
        # add an extra message indicating who it is.
        otw_exstr = ""
        if ctx_omwcount > 0:
            otw_exstr = " including {0} and the people with them! Be considerate and wait for them if possible".format(", ".join(ctx_omwlist))
        await Meowth.send_message(ctx.message.channel, "Meowth! {0} on the way{1}!".format(str(ctx_omwcount), otw_exstr))

"""A command to list the number and users who are waiting at the raid."""
@Meowth.command(pass_context=True)
async def waiting(ctx):
    if ctx.message.channel in raidchannel_list:
        ctx_waitingcount = 0
        ctx_waitinglist = []
        for (channel, mention, count) in waiting_list:
            if channel == ctx.message.channel:
                ctx_waitingcount += count
                ctx_waitinglist.append(mention)
        await asyncio.sleep(1)
        
        # If at least 1 person is waiting,
        # add an extra message indicating who it is.
        waiting_exstr = ""
        if ctx_waitingcount > 0:
            waiting_exstr = " including {0} and the people with them! Be considerate and let them know if and when you'll be there".format(", ".join(ctx_waitinglist))
        await Meowth.send_message(ctx.message.channel, "Meowth! {0} waiting at the raid{1}!".format(str(ctx_waitingcount), waiting_exstr))
        # await Meowth.send_message(ctx.message.channel, "Meowth! {0} waiting at the raid including {1} and the people with them! Be considerate and let them know if and when you'll be there!".format(str(ctx_waitingcount),", ".join(ctx_waitinglist)))

"""A command that removes all users currently waiting to start the raid from the waiting list. Users who are waiting
for a second group must reannounce with the here emoji."""
@Meowth.command(pass_context=True)
async def starting(ctx):
    if ctx.message.channel in raidchannel_list:
        ctx_startinglist = []
        for a in waiting_list:
            if a[0] == ctx.message.channel:
                ctx_startinglist.append(a[1])
                waiting_list.remove(a)
        await asyncio.sleep(1)
        
        starting_str = "Meowth! The group that was waiting is starting the raid! Trainers {0}, please respond with {1} if you are waiting for another group!".format(", ".join(ctx_startinglist), here_id)
        if len(ctx_startinglist) == 0:
            starting_str = "Meowth! How can you start when there's no one waiting at this raid!?"
        await Meowth.send_message(ctx.message.channel, starting_str)
        


            
    

            



            
    


Meowth.run(bot_token)
