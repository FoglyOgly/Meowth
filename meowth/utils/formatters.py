import asyncio
import functools

from io import BytesIO

import aiohttp
from datetime import datetime

from colorthief import ColorThief

import discord

emoji_letters = ['🇦','🇧','🇨','🇩','🇪','🇫','🇬','🇭','🇮','🇯','🇰','🇱',
    '🇲','🇳','🇴','🇵','🇶','🇷','🇸','🇹','🇺','🇻','🇼','🇽','🇾','🇿'
]

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

def make_embed(msg_type='', title=None, icon=None, content='',
               msg_colour=None, guild=None, title_url=None,
               thumbnail='', image='', fields=None, footer=None,
               footer_icon=None, inline=True):
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

async def _read_image_from_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.read()

async def _dominant_color_from_url(url):
    """Returns an rgb tuple consisting the dominant color given a image url."""
    with BytesIO(await _read_image_from_url(url)) as fp:
        loop = asyncio.get_event_loop()
        get_colour = functools.partial(ColorThief(fp).get_color, quality=1)
        return await loop.run_in_executor(None, get_colour)

async def url_color(url):
    return discord.Colour.from_rgb(*(await _dominant_color_from_url(url)))

async def user_color(user):
    return await url_color(user.avatar.with_format('png'))

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

async def ask(bot, message_list, user_list=None, timeout=60, *, react_list=['✅', '❎']):
    if user_list and type(user_list) != list:
        user_list = [user_list]
    message_id_list = [x.id for x in message_list]
    
    def check(payload):
        user_id = payload.user_id
        message_id = payload.message_id
        if payload.emoji.is_custom_emoji():
            emoji = payload.emoji.id
        else:
            emoji = str(payload.emoji)
        if user_list and type(user_list) is list:
            return (user_id in user_list) and (message_id in message_id_list) and (emoji in react_list)
        elif not user_list:
            return (user_id != bot.user.id) and (message_id in message_id_list) and (emoji in react_list)
    for r in react_list:
        if isinstance(r, int):
            r = bot.get_emoji(r)
        for message in message_list:
            await message.add_reaction(r)
    try:
        payload = await bot.wait_for('raw_reaction_add', check=check, timeout=timeout)
        for message in message_list:
            try:
                await message.clear_reactions()
            except discord.Forbidden:
                pass
        return payload
    except asyncio.TimeoutError:
        for message in message_list:
            try:
                await message.clear_reactions()
            except:
                pass
        return

async def poll(bot, message_list, timeout=3600, *, react_list=['✅', '❎']):
    for r in react_list:
        if isinstance(r, int):
            r = bot.get_emoji(r)
        for message in message_list:
            await message.add_reaction(r)
    try:
        await asyncio.sleep(timeout)
    except asyncio.CancelledError:
        raise
    finally:
        react_dict = {}
        for r in react_list:
            if isinstance(r, int):
                r = bot.get_emoji(r)
            react_dict[r] = 0
        for message in message_list:
            msg = await message.channel.fetch_message(message.id)
            for reaction in msg.reactions:
                if reaction.emoji in react_dict:
                    react_dict[reaction.emoji] += reaction.count
        results = [(k, react_dict[k]) for k in sorted(react_dict, key=react_dict.get, reverse=True)]
        return results


def mc_emoji(length: int):
    return [emoji_letters[i] for i in range(length)]

def mc_embed(choice_dict: dict):
    embed = discord.Embed()
    items = [f'{k}: {v}' for k,v in choice_dict.items()] 
    embed.add_field(name='Choices', value='\n'.join(items))
    return embed

def perms_or(channel_list: list):
    overwrite_dict = {}
    pair_dict = {}
    for channel in channel_list:
        for key in channel.channel.overwrites:
            a, d = channel.channel.overwrites[key].pair()
            x, y = pair_dict.get(key, (0,2146958591))
            x |= a.value
            y &= d.value
            pair_dict[key] = (x, y)
    for key in pair_dict:
        x, y = pair_dict[key]
        a, d = (discord.Permissions(permissions=x), discord.Permissions(permissions=y))
        overwrite = discord.PermissionOverwrite.from_pair(a, d)
        overwrite_dict[key] = overwrite
    return overwrite_dict

def deleted_message_embed(bot, data):
    guild_id = data['guild_id']
    guild = bot.get_guild(guild_id)
    author_id = data['author_id']
    display_name = f"<@!{author_id}>"
    content = data['content']
    embed = make_embed(title=display_name, content=content)
    sent = data['sent']
    sentdt = datetime.fromtimestamp(sent)
    embed.timestamp = sentdt
    return embed

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
            f"`{prefix}weather <weather>`\n"
            f"`{prefix}timerset <minutes>`\n"
            f"`{prefix}group <minutes>`\n"
            "**RSVP**\n"
            f"`{prefix}(i/c/h)...\n"
            "[total]...\n"
            "[team counts]`\n"
            "**Lists**\n"
            f"`{prefix}list [status]`\n"
            f"`{prefix}list [status] tags`\n"
            f"`{prefix}list teams`\n\n"
            f"`{prefix}starting`"))
    helpembed.add_field(
        name="Description",
        value=(
            "`Sets in-game weather`\n"
            "`Sets hatch/raid timer`\n"
            "`Creates a group`\n\n"
            "`interested/coming/here`\n"
            "`# of trainers`\n"
            "`# from each team (ex. 3m for 3 Mystic)`\n\n"
            "`Lists trainers by status`\n"
            "`@mentions trainers by status`\n"
            "`Lists trainers by team`\n\n"
            "`Moves trainers in current group to a lobby.`"))
    if not user:
        return helpembed
    await user.send(embed=helpembed)