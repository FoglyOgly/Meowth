import re

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

import discord

def get_match(word_list: list, word: str, score_cutoff: int = 60):
    """Uses fuzzywuzzy to see if word is close to entries in word_list

    Returns a tuple of (MATCH, SCORE)
    """
    result = process.extractOne(
        word, word_list, scorer=fuzz.ratio, score_cutoff=score_cutoff)
    if not result:
        return (None, None)
    return result

def colour(*args):
    """Returns a discord Colour object.

    Pass one as an argument to define colour:
        `int` match colour value.
        `str` match common colour names.
        `discord.Guild` bot's guild colour.
        `None` light grey.
    """
    arg = args[0] if args else None
    if isinstance(arg, int):
        return discord.Colour(arg)
    if isinstance(arg, str):
        colour = arg
        try:
            return getattr(discord.Colour, colour)()
        except AttributeError:
            return discord.Colour.lighter_grey()
    if isinstance(arg, discord.Guild):
        return arg.me.colour
    else:
        return discord.Colour.lighter_grey()

def get_embed_index(embed_fields, field_names: list):
    """Returns an index of embed filed name present in filed_names.

    If none of filed_names is present in embed_fields None is returned.
    """
    index = 0
    for embed_proxy in embed_fields:
        if embed_proxy.name in field_names:
            return index
        index += 1
    return None

def add_embed_field(newembed, oldembed, fields_names: list, name_overrride=None, value_override=None, inline_override=None):
    """Return newembed with possibly new field added.

    New filed is added if any of field_names is present in oldembed. By default new filed added has
    the values from oldembed, but each filed can be overriden.
    """
    index = get_embed_index(oldembed.fields, fields_names)
    if index is not None:
        new_name = oldembed.fields[index].name if name_overrride is None else name_overrride
        new_value = oldembed.fields[index].value if value_override is None else value_override
        new_inline = oldembed.fields[index].inline if inline_override is None else inline_override
        newembed.add_field(name=new_name, value=new_value, inline=new_inline)
    return newembed

def update_embed_field(newembed, oldembed, fields_names: list, name_overrride=None, value_override=None, inline_override=None):
    """Return newembed with possibly updated field.

    The filed gets updated if any of field_names is present in oldembed. By default new filed is updated with
    the values from oldembed, but each filed can be overriden.
    """
    index = get_embed_index(oldembed.fields, fields_names)
    if index is not None:
        new_name = oldembed.fields[index].name if name_overrride is None else name_overrride
        new_value = oldembed.fields[index].value if value_override is None else value_override
        new_inline = oldembed.fields[index].inline if inline_override is None else inline_override
        newembed.set_field_at(index, name=new_name, value=new_value, inline=new_inline)
    return newembed

def make_embed(msg_type='', title=None, icon=None, content=None,
               msg_colour=None, guild=None, title_url=None,
               thumbnail='', image=''):
    """Returns a formatted discord embed object.

    Define either a type or a colour.
    Types are:
    error, warning, info, success, help.
    """
    embed_types = {
        'error':{
            'icon':'https://i.imgur.com/juhq2uJ.png',
            'colour':'red'
        },
        'warning':{
            'icon':'https://i.imgur.com/4JuaNt9.png',
            'colour':'gold'
        },
        'info':{
            'icon':'https://i.imgur.com/wzryVaS.png',
            'colour':'blue'
        },
        'success':{
            'icon':'https://i.imgur.com/ZTKc3mr.png',
            'colour':'green'
        },
        'help':{
            'icon':'https://i.imgur.com/kTTIZzR.png',
            'colour':'blue'
        }
    }
    if msg_type in embed_types.keys():
        msg_colour = embed_types[msg_type]['colour']
        icon = embed_types[msg_type]['icon']
    if guild and not msg_colour:
        msg_colour = colour(guild)
    else:
        if not isinstance(msg_colour, discord.Colour):
            msg_colour = colour(msg_colour)
    embed = discord.Embed(description=content, colour=msg_colour)
    if not title_url:
        title_url = discord.Embed.Empty
    if not icon:
        icon = discord.Embed.Empty
    if title:
        embed.set_author(name=title, icon_url=icon, url=title_url)
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    if image:
        embed.set_image(url=image)
    return embed

def bold(msg: str):
    """Format to bold markdown text"""
    return f'**{msg}**'

def italics(msg: str):
    """Format to italics markdown text"""
    return f'*{msg}*'

def bolditalics(msg: str):
    """Format to bold italics markdown text"""
    return f'***{msg}***'

def code(msg: str):
    """Format to markdown code block"""
    return f'```{msg}```'

def pycode(msg: str):
    """Format to code block with python code highlighting"""
    return f'```py\n{msg}```'

def ilcode(msg: str):
    """Format to inline markdown code"""
    return f'`{msg}`'

def convert_to_bool(argument):
    lowered = argument.lower()
    if lowered in ('yes', 'y', 'true', 't', '1', 'enable', 'on'):
        return True
    elif lowered in ('no', 'n', 'false', 'f', '0', 'disable', 'off'):
        return False
    else:
        return None

def sanitize_channel_name(name):
    """Converts a given string into a compatible discord channel name."""
    # Remove all characters other than alphanumerics,
    # dashes, underscores, and spaces
    ret = re.sub(r'[^a-zA-Z0-9ąćęłńóśżźĄĆĘŁŃÓŚŻŹ _\\-]', '', name)
    # Replace spaces with dashes
    ret = ret.replace(' ', '-')
    return ret

async def get_raid_help(prefix, avatar, user=None):
    helpembed = discord.Embed(colour=discord.Colour.lighter_grey())
    helpembed.set_author(name="Raid Coordination Help", icon_url=avatar)
    helpembed.add_field(
        name="Key",
        value="<> denote required arguments, [] denote optional arguments",
        inline=False)
    helpembed.add_field(
        name="Raid MGMT Commands",
        value=(
            f"`{prefix}raid <species>`\n"
            f"`{prefix}weather <weather>`\n"
            f"`{prefix}timerset <minutes>`\n"
            f"`{prefix}starttime <time>`\n"
            "`<google maps link>`\n"
            "**RSVP**\n"
            f"`{prefix}(i/c/h)...\n"
            "[total]...\n"
            "[team counts]`\n"
            "**Lists**\n"
            f"`{prefix}list [status]`\n"
            f"`{prefix}list [status] tags`\n"
            f"`{prefix}list teams`\n\n"
            f"`{prefix}starting [team]`"))
    helpembed.add_field(
        name="Description",
        value=(
            "`Hatches Egg channel`\n"
            "`Sets in-game weather`\n"
            "`Sets hatch/raid timer`\n"
            "`Sets start time`\n"
            "`Updates raid location`\n\n"
            "`interested/coming/here`\n"
            "`# of trainers`\n"
            "`# from each team (ex. 3m for 3 Mystic)`\n\n"
            "`Lists trainers by status`\n"
            "`@mentions trainers by status`\n"
            "`Lists trainers by team`\n\n"
            "`Moves trainers on 'here' list to a lobby.`"))
    if not user:
        return helpembed
    await user.send(embed=helpembed)
