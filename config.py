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

# Used for Meowth's welcome message. New members are
# directed check out this #channel first.
welcome_channel = 'announcements'

# Used for Meowth's welcome message. New members are
# directed to ask an @admin if they have questions
admin_role = 'admin'

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
    'normal'   : "<:normal:id>",
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
