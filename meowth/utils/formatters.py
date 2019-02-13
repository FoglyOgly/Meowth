import asyncio
import functools

from io import BytesIO

import aiohttp

from colorthief import ColorThief

import discord


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
    return await url_color(user.avatar_url_as(static_format='png'))

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
            await message.clear_reactions()
        return payload
    except asyncio.TimeoutError:
        for message in message_list:
            await message.clear_reactions()
        return

def mc_emoji(length: int):
    if length > 10:
        return None
    elif length < 10:
        return [f'{i}\u20e3' for i in range(1, length+1)]
    else:
        return [f'{i}\u20e3' for i in range(length+1)]

def mc_embed(choice_dict: dict):
    embed = discord.Embed()
    items = [f'{k}: {v}' for k,v in choice_dict.items()] 
    embed.add_field(name='Choices', value='\n'.join(items))
    return embed

def perms_or(channel_list: list):
    overwrite_dict = {}
    pair_dict = {}
    for channel in channel_list:
        for overwrite in channel.overwrites:
            key = overwrite[0]
            a, d = overwrite[1].pair()
            x, y = pair_dict.get(key, (0,2146958591))
            x |= a
            y &= d
            pair_dict[key] = (x, y)
    for key in pair_dict:
        x, y = pair_dict[key]
        a, d = (discord.Permissions(permissions=x), discord.Permissions(permissions=y))
        overwrite = discord.PermissionOverwrite.from_pair(a, d)
        overwrite_dict[key] = overwrite
    return overwrite_dict
            