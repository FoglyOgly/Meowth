import re

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

import discord
import asyncio

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

def make_embed(msg_type='', title=None, icon=None, content=None,
               msg_colour=None, guild=None, title_url=None,
               thumbnail='', image='', fields=None, footer=None,
               footer_icon=None, inline=False):
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
    if fields:
        for key, value in fields.items():
            ilf = inline
            if not isinstance(value, str):
                ilf = value[0]
                value = value[1]
            embed.add_field(name=key, value=value, inline=ilf)
    if footer:
        footer = {'text':footer}
        if footer_icon:
            footer['icon_url'] = footer_icon
        embed.set_footer(**footer)
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
    ret = re.sub('[^a-zA-Z0-9 _\\-]', '', name)
    # Replace spaces with dashes
    ret = ret.replace(' ', '-')
    return ret

async def get_raid_help(prefix, avatar, user=None):
    helpembed = discord.Embed(colour=discord.Colour.lighter_grey())
    helpembed.set_author(name="Raid Coordination Help", icon_url=avatar)
    helpembed.add_field(
        name="Key",
        value="<> indique un argument obligatoire, [] indique un argument optionel",
        inline=False)
    helpembed.add_field(
        name="Raid MGMT Commands/Description",
        value=(
            f"`{prefix}raid <species>`\n"
            "`-> Indique le PKM éclos`\n"
            f"`{prefix}weather <weather>`\n"
            "`-> Indique la météo du jeu`\n"
            f"`{prefix}timerset <minutes>`\n"
            "`-> Indique le temps avant éclosion/dépop (en MM)`\n"
            f"`{prefix}starttime <time>`\n"
            "`-> Indique l'heure de début (HH:MM)`\n"
            "`<lien google maps>`\n"
            "`-> Mets à jour l'emplacement`\n"
            "**RSVP**\n"
            f"`{prefix}(i/c/h) [nb total] [nb par équipe]`\n"
            "`-> (i/c/h) interested/coming/here`\n"
            "`-> [nb total] de dresseurs présents`\n"
            "`-> [nb par équipe] pour chaque équipe (ex. 3m for 3 Mystic)`\n"
            "**Lists**\n"
            f"`{prefix}list [status]`\n"
            "`-> Liste les dresseurs par status`\n"
            f"`{prefix}list [status] tags`\n"
            "`-> @mentions les dresseurs par status`\n"
            f"`{prefix}list teams`\n"
            "`-> Liste les dresseurs par équipe`\n\n"
            f"`{prefix}starting [team]`\n"
            "`-> Déplace les dresseurs de la liste 'here' à lobby.`"))
    if not user:
        return helpembed
    await user.send(embed=helpembed)

def get_number(bot, pkm_name):
    try:
        number = bot.pkmn_info['pokemon_list'].index(pkm_name) + 1
    except ValueError:
        number = None
    return number

def get_name(bot, pkmn_number):
    pkmn_number = int(pkmn_number) - 1
    try:
        name = bot.pkmn_info['pokemon_list'][pkmn_number]
    except IndexError:
        name = None
    return name

def get_raidlist(bot):
    raidlist = []
    for level in bot.raid_info['raid_eggs']:
        for pokemon in bot.raid_info['raid_eggs'][level]['pokemon']:
            raidlist.append(pokemon)
            raidlist.append(get_name(pokemon).lower())
    return raidlist

def get_level(bot, pkmn):
    if str(pkmn).isdigit():
        pkmn_number = pkmn
    else:
        pkmn_number = get_number(bot, pkmn)
    for level in bot.raid_info['raid_eggs']:
        for level, pkmn_list in bot.raid_info['raid_eggs'].items():
            if pkmn_number in pkmn_list["pokemon"]:
                return level

async def ask(bot, message, user_list=None, timeout=60, *, react_list=['✅', '❎']):
    if user_list and type(user_list) != __builtins__.list:
        user_list = [user_list]
    def check(reaction, user):
        if user_list and type(user_list) is __builtins__.list:
            return (user.id in user_list) and (reaction.message.id == message.id) and (reaction.emoji in react_list)
        elif not user_list:
            return (user.id != message.author.id) and (reaction.message.id == message.id) and (reaction.emoji in react_list)
    for r in react_list:
        await asyncio.sleep(0.25)
        await message.add_reaction(r)
    try:
        reaction, user = await bot.wait_for('reaction_add', check=check, timeout=timeout)
        return reaction, user
    except asyncio.TimeoutError:
        await message.clear_reactions()
        return
