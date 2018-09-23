
import asyncio
import copy
import datetime
import functools
import gettext
import io
import json
import os
import pickle
import re
import sys
import tempfile
import textwrap
import time
import traceback

from contextlib import redirect_stdout
from io import BytesIO
from operator import itemgetter
from time import strftime

import aiohttp
import dateparser
import hastebin
from dateutil import tz
from dateutil.relativedelta import relativedelta

import discord
from discord.ext import commands

from meowth import checks
from meowth import pkmn_match
from meowth import utils
from meowth.bot import MeowthBot
from meowth.errors import custom_error_handling
from meowth.logs import init_loggers

logger = init_loggers()

def _get_prefix(bot, message):
    guild = message.guild
    try:
        prefix = bot.guild_dict[guild.id]['configure_dict']['settings']['prefix']
    except (KeyError, AttributeError):
        prefix = None
    if not prefix:
        prefix = bot.config['default_prefix']
    return commands.when_mentioned_or(prefix)(bot, message)

Meowth = MeowthBot(
    command_prefix=_get_prefix, case_insensitive=True,
    activity=discord.Game(name="Pokemon Go"))

custom_error_handling(Meowth, logger)
try:
    with open(os.path.join('data', 'serverdict'), 'rb') as fd:
        Meowth.guild_dict = pickle.load(fd)
    logger.info('Serverdict Loaded Successfully')
except OSError:
    logger.info('Serverdict Not Found - Looking for Backup')
    try:
        with open(os.path.join('data', 'serverdict_backup'), 'rb') as fd:
            Meowth.guild_dict = pickle.load(fd)
        logger.info('Serverdict Backup Loaded Successfully')
    except OSError:
        logger.info('Serverdict Backup Not Found - Creating New Serverdict')
        Meowth.guild_dict = {

        }
        with open(os.path.join('data', 'serverdict'), 'wb') as fd:
            pickle.dump(Meowth.guild_dict, fd, (- 1))
        logger.info('Serverdict Created')


guild_dict = Meowth.guild_dict


config = {}
pkmn_info = {}
type_chart = {}
type_list = []
raid_info = {}

active_raids = []
active_wilds = []
# Append path of this script to the path of
# config files which we're loading.
# Assumes that config files will always live in the same directory.
script_path = os.path.dirname(os.path.realpath(__file__))
"""
Helper functions
"""


def load_config():
    global config
    global pkmn_info
    global pkmn_info_reference
    global type_chart
    global type_list
    global raid_info
    # Load configuration
    with open('config.json', 'r') as fd:
        config = json.load(fd)
    # Set up message catalog access
    language = gettext.translation(
        'meowth', localedir='locale', languages=[config['bot-language']])
    language.install()
    pokemon_language = [config['pokemon-language']]
    pokemon_path_source = os.path.join(
        'locale', '{0}', 'pkmn.json').format(config['pokemon-language'])
    raid_path_source = os.path.join('data', 'raid_info.json')
    # Load Pokemon list and raid info
    with open(pokemon_path_source, 'r', encoding='utf-8') as fd:
        pkmn_info = json.load(fd)
    if 'en' != config['pokemon-language']:
         pokemon_path_source_reference = os.path.join('locale', 'en', 'pkmn.json')
         with open(pokemon_path_source_reference, 'r', encoding='utf-8') as fd:
            pkmn_info_reference = json.load(fd)
    else:
         pkmn_info_reference = pkmn_info
    with open(raid_path_source, 'r', encoding='utf-8') as fd:
        raid_info = json.load(fd)
    # Load type information
    with open(os.path.join('data', 'type_chart.json'), 'r') as fd:
        type_chart = json.load(fd)
    with open(os.path.join('data', 'type_list.json'), 'r') as fd:
        type_list = json.load(fd)
    # Set spelling dictionary to our list of Pokemon
    pkmn_match.set_list(pkmn_info['pokemon_list'])
    return (pokemon_path_source, raid_path_source)

pkmn_path, raid_path = load_config()

Meowth.pkmn_info = pkmn_info
Meowth.raid_info = raid_info
Meowth.type_list = type_list
Meowth.type_chart = type_chart

Meowth.config = config
Meowth.pkmn_info_path = pkmn_path
Meowth.raid_json_path = raid_path

default_exts = ['datahandler', 'tutorial', 'silph', 'utilities', 'gymmatching', 'pokemon', 'trade']

for ext in default_exts:
    try:
        Meowth.load_extension(f"meowth.exts.{ext}")
    except Exception as e:
        print(f'**Error when loading extension {ext}:**\n{type(e).__name__}: {e}')
    else:
        if 'debug' in sys.argv[1:]:
            print(f'Loaded {ext} extension.')

@Meowth.command(name='load')
@checks.is_owner()
async def _load(ctx, *extensions):
    for ext in extensions:
        try:
            ctx.bot.unload_extension(f"meowth.exts.{ext}")
            ctx.bot.load_extension(f"meowth.exts.{ext}")
        except Exception as e:
            error_title = _('**Error when loading extension')
            await ctx.send(f'{error_title} {ext}:**\n'
                           f'{type(e).__name__}: {e}')
        else:
            await ctx.send(_('**Extension {ext} Loaded.**\n').format(ext=ext))

@Meowth.command(name='unload')
@checks.is_owner()
async def _unload(ctx, *extensions):
    exts = [e for e in extensions if f"exts.{e}" in Meowth.extensions]
    for ext in exts:
        ctx.bot.unload_extension(f"exts.{ext}")
    s = 's' if len(exts) > 1 else ''
    await ctx.send(_("**Extension{plural} {est} unloaded.**\n").format(plural=s, est=', '.join(exts)))

# Given a Pokemon name, return a list of its
# weaknesses as defined in the type chart

def get_type(guild, pkmn_number):
    pkmn_number = int(pkmn_number) - 1
    types = type_list[pkmn_number]
    ret = []
    for type in types:
        ret.append(parse_emoji(guild, config['type_id_dict'][type.lower()]))
    return ret

def get_name(pkmn_number):
    pkmn_number = int(pkmn_number) - 1
    try:
        name = pkmn_info['pokemon_list'][pkmn_number]
    except IndexError:
        name = None
    return name

def get_number(pkm_name):
    try:
        number = pkmn_info['pokemon_list'].index(pkm_name) + 1
    except ValueError:
        number = None
    return number

def get_level(pkmn, max_lvl=5):
    if str(pkmn).isdigit():
        pkmn_number = pkmn
    else:
        pkmn_number = get_number(pkmn)
    for level in raid_info['raid_eggs']:
        for level, pkmn_list in raid_info['raid_eggs'].items():
            if pkmn_number in pkmn_list["pokemon"]:
                if str(level).isdigit() and str(level) != str(min([max_lvl, int(level)])):
                    return str(max_lvl)
                return level

def get_raidlist():
    raidlist = []
    for level in raid_info['raid_eggs']:
        for pokemon in raid_info['raid_eggs'][level]['pokemon']:
            raidlist.append(pokemon)
            raidlist.append(get_name(pokemon).lower())
    return raidlist

# Given a Pokemon name, return a list of its
# weaknesses as defined in the type chart

def get_weaknesses(species):
    # Get the Pokemon's number
    number = pkmn_info['pokemon_list'].index(species)
    # Look up its type
    pk_type = type_list[number]

    # Calculate sum of its weaknesses
    # and resistances.
    # -2 == immune
    # -1 == NVE
    #  0 == neutral
    #  1 == SE
    #  2 == double SE
    type_eff = {}
    for type in pk_type:
        for atk_type in type_chart[type]:
            if atk_type not in type_eff:
                type_eff[atk_type] = 0
            type_eff[atk_type] += type_chart[type][atk_type]
    ret = []
    for (type, effectiveness) in sorted(type_eff.items(), key=(lambda x: x[1]), reverse=True):
        if effectiveness == 1:
            ret.append(type.lower())
        elif effectiveness == 2:
            ret.append(type.lower() + 'x2')
    return ret

# Given a list of weaknesses, return a
# space-separated string of their type IDs,
# as defined in the type_id_dict

def weakness_to_str(guild, weak_list):
    ret = ''
    for weakness in weak_list:

        x2 = ''
        if weakness[(- 2):] == 'x2':
            weakness = weakness[:(- 2)]
            x2 = 'x2'
        # Append to string
        ret += (parse_emoji(guild,
                config['type_id_dict'][weakness]) + x2) + ' '
    return ret

# Convert an arbitrary string into something which
# is acceptable as a Discord channel name.

def sanitize_channel_name(name):
    # Remove all characters other than alphanumerics,
    # dashes, underscores, and spaces
    ret = re.sub('[^a-zA-Z0-9 _\\-]', '', name)
    # Replace spaces with dashes
    ret = ret.replace(' ', '-')
    return ret

# Given a string, if it fits the pattern :emoji name:,
# and <emoji_name> is in the server's emoji list, then
# return the string <:emoji name:emoji id>. Otherwise,
# just return the string unmodified.

def parse_emoji(guild, emoji_string):
    if (emoji_string[0] == ':') and (emoji_string[(- 1)] == ':'):
        emoji = discord.utils.get(guild.emojis, name=emoji_string.strip(':'))
        if emoji:
            emoji_string = '<:{0}:{1}>'.format(emoji.name, emoji.id)
    return emoji_string

def print_emoji_name(guild, emoji_string):
    # By default, just print the emoji_string
    ret = ('`' + emoji_string) + '`'
    emoji = parse_emoji(guild, emoji_string)
    # If the string was transformed by the parse_emoji
    # call, then it really was an emoji and we should
    # add the raw string so people know what to write.
    if emoji != emoji_string:
        ret = ((emoji + ' (`') + emoji_string) + '`)'
    return ret

# Given an arbitrary string, create a Google Maps
# query using the configured hints

def create_gmaps_query(details, channel, type="raid"):
    if type == "raid" or type == "egg":
        report = "raid"
    else:
        report = type
    if "/maps" in details and "http" in details:
        mapsindex = details.find('/maps')
        newlocindex = details.rfind('http', 0, mapsindex)
        if newlocindex == (- 1):
            return
        newlocend = details.find(' ', newlocindex)
        if newlocend == (- 1):
            newloc = details[newlocindex:]
            return newloc
        else:
            newloc = details[newlocindex:newlocend + 1]
            return newloc
    details_list = details.split()
    #look for lat/long coordinates in the location details. If provided,
    #then channel location hints are not needed in the  maps query
    if re.match (r'^\s*-?\d{1,2}\.?\d*,\s*-?\d{1,3}\.?\d*\s*$', details): #regex looks for lat/long in the format similar to 42.434546, -83.985195.
        return "https://www.google.com/maps/search/?api=1&query={0}".format('+'.join(details_list))
    loc_list = guild_dict[channel.guild.id]['configure_dict'][report]['report_channels'][channel.id].split()
    return 'https://www.google.com/maps/search/?api=1&query={0}+{1}'.format('+'.join(details_list), '+'.join(loc_list))

# Given a User, check that it is Meowth's master

def check_master(user):
    return str(user) == config['master']

def check_server_owner(user, guild):
    return str(user) == str(guild.owner)

# Given a violating message, raise an exception
# reporting unauthorized use of admin commands

def raise_admin_violation(message):
    raise Exception(_('Received admin command {command} from unauthorized user, {user}!').format(
        command=message.content, user=message.author))

def spellcheck(word):
    suggestion = pkmn_match.get_pkmn(re.sub(r"[^A-Za-z0-9 ]+", '', word))
    # If we have a spellcheck suggestion
    if suggestion and suggestion != word:
        result = pkmn_info['pokemon_list'][suggestion]
        return result

async def autocorrect(entered_word, destination, author):
    msg = _("Meowth! **{word}** isn't a Pokemon!").format(word=entered_word.title())
    if spellcheck(entered_word) and (spellcheck(entered_word) != entered_word):
        msg += _(' Did you mean **{correction}**?').format(correction=spellcheck(entered_word).title())
        question = await destination.send(msg)
        if author:
            try:
                timeout = False
                res, reactuser = await ask(question, destination, author.id)
            except TypeError:
                timeout = True
            await question.delete()
            if timeout or res.emoji == '❎':
                return None
            elif res.emoji == '✅':
                return spellcheck(entered_word)
            else:
                return None
        else:
            return None
    else:
        question = await destination.send(msg)
        return

def do_template(message, author, guild):
    not_found = []

    def template_replace(match):
        if match.group(3):
            if match.group(3) == 'user':
                return '{user}'
            elif match.group(3) == 'server':
                return guild.name
            else:
                return match.group(0)
        if match.group(4):
            emoji = (':' + match.group(4)) + ':'
            return parse_emoji(guild, emoji)
        match_type = match.group(1)
        full_match = match.group(0)
        match = match.group(2)
        if match_type == '<':
            mention_match = re.search('(#|@!?|&)([0-9]+)', match)
            match_type = mention_match.group(1)[0]
            match = mention_match.group(2)
        if match_type == '@':
            member = guild.get_member_named(match)
            if match.isdigit() and (not member):
                member = guild.get_member(match)
            if (not member):
                not_found.append(full_match)
            return member.mention if member else full_match
        elif match_type == '#':
            channel = discord.utils.get(guild.text_channels, name=match)
            if match.isdigit() and (not channel):
                channel = guild.get_channel(match)
            if (not channel):
                not_found.append(full_match)
            return channel.mention if channel else full_match
        elif match_type == '&':
            role = discord.utils.get(guild.roles, name=match)
            if match.isdigit() and (not role):
                role = discord.utils.get(guild.roles, id=int(match))
            if (not role):
                not_found.append(full_match)
            return role.mention if role else full_match
    template_pattern = '(?i){(@|#|&|<)([^{}]+)}|{(user|server)}|<*:([a-zA-Z0-9]+):[0-9]*>*'
    msg = re.sub(template_pattern, template_replace, message)
    return (msg, not_found)

async def ask(message, destination, user_list=None, *, react_list=['✅', '❎']):
    if user_list and type(user_list) != __builtins__.list:
        user_list = [user_list]
    def check(reaction, user):
        if user_list and type(user_list) is __builtins__.list:
            return (user.id in user_list) and (reaction.message.id == message.id) and (reaction.emoji in react_list)
        elif not user_list:
            return (user.id != message.guild.me.id) and (reaction.message.id == message.id) and (reaction.emoji in react_list)
    for r in react_list:
        await asyncio.sleep(0.25)
        await message.add_reaction(r)
    try:
        reaction, user = await Meowth.wait_for('reaction_add', check=check, timeout=60)
        return reaction, user
    except asyncio.TimeoutError:
        await message.clear_reactions()
        return

def get_gyms(guild_id):
    gym_matching_cog = Meowth.cogs.get('GymMatching')
    if not gym_matching_cog:
        return None
    gyms = gym_matching_cog.get_gyms(guild_id)
    return gyms

async def gym_match_prompt(channel, author_id, gym_name, gyms):
    gym_matching_cog = Meowth.cogs.get('GymMatching')
    match, score = gym_matching_cog.gym_match(gym_name, gyms)
    if not match:
        return None
    if score < 80:
        try:
            question = _("Did you mean: '{0}'").format(match)
            q_msg = await channel.send(question)
            reaction, __ = await ask(q_msg, channel, author_id)
        except TypeError:
            return None
        if not reaction:
            return None
        if reaction.emoji == '✅':
            await q_msg.delete()
            return match
        return None
    return match

async def letter_case(iterable, find, *, limits=None):
    servercase_list = []
    lowercase_list = []
    for item in iterable:
        if not item.name:
            continue
        elif item.name and (not limits or item.name.lower() in limits):
            servercase_list.append(item.name)
            lowercase_list.append(item.name.lower())
    if find.lower() in lowercase_list:
        index = lowercase_list.index(find.lower())
        return servercase_list[index]
    else:
        return None

def get_category(channel, level, category_type="raid"):
    guild = channel.guild
    if category_type == "raid" or category_type == "egg":
        report = "raid"
    else:
        report = category_type
    catsort = guild_dict[guild.id]['configure_dict'][report].get('categories', None)
    if catsort == "same":
        return channel.category
    elif catsort == "region":
        category = discord.utils.get(guild.categories,id=guild_dict[guild.id]['configure_dict'][report]['category_dict'][channel.id])
        return category
    elif catsort == "level":
        category = discord.utils.get(guild.categories,id=guild_dict[guild.id]['configure_dict'][report]['category_dict'][level])
        return category
    else:
        return None

def get_raidtext(type, pkmn, level, member, channel):
    if type == "raid":
        roletest = ""
        role = discord.utils.get(channel.guild.roles, name=pkmn)
        if role:
            roletest = _("{pokemon} - ").format(pokemon=role.mention)
            raidtext = _("{roletest}Meowth! {pkmn} raid reported by {member} in {channel}! Coordinate here!\n\nFor help, react to this message with the question mark and I will DM you a list of commands you can use!").format(roletest=roletest, pkmn=pkmn.title(), member=member.mention, channel=channel.mention)
    elif type == "egg":
        raidtext = _("Meowth! Level {level} raid egg reported by {member} in {channel}! Coordinate here!\n\nFor help, react to this message with the question mark and I will DM you a list of commands you can use!").format(level=level, member=member.mention, channel=channel.mention)
    elif type == "exraid":
        raidtext = _("Meowth! EX raid reported by {member} in {channel}! Coordinate here!\n\nFor help, react to this message with the question mark and I will DM you a list of commands you can use!").format(member=member.mention, channel=channel.mention)
    return raidtext

async def create_raid_channel(type, pkmn, level, details, report_channel):
    guild = report_channel.guild
    if type == "exraid":
        name = _("exraid-egg-")
        raid_channel_overwrite_list = channel.overwrites
        if guild_dict[guild.id]['configure_dict']['invite']['enabled']:
            if guild_dict[guild.id]['configure_dict']['exraid']['permissions'] == "everyone":
                everyone_overwrite = (guild.default_role, discord.PermissionOverwrite(send_messages=False))
                raid_channel_overwrite_list.append(everyone_overwrite)
            for overwrite in raid_channel_overwrite_list:
                if isinstance(overwrite[0], discord.Role):
                    if overwrite[0].permissions.manage_guild or overwrite[0].permissions.manage_channels or overwrite[0].permissions.manage_messages:
                        continue
                    overwrite[1].send_messages = False
                elif isinstance(overwrite[0], discord.Member):
                    if channel.permissions_for(overwrite[0]).manage_guild or channel.permissions_for(overwrite[0]).manage_channels or channel.permissions_for(overwrite[0]).manage_messages:
                        continue
                    overwrite[1].send_messages = False
                if (overwrite[0].name not in guild.me.top_role.name) and (overwrite[0].name not in guild.me.name):
                    overwrite[1].send_messages = False
        else:
            if guild_dict[guild.id]['configure_dict']['exraid']['permissions'] == "everyone":
                everyone_overwrite = (guild.default_role, discord.PermissionOverwrite(send_messages=True))
                raid_channel_overwrite_list.append(everyone_overwrite)
        meowth_overwrite = (Meowth.user, discord.PermissionOverwrite(send_messages=True, read_messages=True, manage_roles=True))
        raid_channel_overwrite_list.append(meowth_overwrite)
        raid_channel = await guild.create_text_channel(raid_channel_name, overwrites=raid_channel_overwrites,category=raid_channel_category)
        if guild_dict[guild.id]['configure_dict']['invite']['enabled']:
            for role in guild.role_hierarchy:
                if role.permissions.manage_guild or role.permissions.manage_channels or role.permissions.manage_messages:
                    raid_channel_overwrite_list.append((role, discord.PermissionOverwrite(send_messages=True)))
    elif type == "raid":
        name = pkmn + "-"
        raid_channel_overwrite_list = report_channel.overwrites
        level = get_level(pkmn)
    elif type == "egg":
        name = _("level-{level}-egg-").format(level=str(level))
        raid_channel_overwrite_list = report_channel.overwrites
    name += sanitize_channel_name(details)
    cat = get_category(report_channel, str(level), category_type=type)
    ow = dict(raid_channel_overwrite_list)
    return await guild.create_text_channel(name, overwrites=ow, category=cat)

@Meowth.command(hidden=True)
async def template(ctx, *, sample_message):
    """Sample template messages to see how they would appear."""
    embed = None
    (msg, errors) = do_template(sample_message, ctx.author, ctx.guild)
    if errors:
        if msg.startswith('[') and msg.endswith(']'):
            embed = discord.Embed(
                colour=ctx.guild.me.colour, description=msg[1:(- 1)])
            embed.add_field(name=_('Warning'), value=_('The following could not be found:\n{}').format(
                '\n'.join(errors)))
            await ctx.channel.send(embed=embed)
        else:
            msg = _('{}\n\n**Warning:**\nThe following could not be found: {}').format(
                msg, ', '.join(errors))
            await ctx.channel.send(msg)
    elif msg.startswith('[') and msg.endswith(']'):
        await ctx.channel.send(embed=discord.Embed(colour=ctx.guild.me.colour, description=msg[1:(- 1)].format(user=ctx.author.mention)))
    else:
        await ctx.channel.send(msg.format(user=ctx.author.mention))

"""
Server Management
"""

async def wild_expiry_check(message):
    logger.info('Expiry_Check - ' + message.channel.name)
    guild = message.channel.guild
    global active_wilds
    message = await message.channel.get_message(message.id)
    if message not in active_wilds:
        active_wilds.append(message)
        logger.info(
        'wild_expiry_check - Message added to watchlist - ' + message.channel.name
        )
        await asyncio.sleep(0.5)
        while True:
            try:
                if guild_dict[guild.id]['wildreport_dict'][message.id]['exp'] <= time.time():
                    await expire_wild(message)
            except KeyError:
                pass
            await asyncio.sleep(30)
            continue

async def expire_wild(message):
    guild = message.channel.guild
    channel = message.channel
    wild_dict = guild_dict[guild.id]['wildreport_dict']
    try:
        await message.edit(embed=discord.Embed(description=guild_dict[guild.id]['wildreport_dict'][message.id]['expedit']['embedcontent'], colour=message.embeds[0].colour.value))
        await message.clear_reactions()
    except discord.errors.NotFound:
        pass
    try:
        user_message = await channel.get_message(wild_dict[message.id]['reportmessage'])
        await user_message.delete()
    except (discord.errors.NotFound, discord.errors.Forbidden, discord.errors.HTTPException):
        pass
    del guild_dict[guild.id]['wildreport_dict'][message.id]

async def expiry_check(channel):
    logger.info('Expiry_Check - ' + channel.name)
    guild = channel.guild
    global active_raids
    channel = Meowth.get_channel(channel.id)
    if channel not in active_raids:
        active_raids.append(channel)
        logger.info(
            'Expire_Channel - Channel Added To Watchlist - ' + channel.name)
        await asyncio.sleep(0.5)
        while True:
            try:
                if guild_dict[guild.id]['raidchannel_dict'][channel.id].get('meetup',{}):
                    now = datetime.datetime.utcnow() + datetime.timedelta(hours=guild_dict[guild.id]['configure_dict']['settings']['offset'])
                    start = guild_dict[guild.id]['raidchannel_dict'][channel.id]['meetup'].get('start',False)
                    end = guild_dict[guild.id]['raidchannel_dict'][channel.id]['meetup'].get('end',False)
                    if start and guild_dict[guild.id]['raidchannel_dict'][channel.id]['type'] == 'egg':
                        if start < now:
                            pokemon = get_name(raid_info['raid_eggs']['EX']['pokemon'][0])
                            await _eggtoraid(pokemon, channel, author=None)
                    if end and end < now:
                        event_loop.create_task(expire_channel(channel))
                        try:
                            active_raids.remove(channel)
                        except ValueError:
                            logger.info(
                                'Expire_Channel - Channel Removal From Active Raid Failed - Not in List - ' + channel.name)
                        logger.info(
                            'Expire_Channel - Channel Expired And Removed From Watchlist - ' + channel.name)
                        break
                elif guild_dict[guild.id]['raidchannel_dict'][channel.id]['active']:
                    if guild_dict[guild.id]['raidchannel_dict'][channel.id]['exp']:
                        if guild_dict[guild.id]['raidchannel_dict'][channel.id]['exp'] <= time.time():
                            if guild_dict[guild.id]['raidchannel_dict'][channel.id]['type'] == 'egg':
                                pokemon = guild_dict[guild.id]['raidchannel_dict'][channel.id]['pokemon']
                                egglevel = guild_dict[guild.id]['raidchannel_dict'][channel.id]['egglevel']
                                if not pokemon and len(raid_info['raid_eggs'][egglevel]['pokemon']) == 1:
                                    pokemon = get_name(raid_info['raid_eggs'][egglevel]['pokemon'][0])
                                elif not pokemon and egglevel == "5" and guild_dict[channel.guild.id]['configure_dict']['settings'].get('regional',None) in raid_info['raid_eggs']["5"]['pokemon']:
                                    pokemon = get_name(guild_dict[channel.guild.id]['configure_dict']['settings']['regional'])
                                if pokemon:
                                    logger.info(
                                        'Expire_Channel - Egg Auto Hatched - ' + channel.name)
                                    try:
                                        active_raids.remove(channel)
                                    except ValueError:
                                        logger.info(
                                            'Expire_Channel - Channel Removal From Active Raid Failed - Not in List - ' + channel.name)
                                    await _eggtoraid(pokemon.lower(), channel, author=None)
                                    break
                            event_loop.create_task(expire_channel(channel))
                            try:
                                active_raids.remove(channel)
                            except ValueError:
                                logger.info(
                                    'Expire_Channel - Channel Removal From Active Raid Failed - Not in List - ' + channel.name)
                            logger.info(
                                'Expire_Channel - Channel Expired And Removed From Watchlist - ' + channel.name)
                            break
            except:
                pass
            await asyncio.sleep(30)
            continue

async def expire_channel(channel):
    guild = channel.guild
    alreadyexpired = False
    logger.info('Expire_Channel - ' + channel.name)
    # If the channel exists, get ready to delete it.
    # Otherwise, just clean up the dict since someone
    # else deleted the actual channel at some point.
    channel_exists = Meowth.get_channel(channel.id)
    channel = channel_exists
    if (channel_exists == None) and (not Meowth.is_closed()):
        try:
            del guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]
        except KeyError:
            pass
        return
    elif (channel_exists):
        dupechannel = False
        if guild_dict[guild.id]['raidchannel_dict'][channel.id]['active'] == False:
            alreadyexpired = True
        else:
            guild_dict[guild.id]['raidchannel_dict'][channel.id]['active'] = False
        logger.info('Expire_Channel - Channel Expired - ' + channel.name)
        dupecount = guild_dict[guild.id]['raidchannel_dict'][channel.id].get('duplicate',0)
        if dupecount >= 3:
            dupechannel = True
            guild_dict[guild.id]['raidchannel_dict'][channel.id]['duplicate'] = 0
            guild_dict[guild.id]['raidchannel_dict'][channel.id]['exp'] = time.time()
            if (not alreadyexpired):
                await channel.send(_('This channel has been successfully reported as a duplicate and will be deleted in 1 minute. Check the channel list for the other raid channel to coordinate in!\nIf this was in error, reset the raid with **!timerset**'))
            delete_time = (guild_dict[guild.id]['raidchannel_dict'][channel.id]['exp'] + (1 * 60)) - time.time()
        elif guild_dict[guild.id]['raidchannel_dict'][channel.id]['type'] == 'egg' and not guild_dict[guild.id]['raidchannel_dict'][channel.id].get('meetup',{}):
            if (not alreadyexpired):
                pkmn = guild_dict[guild.id]['raidchannel_dict'][channel.id].get('pokemon', None)
                if pkmn:
                    await _eggtoraid(pkmn, channel)
                    return
                maybe_list = []
                trainer_dict = copy.deepcopy(
                    guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['trainer_dict'])
                for trainer in trainer_dict.keys():
                    if trainer_dict[trainer]['status']['maybe']:
                        user = channel.guild.get_member(trainer)
                        maybe_list.append(user.mention)
                h = _('hatched-')
                new_name = h if h not in channel.name else ''
                new_name += channel.name
                await channel.edit(name=new_name)
                await channel.send(_("**This egg has hatched!**\n\n...or the time has just expired. Trainers {trainer_list}: Update the raid to the pokemon that hatched using **!raid <pokemon>** or reset the hatch timer with **!timerset**. This channel will be deactivated until I get an update and I'll delete it in 45 minutes if I don't hear anything.").format(trainer_list=', '.join(maybe_list)))
            delete_time = (guild_dict[guild.id]['raidchannel_dict'][channel.id]['exp'] + (45 * 60)) - time.time()
            expiremsg = _('**This level {level} raid egg has expired!**').format(
                level=guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['egglevel'])
        else:
            if (not alreadyexpired):
                e = _('expired-')
                new_name = e if e not in channel.name else ''
                new_name += channel.name
                await channel.edit(name=new_name)
                await channel.send(_('This channel timer has expired! The channel has been deactivated and will be deleted in 5 minutes.\nTo reactivate the channel, use **!timerset** to set the timer again.'))
            delete_time = (guild_dict[guild.id]['raidchannel_dict'][channel.id]['exp'] + (5 * 60)) - time.time()
            raidtype = _("event") if guild_dict[guild.id]['raidchannel_dict'][channel.id].get('meetup',False) else _(" raid")
            expiremsg = _('**This {pokemon}{raidtype} has expired!**').format(
                pokemon=guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['pokemon'].capitalize(), raidtype=raidtype)
        await asyncio.sleep(delete_time)
        # If the channel has already been deleted from the dict, someone
        # else got to it before us, so don't do anything.
        # Also, if the channel got reactivated, don't do anything either.
        try:
            if (guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['active'] == False) and (not Meowth.is_closed()):
                if dupechannel:
                    try:
                        report_channel = Meowth.get_channel(
                            guild_dict[guild.id]['raidchannel_dict'][channel.id]['reportcity'])
                        reportmsg = await report_channel.get_message(guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['raidreport'])
                        await reportmsg.delete()
                    except:
                        pass
                else:
                    try:
                        report_channel = Meowth.get_channel(
                            guild_dict[guild.id]['raidchannel_dict'][channel.id]['reportcity'])
                        reportmsg = await report_channel.get_message(guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['raidreport'])
                        await reportmsg.edit(embed=discord.Embed(description=expiremsg, colour=channel.guild.me.colour))
                    except:
                        pass
                    # channel doesn't exist anymore in serverdict
                archive = guild_dict[guild.id]['raidchannel_dict'][channel.id].get('archive',False)
                logs = guild_dict[channel.guild.id]['raidchannel_dict'][channel.id].get('logs', {})
                channel_exists = Meowth.get_channel(channel.id)
                if channel_exists == None:
                    return
                elif not archive and not logs:
                    try:
                        del guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]
                    except KeyError:
                        pass
                    await channel_exists.delete()
                    logger.info(
                        'Expire_Channel - Channel Deleted - ' + channel.name)
                elif archive or logs:
                    try:
                        for overwrite in channel.overwrites:
                            if isinstance(overwrite[0], discord.Role):
                                if overwrite[0].permissions.manage_guild or overwrite[0].permissions.manage_channels:
                                    await channel.set_permissions(overwrite[0], read_messages=True)
                                    continue
                            elif isinstance(overwrite[0], discord.Member):
                                if channel.permissions_for(overwrite[0]).manage_guild or channel.permissions_for(overwrite[0]).manage_channels:
                                    await channel.set_permissions(overwrite[0], read_messages=True)
                                    continue
                            if (overwrite[0].name not in guild.me.top_role.name) and (overwrite[0].name not in guild.me.name):
                                await channel.set_permissions(overwrite[0], read_messages=False)
                        for role in guild.role_hierarchy:
                            if role.permissions.manage_guild or role.permissions.manage_channels:
                                await channel.set_permissions(role, read_messages=True)
                            continue
                        await channel.set_permissions(guild.default_role, read_messages=False)
                    except (discord.errors.Forbidden, discord.errors.HTTPException, discord.errors.InvalidArgument):
                        pass
                    new_name = _('archived-')
                    if new_name not in channel.name:
                        new_name += channel.name
                        category = guild_dict[channel.guild.id]['configure_dict'].get('archive', {}).get('category', 'same')
                        if category == 'same':
                            newcat = channel.category
                        else:
                            newcat = channel.guild.get_channel(category)
                        await channel.edit(name=new_name, category=newcat)
                        await channel.send(_('-----------------------------------------------\n**The channel has been archived and removed from view for everybody but Meowth and those with Manage Channel permissions. Any messages that were deleted after the channel was marked for archival will be posted below. You will need to delete this channel manually.**\n-----------------------------------------------'))
                        while logs:
                            earliest = min(logs)
                            embed = discord.Embed(colour=logs[earliest]['color_int'], description=logs[earliest]['content'], timestamp=logs[earliest]['created_at'])
                            if logs[earliest]['author_nick']:
                                embed.set_author(name="{name} [{nick}]".format(name=logs[earliest]['author_str'],nick=logs[earliest]['author_nick']), icon_url = logs[earliest]['author_avy'])
                            else:
                                embed.set_author(name=logs[earliest]['author_str'], icon_url = logs[earliest]['author_avy'])
                            await channel.send(embed=embed)
                            del logs[earliest]
                            await asyncio.sleep(.25)
                        del guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]
        except:
            pass

Meowth.expire_channel = expire_channel

async def channel_cleanup(loop=True):
    while (not Meowth.is_closed()):
        global active_raids
        guilddict_chtemp = copy.deepcopy(guild_dict)
        logger.info('Channel_Cleanup ------ BEGIN ------')
        # for every server in save data
        for guildid in guilddict_chtemp.keys():
            guild = Meowth.get_guild(guildid)
            log_str = 'Channel_Cleanup - Server: ' + str(guildid)
            log_str = log_str + ' - CHECKING FOR SERVER'
            if guild == None:
                logger.info(log_str + ': NOT FOUND')
                continue
            logger.info(((log_str + ' (') + guild.name) +
                        ')  - BEGIN CHECKING SERVER')
            # clear channel lists
            dict_channel_delete = []
            discord_channel_delete = []
            # check every raid channel data for each server
            for channelid in guilddict_chtemp[guildid]['raidchannel_dict']:
                channel = Meowth.get_channel(channelid)
                log_str = 'Channel_Cleanup - Server: ' + guild.name
                log_str = (log_str + ': Channel:') + str(channelid)
                logger.info(log_str + ' - CHECKING')
                channelmatch = Meowth.get_channel(channelid)
                if channelmatch == None:
                    # list channel for deletion from save data
                    dict_channel_delete.append(channelid)
                    logger.info(log_str + " - DOESN'T EXIST IN DISCORD")
                # otherwise, if meowth can still see the channel in discord
                else:
                    logger.info(
                        ((log_str + ' (') + channel.name) + ') - EXISTS IN DISCORD')
                    # if the channel save data shows it's not an active raid
                    if guilddict_chtemp[guildid]['raidchannel_dict'][channelid]['active'] == False:
                        if guilddict_chtemp[guildid]['raidchannel_dict'][channelid]['type'] == 'egg':
                            # and if it has been expired for longer than 45 minutes already
                            if guilddict_chtemp[guildid]['raidchannel_dict'][channelid]['exp'] < (time.time() - (45 * 60)):
                                # list the channel to be removed from save data
                                dict_channel_delete.append(channelid)
                                # and list the channel to be deleted in discord
                                discord_channel_delete.append(channel)
                                logger.info(
                                    log_str + ' - 15+ MIN EXPIRY NONACTIVE EGG')
                                continue
                            # and if it has been expired for longer than 5 minutes already
                        elif guilddict_chtemp[guildid]['raidchannel_dict'][channelid]['exp'] < (time.time() - (5 * 60)):
                                # list the channel to be removed from save data
                            dict_channel_delete.append(channelid)
                                # and list the channel to be deleted in discord
                            discord_channel_delete.append(channel)
                            logger.info(
                                log_str + ' - 5+ MIN EXPIRY NONACTIVE RAID')
                            continue
                        event_loop.create_task(expire_channel(channel))
                        logger.info(
                            log_str + ' - = RECENTLY EXPIRED NONACTIVE RAID')
                        continue
                    # if the channel save data shows it as an active raid still
                    elif guilddict_chtemp[guildid]['raidchannel_dict'][channelid]['active'] == True:
                        # if it's an exraid
                        if guilddict_chtemp[guildid]['raidchannel_dict'][channelid]['type'] == 'exraid':
                            logger.info(log_str + ' - EXRAID')

                            continue
                        # or if the expiry time for the channel has already passed within 5 minutes
                        elif guilddict_chtemp[guildid]['raidchannel_dict'][channelid]['exp'] <= time.time():
                            # list the channel to be sent to the channel expiry function
                            event_loop.create_task(expire_channel(channel))
                            logger.info(log_str + ' - RECENTLY EXPIRED')

                            continue

                        if channel not in active_raids:
                            # if channel is still active, make sure it's expiry is being monitored
                            event_loop.create_task(expiry_check(channel))
                            logger.info(
                                log_str + ' - MISSING FROM EXPIRY CHECK')
                            continue
            # for every channel listed to have save data deleted
            for c in dict_channel_delete:
                try:
                    # attempt to delete the channel from save data
                    del guild_dict[guildid]['raidchannel_dict'][c]
                    logger.info(
                        'Channel_Cleanup - Channel Savedata Cleared - ' + str(c))
                except KeyError:
                    pass
            # for every channel listed to have the discord channel deleted
            for c in discord_channel_delete:
                try:
                    # delete channel from discord
                    await c.delete()
                    logger.info(
                        'Channel_Cleanup - Channel Deleted - ' + c.name)
                except:
                    logger.info(
                        'Channel_Cleanup - Channel Deletion Failure - ' + c.name)
                    pass
        # save server_dict changes after cleanup
        logger.info('Channel_Cleanup - SAVING CHANGES')
        try:
            await _save()
        except Exception as err:
            logger.info('Channel_Cleanup - SAVING FAILED' + err)
        logger.info('Channel_Cleanup ------ END ------')
        await asyncio.sleep(600)
        continue

async def guild_cleanup(loop=True):
    while (not Meowth.is_closed()):
        guilddict_srvtemp = copy.deepcopy(guild_dict)
        logger.info('Server_Cleanup ------ BEGIN ------')
        guilddict_srvtemp = guild_dict
        dict_guild_list = []
        bot_guild_list = []
        dict_guild_delete = []
        for guildid in guilddict_srvtemp.keys():
            dict_guild_list.append(guildid)
        for guild in Meowth.guilds:
            bot_guild_list.append(guild.id)
        guild_diff = set(dict_guild_list) - set(bot_guild_list)
        for s in guild_diff:
            dict_guild_delete.append(s)
        for s in dict_guild_delete:
            try:
                del guild_dict[s]
                logger.info(('Server_Cleanup - Cleared ' + str(s)) +
                            ' from save data')
            except KeyError:
                pass
        logger.info('Server_Cleanup - SAVING CHANGES')
        try:
            await _save()
        except Exception as err:
            logger.info('Server_Cleanup - SAVING FAILED' + err)
        logger.info('Server_Cleanup ------ END ------')
        await asyncio.sleep(7200)
        continue

async def message_cleanup(loop=True):
    while (not Meowth.is_closed()):
        logger.info('message_cleanup ------ BEGIN ------')
        guilddict_temp = copy.deepcopy(guild_dict)
        for guildid in guilddict_temp.keys():
            questreport_dict = guilddict_temp[guildid].get('questreport_dict',{})
            wildreport_dict = guilddict_temp[guildid].get('wildreport_dict',{})
            report_dict_dict = {
                'questreport_dict':questreport_dict,
                'wildreport_dict':wildreport_dict,
            }
            report_edit_dict = {}
            report_delete_dict = {}
            for report_dict in report_dict_dict:
                for reportid in report_dict_dict[report_dict].keys():
                    if report_dict_dict[report_dict][reportid].get('exp', 0) <= time.time():
                        report_channel = Meowth.get_channel(report_dict_dict[report_dict][reportid].get('reportchannel'))
                        if report_channel:
                            user_report = report_dict_dict[report_dict][reportid].get('reportmessage',None)
                            if user_report:
                                report_delete_dict[user_report] = {"action":"delete","channel":report_channel}
                            if report_dict_dict[report_dict][reportid].get('expedit') == "delete":
                                report_delete_dict[reportid] = {"action":"delete","channel":report_channel}
                            else:
                                report_edit_dict[reportid] = {"action":report_dict_dict[report_dict][reportid]['expedit'],"channel":report_channel}
                        try:
                            del guild_dict[guildid][report_dict][reportid]
                        except KeyError:
                            pass
            for messageid in report_delete_dict.keys():
                try:
                    report_message = await report_delete_dict[messageid]['channel'].get_message(messageid)
                    await report_message.delete()
                except (discord.errors.NotFound, discord.errors.Forbidden, discord.errors.HTTPException, KeyError):
                    pass
            for messageid in report_edit_dict.keys():
                try:
                    report_message = await report_edit_dict[messageid]['channel'].get_message(messageid)
                    await report_message.edit(content=report_edit_dict[messageid]['action']['content'],embed=discord.Embed(description=report_edit_dict[messageid]['action'].get('embedcontent'), colour=report_message.embeds[0].colour.value))
                    await report_message.clear_reactions()
                except (discord.errors.NotFound, discord.errors.Forbidden, discord.errors.HTTPException, IndexError, KeyError):
                    pass
        # save server_dict changes after cleanup
        logger.info('message_cleanup - SAVING CHANGES')
        try:
            await _save()
        except Exception as err:
            logger.info('message_cleanup - SAVING FAILED' + err)
        logger.info('message_cleanup ------ END ------')
        await asyncio.sleep(600)
        continue

async def _print(owner, message):
    if 'launcher' in sys.argv[1:]:
        if 'debug' not in sys.argv[1:]:
            await owner.send(message)
    print(message)
    logger.info(message)

async def maint_start():
    try:
#        event_loop.create_task(guild_cleanup())
        event_loop.create_task(channel_cleanup())
        event_loop.create_task(message_cleanup())
        logger.info('Maintenance Tasks Started')
    except KeyboardInterrupt as e:
        tasks.cancel()

event_loop = asyncio.get_event_loop()

"""
Events
"""
@Meowth.event
async def on_ready():
    Meowth.owner = discord.utils.get(
        Meowth.get_all_members(), id=config['master'])
    await _print(Meowth.owner, _('Starting up...'))
    Meowth.uptime = datetime.datetime.now()
    msg_success = 0
    msg_fail = 0
    guilds = len(Meowth.guilds)
    users = 0
    for guild in Meowth.guilds:
        users += guild.member_count
        try:
            if guild.id not in guild_dict:
                guild_dict[guild.id] = {
                    'configure_dict':{
                        'welcome': {'enabled':False,'welcomechan':'','welcomemsg':''},
                        'want': {'enabled':False, 'report_channels': []},
                        'raid': {'enabled':False, 'report_channels': {}, 'categories':'same','category_dict':{}},
                        'exraid': {'enabled':False, 'report_channels': {}, 'categories':'same','category_dict':{}, 'permissions':'everyone'},
                        'wild': {'enabled':False, 'report_channels': {}},
                        'counters': {'enabled':False, 'auto_levels': []},
                        'research': {'enabled':False, 'report_channels': {}},
                        'archive': {'enabled':False, 'category':'same','list':None},
                        'invite': {'enabled':False},
                        'team':{'enabled':False},
                        'settings':{'offset':0,'regional':None,'done':False,'prefix':None,'config_sessions':{}}
                    },
                    'wildreport_dict:':{},
                    'questreport_dict':{},
                    'raidchannel_dict':{},
                    'trainers':{}
                }
            else:
                guild_dict[guild.id]['configure_dict'].setdefault('trade', {})
        except KeyError:
            guild_dict[guild.id] = {
                'configure_dict':{
                    'welcome': {'enabled':False,'welcomechan':'','welcomemsg':''},
                    'want': {'enabled':False, 'report_channels': []},
                    'raid': {'enabled':False, 'report_channels': {}, 'categories':'same','category_dict':{}},
                    'exraid': {'enabled':False, 'report_channels': {}, 'categories':'same','category_dict':{}, 'permissions':'everyone'},
                    'counters': {'enabled':False, 'auto_levels': []},
                    'wild': {'enabled':False, 'report_channels': {}},
                    'research': {'enabled':False, 'report_channels': {}},
                    'archive': {'enabled':False, 'category':'same','list':None},
                    'invite': {'enabled':False},
                    'team':{'enabled':False},
                    'settings':{'offset':0,'regional':None,'done':False,'prefix':None,'config_sessions':{}}
                },
                'wildreport_dict:':{},
                'questreport_dict':{},
                'raidchannel_dict':{},
                'trainers':{}
            }
    await _print(Meowth.owner, _("Meowth! That's right!\n\n{server_count} servers connected.\n{member_count} members found.").format(server_count=guilds, member_count=users))
    await maint_start()

@Meowth.event
async def on_guild_join(guild):
    owner = guild.owner
    guild_dict[guild.id] = {
        'configure_dict':{
            'welcome': {'enabled':False,'welcomechan':'','welcomemsg':''},
            'want': {'enabled':False, 'report_channels': []},
            'raid': {'enabled':False, 'report_channels': {}, 'categories':'same','category_dict':{}},
            'exraid': {'enabled':False, 'report_channels': {}, 'categories':'same','category_dict':{}, 'permissions':'everyone'},
            'counters': {'enabled':False, 'auto_levels': []},
            'wild': {'enabled':False, 'report_channels': {}},
            'research': {'enabled':False, 'report_channels': {}},
            'archive': {'enabled':False, 'category':'same','list':None},
            'invite': {'enabled':False},
            'team':{'enabled':False},
            'settings':{'offset':0,'regional':None,'done':False,'prefix':None,'config_sessions':{}}
        },
        'wildreport_dict:':{},
        'questreport_dict':{},
        'raidchannel_dict':{},
        'trainers':{},
        'trade_dict': {}
    }
    await owner.send(_("Meowth! I'm Meowth, a Discord helper bot for Pokemon Go communities, and someone has invited me to your server! Type **!help** to see a list of things I can do, and type **!configure** in any channel of your server to begin!"))

@Meowth.event
async def on_guild_remove(guild):
    try:
        if guild.id in guild_dict:
            try:
                del guild_dict[guild.id]
            except KeyError:
                pass
    except KeyError:
        pass

@Meowth.event
async def on_member_join(member):
    'Welcome message to the server and some basic instructions.'
    guild = member.guild
    team_msg = _(' or ').join(['**!team {0}**'.format(team)
                           for team in config['team_dict'].keys()])
    if not guild_dict[guild.id]['configure_dict']['welcome']['enabled']:
        return
    # Build welcome message
    if guild_dict[guild.id]['configure_dict']['welcome'].get('welcomemsg', 'default') == "default":
        admin_message = _(' If you have any questions just ask an admin.')
        welcomemessage = _('Meowth! Welcome to {server}, {user}! ')
        if guild_dict[guild.id]['configure_dict']['team']['enabled']:
            welcomemessage += _('Set your team by typing {team_command}.').format(
                team_command=team_msg)
        welcomemessage += admin_message
    else:
        welcomemessage = guild_dict[guild.id]['configure_dict']['welcome']['welcomemsg']

    if guild_dict[guild.id]['configure_dict']['welcome']['welcomechan'] == 'dm':
        send_to = member
    elif str(guild_dict[guild.id]['configure_dict']['welcome']['welcomechan']).isdigit():
        send_to = discord.utils.get(guild.text_channels, id=int(guild_dict[guild.id]['configure_dict']['welcome']['welcomechan']))
    else:
        send_to = discord.utils.get(guild.text_channels, name=guild_dict[guild.id]['configure_dict']['welcome']['welcomechan'])
    if send_to:
        if welcomemessage.startswith("[") and welcomemessage.endswith("]"):
            await send_to.send(embed=discord.Embed(colour=guild.me.colour, description=welcomemessage[1:-1].format(server=guild.name, user=member.mention)))
        else:
            await send_to.send(welcomemessage.format(server=guild.name, user=member.mention))
    else:
        return

@Meowth.event
async def on_message(message):
    if message.guild != None:
        raid_status = guild_dict[message.guild.id]['raidchannel_dict'].get(message.channel.id, None)
        if raid_status:
            if guild_dict[message.guild.id]['configure_dict'].get('archive', {}).get('enabled', False) and guild_dict[message.guild.id]['configure_dict'].get('archive', {}).get('list', []):
                for phrase in guild_dict[message.guild.id]['configure_dict']['archive']['list']:
                    if phrase in message.content:
                        await _archive(message.channel)
            if guild_dict[message.guild.id]['raidchannel_dict'][message.channel.id]['active']:
                trainer_dict = guild_dict[message.guild.id]['raidchannel_dict'][message.channel.id]['trainer_dict']
                if message.author.id in trainer_dict:
                    count = trainer_dict[message.author.id].get('count',1)
                else:
                    count = 1
                omw_emoji = parse_emoji(message.guild, config['omw_id'])
                if message.content.startswith(omw_emoji):
                    try:
                        if guild_dict[message.guild.id]['raidchannel_dict'][message.channel.id]['type'] == 'egg':
                            if guild_dict[message.guild.id]['raidchannel_dict'][message.channel.id]['pokemon'] == '':
                                await message.channel.send(_("Meowth! Please wait until the raid egg has hatched before announcing you're coming or present."))
                                return
                    except:
                        pass
                    emoji_count = message.content.count(omw_emoji)
                    await _coming(message.channel, message.author, emoji_count, party=None)
                    return
                here_emoji = parse_emoji(message.guild, config['here_id'])
                if message.content.startswith(here_emoji):
                    try:
                        if guild_dict[message.guild.id]['raidchannel_dict'][message.channel.id]['type'] == 'egg':
                            if guild_dict[message.guild.id]['raidchannel_dict'][message.channel.id]['pokemon'] == '':
                                await message.channel.send(_("Meowth! Please wait until the raid egg has hatched before announcing you're coming or present."))
                                return
                    except:
                        pass
                    emoji_count = message.content.count(here_emoji)
                    await _here(message.channel, message.author, emoji_count, party=None)
                    return
                if "/maps" in message.content and "http" in message.content:
                    newcontent = message.content.replace("<","").replace(">","")
                    newloc = create_gmaps_query(newcontent, message.channel, type=guild_dict[message.guild.id]['raidchannel_dict'][message.channel.id]['type'])
                    oldraidmsg = await message.channel.get_message(guild_dict[message.guild.id]['raidchannel_dict'][message.channel.id]['raidmessage'])
                    report_channel = Meowth.get_channel(guild_dict[message.guild.id]['raidchannel_dict'][message.channel.id]['reportcity'])
                    oldreportmsg = await report_channel.get_message(guild_dict[message.guild.id]['raidchannel_dict'][message.channel.id]['raidreport'])
                    oldembed = oldraidmsg.embeds[0]
                    newembed = discord.Embed(title=oldembed.title, url=newloc, colour=message.guild.me.colour)
                    for field in oldembed.fields:
                        newembed.add_field(name=field.name, value=field.value, inline=field.inline)
                    newembed.set_footer(text=oldembed.footer.text, icon_url=oldembed.footer.icon_url)
                    newembed.set_thumbnail(url=oldembed.thumbnail.url)
                    try:
                        await oldraidmsg.edit(new_content=oldraidmsg.content, embed=newembed, content=oldraidmsg.content)
                    except:
                        pass
                    try:
                         await oldreportmsg.edit(new_content=oldreportmsg.content, embed=newembed, content=oldreportmsg.content)
                    except:
                        pass
                    guild_dict[message.guild.id]['raidchannel_dict'][message.channel.id]['raidmessage'] = oldraidmsg.id
                    guild_dict[message.guild.id]['raidchannel_dict'][message.channel.id]['raidreport'] = oldreportmsg.id
                    otw_list = []
                    trainer_dict = copy.deepcopy(guild_dict[message.guild.id]['raidchannel_dict'][message.channel.id]['trainer_dict'])
                    for trainer in trainer_dict.keys():
                        if trainer_dict[trainer]['status']['coming']:
                            user = message.guild.get_member(trainer)
                            otw_list.append(user.mention)
                    await message.channel.send(content=_('Meowth! Someone has suggested a different location for the raid! Trainers {trainer_list}: make sure you are headed to the right place!').format(trainer_list=', '.join(otw_list)), embed=newembed)
                    return
    if (not message.author.bot):
        await Meowth.process_commands(message)

@Meowth.event
async def on_message_delete(message):
    guild = message.guild
    channel = message.channel
    author = message.author
    if channel.id in guild_dict[guild.id]['raidchannel_dict'] and guild_dict[guild.id]['configure_dict']['archive']['enabled']:
        if message.content.strip() == "!archive":
            guild_dict[guild.id]['raidchannel_dict'][channel.id]['archive'] = True
        if guild_dict[guild.id]['raidchannel_dict'][channel.id].get('archive', False):
            logs = guild_dict[guild.id]['raidchannel_dict'][channel.id].get('logs', {})
            logs[message.id] = {'author_id': message.author.id, 'author_str': str(message.author),'author_avy':message.author.avatar_url,'author_nick':message.author.nick,'color_int':message.author.color.value,'content': message.clean_content,'created_at':message.created_at}
            guild_dict[guild.id]['raidchannel_dict'][channel.id]['logs'] = logs

@Meowth.event
async def on_raw_reaction_add(payload):
    channel = Meowth.get_channel(payload.channel_id)
    try:
        message = await channel.get_message(payload.message_id)
    except (discord.errors.NotFound, AttributeError, discord.Forbidden):
        return
    guild = message.guild
    try:
        user = guild.get_member(payload.user_id)
    except AttributeError:
        return
    guild = message.guild
    if channel.id in guild_dict[guild.id]['raidchannel_dict'] and user.id != Meowth.user.id:
        if message.id == guild_dict[guild.id]['raidchannel_dict'][channel.id].get('ctrsmessage',None):
            ctrs_dict = guild_dict[guild.id]['raidchannel_dict'][channel.id]['ctrs_dict']
            for i in ctrs_dict:
                if ctrs_dict[i]['emoji'] == str(payload.emoji):
                    newembed = ctrs_dict[i]['embed']
                    moveset = i
                    break
            else:
                return
            await message.edit(embed=newembed)
            guild_dict[guild.id]['raidchannel_dict'][channel.id]['moveset'] = moveset
            await message.remove_reaction(payload.emoji, user)
        elif message.id == guild_dict[guild.id]['raidchannel_dict'][channel.id].get('raidmessage',None):
            if str(payload.emoji) == '\u2754':
                prefix = guild_dict[guild.id]['configure_dict']['settings']['prefix']
                prefix = prefix or Meowth.config['default_prefix']
                avatar = Meowth.user.avatar_url
                await utils.get_raid_help(prefix, avatar, user)
            await message.remove_reaction(payload.emoji, user)
    try:
        wildreport_dict = guild_dict[guild.id]['wildreport_dict']
    except KeyError:
        wildreport_dict = []
    if message.id in wildreport_dict and user.id != Meowth.user.id:
        wild_dict = guild_dict[guild.id]['wildreport_dict'][message.id]
        if str(payload.emoji) == '🏎':
            wild_dict['omw'].append(user.mention)
            guild_dict[guild.id]['wildreport_dict'][message.id] = wild_dict
        elif str(payload.emoji) == '💨':
            for reaction in message.reactions:
                if reaction.emoji == '💨' and reaction.count >= 2:
                    if wild_dict['omw']:
                        despawn = _("has despawned")
                        await channel.send(f"{', '.join(wild_dict['omw'])}: {wild_dict['pokemon'].title()} {despawn}!")
                    await expire_wild(message)

"""
Admin Commands
"""
@Meowth.command(hidden=True, name="eval")
@checks.is_owner()
async def _eval(ctx, *, body: str):
    """Evaluates a code"""
    env = {
        'bot': ctx.bot,
        'ctx': ctx,
        'channel': ctx.channel,
        'author': ctx.author,
        'guild': ctx.guild,
        'message': ctx.message
    }
    def cleanup_code(content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])
        # remove `foo`
        return content.strip('` \n')
    env.update(globals())
    body = cleanup_code(body)
    stdout = io.StringIO()
    to_compile = (f'async def func():\n{textwrap.indent(body, "  ")}')
    try:
        exec(to_compile, env)
    except Exception as e:
        return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')
    func = env['func']
    try:
        with redirect_stdout(stdout):
            ret = await func()
    except Exception as e:
        value = stdout.getvalue()
        await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
    else:
        value = stdout.getvalue()
        try:
            await ctx.message.add_reaction('\u2705')
        except:
            pass
        if ret is None:
            if value:
                paginator = commands.Paginator(prefix='```py')
                for line in textwrap.wrap(value, 80):
                    paginator.add_line(line.rstrip().replace('`', '\u200b`'))
                for p in paginator.pages:
                    await ctx.send(p)
        else:
            ctx.bot._last_result = ret
            await ctx.send(f'```py\n{value}{ret}\n```')

@Meowth.command()
@checks.is_owner()
async def save(ctx):
    """Enregistrer l'état persistant dans le fichier.

     Utilisation:!save
     Le chemin du fichier est relatif au répertoire courant."""
    try:
        await _save()
        logger.info('CONFIG SAVED')
    except Exception as err:
        await _print(Meowth.owner, _('Error occured while trying to save!'))
        await _print(Meowth.owner, err)

async def _save():
    with tempfile.NamedTemporaryFile('wb', dir=os.path.dirname(os.path.join('data', 'serverdict')), delete=False) as tf:
        pickle.dump(guild_dict, tf, (- 1))
        tempname = tf.name
    try:
        os.remove(os.path.join('data', 'serverdict_backup'))
    except OSError as e:
        pass
    try:
        os.rename(os.path.join('data', 'serverdict'), os.path.join('data', 'serverdict_backup'))
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise
    os.rename(tempname, os.path.join('data', 'serverdict'))

@Meowth.command()
@checks.is_owner()
async def restart(ctx):
    """Redémarrez après l'enregistrement.

     Utilisation:!restart.
     Appelle la fonction de sauvegarde et redémarre Meowth."""
    try:
        await _save()
    except Exception as err:
        await _print(Meowth.owner, _('Error occured while trying to save!'))
        await _print(Meowth.owner, err)
    await ctx.channel.send(_('Restarting...'))
    Meowth._shutdown_mode = 26
    await Meowth.logout()

@Meowth.command()
@checks.is_owner()
async def exit(ctx):
    """Quitter après l'enregistrement.

     Utilisation:!exit.
     Appelle la fonction de sauvegarde et quitte le script."""
    try:
        await _save()
    except Exception as err:
        await _print(Meowth.owner, _('Error occured while trying to save!'))
        await _print(Meowth.owner, err)
    await ctx.channel.send(_('Shutting down...'))
    Meowth._shutdown_mode = 0
    await Meowth.logout()

@Meowth.group(name='set', case_insensitive=True)
async def _set(ctx):
    """Change un paramètre."""
    if ctx.invoked_subcommand == None:
        raise commands.BadArgument()
        return

@_set.command()
@commands.has_permissions(manage_guild=True)
async def regional(ctx, regional):
    """Change le pokemon régional du serveur."""

    if regional.isdigit():
        regional = int(regional)
    else:
        regional = regional.lower()
        if regional == "reset" and checks.is_dev_or_owner(ctx):
            msg = _("Are you sure you want to clear all regionals?")
            question = await ctx.channel.send(msg)
            try:
                timeout = False
                res, reactuser = await ask(question, ctx.message.channel, ctx.message.author.id)
            except TypeError:
                timeout = True
            await question.delete()
            if timeout or res.emoji == '❎':
                return
            elif res.emoji == '✅':
                pass
            else:
                return
            guild_dict_copy = copy.deepcopy(guild_dict)
            for guildid in guild_dict_copy.keys():
                guild_dict[guildid]['configure_dict']['settings']['regional'] = None
            return
        elif regional == 'clear':
            regional = None
            _set_regional(Meowth, ctx.guild, regional)
            await ctx.message.channel.send(_("Meowth! Regional raid boss cleared!"))
            return
        else:
            regional = get_number(regional)
    if regional in get_raidlist():
        _set_regional(Meowth, ctx.guild, regional)
        await ctx.message.channel.send(_("Meowth! Regional raid boss set to **{boss}**!").format(boss=get_name(regional).title()))

    else:
        await ctx.message.channel.send(_("Meowth! That Pokemon doesn't appear in raids!"))
        return

def _set_regional(bot, guild, regional):
    bot.guild_dict[guild.id]['configure_dict']['settings']['regional'] = regional

@_set.command()
@commands.has_permissions(manage_guild=True)
async def timezone(ctx,*, timezone: str = ''):
    """Modifie le fuseau horaire du serveur."""
    try:
        timezone = float(timezone)
    except ValueError:
        await ctx.channel.send(_("I couldn't convert your answer to an appropriate timezone! Please double check what you sent me and resend a number from **-12** to **12**."))
        return
    if (not ((- 12) <= timezone <= 14)):
        await ctx.channel.send(_("I couldn't convert your answer to an appropriate timezone! Please double check what you sent me and resend a number from **-12** to **12**."))
        return
    _set_timezone(Meowth, ctx.guild, timezone)
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=guild_dict[ctx.channel.guild.id]['configure_dict']['settings']['offset'])
    await ctx.channel.send(_("Timezone has been set to: `UTC{offset}`\nThe current time is **{now}**").format(offset=timezone,now=now.strftime("%H:%M")))

def _set_timezone(bot, guild, timezone):
    bot.guild_dict[guild.id]['configure_dict']['settings']['offset'] = timezone

@_set.command()
@commands.has_permissions(manage_guild=True)
async def prefix(ctx, prefix=None):
    """Change le préfixe du serveur."""
    if prefix == 'clear':
        prefix = None
    prefix = prefix.strip()
    _set_prefix(Meowth, ctx.guild, prefix)
    if prefix != None:
        await ctx.channel.send(_('Prefix has been set to: `{}`').format(prefix))
    else:
        default_prefix = Meowth.config['default_prefix']
        await ctx.channel.send(_('Prefix has been reset to default: `{}`').format(default_prefix))

def _set_prefix(bot, guild, prefix):
    bot.guild_dict[guild.id]['configure_dict']['settings']['prefix'] = prefix

@_set.command()
async def silph(ctx, silph_user: str = None):
    """Lie un membre du serveur à une carte Silph Road Travelers."""
    if not silph_user:
        await ctx.send(_('Silph Road Travelers Card cleared!'))
        try:
            del guild_dict[ctx.guild.id]['trainers'][ctx.author.id]['silphid']
        except:
            pass
        return

    silph_cog = ctx.bot.cogs.get('Silph')
    if not silph_cog:
        return await ctx.send(
            _("The Silph Extension isn't accessible at the moment, sorry!"))

    async with ctx.typing():
        card = await silph_cog.get_silph_card(silph_user)
        if not card:
            return await ctx.send(_('Silph Card for {silph_user} not found.').format(silph_user=silph_user))

    if not card.discord_name:
        return await ctx.send(
            _('No Discord account found linked to this Travelers Card!'))

    if card.discord_name != str(ctx.author):
        return await ctx.send(
            _('This Travelers Card is linked to another Discord account!'))

    try:
        offset = ctx.bot.guild_dict[ctx.guild.id]['configure_dict']['settings']['offset']
    except KeyError:
        offset = None

    trainers = guild_dict[ctx.guild.id].get('trainers', {})
    author = trainers.get(ctx.author.id,{})
    author['silphid'] = silph_user
    trainers[ctx.author.id] = author
    guild_dict[ctx.guild.id]['trainers'] = trainers

    await ctx.send(
        _('This Travelers Card has been successfully linked to you!'),
        embed=card.embed(offset))

@_set.command()
async def pokebattler(ctx, pbid: int = 0):
    """Lie un membre du serveur à un ID PokeBattler."""
    if not pbid:
        await ctx.send(_('Pokebattler ID cleared!'))
        try:
            del guild_dict[ctx.guild.id]['trainers'][ctx.author.id]['pokebattlerid']
        except:
            pass
        return
    trainers = guild_dict[ctx.guild.id].get('trainers',{})
    author = trainers.get(ctx.author.id,{})
    author['pokebattlerid'] = pbid
    trainers[ctx.author.id] = author
    guild_dict[ctx.guild.id]['trainers'] = trainers
    await ctx.send(_('Pokebattler ID set to {pbid}!').format(pbid=pbid))

@Meowth.group(name='get', case_insensitive=True)
@commands.has_permissions(manage_guild=True)
async def _get(ctx):
    """Obtenir une valeur de paramètre"""
    if ctx.invoked_subcommand == None:
        raise commands.BadArgument()
        return

@_get.command()
@commands.has_permissions(manage_guild=True)
async def prefix(ctx):
    """Obtenir le préfixe du serveur."""
    prefix = _get_prefix(Meowth, ctx.message)
    await ctx.channel.send(_('Prefix for this server is: `{}`').format(prefix))

@_get.command()
@commands.has_permissions(manage_guild=True)
async def perms(ctx, channel_id = None):
    """Afficher les autorisations de Miaoussier pour la guilde et la chaîne."""
    channel = discord.utils.get(ctx.bot.get_all_channels(), id=channel_id)
    guild = channel.guild if channel else ctx.guild
    channel = channel or ctx.channel
    guild_perms = guild.me.guild_permissions
    chan_perms = channel.permissions_for(guild.me)
    req_perms = discord.Permissions(268822608)

    embed = discord.Embed(colour=ctx.guild.me.colour)
    embed.set_author(name=_('Bot Permissions'), icon_url="https://i.imgur.com/wzryVaS.png")

    wrap = functools.partial(textwrap.wrap, width=20)
    names = [wrap(channel.name), wrap(guild.name)]
    if channel.category:
        names.append(wrap(channel.category.name))
    name_len = max(len(n) for n in names)
    def same_len(txt):
        return '\n'.join(txt + ([' '] * (name_len-len(txt))))
    names = [same_len(n) for n in names]
    chan_msg = [f"**{names[0]}** \n{channel.id} \n"]
    guild_msg = [f"**{names[1]}** \n{guild.id} \n"]
    def perms_result(perms):
        data = []
        meet_req = perms >= req_perms
        result = _("**PASS**") if meet_req else _("**FAIL**")
        data.append(f"{result} - {perms.value} \n")
        true_perms = [k for k, v in dict(perms).items() if v is True]
        false_perms = [k for k, v in dict(perms).items() if v is False]
        req_perms_list = [k for k, v in dict(req_perms).items() if v is True]
        true_perms_str = '\n'.join(true_perms)
        if not meet_req:
            missing = '\n'.join([p for p in false_perms if p in req_perms_list])
            meet_req_result = _("**MISSING**")
            data.append(f"{meet_req_result} \n{missing} \n")
        if true_perms_str:
            meet_req_result = _("**ENABLED**")
            data.append(f"{meet_req_result} \n{true_perms_str} \n")
        return '\n'.join(data)
    guild_msg.append(perms_result(guild_perms))
    chan_msg.append(perms_result(chan_perms))
    embed.add_field(name=_('GUILD'), value='\n'.join(guild_msg))
    if channel.category:
        cat_perms = channel.category.permissions_for(guild.me)
        cat_msg = [f"**{names[2]}** \n{channel.category.id} \n"]
        cat_msg.append(perms_result(cat_perms))
        embed.add_field(name=_('CATEGORY'), value='\n'.join(cat_msg))
    embed.add_field(name=_('CHANNEL'), value='\n'.join(chan_msg))

    try:
        await ctx.send(embed=embed)
    except discord.errors.Forbidden:
        # didn't have permissions to send a message with an embed
        try:
            msg = _("I couldn't send an embed here, so I've sent you a DM")
            await ctx.send(msg)
        except discord.errors.Forbidden:
            # didn't have permissions to send a message at all
            pass
        await ctx.author.send(embed=embed)

@Meowth.command()
@commands.has_permissions(manage_guild=True)
async def welcome(ctx, user: discord.Member=None):
    """Test de bienvenue sur vous-même ou membre mentionné.

     Utilisation:!welcome [@member]"""
    if (not user):
        user = ctx.author
    await on_member_join(user)

@Meowth.command(hidden=True)
@commands.has_permissions(manage_guild=True)
async def outputlog(ctx):
    """Obtenez le journal Miaou actuel.

     Utilisation:!outputlog
     La sortie est un lien vers hastebin."""
    with open(os.path.join('logs', 'meowth.log'), 'r', encoding='latin-1', errors='replace') as logfile:
        logdata = logfile.read()
    await ctx.channel.send(hastebin.post(logdata))

@Meowth.command(aliases=['say'])
@commands.has_permissions(manage_guild=True)
async def announce(ctx, *, announce=None):
    """Répète votre message dans un embed de Meowth.

     Utilisation:!announce [annonce]
     Si l'annonce n'est pas ajoutée en même temps que la commande, Miaouss attendra 3 minutes pour un message de suivi contenant l'annonce."""
    message = ctx.message
    channel = message.channel
    guild = message.guild
    author = message.author
    if announce == None:
        announcewait = await channel.send(_("I'll wait for your announcement!"))
        announcemsg = await Meowth.wait_for('message', timeout=180, check=(lambda reply: reply.author == message.author))
        await announcewait.delete()
        if announcemsg != None:
            announce = announcemsg.content
            await announcemsg.delete()
        else:
            confirmation = await channel.send(_("Meowth! You took too long to send me your announcement! Retry when you're ready."))
    embeddraft = discord.Embed(colour=guild.me.colour, description=announce)
    if ctx.invoked_with == "announce":
        title = _('Announcement')
        if Meowth.user.avatar_url:
            embeddraft.set_author(name=title, icon_url=Meowth.user.avatar_url)
        else:
            embeddraft.set_author(name=title)
    draft = await channel.send(embed=embeddraft)
    reaction_list = ['❔', '✅', '❎']
    owner_msg_add = ''
    if checks.is_owner_check(ctx):
        owner_msg_add = '🌎 '
        owner_msg_add += _('to send it to all servers, ')
        reaction_list.insert(0, '🌎')

    def check(reaction, user):
        if user.id == author.id:
            if (str(reaction.emoji) in reaction_list) and (reaction.message.id == rusure.id):
                return True
        return False
    msg = _("That's what you sent, does it look good? React with ")
    msg += "{}❔ "
    msg += _("to send to another channel, ")
    msg += "✅ "
    msg += _("to send it to this channel, or ")
    msg += "❎ "
    msg += _("to cancel")
    rusure = await channel.send(msg.format(owner_msg_add))
    try:
        timeout = False
        res, reactuser = await ask(rusure, channel, author.id, react_list=reaction_list)
    except TypeError:
        timeout = True
    if not timeout:
        await rusure.delete()
        if res.emoji == '❎':
            confirmation = await channel.send(_('Announcement Cancelled.'))
            await draft.delete()
        elif res.emoji == '✅':
            confirmation = await channel.send(_('Announcement Sent.'))
        elif res.emoji == '❔':
            channelwait = await channel.send(_('What channel would you like me to send it to?'))
            channelmsg = await Meowth.wait_for('message', timeout=60, check=(lambda reply: reply.author == message.author))
            if channelmsg.content.isdigit():
                sendchannel = Meowth.get_channel(int(channelmsg.content))
            elif channelmsg.raw_channel_mentions:
                sendchannel = Meowth.get_channel(channelmsg.raw_channel_mentions[0])
            else:
                sendchannel = discord.utils.get(guild.text_channels, name=channelmsg.content)
            if (channelmsg != None) and (sendchannel != None):
                announcement = await sendchannel.send(embed=embeddraft)
                confirmation = await channel.send(_('Announcement Sent.'))
            elif sendchannel == None:
                confirmation = await channel.send(_("Meowth! That channel doesn't exist! Retry when you're ready."))
            else:
                confirmation = await channel.send(_("Meowth! You took too long to send me your announcement! Retry when you're ready."))
            await channelwait.delete()
            await channelmsg.delete()
            await draft.delete()
        elif (res.emoji == '🌎') and checks.is_owner_check(ctx):
            failed = 0
            sent = 0
            count = 0
            recipients = {

            }
            embeddraft.set_footer(text=_('For support, contact us on our Discord server. Invite Code: hhVjAN8'))
            embeddraft.colour = discord.Colour.lighter_grey()
            for guild in Meowth.guilds:
                recipients[guild.name] = guild.owner
            for (guild, destination) in recipients.items():
                try:
                    await destination.send(embed=embeddraft)
                except discord.HTTPException:
                    failed += 1
                    logger.info('Announcement Delivery Failure: {} - {}'.format(destination.name, guild))
                else:
                    sent += 1
                count += 1
            logger.info('Announcement sent to {} server owners: {} successful, {} failed.'.format(count, sent, failed))
            confirmation = await channel.send(_('Announcement sent to {} server owners: {} successful, {} failed.').format(count, sent, failed))
        await asyncio.sleep(10)
        await confirmation.delete()
    else:
        await rusure.delete()
        confirmation = await channel.send(_('Announcement Timed Out.'))
        await asyncio.sleep(10)
        await confirmation.delete()
    await asyncio.sleep(30)
    await message.delete()

@Meowth.group(case_insensitive=True, invoke_without_command=True)
@commands.has_permissions(manage_guild=True)
async def configure(ctx, *, configlist: str=""):
    """Configuration de Meowth

     Utilisation:!configure [list]
     Meowth vous indiquera comment configurer Meowth pour votre serveur.
     Si ce n'est pas la première fois que vous configurez, vous pouvez choisir une section à laquelle vous souhaitez accéder.
     Vous pouvez également inclure une [liste] de sections séparées par des virgules parmi les suivantes:
     tous, équipe, bienvenue, raid, effrayer, inviter, compteurs, sauvage, recherche, vouloir, archive, fuseau horaire"""
    await _configure(ctx, configlist)

async def _configure(ctx, configlist):
    guild = ctx.message.guild
    owner = ctx.message.author
    try:
        await ctx.message.delete()
    except (discord.errors.Forbidden, discord.errors.HTTPException):
        pass
    config_sessions = guild_dict[ctx.guild.id]['configure_dict']['settings'].setdefault('config_sessions',{}).setdefault(owner.id,0) + 1
    guild_dict[ctx.guild.id]['configure_dict']['settings']['config_sessions'][owner.id] = config_sessions
    for session in guild_dict[guild.id]['configure_dict']['settings']['config_sessions'].keys():
        if not guild.get_member(session):
            try:
                del guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][session]
            except KeyError:
                pass
    config_dict_temp = getattr(ctx, 'config_dict_temp',copy.deepcopy(guild_dict[guild.id]['configure_dict']))
    firstconfig = False
    all_commands = [str(x) for x in config_dict_temp.keys()]
    enabled_commands = []
    configreplylist = []
    config_error = False
    if not config_dict_temp['settings']['done']:
        firstconfig = True
    if configlist and not firstconfig:
        configlist = configlist.lower().replace("timezone","settings").split(",")
        configlist = [x.strip().lower() for x in configlist]
        diff =  set(configlist) - set(all_commands)
        if diff and "all" in diff:
            configreplylist = all_commands
        elif not diff:
            configreplylist = configlist
        else:
            await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("I'm sorry, I couldn't understand some of what you entered. Let's just start here.")))
    if config_dict_temp['settings']['config_sessions'][owner.id] > 1:
        await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("**MULTIPLE SESSIONS!**\n\nIt looks like you have **{yoursessions}** active configure sessions. I recommend you send **cancel** first and then send your request again to avoid confusing me.\n\nYour Sessions: **{yoursessions}** | Total Sessions: **{allsessions}**").format(allsessions=sum(config_dict_temp['settings']['config_sessions'].values()),yoursessions=config_dict_temp['settings']['config_sessions'][owner.id])))
    configmessage = _("Meowth! That's Right! Welcome to the configuration for Meowth the Pokemon Go Helper Bot! I will be guiding you through some steps to get me setup on your server.\n\n**Role Setup**\nBefore you begin the configuration, please make sure my role is moved to the top end of the server role hierarchy. It can be under admins and mods, but must be above team and general roles. [Here is an example](http://i.imgur.com/c5eaX1u.png)")
    if not firstconfig and not configreplylist:
        configmessage += _("\n\n**Welcome Back**\nThis isn't your first time configuring. You can either reconfigure everything by replying with **all** or reply with a comma separated list to configure those commands. Example: `want, raid, wild`")
        for commandconfig in config_dict_temp.keys():
            if config_dict_temp[commandconfig].get('enabled',False):
                enabled_commands.append(commandconfig)
        configmessage += _("\n\n**Enabled Commands:**\n{enabled_commands}").format(enabled_commands=", ".join(enabled_commands))
        configmessage += _("\n\n**All Commands:**\n**all** - To redo configuration\n**team** - For Team Assignment configuration\n**welcome** - For Welcome Message configuration\n**raid** - for raid command configuration\n**exraid** - for EX raid command configuration\n**invite** - for invite command configuration\n**counters** - for automatic counters configuration\n**wild** - for wild command configuration\n**research** - for !research command configuration\n**meetup** - for !meetup command configuration\n**want** - for want/unwant command configuration\n**archive** - For !archive configuration\n**trade** - For trade command configuration\n**timezone** - For timezone configuration")
        configmessage += _('\n\nReply with **cancel** at any time throughout the questions to cancel the configure process.')
        await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=configmessage).set_author(name=_('Meowth Configuration - {guild}').format(guild=guild.name), icon_url=Meowth.user.avatar_url))
        while True:
            def check(m):
                return m.guild == None and m.author == owner
            configreply = await Meowth.wait_for('message', check=check)
            configreply.content = configreply.content.replace("timezone", "settings")
            if configreply.content.lower() == 'cancel':
                await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('**CONFIG CANCELLED!**\n\nNo changes have been made.')))
                try:
                    del guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id]
                except KeyError:
                    pass
                return None
            elif "all" in configreply.content.lower():
                configreplylist = all_commands
                break
            else:
                configreplylist = configreply.content.lower().split(",")
                configreplylist = [x.strip() for x in configreplylist]
                for configreplyitem in configreplylist:
                    if configreplyitem not in all_commands:
                        config_error = True
                        break
            if config_error:
                await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("I'm sorry I don't understand. Please reply with the choices above.")))
                continue
            else:
                break
    elif firstconfig == True:
        configmessage += _('\n\nReply with **cancel** at any time throughout the questions to cancel the configure process.')
        await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=configmessage).set_author(name=_('Meowth Configuration - {guild}').format(guild=guild.name), icon_url=Meowth.user.avatar_url))
        configreplylist = all_commands
    try:
        if "team" in configreplylist:
            ctx = await _configure_team(ctx)
            if not ctx:
                return None
        if "welcome" in configreplylist:
            ctx = await _configure_welcome(ctx)
            if not ctx:
                return None
        if "raid" in configreplylist:
            ctx = await _configure_raid(ctx)
            if not ctx:
                return None
        if "exraid" in configreplylist:
            ctx = await _configure_exraid(ctx)
            if not ctx:
                return None
        if "meetup" in configreplylist:
            ctx = await _configure_meetup(ctx)
            if not ctx:
                return None
        if "invite" in configreplylist:
            ctx = await _configure_invite(ctx)
            if not ctx:
                return None
        if "counters" in configreplylist:
            ctx = await _configure_counters(ctx)
            if not ctx:
                return None
        if "wild" in configreplylist:
            ctx = await _configure_wild(ctx)
            if not ctx:
                return None
        if "research" in configreplylist:
            ctx = await _configure_research(ctx)
            if not ctx:
                return None
        if "want" in configreplylist:
            ctx = await _configure_want(ctx)
            if not ctx:
                return None
        if "archive" in configreplylist:
            ctx = await _configure_archive(ctx)
            if not ctx:
                return None
        if "trade" in configreplylist:
            ctx = await _configure_trade(ctx)
            if not ctx:
                return None
        if "settings" in configreplylist:
            ctx = await _configure_settings(ctx)
            if not ctx:
                return None
    finally:
        if ctx:
            ctx.config_dict_temp['settings']['done'] = True
            guild_dict[guild.id]['configure_dict'] = ctx.config_dict_temp
            await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_("Meowth! Alright! Your settings have been saved and I'm ready to go! If you need to change any of these settings, just type **!configure** in your server again.")).set_author(name=_('Configuration Complete'), icon_url=Meowth.user.avatar_url))
        try:
            del guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id]
        except KeyError:
            pass

@configure.command(name='all')
async def configure_all(ctx):
    """Tous les paramètres"""
    await _configure(ctx, "all")

@configure.command()
async def team(ctx):
    """!team command settings"""
    guild = ctx.message.guild
    owner = ctx.message.author
    try:
        await ctx.message.delete()
    except (discord.errors.Forbidden, discord.errors.HTTPException):
        pass
    if not guild_dict[guild.id]['configure_dict']['settings']['done']:
        await _configure(ctx, "all")
        return
    config_sessions = guild_dict[ctx.guild.id]['configure_dict']['settings'].setdefault('config_sessions',{}).setdefault(owner.id,0) + 1
    guild_dict[ctx.guild.id]['configure_dict']['settings']['config_sessions'][owner.id] = config_sessions
    if guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id] > 1:
        await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("**MULTIPLE SESSIONS!**\n\nIt looks like you have **{yoursessions}** active configure sessions. I recommend you send **cancel** first and then send your request again to avoid confusing me.\n\nYour Sessions: **{yoursessions}** | Total Sessions: **{allsessions}**").format(allsessions=sum(guild_dict[guild.id]['configure_dict']['settings']['config_sessions'].values()),yoursessions=guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id])))
    ctx = await _configure_team(ctx)
    if ctx:
        guild_dict[guild.id]['configure_dict'] = ctx.config_dict_temp
        await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_("Meowth! Alright! Your settings have been saved and I'm ready to go! If you need to change any of these settings, just type **!configure** in your server again.")).set_author(name=_('Configuration Complete'), icon_url=Meowth.user.avatar_url))
    try:
        del guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id]
    except KeyError:
        pass

async def _configure_team(ctx):
    guild = ctx.message.guild
    owner = ctx.message.author
    config_dict_temp = getattr(ctx, 'config_dict_temp',copy.deepcopy(guild_dict[guild.id]['configure_dict']))
    await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_("Team assignment allows users to assign their Pokemon Go team role using the **!team** command. If you have a bot that handles this already, you may want to disable this feature.\n\nIf you are to use this feature, ensure existing team roles are as follows: mystic, valor, instinct. These must be all lowercase letters. If they don't exist yet, I'll make some for you instead.\n\nRespond here with: **N** to disable, **Y** to enable:")).set_author(name=_('Team Assignments'), icon_url=Meowth.user.avatar_url))
    while True:
        teamreply = await Meowth.wait_for('message', check=(lambda message: (message.guild == None) and message.author == owner))
        if teamreply.content.lower() == 'y':
            config_dict_temp['team']['enabled'] = True
            high_roles = []
            guild_roles = []
            lowercase_roles = []
            for role in guild.roles:
                if role.name.lower() in config['team_dict'] and role.name not in guild_roles:
                    guild_roles.append(role.name)
            lowercase_roles = [element.lower() for element in guild_roles]
            for team in config['team_dict'].keys():
                temp_role = discord.utils.get(guild.roles, name=team)
                if temp_role == None:
                    try:
                        await guild.create_role(name=team, hoist=False, mentionable=True)
                    except discord.errors.HTTPException:
                        pass
            await owner.send(embed=discord.Embed(colour=discord.Colour.green(), description=_('Team Assignments enabled!')))
            break
        elif teamreply.content.lower() == 'n':
            config_dict_temp['team']['enabled'] = False
            await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('Team Assignments disabled!')))
            break
        elif teamreply.content.lower() == 'cancel':
            await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('**CONFIG CANCELLED!**\n\nNo changes have been made.')))
            return None
        else:
            await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("I'm sorry I don't understand. Please reply with either **N** to disable, or **Y** to enable.")))
            continue
    ctx.config_dict_temp = config_dict_temp
    return ctx

@configure.command()
async def welcome(ctx):
    """Welcome message settings"""
    guild = ctx.message.guild
    owner = ctx.message.author
    try:
        await ctx.message.delete()
    except (discord.errors.Forbidden, discord.errors.HTTPException):
        pass
    if not guild_dict[guild.id]['configure_dict']['settings']['done']:
        await _configure(ctx, "all")
        return
    config_sessions = guild_dict[ctx.guild.id]['configure_dict']['settings'].setdefault('config_sessions',{}).setdefault(owner.id,0) + 1
    guild_dict[ctx.guild.id]['configure_dict']['settings']['config_sessions'][owner.id] = config_sessions
    if guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id] > 1:
        await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("**MULTIPLE SESSIONS!**\n\nIt looks like you have **{yoursessions}** active configure sessions. I recommend you send **cancel** first and then send your request again to avoid confusing me.\n\nYour Sessions: **{yoursessions}** | Total Sessions: **{allsessions}**").format(allsessions=sum(guild_dict[guild.id]['configure_dict']['settings']['config_sessions'].values()),yoursessions=guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id])))
    ctx = await _configure_welcome(ctx)
    if ctx:
        guild_dict[guild.id]['configure_dict'] = ctx.config_dict_temp
        await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_("Meowth! Alright! Your settings have been saved and I'm ready to go! If you need to change any of these settings, just type **!configure** in your server again.")).set_author(name=_('Configuration Complete'), icon_url=Meowth.user.avatar_url))
    try:
        del guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id]
    except KeyError:
        pass

async def _configure_welcome(ctx):
    guild = ctx.message.guild
    owner = ctx.message.author
    config_dict_temp = getattr(ctx, 'config_dict_temp',copy.deepcopy(guild_dict[guild.id]['configure_dict']))
    welcomeconfig = _('I can welcome new members to the server with a short message. Here is an example, but it is customizable:\n\n')
    if config_dict_temp['team']['enabled']:
        welcomeconfig += _("Meowth! Welcome to {server_name}, {owner_name.mention}! Set your team by typing '**!team mystic**' or '**!team valor**' or '**!team instinct**' without quotations. If you have any questions just ask an admin.").format(server_name=guild.name, owner_name=owner)
    else:
        welcomeconfig += _('Meowth! Welcome to {server_name}, {owner_name.mention}! If you have any questions just ask an admin.').format(server_name=guild, owner_name=owner)
    welcomeconfig += _('\n\nThis welcome message can be in a specific channel or a direct message. If you have a bot that handles this already, you may want to disable this feature.\n\nRespond with: **N** to disable, **Y** to enable:')
    await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=welcomeconfig).set_author(name=_('Welcome Message'), icon_url=Meowth.user.avatar_url))
    while True:
        welcomereply = await Meowth.wait_for('message', check=(lambda message: (message.guild == None) and message.author == owner))
        if welcomereply.content.lower() == 'y':
            config_dict_temp['welcome']['enabled'] = True
            await owner.send(embed=discord.Embed(colour=discord.Colour.green(), description=_('Welcome Message enabled!')))
            await owner.send(embed=discord.Embed(
                colour=discord.Colour.lighter_grey(),
                description=(_("Would you like a custom welcome message? "
                             "You can reply with **N** to use the default message above or enter your own below.\n\n"
                             "I can read all [discord formatting](https://support.discordapp.com/hc/en-us/articles/210298617-Markdown-Text-101-Chat-Formatting-Bold-Italic-Underline-) "
                             "and I have the following template tags:\n\n"
                             "**{@member}** - Replace member with user name or ID\n"
                             "**{#channel}** - Replace channel with channel name or ID\n"
                             "**{&role}** - Replace role name or ID (shows as @deleted-role DM preview)\n"
                             "**{user}** - Will mention the new user\n"
                             "**{server}** - Will print your server's name\n"
                             "Surround your message with [] to send it as an embed. **Warning:** Mentions within embeds may be broken on mobile, this is a Discord bug."))).set_author(name=_("Welcome Message"), icon_url=Meowth.user.avatar_url))
            if config_dict_temp['welcome']['welcomemsg'] != 'default':
                await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=config_dict_temp['welcome']['welcomemsg']).set_author(name=_("Current Welcome Message"), icon_url=Meowth.user.avatar_url))
            while True:
                welcomemsgreply = await Meowth.wait_for('message', check=(lambda message: (message.guild == None) and (message.author == owner)))
                if welcomemsgreply.content.lower() == 'n':
                    config_dict_temp['welcome']['welcomemsg'] = 'default'
                    await owner.send(embed=discord.Embed(colour=discord.Colour.green(), description=_("Default welcome message set")))
                    break
                elif welcomemsgreply.content.lower() == "cancel":
                    await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_("**CONFIG CANCELLED!**\n\nNo changes have been made.")))
                    return None
                elif len(welcomemsgreply.content) > 500:
                    await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("Please shorten your message to less than 500 characters. You entered {count}.").format(count=len(welcomemsgreply.content))))
                    continue
                else:
                    welcomemessage, errors = do_template(welcomemsgreply.content, owner, guild)
                    if errors:
                        if welcomemessage.startswith("[") and welcomemessage.endswith("]"):
                            embed = discord.Embed(colour=guild.me.colour, description=welcomemessage[1:-1].format(user=owner.mention))
                            embed.add_field(name=_('Warning'), value=_('The following could not be found:\n{}').format('\n'.join(errors)))
                            await owner.send(embed=embed)
                        else:
                            await owner.send(_("{msg}\n\n**Warning:**\nThe following could not be found: {errors}").format(msg=welcomemessage, errors=', '.join(errors)))
                        await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("Please check the data given and retry a new welcome message, or reply with **N** to use the default.")))
                        continue
                    else:
                        if welcomemessage.startswith("[") and welcomemessage.endswith("]"):
                            embed = discord.Embed(colour=guild.me.colour, description=welcomemessage[1:-1].format(user=owner.mention))
                            question = await owner.send(content=_("Here's what you sent. Does it look ok?"),embed=embed)
                            try:
                                timeout = False
                                res, reactuser = await ask(question, owner, owner.id)
                            except TypeError:
                                timeout = True
                        else:
                            question = await owner.send(content=_("Here's what you sent. Does it look ok?\n\n{welcome}").format(welcome=welcomemessage.format(user=owner.mention)))
                            try:
                                timeout = False
                                res, reactuser = await ask(question, owner, owner.id)
                            except TypeError:
                                timeout = True
                    if timeout or res.emoji == '❎':
                        await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("Please enter a new welcome message, or reply with **N** to use the default.")))
                        continue
                    else:
                        config_dict_temp['welcome']['welcomemsg'] = welcomemessage
                        await owner.send(embed=discord.Embed(colour=discord.Colour.green(), description=_("Welcome Message set to:\n\n{}").format(config_dict_temp['welcome']['welcomemsg'])))
                        break
                break
            await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_("Which channel in your server would you like me to post the Welcome Messages? You can also choose to have them sent to the new member via Direct Message (DM) instead.\n\nRespond with: **channel-name** or ID of a channel in your server or **DM** to Direct Message:")).set_author(name=_("Welcome Message Channel"), icon_url=Meowth.user.avatar_url))
            while True:
                welcomechannelreply = await Meowth.wait_for('message',check=lambda message: message.guild == None and message.author == owner)
                if welcomechannelreply.content.lower() == "dm":
                    config_dict_temp['welcome']['welcomechan'] = "dm"
                    await owner.send(embed=discord.Embed(colour=discord.Colour.green(), description=_("Welcome DM set")))
                    break
                elif " " in welcomechannelreply.content.lower():
                    await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("Channel names can't contain spaces, sorry. Please double check the name and send your response again.")))
                    continue
                elif welcomechannelreply.content.lower() == "cancel":
                    await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('**CONFIG CANCELLED!**\n\nNo changes have been made.')))
                    return None
                else:
                    item = welcomechannelreply.content
                    channel = None
                    if item.isdigit():
                        channel = discord.utils.get(guild.text_channels, id=int(item))
                    if not channel:
                        item = re.sub('[^a-zA-Z0-9 _\\-]+', '', item)
                        item = item.replace(" ","-")
                        name = await letter_case(guild.text_channels, item.lower())
                        channel = discord.utils.get(guild.text_channels, name=name)
                    if channel:
                        guild_channel_list = []
                        for textchannel in guild.text_channels:
                            guild_channel_list.append(textchannel.id)
                        diff = set([channel.id]) - set(guild_channel_list)
                    else:
                        diff = True
                    if (not diff):
                        config_dict_temp['welcome']['welcomechan'] = channel.id
                        ow = channel.overwrites_for(Meowth.user)
                        ow.send_messages = True
                        ow.read_messages = True
                        ow.manage_roles = True
                        try:
                            await channel.set_permissions(Meowth.user, overwrite = ow)
                        except (discord.errors.Forbidden, discord.errors.HTTPException, discord.errors.InvalidArgument):
                            await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_('I couldn\'t set my own permissions in this channel. Please ensure I have the correct permissions in {channel} using **{prefix}get perms**.').format(prefix=ctx.prefix, channel=channel.mention)))
                        await owner.send(embed=discord.Embed(colour=discord.Colour.green(), description=_('Welcome Channel set to {channel}').format(channel=welcomechannelreply.content.lower())))
                        break
                    else:
                        await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("The channel you provided isn't in your server. Please double check your channel and resend your response.")))
                        continue
                break
            break
        elif welcomereply.content.lower() == 'n':
            config_dict_temp['welcome']['enabled'] = False
            await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('Welcome Message disabled!')))
            break
        elif welcomereply.content.lower() == 'cancel':
            await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('**CONFIG CANCELLED!**\n\nNo changes have been made.')))
            return None
        else:
            await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("I'm sorry I don't understand. Please reply with either **N** to disable, or **Y** to enable.")))
            continue
    ctx.config_dict_temp = config_dict_temp
    return ctx

@configure.command()
async def raid(ctx):
    """!raid reporting settings"""
    guild = ctx.message.guild
    owner = ctx.message.author
    try:
        await ctx.message.delete()
    except (discord.errors.Forbidden, discord.errors.HTTPException):
        pass
    if not guild_dict[guild.id]['configure_dict']['settings']['done']:
        await _configure(ctx, "all")
        return
    config_sessions = guild_dict[ctx.guild.id]['configure_dict']['settings'].setdefault('config_sessions',{}).setdefault(owner.id,0) + 1
    guild_dict[ctx.guild.id]['configure_dict']['settings']['config_sessions'][owner.id] = config_sessions
    if guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id] > 1:
        await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("**MULTIPLE SESSIONS!**\n\nIt looks like you have **{yoursessions}** active configure sessions. I recommend you send **cancel** first and then send your request again to avoid confusing me.\n\nYour Sessions: **{yoursessions}** | Total Sessions: **{allsessions}**").format(allsessions=sum(guild_dict[guild.id]['configure_dict']['settings']['config_sessions'].values()),yoursessions=guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id])))
    ctx = await _configure_raid(ctx)
    if ctx:
        guild_dict[guild.id]['configure_dict'] = ctx.config_dict_temp
        await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_("Meowth! Alright! Your settings have been saved and I'm ready to go! If you need to change any of these settings, just type **!configure** in your server again.")).set_author(name=_('Configuration Complete'), icon_url=Meowth.user.avatar_url))
    try:
        del guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id]
    except KeyError:
        pass

async def _configure_raid(ctx):
    guild = ctx.message.guild
    owner = ctx.message.author
    config_dict_temp = getattr(ctx, 'config_dict_temp',copy.deepcopy(guild_dict[guild.id]['configure_dict']))
    await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_("Raid Reporting allows users to report active raids with **!raid** or raid eggs with **!raidegg**. Pokemon raid reports are contained within one or more channels. Each channel will be able to represent different areas/communities. I'll need you to provide a list of channels in your server you will allow reports from in this format: `channel-name, channel-name, channel-name`\n\nExample: `kansas-city-raids, hull-raids, sydney-raids`\n\nIf you do not require raid or raid egg reporting, you may want to disable this function.\n\nRespond with: **N** to disable, or the **channel-name** list to enable, each seperated with a comma and space:")).set_author(name=_('Raid Reporting Channels'), icon_url=Meowth.user.avatar_url))
    citychannel_dict = {}
    while True:
        citychannels = await Meowth.wait_for('message', check=(lambda message: (message.guild == None) and message.author == owner))
        if citychannels.content.lower() == 'n':
            config_dict_temp['raid']['enabled'] = False
            await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('Raid Reporting disabled')))
            break
        elif citychannels.content.lower() == 'cancel':
            await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('**CONFIG CANCELLED!**\n\nNo changes have been made.')))
            return None
        else:
            config_dict_temp['raid']['enabled'] = True
            citychannel_list = citychannels.content.lower().split(',')
            citychannel_list = [x.strip() for x in citychannel_list]
            guild_channel_list = []
            for channel in guild.text_channels:
                guild_channel_list.append(channel.id)
            citychannel_objs = []
            citychannel_names = []
            citychannel_errors = []
            for item in citychannel_list:
                channel = None
                if item.isdigit():
                    channel = discord.utils.get(guild.text_channels, id=int(item))
                if not channel:
                    item = re.sub('[^a-zA-Z0-9 _\\-]+', '', item)
                    item = item.replace(" ","-")
                    name = await letter_case(guild.text_channels, item.lower())
                    channel = discord.utils.get(guild.text_channels, name=name)
                if channel:
                    citychannel_objs.append(channel)
                    citychannel_names.append(channel.name)
                else:
                    citychannel_errors.append(item)
            citychannel_list = [x.id for x in citychannel_objs]
            diff = set(citychannel_list) - set(guild_channel_list)
            if (not diff) and (not citychannel_errors):
                await owner.send(embed=discord.Embed(colour=discord.Colour.green(), description=_('Raid Reporting Channels enabled')))
                for channel in citychannel_objs:
                    ow = channel.overwrites_for(Meowth.user)
                    ow.send_messages = True
                    ow.read_messages = True
                    ow.manage_roles = True
                    try:
                        await channel.set_permissions(Meowth.user, overwrite = ow)
                    except (discord.errors.Forbidden, discord.errors.HTTPException, discord.errors.InvalidArgument):
                        await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_('I couldn\'t set my own permissions in this channel. Please ensure I have the correct permissions in {channel} using **{prefix}get perms**.').format(prefix=ctx.prefix, channel=channel.mention)))
                break
            else:
                await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("The channel list you provided doesn't match with your servers channels.\n\nThe following aren't in your server: **{invalid_channels}**\n\nPlease double check your channel list and resend your reponse.").format(invalid_channels=', '.join(citychannel_errors))))
                continue
    if config_dict_temp['raid']['enabled']:
        await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_('For each report, I generate Google Maps links to give people directions to the raid or egg! To do this, I need to know which suburb/town/region each report channel represents, to ensure we get the right location in the map. For each report channel you provided, I will need its corresponding general location using only letters and spaces, with each location seperated by a comma and space.\n\nExample: `kansas city mo, hull uk, sydney nsw australia`\n\nEach location will have to be in the same order as you provided the channels in the previous question.\n\nRespond with: **location info, location info, location info** each matching the order of the previous channel list below.')).set_author(name=_('Raid Reporting Locations'), icon_url=Meowth.user.avatar_url))
        await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_('{citychannel_list}').format(citychannel_list=citychannels.content.lower()[:2000])).set_author(name=_('Entered Channels'), icon_url=Meowth.user.avatar_url))
        while True:
            cities = await Meowth.wait_for('message', check=(lambda message: (message.guild == None) and message.author == owner))
            if cities.content.lower() == 'cancel':
                await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('**CONFIG CANCELLED!**\n\nNo changes have been made.')))
                return None
            city_list = cities.content.split(',')
            city_list = [x.strip() for x in city_list]
            if len(city_list) == len(citychannel_list):
                for i in range(len(citychannel_list)):
                    citychannel_dict[citychannel_list[i]] = city_list[i]
                break
            else:
                await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("The number of cities doesn't match the number of channels you gave me earlier!\n\nI'll show you the two lists to compare:\n\n{channellist}\n{citylist}\n\nPlease double check that your locations match up with your provided channels and resend your response.").format(channellist=', '.join(citychannel_names), citylist=', '.join(city_list))))
                continue
        config_dict_temp['raid']['report_channels'] = citychannel_dict
        await owner.send(embed=discord.Embed(colour=discord.Colour.green(), description=_('Raid Reporting Locations are set')))
        await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_("How would you like me to categorize the raid channels I create? Your options are:\n\n**none** - If you don't want them categorized\n**same** - If you want them in the same category as the reporting channel\n**region** - If you want them categorized by region\n**level** - If you want them categorized by level.")).set_author(name=_('Raid Reporting Categories'), icon_url=Meowth.user.avatar_url))
        while True:
            guild = Meowth.get_guild(guild.id)
            guild_catlist = []
            for cat in guild.categories:
                guild_catlist.append(cat.id)
            category_dict = {}
            categories = await Meowth.wait_for('message', check=lambda message: message.guild == None and message.author == owner)
            if categories.content.lower() == 'cancel':
                await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('**CONFIG CANCELLED!**\n\nNo changes have been made.')))
                return None
            elif categories.content.lower() == 'none':
                config_dict_temp['raid']['categories'] = None
                break
            elif categories.content.lower() == 'same':
                config_dict_temp['raid']['categories'] = 'same'
                break
            elif categories.content.lower() == 'region':
                while True:
                    guild = Meowth.get_guild(guild.id)
                    guild_catlist = []
                    for cat in guild.categories:
                        guild_catlist.append(cat.id)
                    config_dict_temp['raid']['categories'] = 'region'
                    await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(),description=_("In the same order as they appear below, please give the names of the categories you would like raids reported in each channel to appear in. You do not need to use different categories for each channel, but they do need to be pre-existing categories. Separate each category name with a comma. Response can be either category name or ID.\n\nExample: `kansas city, hull, 1231231241561337813`\n\nYou have configured the following channels as raid reporting channels.")).set_author(name=_('Raid Reporting Categories'), icon_url=Meowth.user.avatar_url))
                    await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_('{citychannel_list}').format(citychannel_list=citychannels.content.lower()[:2000])).set_author(name=_('Entered Channels'), icon_url=Meowth.user.avatar_url))
                    regioncats = await Meowth.wait_for('message', check=lambda message: message.guild == None and message.author == owner)
                    if regioncats.content.lower() == "cancel":
                        await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('**CONFIG CANCELLED!**\n\nNo changes have been made.')))
                        return None
                    regioncat_list = regioncats.content.split(',')
                    regioncat_list = [x.strip() for x in regioncat_list]
                    regioncat_ids = []
                    regioncat_names = []
                    regioncat_errors = []
                    for item in regioncat_list:
                        category = None
                        if item.isdigit():
                            category = discord.utils.get(guild.categories, id=int(item))
                        if not category:
                            name = await letter_case(guild.categories, item.lower())
                            category = discord.utils.get(guild.categories, name=name)
                        if category:
                            regioncat_ids.append(category.id)
                            regioncat_names.append(category.name)
                        else:
                            regioncat_errors.append(item)
                    regioncat_list = regioncat_ids
                    if len(regioncat_list) == len(citychannel_list):
                        catdiff = set(regioncat_list) - set(guild_catlist)
                        if (not catdiff) and (not regioncat_errors):
                            for i in range(len(citychannel_list)):
                                category_dict[citychannel_list[i]] = regioncat_list[i]
                            break
                        else:
                            msg = _("The category list you provided doesn't match with your server's categories.")
                            if regioncat_errors:
                                msg += _("\n\nThe following aren't in your server: **{invalid_categories}**").format(invalid_categories=', '.join(regioncat_errors))
                            msg += _("\n\nPlease double check your category list and resend your response. If you just made these categories, try again.")
                            await owner.send(embed=discord.Embed(colour=discord.Colour.orange(),description=msg))
                            continue
                    else:
                        msg = _("The number of categories I found in your server doesn't match the number of channels you gave me earlier!\n\nI'll show you the two lists to compare:\n\n**Matched Channels:** {channellist}\n**Matched Categories:** {catlist}\n\nPlease double check that your categories match up with your provided channels and resend your response.").format(channellist=', '.join(citychannel_names), catlist=', '.join(regioncat_names) if len(regioncat_list)>0 else "None")
                        if regioncat_errors:
                            msg += _("\n\nThe following aren't in your server: **{invalid_categories}**").format(invalid_categories=', '.join(regioncat_errors))
                        await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=msg))
                        continue
                    break
            elif categories.content.lower() == 'level':
                config_dict_temp['raid']['categories'] = 'level'
                while True:
                    guild = Meowth.get_guild(guild.id)
                    guild_catlist = []
                    for cat in guild.categories:
                        guild_catlist.append(cat.id)
                    await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(),description=_("Pokemon Go currently has five levels of raids. Please provide the names of the categories you would like each level of raid to appear in. Use the following order: 1, 2, 3, 4, 5 \n\nYou do not need to use different categories for each level, but they do need to be pre-existing categories. Separate each category name with a comma. Response can be either category name or ID.\n\nExample: `level 1-3, level 1-3, level 1-3, level 4, 1231231241561337813`")).set_author(name=_('Raid Reporting Categories'), icon_url=Meowth.user.avatar_url))
                    levelcats = await Meowth.wait_for('message', check=lambda message: message.guild == None and message.author == owner)
                    if levelcats.content.lower() == "cancel":
                        await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('**CONFIG CANCELLED!**\n\nNo changes have been made.')))
                        return None
                    levelcat_list = levelcats.content.split(',')
                    levelcat_list = [x.strip() for x in levelcat_list]
                    levelcat_ids = []
                    levelcat_names = []
                    levelcat_errors = []
                    for item in levelcat_list:
                        category = None
                        if item.isdigit():
                            category = discord.utils.get(guild.categories, id=int(item))
                        if not category:
                            name = await letter_case(guild.categories, item.lower())
                            category = discord.utils.get(guild.categories, name=name)
                        if category:
                            levelcat_ids.append(category.id)
                            levelcat_names.append(category.name)
                        else:
                            levelcat_errors.append(item)
                    levelcat_list = levelcat_ids
                    if len(levelcat_list) == 5:
                        catdiff = set(levelcat_list) - set(guild_catlist)
                        if (not catdiff) and (not levelcat_errors):
                            level_list = ["1",'2','3','4','5']
                            for i in range(5):
                                category_dict[level_list[i]] = levelcat_list[i]
                            break
                        else:
                            msg = _("The category list you provided doesn't match with your server's categories.")
                            if levelcat_errors:
                                msg += _("\n\nThe following aren't in your server: **{invalid_categories}**").format(invalid_categories=', '.join(levelcat_errors))
                            msg += _("\n\nPlease double check your category list and resend your response. If you just made these categories, try again.")
                            await owner.send(embed=discord.Embed(colour=discord.Colour.orange(),description=msg))
                            continue
                    else:
                        msg = _("The number of categories I found in your server doesn't match the number of raid levels! Make sure you give me exactly six categories, one for each level of raid. You can use the same category for multiple levels if you want, but I need to see five category names.\n\n**Matched Categories:** {catlist}\n\nPlease double check your categories.").format(catlist=', '.join(levelcat_names) if len(levelcat_list)>0 else "None")
                        if levelcat_errors:
                            msg += _("\n\nThe following aren't in your server: **{invalid_categories}**").format(invalid_categories=', '.join(levelcat_errors))
                        await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=msg))
                        continue
            else:
                await owner.send(embed=discord.Embed(colour=discord.Colour.orange(),description=_("Sorry, I didn't understand your answer! Try again.")))
                continue
            break
        await owner.send(embed=discord.Embed(colour=discord.Colour.green(), description=_('Raid Categories are set')))
        config_dict_temp['raid']['category_dict'] = category_dict
    ctx.config_dict_temp = config_dict_temp
    return ctx

@configure.command()
async def exraid(ctx):
    """!exraid reporting settings"""
    guild = ctx.message.guild
    owner = ctx.message.author
    try:
        await ctx.message.delete()
    except (discord.errors.Forbidden, discord.errors.HTTPException):
        pass
    if not guild_dict[guild.id]['configure_dict']['settings']['done']:
        await _configure(ctx, "all")
        return
    config_sessions = guild_dict[ctx.guild.id]['configure_dict']['settings'].setdefault('config_sessions',{}).setdefault(owner.id,0) + 1
    guild_dict[ctx.guild.id]['configure_dict']['settings']['config_sessions'][owner.id] = config_sessions
    if guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id] > 1:
        await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("**MULTIPLE SESSIONS!**\n\nIt looks like you have **{yoursessions}** active configure sessions. I recommend you send **cancel** first and then send your request again to avoid confusing me.\n\nYour Sessions: **{yoursessions}** | Total Sessions: **{allsessions}**").format(allsessions=sum(guild_dict[guild.id]['configure_dict']['settings']['config_sessions'].values()),yoursessions=guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id])))
    ctx = await _configure_exraid(ctx)
    if ctx:
        guild_dict[guild.id]['configure_dict'] = ctx.config_dict_temp
        await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_("Meowth! Alright! Your settings have been saved and I'm ready to go! If you need to change any of these settings, just type **!configure** in your server again.")).set_author(name=_('Configuration Complete'), icon_url=Meowth.user.avatar_url))
    try:
        del guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id]
    except KeyError:
        pass

async def _configure_exraid(ctx):
    guild = ctx.message.guild
    owner = ctx.message.author
    config_dict_temp = getattr(ctx, 'config_dict_temp',copy.deepcopy(guild_dict[guild.id]['configure_dict']))
    await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_("EX Raid Reporting allows users to report EX raids with **!exraid**. Pokemon EX raid reports are contained within one or more channels. Each channel will be able to represent different areas/communities. I'll need you to provide a list of channels in your server you will allow reports from in this format: `channel-name, channel-name, channel-name`\n\nExample: `kansas-city-raids, hull-raids, sydney-raids`\n\nIf you do not require EX raid reporting, you may want to disable this function.\n\nRespond with: **N** to disable, or the **channel-name** list to enable, each seperated with a comma and space:")).set_author(name=_('EX Raid Reporting Channels'), icon_url=Meowth.user.avatar_url))
    citychannel_dict = {}
    while True:
        citychannels = await Meowth.wait_for('message', check=(lambda message: (message.guild == None) and message.author == owner))
        if citychannels.content.lower() == 'n':
            config_dict_temp['exraid']['enabled'] = False
            await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('EX Raid Reporting disabled')))
            break
        elif citychannels.content.lower() == 'cancel':
            await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('**CONFIG CANCELLED!**\n\nNo changes have been made.')))
            return None
        else:
            config_dict_temp['exraid']['enabled'] = True
            citychannel_list = citychannels.content.lower().split(',')
            citychannel_list = [x.strip() for x in citychannel_list]
            guild_channel_list = []
            for channel in guild.text_channels:
                guild_channel_list.append(channel.id)
            citychannel_objs = []
            citychannel_names = []
            citychannel_errors = []
            for item in citychannel_list:
                channel = None
                if item.isdigit():
                    channel = discord.utils.get(guild.text_channels, id=int(item))
                if not channel:
                    item = re.sub('[^a-zA-Z0-9 _\\-]+', '', item)
                    item = item.replace(" ","-")
                    name = await letter_case(guild.text_channels, item.lower())
                    channel = discord.utils.get(guild.text_channels, name=name)
                if channel:
                    citychannel_objs.append(channel)
                    citychannel_names.append(channel.name)
                else:
                    citychannel_errors.append(item)
            citychannel_list = [x.id for x in citychannel_objs]
            diff = set(citychannel_list) - set(guild_channel_list)
            if (not diff) and (not citychannel_errors):
                await owner.send(embed=discord.Embed(colour=discord.Colour.green(), description=_('EX Raid Reporting Channels enabled')))
                for channel in citychannel_objs:
                    ow = channel.overwrites_for(Meowth.user)
                    ow.send_messages = True
                    ow.read_messages = True
                    ow.manage_roles = True
                    try:
                        await channel.set_permissions(Meowth.user, overwrite = ow)
                    except (discord.errors.Forbidden, discord.errors.HTTPException, discord.errors.InvalidArgument):
                        await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_('I couldn\'t set my own permissions in this channel. Please ensure I have the correct permissions in {channel} using **{prefix}get perms**.').format(prefix=ctx.prefix, channel=channel.mention)))
                break
            else:
                await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("The channel list you provided doesn't match with your servers channels.\n\nThe following aren't in your server: **{invalid_channels}**\n\nPlease double check your channel list and resend your reponse.").format(invalid_channels=', '.join(citychannel_errors))))
                continue
    if config_dict_temp['exraid']['enabled']:
        await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_('For each report, I generate Google Maps links to give people directions to EX raids! To do this, I need to know which suburb/town/region each report channel represents, to ensure we get the right location in the map. For each report channel you provided, I will need its corresponding general location using only letters and spaces, with each location seperated by a comma and space.\n\nExample: `kansas city mo, hull uk, sydney nsw australia`\n\nEach location will have to be in the same order as you provided the channels in the previous question.\n\nRespond with: **location info, location info, location info** each matching the order of the previous channel list below.')).set_author(name=_('EX Raid Reporting Locations'), icon_url=Meowth.user.avatar_url))
        await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_('{citychannel_list}').format(citychannel_list=citychannels.content.lower()[:2000])).set_author(name=_('Entered Channels'), icon_url=Meowth.user.avatar_url))
        while True:
            cities = await Meowth.wait_for('message', check=(lambda message: (message.guild == None) and message.author == owner))
            if cities.content.lower() == 'cancel':
                await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('**CONFIG CANCELLED!**\n\nNo changes have been made.')))
                return None
            city_list = cities.content.split(',')
            city_list = [x.strip() for x in city_list]
            if len(city_list) == len(citychannel_list):
                for i in range(len(citychannel_list)):
                    citychannel_dict[citychannel_list[i]] = city_list[i]
                break
            else:
                await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("The number of cities doesn't match the number of channels you gave me earlier!\n\nI'll show you the two lists to compare:\n\n{channellist}\n{citylist}\n\nPlease double check that your locations match up with your provided channels and resend your response.").format(channellist=', '.join(citychannel_names), citylist=', '.join(city_list))))
                continue
        config_dict_temp['exraid']['report_channels'] = citychannel_dict
        await owner.send(embed=discord.Embed(colour=discord.Colour.green(), description=_('EX Raid Reporting Locations are set')))
        await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_("How would you like me to categorize the EX raid channels I create? Your options are:\n\n**none** - If you don't want them categorized\n**same** - If you want them in the same category as the reporting channel\n**other** - If you want them categorized in a provided category name or ID")).set_author(name=_('EX Raid Reporting Categories'), icon_url=Meowth.user.avatar_url))
        while True:
            guild = Meowth.get_guild(guild.id)
            guild_catlist = []
            for cat in guild.categories:
                guild_catlist.append(cat.id)
            category_dict = {}
            categories = await Meowth.wait_for('message', check=lambda message: message.guild == None and message.author == owner)
            if categories.content.lower() == 'cancel':
                await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('**CONFIG CANCELLED!**\n\nNo changes have been made.')))
                return None
            elif categories.content.lower() == 'none':
                config_dict_temp['exraid']['categories'] = None
                break
            elif categories.content.lower() == 'same':
                config_dict_temp['exraid']['categories'] = 'same'
                break
            elif categories.content.lower() == 'other':
                while True:
                    guild = Meowth.get_guild(guild.id)
                    guild_catlist = []
                    for cat in guild.categories:
                        guild_catlist.append(cat.id)
                    config_dict_temp['exraid']['categories'] = 'region'
                    await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(),description=_("In the same order as they appear below, please give the names of the categories you would like raids reported in each channel to appear in. You do not need to use different categories for each channel, but they do need to be pre-existing categories. Separate each category name with a comma. Response can be either category name or ID.\n\nExample: `kansas city, hull, 1231231241561337813`\n\nYou have configured the following channels as EX raid reporting channels.")).set_author(name=_('EX Raid Reporting Categories'), icon_url=Meowth.user.avatar_url))
                    await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_('{citychannel_list}').format(citychannel_list=citychannels.content.lower()[:2000])).set_author(name=_('Entered Channels'), icon_url=Meowth.user.avatar_url))
                    regioncats = await Meowth.wait_for('message', check=lambda message: message.guild == None and message.author == owner)
                    if regioncats.content.lower() == "cancel":
                        await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('**CONFIG CANCELLED!**\n\nNo changes have been made.')))
                        return None
                    regioncat_list = regioncats.content.split(',')
                    regioncat_list = [x.strip() for x in regioncat_list]
                    regioncat_ids = []
                    regioncat_names = []
                    regioncat_errors = []
                    for item in regioncat_list:
                        category = None
                        if item.isdigit():
                            category = discord.utils.get(guild.categories, id=int(item))
                        if not category:
                            name = await letter_case(guild.categories, item.lower())
                            category = discord.utils.get(guild.categories, name=name)
                        if category:
                            regioncat_ids.append(category.id)
                            regioncat_names.append(category.name)
                        else:
                            regioncat_errors.append(item)
                    regioncat_list = regioncat_ids
                    if len(regioncat_list) == len(citychannel_list):
                        catdiff = set(regioncat_list) - set(guild_catlist)
                        if (not catdiff) and (not regioncat_errors):
                            for i in range(len(citychannel_list)):
                                category_dict[citychannel_list[i]] = regioncat_list[i]
                            break
                        else:
                            msg = _("The category list you provided doesn't match with your server's categories.")
                            if regioncat_errors:
                                msg += _("\n\nThe following aren't in your server: **{invalid_categories}**").format(invalid_categories=', '.join(regioncat_errors))
                            msg += _("\n\nPlease double check your category list and resend your response. If you just made these categories, try again.")
                            await owner.send(embed=discord.Embed(colour=discord.Colour.orange(),description=msg))
                            continue
                    else:
                        msg = _("The number of categories I found in your server doesn't match the number of channels you gave me earlier!\n\nI'll show you the two lists to compare:\n\n**Matched Channels:** {channellist}\n**Matched Categories:** {catlist}\n\nPlease double check that your categories match up with your provided channels and resend your response.").format(channellist=', '.join(citychannel_names), catlist=', '.join(regioncat_names) if len(regioncat_list)>0 else "None")
                        if regioncat_errors:
                            msg += _("\n\nThe following aren't in your server: **{invalid_categories}**").format(invalid_categories=', '.join(regioncat_errors))
                        await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=msg))
                        continue
                    break
            else:
                await owner.send(embed=discord.Embed(colour=discord.Colour.orange(),description=_("Sorry, I didn't understand your answer! Try again.")))
                continue
            break
        await owner.send(embed=discord.Embed(colour=discord.Colour.green(), description=_('EX Raid Categories are set')))
        config_dict_temp['exraid']['category_dict'] = category_dict
        await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_("Who do you want to be able to **see** the EX Raid channels? Your options are:\n\n**everyone** - To have everyone be able to see all reported EX Raids\n**same** - To only allow those with access to the reporting channel.")).set_author(name=_('EX Raid Channel Read Permissions'), icon_url=Meowth.user.avatar_url))
        while True:
            permsconfigset = await Meowth.wait_for('message', check=(lambda message: (message.guild == None) and message.author == owner))
            if permsconfigset.content.lower() == 'everyone':
                config_dict_temp['exraid']['permissions'] = "everyone"
                await owner.send(embed=discord.Embed(colour=discord.Colour.green(), description=_('Everyone permission enabled')))
                break
            elif permsconfigset.content.lower() == 'same':
                config_dict_temp['exraid']['permissions'] = "same"
                await owner.send(embed=discord.Embed(colour=discord.Colour.green(), description=_('Same permission enabled')))
                break
            elif permsconfigset.content.lower() == 'cancel':
                await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('**CONFIG CANCELLED!**\n\nNo changes have been made.')))
                return None
            else:
                await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("I'm sorry I don't understand. Please reply with either **N** to disable, or **Y** to enable.")))
                continue
    ctx.config_dict_temp = config_dict_temp
    return ctx

@configure.command()
async def invite(ctx):
    """!invite command settings"""
    guild = ctx.message.guild
    owner = ctx.message.author
    try:
        await ctx.message.delete()
    except (discord.errors.Forbidden, discord.errors.HTTPException):
        pass
    if not guild_dict[guild.id]['configure_dict']['settings']['done']:
        await _configure(ctx, "all")
        return
    config_sessions = guild_dict[ctx.guild.id]['configure_dict']['settings'].setdefault('config_sessions',{}).setdefault(owner.id,0) + 1
    guild_dict[ctx.guild.id]['configure_dict']['settings']['config_sessions'][owner.id] = config_sessions
    if guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id] > 1:
        await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("**MULTIPLE SESSIONS!**\n\nIt looks like you have **{yoursessions}** active configure sessions. I recommend you send **cancel** first and then send your request again to avoid confusing me.\n\nYour Sessions: **{yoursessions}** | Total Sessions: **{allsessions}**").format(allsessions=sum(guild_dict[guild.id]['configure_dict']['settings']['config_sessions'].values()),yoursessions=guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id])))
    ctx = await _configure_invite(ctx)
    if ctx:
        guild_dict[guild.id]['configure_dict'] = ctx.config_dict_temp
        await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_("Meowth! Alright! Your settings have been saved and I'm ready to go! If you need to change any of these settings, just type **!configure** in your server again.")).set_author(name=_('Configuration Complete'), icon_url=Meowth.user.avatar_url))
    try:
        del guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id]
    except KeyError:
        pass

async def _configure_invite(ctx):
    guild = ctx.message.guild
    owner = ctx.message.author
    config_dict_temp = getattr(ctx, 'config_dict_temp',copy.deepcopy(guild_dict[guild.id]['configure_dict']))
    await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_('Do you want access to EX raids controlled through members using the **!invite** command?\nIf enabled, members will have read-only permissions for all EX Raids until they use **!invite** to gain access. If disabled, EX Raids will inherit the permissions from their reporting channels.\n\nRespond with: **N** to disable, or **Y** to enable:')).set_author(name=_('Invite Configuration'), icon_url=Meowth.user.avatar_url))
    while True:
        inviteconfigset = await Meowth.wait_for('message', check=(lambda message: (message.guild == None) and message.author == owner))
        if inviteconfigset.content.lower() == 'y':
            config_dict_temp['invite']['enabled'] = True
            await owner.send(embed=discord.Embed(colour=discord.Colour.green(), description=_('Invite Command enabled')))
            break
        elif inviteconfigset.content.lower() == 'n':
            config_dict_temp['invite']['enabled'] = False
            await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('Invite Command disabled')))
            break
        elif inviteconfigset.content.lower() == 'cancel':
            await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('**CONFIG CANCELLED!**\n\nNo changes have been made.')))
            return None
        else:
            await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("I'm sorry I don't understand. Please reply with either **N** to disable, or **Y** to enable.")))
            continue
    ctx.config_dict_temp = config_dict_temp
    return ctx

@configure.command()
async def counters(ctx):
    """Automatic counters settings"""
    guild = ctx.message.guild
    owner = ctx.message.author
    try:
        await ctx.message.delete()
    except (discord.errors.Forbidden, discord.errors.HTTPException):
        pass
    if not guild_dict[guild.id]['configure_dict']['settings']['done']:
        await _configure(ctx, "all")
        return
    config_sessions = guild_dict[ctx.guild.id]['configure_dict']['settings'].setdefault('config_sessions',{}).setdefault(owner.id,0) + 1
    guild_dict[ctx.guild.id]['configure_dict']['settings']['config_sessions'][owner.id] = config_sessions
    ctx = await _configure_counters(ctx)
    if ctx:
        guild_dict[guild.id]['configure_dict'] = ctx.config_dict_temp
        await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_("Meowth! Alright! Your settings have been saved and I'm ready to go! If you need to change any of these settings, just type **!configure** in your server again.")).set_author(name=_('Configuration Complete'), icon_url=Meowth.user.avatar_url))
    try:
        del guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id]
    except KeyError:
        pass

async def _configure_counters(ctx):
    guild = ctx.message.guild
    owner = ctx.message.author
    config_dict_temp = getattr(ctx, 'config_dict_temp',copy.deepcopy(guild_dict[guild.id]['configure_dict']))
    await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_('Do you want to generate an automatic counters list in newly created raid channels using PokeBattler?\nIf enabled, I will post a message containing the best counters for the raid boss in new raid channels. Users will still be able to use **!counters** to generate this list.\n\nRespond with: **N** to disable, or enable with a comma separated list of boss levels that you would like me to generate counters for. Example:`3,4,5,EX`')).set_author(name=_('Automatic Counters Configuration'), icon_url=Meowth.user.avatar_url))
    while True:
        countersconfigset = await Meowth.wait_for('message', check=(lambda message: (message.guild == None) and message.author == owner))
        if countersconfigset.content.lower() == 'n':
            config_dict_temp['counters']['enabled'] = False
            config_dict_temp['counters']['auto_levels'] = []
            await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('Automatic Counters disabled')))
            break
        elif countersconfigset.content.lower() == 'cancel':
            await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('**CONFIG CANCELLED!**\n\nNo changes have been made.')))
            return None
        else:
            raidlevel_list = countersconfigset.content.lower().split(',')
            raidlevel_list = [x.strip() for x in raidlevel_list]
            counterlevels = []
            for level in raidlevel_list:
                if level.isdigit() and (int(level) <= 5):
                    counterlevels.append(str(level))
                elif level == "ex":
                    counterlevels.append("EX")
            if len(counterlevels) > 0:
                config_dict_temp['counters']['enabled'] = True
                config_dict_temp['counters']['auto_levels'] = counterlevels
                await owner.send(embed=discord.Embed(colour=discord.Colour.green(), description=_('Automatic Counter Levels set to: {levels}').format(levels=', '.join((str(x) for x in config_dict_temp['counters']['auto_levels'])))))
                break
            else:
                await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("Please enter at least one level from 1 to EX separated by comma. Ex: `4,5,EX` or **N** to turn off automatic counters.")))
                continue
    ctx.config_dict_temp = config_dict_temp
    return ctx

@configure.command()
async def wild(ctx):
    """!wild reporting settings"""
    guild = ctx.message.guild
    owner = ctx.message.author
    try:
        await ctx.message.delete()
    except (discord.errors.Forbidden, discord.errors.HTTPException):
        pass
    if not guild_dict[guild.id]['configure_dict']['settings']['done']:
        await _configure(ctx, "all")
        return
    config_sessions = guild_dict[ctx.guild.id]['configure_dict']['settings'].setdefault('config_sessions',{}).setdefault(owner.id,0) + 1
    guild_dict[ctx.guild.id]['configure_dict']['settings']['config_sessions'][owner.id] = config_sessions
    if guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id] > 1:
        await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("**MULTIPLE SESSIONS!**\n\nIt looks like you have **{yoursessions}** active configure sessions. I recommend you send **cancel** first and then send your request again to avoid confusing me.\n\nYour Sessions: **{yoursessions}** | Total Sessions: **{allsessions}**").format(allsessions=sum(guild_dict[guild.id]['configure_dict']['settings']['config_sessions'].values()),yoursessions=guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id])))
    ctx = await _configure_wild(ctx)
    if ctx:
        guild_dict[guild.id]['configure_dict'] = ctx.config_dict_temp
        await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_("Meowth! Alright! Your settings have been saved and I'm ready to go! If you need to change any of these settings, just type **!configure** in your server again.")).set_author(name=_('Configuration Complete'), icon_url=Meowth.user.avatar_url))
    try:
        del guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id]
    except KeyError:
        pass

async def _configure_wild(ctx):
    guild = ctx.message.guild
    owner = ctx.message.author
    config_dict_temp = getattr(ctx, 'config_dict_temp',copy.deepcopy(guild_dict[guild.id]['configure_dict']))
    await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_("Wild Reporting allows users to report wild spawns with **!wild**. Pokemon **wild** reports are contained within one or more channels. Each channel will be able to represent different areas/communities. I'll need you to provide a list of channels in your server you will allow reports from in this format: `channel-name, channel-name, channel-name`\n\nExample: `kansas-city-wilds, hull-wilds, sydney-wilds`\n\nIf you do not require **wild** reporting, you may want to disable this function.\n\nRespond with: **N** to disable, or the **channel-name** list to enable, each seperated with a comma and space:")).set_author(name=_('Wild Reporting Channels'), icon_url=Meowth.user.avatar_url))
    citychannel_dict = {}
    while True:
        citychannels = await Meowth.wait_for('message', check=(lambda message: (message.guild == None) and message.author == owner))
        if citychannels.content.lower() == 'n':
            config_dict_temp['wild']['enabled'] = False
            await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('Wild Reporting disabled')))
            break
        elif citychannels.content.lower() == 'cancel':
            await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('**CONFIG CANCELLED!**\n\nNo changes have been made.')))
            return None
        else:
            config_dict_temp['wild']['enabled'] = True
            citychannel_list = citychannels.content.lower().split(',')
            citychannel_list = [x.strip() for x in citychannel_list]
            guild_channel_list = []
            for channel in guild.text_channels:
                guild_channel_list.append(channel.id)
            citychannel_objs = []
            citychannel_names = []
            citychannel_errors = []
            for item in citychannel_list:
                channel = None
                if item.isdigit():
                    channel = discord.utils.get(guild.text_channels, id=int(item))
                if not channel:
                    item = re.sub('[^a-zA-Z0-9 _\\-]+', '', item)
                    item = item.replace(" ","-")
                    name = await letter_case(guild.text_channels, item.lower())
                    channel = discord.utils.get(guild.text_channels, name=name)
                if channel:
                    citychannel_objs.append(channel)
                    citychannel_names.append(channel.name)
                else:
                    citychannel_errors.append(item)
            citychannel_list = [x.id for x in citychannel_objs]
            diff = set(citychannel_list) - set(guild_channel_list)
            if (not diff) and (not citychannel_errors):
                await owner.send(embed=discord.Embed(colour=discord.Colour.green(), description=_('Wild Reporting Channels enabled')))
                for channel in citychannel_objs:
                    ow = channel.overwrites_for(Meowth.user)
                    ow.send_messages = True
                    ow.read_messages = True
                    ow.manage_roles = True
                    try:
                        await channel.set_permissions(Meowth.user, overwrite = ow)
                    except (discord.errors.Forbidden, discord.errors.HTTPException, discord.errors.InvalidArgument):
                        await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_('I couldn\'t set my own permissions in this channel. Please ensure I have the correct permissions in {channel} using **{prefix}get perms**.').format(prefix=ctx.prefix, channel=channel.mention)))
                break
            else:
                await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("The channel list you provided doesn't match with your servers channels.\n\nThe following aren't in your server: **{invalid_channels}**\n\nPlease double check your channel list and resend your reponse.").format(invalid_channels=', '.join(citychannel_errors))))
                continue
    if config_dict_temp['wild']['enabled']:
        await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_('For each report, I generate Google Maps links to give people directions to wild spawns! To do this, I need to know which suburb/town/region each report channel represents, to ensure we get the right location in the map. For each report channel you provided, I will need its corresponding general location using only letters and spaces, with each location seperated by a comma and space.\n\nExample: `kansas city mo, hull uk, sydney nsw australia`\n\nEach location will have to be in the same order as you provided the channels in the previous question.\n\nRespond with: **location info, location info, location info** each matching the order of the previous channel list below.')).set_author(name=_('Wild Reporting Locations'), icon_url=Meowth.user.avatar_url))
        await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_('{citychannel_list}').format(citychannel_list=citychannels.content.lower()[:2000])).set_author(name=_('Entered Channels'), icon_url=Meowth.user.avatar_url))
        while True:
            cities = await Meowth.wait_for('message', check=(lambda message: (message.guild == None) and message.author == owner))
            if cities.content.lower() == 'cancel':
                await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('**CONFIG CANCELLED!**\n\nNo changes have been made.')))
                return None
            city_list = cities.content.split(',')
            city_list = [x.strip() for x in city_list]
            if len(city_list) == len(citychannel_list):
                for i in range(len(citychannel_list)):
                    citychannel_dict[citychannel_list[i]] = city_list[i]
                break
            else:
                await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("The number of cities doesn't match the number of channels you gave me earlier!\n\nI'll show you the two lists to compare:\n\n{channellist}\n{citylist}\n\nPlease double check that your locations match up with your provided channels and resend your response.").format(channellist=', '.join(citychannel_names), citylist=', '.join(city_list))))
                continue
        config_dict_temp['wild']['report_channels'] = citychannel_dict
        await owner.send(embed=discord.Embed(colour=discord.Colour.green(), description=_('Wild Reporting Locations are set')))
    ctx.config_dict_temp = config_dict_temp
    return ctx

@configure.command()
async def research(ctx):
    """!research reporting settings"""
    guild = ctx.message.guild
    owner = ctx.message.author
    try:
        await ctx.message.delete()
    except (discord.errors.Forbidden, discord.errors.HTTPException):
        pass
    if not guild_dict[guild.id]['configure_dict']['settings']['done']:
        await _configure(ctx, "all")
        return
    config_sessions = guild_dict[ctx.guild.id]['configure_dict']['settings'].setdefault('config_sessions',{}).setdefault(owner.id,0) + 1
    guild_dict[ctx.guild.id]['configure_dict']['settings']['config_sessions'][owner.id] = config_sessions
    if guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id] > 1:
        await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("**MULTIPLE SESSIONS!**\n\nIt looks like you have **{yoursessions}** active configure sessions. I recommend you send **cancel** first and then send your request again to avoid confusing me.\n\nYour Sessions: **{yoursessions}** | Total Sessions: **{allsessions}**").format(allsessions=sum(guild_dict[guild.id]['configure_dict']['settings']['config_sessions'].values()),yoursessions=guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id])))
    ctx = await _configure_research(ctx)
    if ctx:
        guild_dict[guild.id]['configure_dict'] = ctx.config_dict_temp
        await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_("Meowth! Alright! Your settings have been saved and I'm ready to go! If you need to change any of these settings, just type **!configure** in your server again.")).set_author(name=_('Configuration Complete'), icon_url=Meowth.user.avatar_url))
    try:
        del guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id]
    except KeyError:
        pass

async def _configure_research(ctx):
    guild = ctx.message.guild
    owner = ctx.message.author
    config_dict_temp = getattr(ctx, 'config_dict_temp',copy.deepcopy(guild_dict[guild.id]['configure_dict']))
    await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_("Research Reporting allows users to report field research with **!research**. Pokemon **research** reports are contained within one or more channels. Each channel will be able to represent different areas/communities. I'll need you to provide a list of channels in your server you will allow reports from in this format: `channel-name, channel-name, channel-name`\n\nExample: `kansas-city-research, hull-research, sydney-research`\n\nIf you do not require **research** reporting, you may want to disable this function.\n\nRespond with: **N** to disable, or the **channel-name** list to enable, each seperated with a comma and space:")).set_author(name=_('Research Reporting Channels'), icon_url=Meowth.user.avatar_url))
    citychannel_dict = {}
    while True:
        citychannels = await Meowth.wait_for('message', check=(lambda message: (message.guild == None) and message.author == owner))
        if citychannels.content.lower() == 'n':
            config_dict_temp['research']['enabled'] = False
            await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('Research Reporting disabled')))
            break
        elif citychannels.content.lower() == 'cancel':
            await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('**CONFIG CANCELLED!**\n\nNo changes have been made.')))
            return None
        else:
            config_dict_temp['research']['enabled'] = True
            citychannel_list = citychannels.content.lower().split(',')
            citychannel_list = [x.strip() for x in citychannel_list]
            guild_channel_list = []
            for channel in guild.text_channels:
                guild_channel_list.append(channel.id)
            citychannel_objs = []
            citychannel_names = []
            citychannel_errors = []
            for item in citychannel_list:
                channel = None
                if item.isdigit():
                    channel = discord.utils.get(guild.text_channels, id=int(item))
                if not channel:
                    item = re.sub('[^a-zA-Z0-9 _\\-]+', '', item)
                    item = item.replace(" ","-")
                    name = await letter_case(guild.text_channels, item.lower())
                    channel = discord.utils.get(guild.text_channels, name=name)
                if channel:
                    citychannel_objs.append(channel)
                    citychannel_names.append(channel.name)
                else:
                    citychannel_errors.append(item)
            citychannel_list = [x.id for x in citychannel_objs]
            diff = set(citychannel_list) - set(guild_channel_list)
            if (not diff) and (not citychannel_errors):
                await owner.send(embed=discord.Embed(colour=discord.Colour.green(), description=_('Research Reporting Channels enabled')))
                for channel in citychannel_objs:
                    ow = channel.overwrites_for(Meowth.user)
                    ow.send_messages = True
                    ow.read_messages = True
                    ow.manage_roles = True
                    try:
                        await channel.set_permissions(Meowth.user, overwrite = ow)
                    except (discord.errors.Forbidden, discord.errors.HTTPException, discord.errors.InvalidArgument):
                        await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_('I couldn\'t set my own permissions in this channel. Please ensure I have the correct permissions in {channel} using **{prefix}get perms**.').format(prefix=ctx.prefix, channel=channel.mention)))
                break
            else:
                await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("The channel list you provided doesn't match with your servers channels.\n\nThe following aren't in your server: **{invalid_channels}**\n\nPlease double check your channel list and resend your reponse.").format(invalid_channels=', '.join(citychannel_errors))))
                continue
    if config_dict_temp['research']['enabled']:
        await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_('For each report, I generate Google Maps links to give people directions to field research! To do this, I need to know which suburb/town/region each report channel represents, to ensure we get the right location in the map. For each report channel you provided, I will need its corresponding general location using only letters and spaces, with each location seperated by a comma and space.\n\nExample: `kansas city mo, hull uk, sydney nsw australia`\n\nEach location will have to be in the same order as you provided the channels in the previous question.\n\nRespond with: **location info, location info, location info** each matching the order of the previous channel list below.')).set_author(name=_('Research Reporting Locations'), icon_url=Meowth.user.avatar_url))
        await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_('{citychannel_list}').format(citychannel_list=citychannels.content.lower()[:2000])).set_author(name=_('Entered Channels'), icon_url=Meowth.user.avatar_url))
        while True:
            cities = await Meowth.wait_for('message', check=(lambda message: (message.guild == None) and message.author == owner))
            if cities.content.lower() == 'cancel':
                await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('**CONFIG CANCELLED!**\n\nNo changes have been made.')))
                return None
            city_list = cities.content.split(',')
            city_list = [x.strip() for x in city_list]
            if len(city_list) == len(citychannel_list):
                for i in range(len(citychannel_list)):
                    citychannel_dict[citychannel_list[i]] = city_list[i]
                break
            else:
                await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("The number of cities doesn't match the number of channels you gave me earlier!\n\nI'll show you the two lists to compare:\n\n{channellist}\n{citylist}\n\nPlease double check that your locations match up with your provided channels and resend your response.").format(channellist=', '.join(citychannel_names), citylist=', '.join(city_list))))
                continue
        config_dict_temp['research']['report_channels'] = citychannel_dict
        await owner.send(embed=discord.Embed(colour=discord.Colour.green(), description=_('Research Reporting Locations are set')))
    ctx.config_dict_temp = config_dict_temp
    return ctx

@configure.command(aliases=['event'])
async def meetup(ctx):
    """!meetup reporting settings"""
    guild = ctx.message.guild
    owner = ctx.message.author
    try:
        await ctx.message.delete()
    except (discord.errors.Forbidden, discord.errors.HTTPException):
        pass
    if not guild_dict[guild.id]['configure_dict']['settings']['done']:
        await _configure(ctx, "all")
        return
    config_sessions = guild_dict[ctx.guild.id]['configure_dict']['settings'].setdefault('config_sessions',{}).setdefault(owner.id,0) + 1
    guild_dict[ctx.guild.id]['configure_dict']['settings']['config_sessions'][owner.id] = config_sessions
    if guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id] > 1:
        await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("**MULTIPLE SESSIONS!**\n\nIt looks like you have **{yoursessions}** active configure sessions. I recommend you send **cancel** first and then send your request again to avoid confusing me.\n\nYour Sessions: **{yoursessions}** | Total Sessions: **{allsessions}**").format(allsessions=sum(guild_dict[guild.id]['configure_dict']['settings']['config_sessions'].values()),yoursessions=guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id])))
    ctx = await _configure_meetup(ctx)
    if ctx:
        guild_dict[guild.id]['configure_dict'] = ctx.config_dict_temp
        await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_("Meowth! Alright! Your settings have been saved and I'm ready to go! If you need to change any of these settings, just type **!configure** in your server again.")).set_author(name=_('Configuration Complete'), icon_url=Meowth.user.avatar_url))
    try:
        del guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id]
    except KeyError:
        pass

async def _configure_meetup(ctx):
    guild = ctx.message.guild
    owner = ctx.message.author
    config_dict_temp = getattr(ctx, 'config_dict_temp',copy.deepcopy(guild_dict[guild.id]['configure_dict']))
    config_dict_temp['meetup'] = {}
    await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_("Meetup Reporting allows users to report meetups with **!meetup** or **!event**. Meetup reports are contained within one or more channels. Each channel will be able to represent different areas/communities. I'll need you to provide a list of channels in your server you will allow reports from in this format: `channel-name, channel-name, channel-name`\n\nExample: `kansas-city-meetups, hull-meetups, sydney-meetups`\n\nIf you do not require meetup reporting, you may want to disable this function.\n\nRespond with: **N** to disable, or the **channel-name** list to enable, each seperated with a comma and space:")).set_author(name=_('Meetup Reporting Channels'), icon_url=Meowth.user.avatar_url))
    citychannel_dict = {}
    while True:
        citychannels = await Meowth.wait_for('message', check=(lambda message: (message.guild == None) and message.author == owner))
        if citychannels.content.lower() == 'n':
            config_dict_temp['meetup']['enabled'] = False
            await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('Meetup Reporting disabled')))
            break
        elif citychannels.content.lower() == 'cancel':
            await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('**CONFIG CANCELLED!**\n\nNo changes have been made.')))
            return None
        else:
            config_dict_temp['meetup']['enabled'] = True
            citychannel_list = citychannels.content.lower().split(',')
            citychannel_list = [x.strip() for x in citychannel_list]
            guild_channel_list = []
            for channel in guild.text_channels:
                guild_channel_list.append(channel.id)
            citychannel_objs = []
            citychannel_names = []
            citychannel_errors = []
            for item in citychannel_list:
                channel = None
                if item.isdigit():
                    channel = discord.utils.get(guild.text_channels, id=int(item))
                if not channel:
                    item = re.sub('[^a-zA-Z0-9 _\\-]+', '', item)
                    item = item.replace(" ","-")
                    name = await letter_case(guild.text_channels, item.lower())
                    channel = discord.utils.get(guild.text_channels, name=name)
                if channel:
                    citychannel_objs.append(channel)
                    citychannel_names.append(channel.name)
                else:
                    citychannel_errors.append(item)
            citychannel_list = [x.id for x in citychannel_objs]
            diff = set(citychannel_list) - set(guild_channel_list)
            if (not diff) and (not citychannel_errors):
                await owner.send(embed=discord.Embed(colour=discord.Colour.green(), description=_('Meetup Reporting Channels enabled')))
                for channel in citychannel_objs:
                    ow = channel.overwrites_for(Meowth.user)
                    ow.send_messages = True
                    ow.read_messages = True
                    ow.manage_roles = True
                    try:
                        await channel.set_permissions(Meowth.user, overwrite = ow)
                    except (discord.errors.Forbidden, discord.errors.HTTPException, discord.errors.InvalidArgument):
                        await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_('I couldn\'t set my own permissions in this channel. Please ensure I have the correct permissions in {channel} using **{prefix}get perms**.').format(prefix=ctx.prefix, channel=channel.mention)))
                break
            else:
                await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("The channel list you provided doesn't match with your servers channels.\n\nThe following aren't in your server: **{invalid_channels}**\n\nPlease double check your channel list and resend your reponse.").format(invalid_channels=', '.join(citychannel_errors))))
                continue
    if config_dict_temp['meetup']['enabled']:
        await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_('For each report, I generate Google Maps links to give people directions to meetups! To do this, I need to know which suburb/town/region each report channel represents, to ensure we get the right location in the map. For each report channel you provided, I will need its corresponding general location using only letters and spaces, with each location seperated by a comma and space.\n\nExample: `kansas city mo, hull uk, sydney nsw australia`\n\nEach location will have to be in the same order as you provided the channels in the previous question.\n\nRespond with: **location info, location info, location info** each matching the order of the previous channel list below.')).set_author(name=_('Meetup Reporting Locations'), icon_url=Meowth.user.avatar_url))
        await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_('{citychannel_list}').format(citychannel_list=citychannels.content.lower()[:2000])).set_author(name=_('Entered Channels'), icon_url=Meowth.user.avatar_url))
        while True:
            cities = await Meowth.wait_for('message', check=(lambda message: (message.guild == None) and message.author == owner))
            if cities.content.lower() == 'cancel':
                await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('**CONFIG CANCELLED!**\n\nNo changes have been made.')))
                return None
            city_list = cities.content.split(',')
            city_list = [x.strip() for x in city_list]
            if len(city_list) == len(citychannel_list):
                for i in range(len(citychannel_list)):
                    citychannel_dict[citychannel_list[i]] = city_list[i]
                break
            else:
                await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("The number of cities doesn't match the number of channels you gave me earlier!\n\nI'll show you the two lists to compare:\n\n{channellist}\n{citylist}\n\nPlease double check that your locations match up with your provided channels and resend your response.").format(channellist=', '.join(citychannel_names), citylist=', '.join(city_list))))
                continue
        config_dict_temp['meetup']['report_channels'] = citychannel_dict
        await owner.send(embed=discord.Embed(colour=discord.Colour.green(), description=_('Meetup Reporting Locations are set')))
        await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_("How would you like me to categorize the meetup channels I create? Your options are:\n\n**none** - If you don't want them categorized\n**same** - If you want them in the same category as the reporting channel\n**other** - If you want them categorized in a provided category name or ID")).set_author(name=_('Meetup Reporting Categories'), icon_url=Meowth.user.avatar_url))
        while True:
            guild = Meowth.get_guild(guild.id)
            guild_catlist = []
            for cat in guild.categories:
                guild_catlist.append(cat.id)
            category_dict = {}
            categories = await Meowth.wait_for('message', check=lambda message: message.guild == None and message.author == owner)
            if categories.content.lower() == 'cancel':
                await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('**CONFIG CANCELLED!**\n\nNo changes have been made.')))
                return None
            elif categories.content.lower() == 'none':
                config_dict_temp['meetup']['categories'] = None
                break
            elif categories.content.lower() == 'same':
                config_dict_temp['meetup']['categories'] = 'same'
                break
            elif categories.content.lower() == 'other':
                while True:
                    guild = Meowth.get_guild(guild.id)
                    guild_catlist = []
                    for cat in guild.categories:
                        guild_catlist.append(cat.id)
                    config_dict_temp['meetup']['categories'] = 'region'
                    await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(),description=_("In the same order as they appear below, please give the names of the categories you would like raids reported in each channel to appear in. You do not need to use different categories for each channel, but they do need to be pre-existing categories. Separate each category name with a comma. Response can be either category name or ID.\n\nExample: `kansas city, hull, 1231231241561337813`\n\nYou have configured the following channels as meetup reporting channels.")).set_author(name=_('Meetup Reporting Categories'), icon_url=Meowth.user.avatar_url))
                    await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_('{citychannel_list}').format(citychannel_list=citychannels.content.lower()[:2000])).set_author(name=_('Entered Channels'), icon_url=Meowth.user.avatar_url))
                    regioncats = await Meowth.wait_for('message', check=lambda message: message.guild == None and message.author == owner)
                    if regioncats.content.lower() == "cancel":
                        await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('**CONFIG CANCELLED!**\n\nNo changes have been made.')))
                        return None
                    regioncat_list = regioncats.content.split(',')
                    regioncat_list = [x.strip() for x in regioncat_list]
                    regioncat_ids = []
                    regioncat_names = []
                    regioncat_errors = []
                    for item in regioncat_list:
                        category = None
                        if item.isdigit():
                            category = discord.utils.get(guild.categories, id=int(item))
                        if not category:
                            name = await letter_case(guild.categories, item.lower())
                            category = discord.utils.get(guild.categories, name=name)
                        if category:
                            regioncat_ids.append(category.id)
                            regioncat_names.append(category.name)
                        else:
                            regioncat_errors.append(item)
                    regioncat_list = regioncat_ids
                    if len(regioncat_list) == len(citychannel_list):
                        catdiff = set(regioncat_list) - set(guild_catlist)
                        if (not catdiff) and (not regioncat_errors):
                            for i in range(len(citychannel_list)):
                                category_dict[citychannel_list[i]] = regioncat_list[i]
                            break
                        else:
                            msg = _("The category list you provided doesn't match with your server's categories.")
                            if regioncat_errors:
                                msg += _("\n\nThe following aren't in your server: **{invalid_categories}**").format(invalid_categories=', '.join(regioncat_errors))
                            msg += _("\n\nPlease double check your category list and resend your response. If you just made these categories, try again.")
                            await owner.send(embed=discord.Embed(colour=discord.Colour.orange(),description=msg))
                            continue
                    else:
                        msg = _("The number of categories I found in your server doesn't match the number of channels you gave me earlier!\n\nI'll show you the two lists to compare:\n\n**Matched Channels:** {channellist}\n**Matched Categories:** {catlist}\n\nPlease double check that your categories match up with your provided channels and resend your response.").format(channellist=', '.join(citychannel_names), catlist=', '.join(regioncat_names) if len(regioncat_list)>0 else "None")
                        if regioncat_errors:
                            msg += _("\n\nThe following aren't in your server: **{invalid_categories}**").format(invalid_categories=', '.join(regioncat_errors))
                        await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=msg))
                        continue
                    break
            else:
                await owner.send(embed=discord.Embed(colour=discord.Colour.orange(),description=_("Sorry, I didn't understand your answer! Try again.")))
                continue
            break
        await owner.send(embed=discord.Embed(colour=discord.Colour.green(), description=_('Meetup Categories are set')))
        config_dict_temp['meetup']['category_dict'] = category_dict
    ctx.config_dict_temp = config_dict_temp
    return ctx

@configure.command()
async def want(ctx):
    """!want/!unwant settings"""
    guild = ctx.message.guild
    owner = ctx.message.author
    try:
        await ctx.message.delete()
    except (discord.errors.Forbidden, discord.errors.HTTPException):
        pass
    if not guild_dict[guild.id]['configure_dict']['settings']['done']:
        await _configure(ctx, "all")
        return
    config_sessions = guild_dict[ctx.guild.id]['configure_dict']['settings'].setdefault('config_sessions',{}).setdefault(owner.id,0) + 1
    guild_dict[ctx.guild.id]['configure_dict']['settings']['config_sessions'][owner.id] = config_sessions
    if guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id] > 1:
        await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("**MULTIPLE SESSIONS!**\n\nIt looks like you have **{yoursessions}** active configure sessions. I recommend you send **cancel** first and then send your request again to avoid confusing me.\n\nYour Sessions: **{yoursessions}** | Total Sessions: **{allsessions}**").format(allsessions=sum(guild_dict[guild.id]['configure_dict']['settings']['config_sessions'].values()),yoursessions=guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id])))
    ctx = await _configure_want(ctx)
    if ctx:
        guild_dict[guild.id]['configure_dict'] = ctx.config_dict_temp
        await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_("Meowth! Alright! Your settings have been saved and I'm ready to go! If you need to change any of these settings, just type **!configure** in your server again.")).set_author(name=_('Configuration Complete'), icon_url=Meowth.user.avatar_url))
    try:
        del guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id]
    except KeyError:
        pass

async def _configure_want(ctx):
    guild = ctx.message.guild
    owner = ctx.message.author
    config_dict_temp = getattr(ctx, 'config_dict_temp',copy.deepcopy(guild_dict[guild.id]['configure_dict']))
    await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_("The **!want** and **!unwant** commands let you add or remove roles for Pokemon that will be mentioned in reports. This let you get notifications on the Pokemon you want to track. I just need to know what channels you want to allow people to manage their pokemon with the **!want** and **!unwant** command.\n\nIf you don't want to allow the management of tracked Pokemon roles, then you may want to disable this feature.\n\nRepond with: **N** to disable, or the **channel-name** list to enable, each seperated by a comma and space.")).set_author(name=_('Pokemon Notifications'), icon_url=Meowth.user.avatar_url))
    while True:
        wantchs = await Meowth.wait_for('message', check=(lambda message: (message.guild == None) and message.author == owner))
        if wantchs.content.lower() == 'n':
            config_dict_temp['want']['enabled'] = False
            await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('Pokemon Notifications disabled')))
            break
        elif wantchs.content.lower() == 'cancel':
            await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('**CONFIG CANCELLED!**\n\nNo changes have been made.')))
            return None
        else:
            want_list = wantchs.content.lower().split(',')
            want_list = [x.strip() for x in want_list]
            guild_channel_list = []
            for channel in guild.text_channels:
                guild_channel_list.append(channel.id)
            want_list_objs = []
            want_list_names = []
            want_list_errors = []
            for item in want_list:
                channel = None
                if item.isdigit():
                    channel = discord.utils.get(guild.text_channels, id=int(item))
                if not channel:
                    item = re.sub('[^a-zA-Z0-9 _\\-]+', '', item)
                    item = item.replace(" ","-")
                    name = await letter_case(guild.text_channels, item.lower())
                    channel = discord.utils.get(guild.text_channels, name=name)
                if channel:
                    want_list_objs.append(channel)
                    want_list_names.append(channel.name)
                else:
                    want_list_errors.append(item)
            want_list_set = [x.id for x in want_list_objs]
            diff = set(want_list_set) - set(guild_channel_list)
            if (not diff) and (not want_list_errors):
                config_dict_temp['want']['enabled'] = True
                config_dict_temp['want']['report_channels'] = want_list_set
                for channel in want_list_objs:
                    ow = channel.overwrites_for(Meowth.user)
                    ow.send_messages = True
                    ow.read_messages = True
                    ow.manage_roles = True
                    try:
                        await channel.set_permissions(Meowth.user, overwrite = ow)
                    except (discord.errors.Forbidden, discord.errors.HTTPException, discord.errors.InvalidArgument):
                        await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_('I couldn\'t set my own permissions in this channel. Please ensure I have the correct permissions in {channel} using **{prefix}get perms**.').format(prefix=ctx.prefix, channel=channel.mention)))
                await owner.send(embed=discord.Embed(colour=discord.Colour.green(), description=_('Pokemon Notifications enabled')))
                break
            else:
                await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("The channel list you provided doesn't match with your servers channels.\n\nThe following aren't in your server: **{invalid_channels}**\n\nPlease double check your channel list and resend your reponse.").format(invalid_channels=', '.join(want_list_errors))))
                continue
    ctx.config_dict_temp = config_dict_temp
    return ctx

@configure.command()
async def archive(ctx):
    """Configure !archive command settings"""
    guild = ctx.message.guild
    owner = ctx.message.author
    try:
        await ctx.message.delete()
    except (discord.errors.Forbidden, discord.errors.HTTPException):
        pass
    if not guild_dict[guild.id]['configure_dict']['settings']['done']:
        await _configure(ctx, "all")
        return
    config_sessions = guild_dict[ctx.guild.id]['configure_dict']['settings'].setdefault('config_sessions',{}).setdefault(owner.id,0) + 1
    guild_dict[ctx.guild.id]['configure_dict']['settings']['config_sessions'][owner.id] = config_sessions
    if guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id] > 1:
        await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("**MULTIPLE SESSIONS!**\n\nIt looks like you have **{yoursessions}** active configure sessions. I recommend you send **cancel** first and then send your request again to avoid confusing me.\n\nYour Sessions: **{yoursessions}** | Total Sessions: **{allsessions}**").format(allsessions=sum(guild_dict[guild.id]['configure_dict']['settings']['config_sessions'].values()),yoursessions=guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id])))
    ctx = await _configure_archive(ctx)
    if ctx:
        guild_dict[guild.id]['configure_dict'] = ctx.config_dict_temp
        await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_("Meowth! Alright! Your settings have been saved and I'm ready to go! If you need to change any of these settings, just type **!configure** in your server again.")).set_author(name=_('Configuration Complete'), icon_url=Meowth.user.avatar_url))
    try:
        del guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id]
    except KeyError:
        pass

async def _configure_archive(ctx):
    guild = ctx.message.guild
    owner = ctx.message.author
    config_dict_temp = getattr(ctx, 'config_dict_temp',copy.deepcopy(guild_dict[guild.id]['configure_dict']))
    await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_("The **!archive** command marks temporary raid channels for archival rather than deletion. This can be useful for investigating potential violations of your server's rules in these channels.\n\nIf you would like to disable this feature, reply with **N**. Otherwise send the category you would like me to place archived channels in. You can say **same** to keep them in the same category, or type the name or ID of a category in your server.")).set_author(name=_('Archive Configuration'), icon_url=Meowth.user.avatar_url))
    config_dict_temp['archive'] = {}
    while True:
        archivemsg = await Meowth.wait_for('message', check=(lambda message: (message.guild == None) and message.author == owner))
        if archivemsg.content.lower() == 'cancel':
            await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('**CONFIG CANCELLED!**\n\nNo changes have been made.')))
            return None
        if archivemsg.content.lower() == 'same':
            config_dict_temp['archive']['category'] = 'same'
            config_dict_temp['archive']['enabled'] = True
            await owner.send(embed=discord.Embed(colour=discord.Colour.green(), description=_('Archived channels will remain in the same category.')))
            break
        if archivemsg.content.lower() == 'n':
            config_dict_temp['archive']['enabled'] = False
            await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('Archived Channels disabled.')))
            break
        else:
            item = archivemsg.content
            category = None
            if item.isdigit():
                category = discord.utils.get(guild.categories, id=int(item))
            if not category:
                name = await letter_case(guild.categories, item.lower())
                category = discord.utils.get(guild.categories, name=name)
            if not category:
                await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("I couldn't find the category you replied with! Please reply with **same** to leave archived channels in the same category, or give the name or ID of an existing category.")))
                continue
            config_dict_temp['archive']['category'] = category.id
            config_dict_temp['archive']['enabled'] = True
            await owner.send(embed=discord.Embed(colour=discord.Colour.green(), description=_('Archive category set.')))
            break
    if config_dict_temp['archive']['enabled']:
        await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_("I can also listen in your raid channels for words or phrases that you want to trigger an automatic archival. For example, if discussion of spoofing is against your server rules, you might tell me to listen for the word 'spoofing'.\n\nReply with **none** to disable this feature, or reply with a comma separated list of phrases you want me to listen in raid channels for.")).set_author(name=_('Archive Configuration'), icon_url=Meowth.user.avatar_url))
        phrasemsg = await Meowth.wait_for('message', check=(lambda message: (message.guild == None) and message.author == owner))
        if phrasemsg.content.lower() == 'none':
            config_dict_temp['archive']['list'] = None
            await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('Phrase list disabled.')))
        elif phrasemsg.content.lower() == 'cancel':
            await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('**CONFIG CANCELLED!**\n\nNo changes have been made.')))
            return None
        else:
            phrase_list = phrasemsg.content.lower().split(",")
            for i in range(len(phrase_list)):
                phrase_list[i] = phrase_list[i].strip()
            config_dict_temp['archive']['list'] = phrase_list
            await owner.send(embed=discord.Embed(colour=discord.Colour.green(), description=_('Archive Phrase list set.')))
    ctx.config_dict_temp = config_dict_temp
    return ctx

@configure.command(aliases=['settings'])
async def timezone(ctx):
    """Configure timezone and other settings"""
    guild = ctx.message.guild
    owner = ctx.message.author
    try:
        await ctx.message.delete()
    except (discord.errors.Forbidden, discord.errors.HTTPException):
        pass
    if not guild_dict[guild.id]['configure_dict']['settings']['done']:
        await _configure(ctx, "all")
        return
    config_sessions = guild_dict[ctx.guild.id]['configure_dict']['settings'].setdefault('config_sessions',{}).setdefault(owner.id,0) + 1
    guild_dict[ctx.guild.id]['configure_dict']['settings']['config_sessions'][owner.id] = config_sessions
    if guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id] > 1:
        await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("**MULTIPLE SESSIONS!**\n\nIt looks like you have **{yoursessions}** active configure sessions. I recommend you send **cancel** first and then send your request again to avoid confusing me.\n\nYour Sessions: **{yoursessions}** | Total Sessions: **{allsessions}**").format(allsessions=sum(guild_dict[guild.id]['configure_dict']['settings']['config_sessions'].values()),yoursessions=guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id])))
    ctx = await _configure_settings(ctx)
    if ctx:
        guild_dict[guild.id]['configure_dict'] = ctx.config_dict_temp
        await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_("Meowth! Alright! Your settings have been saved and I'm ready to go! If you need to change any of these settings, just type **!configure** in your server again.")).set_author(name=_('Configuration Complete'), icon_url=Meowth.user.avatar_url))
    try:
        del guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id]
    except KeyError:
        pass

async def _configure_settings(ctx):
    guild = ctx.message.guild
    owner = ctx.message.author
    config_dict_temp = getattr(ctx, 'config_dict_temp',copy.deepcopy(guild_dict[guild.id]['configure_dict']))
    await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_("There are a few settings available that are not within **!configure**. To set these, use **!set <setting>** in any channel to set that setting.\n\nThese include:\n**!set regional <name or number>** - To set a server's regional raid boss\n**!set prefix <prefix>** - To set my command prefix\n**!set timezone <offset>** - To set offset outside of **!configure**\n**!set silph <trainer>** - To set a trainer's SilphRoad card (usable by members)\n**!set pokebattler <ID>** - To set a trainer's pokebattler ID (usable by members)\n\nHowever, we can do your timezone now to help coordinate reports for you. For others, use the **!set** command.\n\nThe current 24-hr time UTC is {utctime}. How many hours off from that are you?\n\nRespond with: A number from **-12** to **12**:").format(utctime=strftime('%H:%M', time.gmtime()))).set_author(name=_('Timezone Configuration and Other Settings'), icon_url=Meowth.user.avatar_url))
    while True:
        offsetmsg = await Meowth.wait_for('message', check=(lambda message: (message.guild == None) and message.author == owner))
        if offsetmsg.content.lower() == 'cancel':
            await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('**CONFIG CANCELLED!**\n\nNo changes have been made.')))
            return None
        else:
            try:
                offset = float(offsetmsg.content)
            except ValueError:
                await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("I couldn't convert your answer to an appropriate timezone!\n\nPlease double check what you sent me and resend a number strarting from **-12** to **12**.")))
                continue
            if (not ((- 12) <= offset <= 14)):
                await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("I couldn't convert your answer to an appropriate timezone!\n\nPlease double check what you sent me and resend a number strarting from **-12** to **12**.")))
                continue
            else:
                break
    config_dict_temp['settings']['offset'] = offset
    await owner.send(embed=discord.Embed(colour=discord.Colour.green(), description=_('Timezone set')))
    ctx.config_dict_temp = config_dict_temp
    return ctx

@configure.command()
async def trade(ctx):
    """!trade reporting settings"""
    guild = ctx.message.guild
    owner = ctx.message.author
    try:
        await ctx.message.delete()
    except (discord.errors.Forbidden, discord.errors.HTTPException):
        pass
    if not guild_dict[guild.id]['configure_dict']['settings']['done']:
        await _configure(ctx, "all")
        return
    config_sessions = guild_dict[ctx.guild.id]['configure_dict']['settings'].setdefault('config_sessions',{}).setdefault(owner.id,0) + 1
    guild_dict[ctx.guild.id]['configure_dict']['settings']['config_sessions'][owner.id] = config_sessions
    if guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id] > 1:
        await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("**MULTIPLE SESSIONS!**\n\nIt looks like you have **{yoursessions}** active configure sessions. I recommend you send **cancel** first and then send your request again to avoid confusing me.\n\nYour Sessions: **{yoursessions}** | Total Sessions: **{allsessions}**").format(allsessions=sum(guild_dict[guild.id]['configure_dict']['settings']['config_sessions'].values()),yoursessions=guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id])))
    ctx = await _configure_trade(ctx)
    if ctx:
        guild_dict[guild.id]['configure_dict'] = ctx.config_dict_temp
        await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_("Meowth! Alright! Your settings have been saved and I'm ready to go! If you need to change any of these settings, just type **!configure** in your server again.")).set_author(name=_('Configuration Complete'), icon_url=Meowth.user.avatar_url))
    try:
        del guild_dict[guild.id]['configure_dict']['settings']['config_sessions'][owner.id]
    except KeyError:
        pass

async def _configure_trade(ctx):
    guild = ctx.message.guild
    owner = ctx.message.author
    config_dict_temp = getattr(ctx, 'config_dict_temp',copy.deepcopy(guild_dict[guild.id]['configure_dict']))
    await owner.send(embed=discord.Embed(colour=discord.Colour.lighter_grey(), description=_("The **!trade** command allows your users to organize and coordinate trades. This command requires at least one channel specifically for trades.\n\nIf you would like to disable this feature, reply with **N**. Otherwise, just send the names or IDs of the channels you want to allow the **!trade** command in, separated by commas.")).set_author(name=_('Trade Configuration'), icon_url=Meowth.user.avatar_url))
    while True:
        trademsg = await Meowth.wait_for('message', check=(lambda message: (message.guild == None) and message.author == owner))
        if trademsg.content.lower() == 'cancel':
            await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('**CONFIG CANCELLED!**\n\nNo changes have been made.')))
            return None
        elif trademsg.content.lower() == 'n':
            config_dict_temp['trade'] = {'enabled': False, 'report_channels': []}
            await owner.send(embed=discord.Embed(colour=discord.Colour.red(), description=_('Trade disabled.')))
            break
        else:
            trade_list = trademsg.content.lower().split(',')
            trade_list = [x.strip() for x in trade_list]
            guild_channel_list = []
            for channel in guild.text_channels:
                guild_channel_list.append(channel.id)
            trade_list_objs = []
            trade_list_names = []
            trade_list_errors = []
            for item in trade_list:
                channel = None
                if item.isdigit():
                    channel = discord.utils.get(guild.text_channels, id=int(item))
                if not channel:
                    item = re.sub('[^a-zA-Z0-9 _\\-]+', '', item)
                    item = item.replace(" ","-")
                    name = await letter_case(guild.text_channels, item.lower())
                    channel = discord.utils.get(guild.text_channels, name=name)
                if channel:
                    trade_list_objs.append(channel)
                    trade_list_names.append(channel.name)
                else:
                    trade_list_errors.append(item)
            trade_list_set = [x.id for x in trade_list_objs]
            diff = set(trade_list_set) - set(guild_channel_list)
            if (not diff) and (not trade_list_errors):
                config_dict_temp['trade']['enabled'] = True
                config_dict_temp['trade']['report_channels'] = trade_list_set
                for channel in trade_list_objs:
                    ow = channel.overwrites_for(Meowth.user)
                    ow.send_messages = True
                    ow.read_messages = True
                    ow.manage_roles = True
                    try:
                        await channel.set_permissions(Meowth.user, overwrite = ow)
                    except (discord.errors.Forbidden, discord.errors.HTTPException, discord.errors.InvalidArgument):
                        await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_('I couldn\'t set my own permissions in this channel. Please ensure I have the correct permissions in {channel} using **{prefix}get perms**.').format(prefix=ctx.prefix, channel=channel.mention)))
                await owner.send(embed=discord.Embed(colour=discord.Colour.green(), description=_('Pokemon Trades enabled')))
                break
            else:
                await owner.send(embed=discord.Embed(colour=discord.Colour.orange(), description=_("The channel list you provided doesn't match with your servers channels.\n\nThe following aren't in your server: **{invalid_channels}**\n\nPlease double check your channel list and resend your reponse.").format(invalid_channels=', '.join(trade_list_errors))))
                continue
    ctx.config_dict_temp = config_dict_temp
    return ctx

@Meowth.command()
@checks.is_owner()
async def reload_json(ctx):
    """Recharge les fichiers JSON pour le serveur

     Utilisation:!reload_json
     Utile pour éviter un redémarrage complet si la liste des boss a été modifiée"""
    load_config()
    await ctx.message.add_reaction('☑')

@Meowth.command()
@checks.is_dev_or_owner()
async def raid_json(ctx, level=None, *, newlist=None):
    'Modifie ou affiche raid_info.json\n\n    Utilisation: !raid_json [level] [list]'
    msg = ''
    if (not level) and (not newlist):
        for level in raid_info['raid_eggs']:
            msg += _('\n**Level {level} raid list:** `{raidlist}` \n').format(level=level, raidlist=raid_info['raid_eggs'][level]['pokemon'])
            for pkmn in raid_info['raid_eggs'][level]['pokemon']:
                msg += '{name} ({number})'.format(name=get_name(pkmn).title(), number=pkmn)
                msg += ' '
            msg += '\n'
        return await ctx.channel.send(msg)
    elif level in raid_info['raid_eggs'] and (not newlist):
        msg += _('**Level {level} raid list:** `{raidlist}` \n').format(level=level, raidlist=raid_info['raid_eggs'][level]['pokemon'])
        for pkmn in raid_info['raid_eggs'][level]['pokemon']:
            msg += '{name} ({number})'.format(name=get_name(pkmn).title(), number=pkmn)
            msg += ' '
        msg += '\n'
        return await ctx.channel.send(msg)
    elif level in raid_info['raid_eggs'] and newlist:
        newlist = [item.strip() for item in newlist.strip('[]').split(',')]
        try:
            intlist = [int(x) for x in newlist]
        except:
            return await ctx.channel.send(_("I couldn't understand the list you supplied! Please use a comma-separated list of Pokemon species numbers."))
        msg += _('I will replace this:\n')
        msg += _('**Level {level} raid list:** `{raidlist}` \n').format(level=level, raidlist=raid_info['raid_eggs'][level]['pokemon'])
        for pkmn in raid_info['raid_eggs'][level]['pokemon']:
            msg += '{name} ({number})'.format(name=get_name(pkmn).title(), number=pkmn)
            msg += ' '
        msg += _('\n\nWith this:\n')
        msg += _('**Level {level} raid list:** `{raidlist}` \n').format(level=level, raidlist=('[' + ', '.join(newlist)) + ']')
        for pkmn in newlist:
            msg += '{name} ({number})'.format(name=get_name(pkmn).title(), number=pkmn)
            msg += ' '
        msg += _('\n\nContinue?')
        question = await ctx.channel.send(msg)
        try:
            timeout = False
            res, reactuser = await ask(question, ctx.channel, ctx.author.id)
        except TypeError:
            timeout = True
        if timeout or res.emoji == '❎':
            return await ctx.channel.send(_("Meowth! Configuration cancelled!"))
        elif res.emoji == '✅':
            with open(os.path.join('data', 'raid_info.json'), 'r') as fd:
                data = json.load(fd)
            tmp = data['raid_eggs'][level]['pokemon']
            data['raid_eggs'][level]['pokemon'] = intlist
            with open(os.path.join('data', 'raid_info.json'), 'w') as fd:
                json.dump(data, fd, indent=2, separators=(', ', ': '))
            load_config()
            await question.clear_reactions()
            await question.add_reaction('☑')
            return await ctx.channel.send(_("Meowth! Configuration successful!"))
        else:
            return await ctx.channel.send(_("Meowth! I'm not sure what went wrong, but configuration is cancelled!"))

@Meowth.command()
@commands.has_permissions(manage_guild=True)
async def reset_board(ctx, *, user=None, type=None):
    guild = ctx.guild
    trainers = guild_dict[guild.id]['trainers']
    tgt_string = ""
    tgt_trainer = None
    if user:
        converter = commands.MemberConverter()
        for argument in user.split():
            try:
                tgt_trainer = await converter.convert(ctx, argument)
                tgt_string = tgt_trainer.display_name
            except:
                tgt_trainer = None
                tgt_string = _("every user")
            if tgt_trainer:
                user = user.replace(argument,"").strip()
                break
        for argument in user.split():
            if "raid" in argument.lower():
                type = "raid_reports"
                break
            elif "egg" in argument.lower():
                type = "egg_reports"
                break
            elif "ex" in argument.lower():
                type = "ex_reports"
                break
            elif "wild" in argument.lower():
                type = "wild_reports"
                break
            elif "res" in argument.lower():
                type = "research_reports"
                break
    if not type:
        type = "total_reports"
    msg = _("Are you sure you want to reset the **{type}** report stats for **{target}**?").format(type=type, target=tgt_string)
    question = await ctx.channel.send(msg)
    try:
        timeout = False
        res, reactuser = await ask(question, ctx.message.channel, ctx.message.author.id)
    except TypeError:
        timeout = True
    await question.delete()
    if timeout or res.emoji == '❎':
        return
    elif res.emoji == '✅':
        pass
    else:
        return
    for trainer in trainers:
        if tgt_trainer:
            trainer = tgt_trainer.id
        if type == "total_reports":
            trainers[trainer]['raid_reports'] = 0
            trainers[trainer]['wild_reports'] = 0
            trainers[trainer]['ex_reports'] = 0
            trainers[trainer]['egg_reports'] = 0
            trainers[trainer]['research_reports'] = 0
        else:
            trainers[trainer][type] = 0
        if tgt_trainer:
            await ctx.send(_("{trainer}'s report stats have been cleared!").format(trainer=tgt_trainer.display_name))
            return
    await ctx.send("This server's report stats have been reset!")

@Meowth.command()
@commands.has_permissions(manage_channels=True)
@checks.raidchannel()
async def changeraid(ctx, newraid):
    """Change le boss du raid.

     Utilisation:!changeraid <nouveau pokemon ou niveau>
     Seulement utilisable par les administrateurs."""
    message = ctx.message
    guild = message.guild
    channel = message.channel
    if (not channel) or (channel.id not in guild_dict[guild.id]['raidchannel_dict']):
        await channel.send(_('The channel you entered is not a raid channel.'))
        return
    if newraid.isdigit():
        raid_channel_name = _('level-{egg_level}-egg-').format(egg_level=newraid)
        raid_channel_name += sanitize_channel_name(guild_dict[guild.id]['raidchannel_dict'][channel.id]['address'])
        guild_dict[guild.id]['raidchannel_dict'][channel.id]['egglevel'] = newraid
        guild_dict[guild.id]['raidchannel_dict'][channel.id]['pokemon'] = ''
        changefrom = guild_dict[guild.id]['raidchannel_dict'][channel.id]['type']
        guild_dict[guild.id]['raidchannel_dict'][channel.id]['type'] = 'egg'
        egg_img = raid_info['raid_eggs'][newraid]['egg_img']
        boss_list = []
        for p in raid_info['raid_eggs'][newraid]['pokemon']:
            p_name = get_name(p).title()
            p_type = get_type(message.guild, p)
            boss_list.append((((p_name + ' (') + str(p)) + ') ') + ''.join(p_type))
        raid_img_url = 'https://raw.githubusercontent.com/FoglyOgly/Meowth/discordpy-v1/images/eggs/{}?cache=0'.format(str(egg_img))
        raid_message = await channel.get_message(guild_dict[guild.id]['raidchannel_dict'][channel.id]['raidmessage'])
        report_channel = Meowth.get_channel(raid_message.raw_channel_mentions[0])
        report_message = await report_channel.get_message(guild_dict[guild.id]['raidchannel_dict'][channel.id]['raidreport'])
        oldembed = raid_message.embeds[0]
        raid_embed = discord.Embed(title=oldembed.title, url=oldembed.url, colour=message.guild.me.colour)
        if len(raid_info['raid_eggs'][newraid]['pokemon']) > 1:
            raid_embed.add_field(name=_('**Possible Bosses:**'), value=_('{bosslist1}').format(bosslist1='\n'.join(boss_list[::2])), inline=True)
            raid_embed.add_field(name='\u200b', value=_('{bosslist2}').format(bosslist2='\n'.join(boss_list[1::2])), inline=True)
        else:
            raid_embed.add_field(name=_('**Possible Bosses:**'), value=_('{bosslist}').format(bosslist=''.join(boss_list)), inline=True)
            raid_embed.add_field(name='\u200b', value='\u200b', inline=True)
        raid_embed.add_field(name=oldembed.fields[2].name, value=oldembed.fields[2].value, inline=True)
        raid_embed.add_field(name=oldembed.fields[3].name, value=oldembed.fields[3].value, inline=True)
        raid_embed.set_footer(text=oldembed.footer.text, icon_url=oldembed.footer.icon_url)
        raid_embed.set_thumbnail(url=raid_img_url)
        for field in oldembed.fields:
            t = _('team')
            s = _('status')
            if (t in field.name.lower()) or (s in field.name.lower()):
                raid_embed.add_field(name=field.name, value=field.value, inline=field.inline)
        if changefrom == "egg":
            raid_message.content = re.sub(_('level\s\d'), _('Level {}').format(newraid), raid_message.content, flags=re.IGNORECASE)
            report_message.content = re.sub(_('level\s\d'), _('Level {}').format(newraid), report_message.content, flags=re.IGNORECASE)
        else:
            raid_message.content = re.sub(_('Meowth!\s.*\sraid\sreported'),_('Meowth! Level {} reported').format(newraid), raid_message.content, flags=re.IGNORECASE)
            report_message.content = re.sub(_('Meowth!\s.*\sraid\sreported'),_('Meowth! Level {}').format(newraid), report_message.content, flags=re.IGNORECASE)
        await raid_message.edit(new_content=raid_message.content, embed=raid_embed, content=raid_message.content)
        try:
            await report_message.edit(new_content=report_message.content, embed=raid_embed, content=report_message.content)
        except (discord.errors.NotFound, AttributeError):
            pass
        await channel.edit(name=raid_channel_name, topic=channel.topic)
    elif newraid and not newraid.isdigit():
        # What a hack, subtract raidtime from exp time because _eggtoraid will add it back
        egglevel = guild_dict[guild.id]['raidchannel_dict'][channel.id]['egglevel']
        if egglevel == "0":
            egglevel = get_level(newraid)
        guild_dict[guild.id]['raidchannel_dict'][channel.id]['exp'] -= 60 * raid_info['raid_eggs'][egglevel]['raidtime']

        await _eggtoraid(newraid, channel, author=message.author)

@Meowth.command()
@commands.has_permissions(manage_channels=True)
@checks.raidchannel()
async def clearstatus(ctx):
    """Efface les listes d'état des raids de raid.

     Utilisation:!clearstatus
     Seulement utilisable par les administrateurs."""
    msg = _("Are you sure you want to clear all status for this raid? Everybody will have to RSVP again. If you are wanting to clear one user's status, use `!setstatus <user> cancel`")
    question = await ctx.channel.send(msg)
    try:
        timeout = False
        res, reactuser = await ask(question, ctx.message.channel, ctx.message.author.id)
    except TypeError:
        timeout = True
    await question.delete()
    if timeout or res.emoji == '❎':
        return
    elif res.emoji == '✅':
        pass
    else:
        return
    try:
        guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['trainer_dict'] = {}
        await ctx.channel.send(_('Meowth! Raid status lists have been cleared!'))
    except KeyError:
        pass

@Meowth.command()
@commands.has_permissions(manage_channels=True)
@checks.raidchannel()
async def setstatus(ctx, member: discord.Member, status,*, status_counts: str = ''):
    """Modifie les listes d'état des canaux de raid.

     Utilisation:!setstatus <utilisateur> <statut> [nombre]
     L'utilisateur peut être une mention ou un numéro d'identification. Le statut peut être interested/i, coming/c, here/h, or cancel/x
     Seulement utilisable par les administrateurs."""
    valid_status_list = ['interested', 'i', 'maybe', 'coming', 'c', 'here', 'h', 'cancel','x']
    if status not in valid_status_list:
        await ctx.message.channel.send(_("Meowth! {status} is not a valid status!").format(status=status))
        return
    ctx.message.author = member
    ctx.message.content = "{}{} {}".format(ctx.prefix, status, status_counts)
    await ctx.bot.process_commands(ctx.message)

@Meowth.command()
@commands.has_permissions(manage_guild=True)
async def cleanroles(ctx):
    """Supprime tous les rôles pokemon de 0 membre.

     Utilisation:!cleanroles"""
    cleancount = 0
    for role in copy.copy(ctx.guild.roles):
        if role.members == [] and role.name in pkmn_info['pokemon_list']:
            server_role = discord.utils.get(ctx.guild.roles, name=role.name)
            await server_role.delete()
            cleancount += 1
    await ctx.message.channel.send(_("Removed {cleancount} empty roles").format(cleancount=cleancount))

@Meowth.command()
@checks.allowarchive()
async def archive(ctx):
    """Marque un canal de raid pour l'archivage.

     Utilisation:!archive"""
    message = ctx.message
    channel = message.channel
    await ctx.message.delete()
    await _archive(channel)

async def _archive(channel):
    guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['archive'] = True
    await asyncio.sleep(10)
    guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['archive'] = True

"""
Miscellaneous
"""

@Meowth.command(name='uptime')
async def cmd_uptime(ctx):
    "Affiche le temps de fonctionnement de Meowth"
    guild = ctx.guild
    channel = ctx.channel
    embed_colour = guild.me.colour or discord.Colour.lighter_grey()
    uptime_str = await _uptime(Meowth)
    embed = discord.Embed(colour=embed_colour, icon_url=Meowth.user.avatar_url)
    embed.add_field(name=_('Uptime'), value=uptime_str)
    try:
        await channel.send(embed=embed)
    except discord.HTTPException:
        await channel.send(_('I need the `Embed links` permission to send this'))

async def _uptime(bot):
    'Shows info about Meowth'
    time_start = bot.uptime
    time_now = datetime.datetime.now()
    ut = relativedelta(time_now, time_start)
    (ut.years, ut.months, ut.days, ut.hours, ut.minutes)
    if ut.years >= 1:
        uptime = _('{yr}y {mth}m {day}d {hr}:{min}').format(yr=ut.years, mth=ut.months, day=ut.days, hr=ut.hours, min=ut.minutes)
    elif ut.months >= 1:
        uptime = _('{mth}m {day}d {hr}:{min}').format(mth=ut.months, day=ut.days, hr=ut.hours, min=ut.minutes)
    elif ut.days >= 1:
        uptime = _('{day} days {hr} hrs {min} mins').format(day=ut.days, hr=ut.hours, min=ut.minutes)
    elif ut.hours >= 1:
        uptime = _('{hr} hrs {min} mins {sec} secs').format(hr=ut.hours, min=ut.minutes, sec=ut.seconds)
    else:
        uptime = _('{min} mins {sec} secs').format(min=ut.minutes, sec=ut.seconds)
    return uptime

@Meowth.command()
async def about(ctx):
    'Affiche des infos sur Meowth'
    author_repo = 'https://github.com/FoglyOgly'
    author_name = 'FoglyOgly'
    bot_repo = author_repo + '/Meowth'
    guild_url = 'https://discord.gg/hhVjAN8'
    owner = Meowth.owner
    channel = ctx.channel
    uptime_str = await _uptime(Meowth)
    yourserver = ctx.message.guild.name
    yourmembers = len(ctx.message.guild.members)
    embed_colour = ctx.guild.me.colour or discord.Colour.lighter_grey()
    about = _("I'm Meowth! A Pokemon Go helper bot for Discord!\n\nI'm made by [{author_name}]({author_repo}) and improvements have been contributed by many other people also.\n\n[Join our server]({server_invite}) if you have any questions or feedback.\n\n").format(author_name=author_name, author_repo=author_repo, server_invite=guild_url)
    member_count = 0
    guild_count = 0
    for guild in Meowth.guilds:
        guild_count += 1
        member_count += len(guild.members)
    embed = discord.Embed(colour=embed_colour, icon_url=Meowth.user.avatar_url)
    embed.add_field(name=_('About Meowth'), value=about, inline=False)
    embed.add_field(name=_('Owner'), value=owner)
    if guild_count > 1:
        embed.add_field(name=_('Servers'), value=guild_count)
        embed.add_field(name=_('Members'), value=member_count)
    embed.add_field(name=_("Your Server"), value=yourserver)
    embed.add_field(name=_("Your Members"), value=yourmembers)
    embed.add_field(name=_('Uptime'), value=uptime_str)
    embed.set_footer(text=_('For support, contact us on our Discord server. Invite Code: hhVjAN8'))
    try:
        await channel.send(embed=embed)
    except discord.HTTPException:
        await channel.send(_('I need the `Embed links` permission to send this'))

@Meowth.command()
@checks.allowteam()
async def team(ctx,*,content):
    """Définissez votre rôle d'équipe.

     Utilisation:!team <nom de l'équipe>
     Les rôles d'équipe doivent être préalablement créés manuellement par l'administrateur du serveur."""
    guild = ctx.guild
    toprole = guild.me.top_role.name
    position = guild.me.top_role.position
    team_msg = _(' or ').join(['**!team {0}**'.format(team) for team in config['team_dict'].keys()])
    high_roles = []
    guild_roles = []
    lowercase_roles = []
    harmony = None
    for role in guild.roles:
        if (role.name.lower() in config['team_dict']) and (role.name not in guild_roles):
            guild_roles.append(role.name)
    lowercase_roles = [element.lower() for element in guild_roles]
    for team in config['team_dict'].keys():
        if team.lower() not in lowercase_roles:
            try:
                temp_role = await guild.create_role(name=team.lower(), hoist=False, mentionable=True)
                guild_roles.append(team.lower())
            except discord.errors.HTTPException:
                await message.channel.send(_('Maximum guild roles reached.'))
                return
            if temp_role.position > position:
                high_roles.append(temp_role.name)
    if high_roles:
        await ctx.channel.send(_('Meowth! My roles are ranked lower than the following team roles: **{higher_roles_list}**\nPlease get an admin to move my roles above them!').format(higher_roles_list=', '.join(high_roles)))
        return
    role = None
    team_split = content.lower().split()
    entered_team = team_split[0]
    entered_team = ''.join([i for i in entered_team if i.isalpha()])
    if entered_team in lowercase_roles:
        index = lowercase_roles.index(entered_team)
        role = discord.utils.get(ctx.guild.roles, name=guild_roles[index])
    if 'harmony' in lowercase_roles:
        index = lowercase_roles.index('harmony')
        harmony = discord.utils.get(ctx.guild.roles, name=guild_roles[index])
    # Check if user already belongs to a team role by
    # getting the role objects of all teams in team_dict and
    # checking if the message author has any of them.    for team in guild_roles:
    for team in guild_roles:
        temp_role = discord.utils.get(ctx.guild.roles, name=team)
        if temp_role:
            # and the user has this role,
            if (temp_role in ctx.author.roles) and (harmony not in ctx.author.roles):
                # then report that a role is already assigned
                await ctx.channel.send(_('Meowth! You already have a team role!'))
                return
            if role and (role.name.lower() == 'harmony') and (harmony in ctx.author.roles):
                # then report that a role is already assigned
                await ctx.channel.send(_('Meowth! You are already in Team Harmony!'))
                return
        # If the role isn't valid, something is misconfigured, so fire a warning.
        else:
            await ctx.channel.send(_('Meowth! {team_role} is not configured as a role on this server. Please contact an admin for assistance.').format(team_role=team))
            return
    # Check if team is one of the three defined in the team_dict
    if entered_team not in config['team_dict'].keys():
        await ctx.channel.send(_('Meowth! "{entered_team}" isn\'t a valid team! Try {available_teams}').format(entered_team=entered_team, available_teams=team_msg))
        return
    # Check if the role is configured on the server
    elif role == None:
        await ctx.channel.send(_('Meowth! The "{entered_team}" role isn\'t configured on this server! Contact an admin!').format(entered_team=entered_team))
    else:
        try:
            if harmony and (harmony in ctx.author.roles):
                await ctx.author.remove_roles(harmony)
            await ctx.author.add_roles(role)
            await ctx.channel.send(_('Meowth! Added {member} to Team {team_name}! {team_emoji}').format(member=ctx.author.mention, team_name=role.name.capitalize(), team_emoji=parse_emoji(ctx.guild, config['team_dict'][entered_team])))
        except discord.Forbidden:
            await ctx.channel.send(_("Meowth! I can't add roles!"))

@Meowth.command(hidden=True)
async def profile(ctx, user: discord.Member = None):
    """Affiche le profil social et de rapport d'un utilisateur.

     Utilisation:!profile [utilisateur]"""
    if not user:
        user = ctx.message.author
    silph = guild_dict[ctx.guild.id]['trainers'].setdefault(user.id,{}).get('silphid',None)
    if silph:
        card = _("Traveler Card")
        silph = f"[{card}](https://sil.ph/{silph.lower()})"
    embed = discord.Embed(title=_("{user}\'s Trainer Profile").format(user=user.display_name), colour=user.colour)
    embed.set_thumbnail(url=user.avatar_url)
    embed.add_field(name=_("Silph Road"), value=f"{silph}", inline=True)
    embed.add_field(name=_("Pokebattler"), value=f"{guild_dict[ctx.guild.id]['trainers'].setdefault(user.id,{}).get('pokebattlerid',None)}", inline=True)
    embed.add_field(name=_("Raid Reports"), value=f"{guild_dict[ctx.guild.id]['trainers'].setdefault(user.id,{}).get('raid_reports',0)}", inline=True)
    embed.add_field(name=_("Egg Reports"), value=f"{guild_dict[ctx.guild.id]['trainers'].setdefault(user.id,{}).get('egg_reports',0)}", inline=True)
    embed.add_field(name=_("EX Raid Reports"), value=f"{guild_dict[ctx.guild.id]['trainers'].setdefault(user.id,{}).get('ex_reports',0)}", inline=True)
    embed.add_field(name=_("Wild Reports"), value=f"{guild_dict[ctx.guild.id]['trainers'].setdefault(user.id,{}).get('wild_reports',0)}", inline=True)
    embed.add_field(name=_("Research Reports"), value=f"{guild_dict[ctx.guild.id]['trainers'].setdefault(user.id,{}).get('research_reports',0)}", inline=True)
    await ctx.send(embed=embed)

@Meowth.command()
async def leaderboard(ctx, type="total"):
    """Affiche les dix premiers annonceurs d'un serveur.

     Utilisation:!leaderboard [type]
     Types acceptés: raids, oeufs, exraids, wilds, recherche"""
    trainers = copy.deepcopy(guild_dict[ctx.guild.id]['trainers'])
    leaderboard = []
    rank = 1
    field_value = ""
    typelist = ["total", "raids", "exraids", "wilds", "research", "eggs"]
    type = type.lower()
    if type not in typelist:
        await ctx.send(_("Leaderboard type not supported. Please select from: **total, raids, eggs, exraids, wilds, research**"))
        return
    for trainer in trainers.keys():
        user = ctx.guild.get_member(trainer)
        raids = trainers[trainer].setdefault('raid_reports', 0)
        wilds = trainers[trainer].setdefault('wild_reports', 0)
        exraids = trainers[trainer].setdefault('ex_reports', 0)
        eggs = trainers[trainer].setdefault('egg_reports', 0)
        research = trainers[trainer].setdefault('research_reports', 0)
        total_reports = raids + wilds + exraids + eggs + research
        trainer_stats = {'trainer':trainer, 'total':total_reports, 'raids':raids, 'wilds':wilds, 'research':research, 'exraids':exraids, 'eggs':eggs}
        if trainer_stats[type] > 0 and user:
            leaderboard.append(trainer_stats)
    leaderboard = sorted(leaderboard,key= lambda x: x[type], reverse=True)[:10]
    embed = discord.Embed(colour=ctx.guild.me.colour)
    embed.set_author(name=_("Reporting Leaderboard ({type})").format(type=type.title()), icon_url=Meowth.user.avatar_url)
    for trainer in leaderboard:
        user = ctx.guild.get_member(trainer['trainer'])
        if user:
            if guild_dict[ctx.guild.id]['configure_dict']['raid']['enabled']:
                field_value += _("Raids: **{raids}** | Eggs: **{eggs}** | ").format(raids=trainer['raids'], eggs=trainer['eggs'])
            if guild_dict[ctx.guild.id]['configure_dict']['exraid']['enabled']:
                field_value += _("EX Raids: **{exraids}** | ").format(exraids=trainer['exraids'])
            if guild_dict[ctx.guild.id]['configure_dict']['wild']['enabled']:
                field_value += _("Wilds: **{wilds}** | ").format(wilds=trainer['wilds'])
            if guild_dict[ctx.guild.id]['configure_dict']['research']['enabled']:
                field_value += _("Research: **{research}** | ").format(research=trainer['research'])
            embed.add_field(name=f"{rank}. {user.display_name} - {type.title()}: **{trainer[type]}**", value=field_value[:-3], inline=False)
            field_value = ""
            rank += 1
    if len(embed.fields) == 0:
        embed.add_field(name=_("No Reports"), value=_("Nobody has made a report or this report type is disabled."))
    await ctx.send(embed=embed)

"""
'configure_dict':{
            'welcome': {'enabled':False,'welcomechan':'','welcomemsg':''},
            'want': {'enabled':False, 'report_channels': []},
            'raid': {'enabled':False, 'report_channels': {}, 'categories':'same','category_dict':{}},
            'exraid': {'enabled':False, 'report_channels': {}, 'categories':'same','category_dict':{}, 'permissions':'everyone'},
            'counters': {'enabled':False, 'auto_levels': []},
            'wild': {'enabled':False, 'report_channels': {}},
            'research': {'enabled':False, 'report_channels': {}},
            'archive': {'enabled':False, 'category':'same','list':None},
            'invite': {'enabled':False},
            'team':{'enabled':False},
            'settings':{'offset':0,'regional':None,'done':False,'prefix':None,'config_sessions':{}}
        },
        'wildreport_dict:':{},
        'questreport_dict':{},
        'raidchannel_dict':{},
        'trainers':{}
"""
"""
Notifications
"""

@Meowth.command()
@checks.allowwant()
async def want(ctx,*,pokemon):
    """Ajouter un Pokémon à votre liste de recherche.

     Utilisation:!want <espèces>
     Miaouss vous mentionnera si quelqu'un rapporte avoir vu
     cette espèce dans leur commande!wild ou!raid."""

    """Dans les coulisses, Meowth suit l'utilisateur!
     créer un rôle de serveur pour l'espèce Pokemon, et
     l'assigner à l'utilisateur."""
    message = ctx.message
    guild = message.guild
    channel = message.channel
    want_split = pokemon.lower().split()
    want_list = []
    added_count = 0
    spellcheck_dict = {

    }
    spellcheck_list = []
    already_want_count = 0
    already_want_list = []
    added_list = []
    role_list = []
    if ',' in ''.join(want_split):
        for pkmn in ''.join(want_split).split(','):
            if pkmn.isdigit():
                pkmn = get_name(pkmn).lower()
            want_list.append(pkmn)
    elif len(want_split) > 1:
        pkmn = ''.join(want_split)
        want_list.append(pkmn)
    else:
        want_list.append(want_split[0])
    for want in want_list:
        entered_want = want
        entered_want = get_name(entered_want).lower() if entered_want.isdigit() else entered_want
        rgx = '[^a-zA-Z0-9]'
        pkmn_match = next((p for p in pkmn_info['pokemon_list'] if re.sub(rgx, '', p) == re.sub(rgx, '', entered_want)), None)
        if pkmn_match:
            entered_want = pkmn_match
        elif len(want_list) == 1 and entered_want == "list":
            msg = _("Meowth! Did you mean **!list wants**?").format(word=entered_want.title())
            question = await message.channel.send(msg)
            return
        else:
            entered_want = spellcheck(entered_want)
            pkmn_match = next((p for p in pkmn_info['pokemon_list'] if re.sub(rgx, "", p) == re.sub(rgx, "", entered_want)), None)
            if not pkmn_match:
                if len(want_list) == 1:
                    msg = _("Meowth! **{word}** isn't a Pokemon!").format(word=entered_want.title())
                    question = await message.channel.send(msg)
                    return
                else:
                    spellcheck_list.append(entered_want)
                    spellcheck_dict[entered_want] = spellcheck(entered_want) if spellcheck(entered_want) != entered_want else None
                    continue
        role = discord.utils.get(guild.roles, name=entered_want)
        # Create role if it doesn't exist yet
        if role == None:
            try:
                role = await guild.create_role(name = entered_want.lower(), hoist = False, mentionable = True)
            except discord.errors.HTTPException:
                await message.channel.send(_('Maximum guild roles reached. Pokemon not added.'))
                return
            await asyncio.sleep(0.5)

        # If user is already wanting the Pokemon,
        # print a less noisy message
        if role in ctx.author.roles:
            already_want_list.append(entered_want.capitalize())
            already_want_count += 1
        else:
            role_list.append(role)
            added_list.append(entered_want.capitalize())
            added_count += 1
    await ctx.author.add_roles(*role_list)
    if (len(want_list) == 1) and ((len(added_list) == 1) or (len(spellcheck_dict) == 1) or (len(already_want_list) == 1)):
        if len(added_list) == 1:
            #If you want Images
            want_number = pkmn_info['pokemon_list'].index(added_list[0].lower()) + 1
            want_img_url = 'https://raw.githubusercontent.com/FoglyOgly/Meowth/discordpy-v1/images/pkmn/{0}_.png?cache=1'.format(str(want_number).zfill(3))
            want_embed = discord.Embed(colour=guild.me.colour)
            want_embed.set_thumbnail(url=want_img_url)
            await channel.send(content=_('Meowth! Got it! {member} wants {pokemon}').format(member=ctx.author.mention, pokemon=added_list[0].capitalize()), embed=want_embed)
            return
            #If you want reaction
            #await ctx.message.add_reaction('☑')
        elif len(already_want_list) == 1:
            await channel.send(content=_('Meowth! {member}, I already know you want {pokemon}!').format(member=ctx.author.mention, pokemon=already_want_list[0].capitalize()))
            return
    else:
        confirmation_msg = _('Meowth! {member}, out of your total {count} items:').format(member=ctx.author.mention, count=(added_count + already_want_count) + len(spellcheck_dict))
        if added_count > 0:
            confirmation_msg += _('\n**{added_count} Added:** \n\t{added_list}').format(added_count=added_count, added_list=', '.join(added_list))
        if already_want_count > 0:
            confirmation_msg += _('\n**{already_want_count} Already Following:** \n\t{already_want_list}').format(already_want_count=already_want_count, already_want_list=', '.join(already_want_list))
        if spellcheck_dict:
            spellcheckmsg = ''
            for word in spellcheck_dict:
                spellcheckmsg += _('\n\t{word}').format(word=word)
                if spellcheck_dict[word]:
                    spellcheckmsg += _(': *({correction}?)*').format(correction=spellcheck_dict[word])
            confirmation_msg += _('\n**{count} Not Valid:**').format(count=len(spellcheck_dict)) + spellcheckmsg
        await channel.send(content=confirmation_msg)

@Meowth.group(case_insensitive=True, invoke_without_command=True)
@checks.allowwant()
async def unwant(ctx,*,pokemon):
    """Retirer un Pokemon de votre liste de recherche.

     Utilisation:!unwant <espèces>
     Vous ne serez plus informé des rapports sur ce Pokémon."""

    """Dans les coulisses, Meowth retire l'utilisateur de
     le rôle de serveur pour les espèces Pokémon."""
    message = ctx.message
    guild = message.guild
    channel = message.channel
    if ctx.invoked_subcommand == None:
        unwant_split = pokemon.lower().split()
        unwant_list = []
        if ',' in ''.join(unwant_split):
            for pkmn in ''.join(unwant_split).split(','):
                if pkmn.isdigit():
                    pkmn = get_name(pkmn).lower()
                unwant_list.append(pkmn)
        else:
            unwant_list.append(unwant_split[0])
        for unwant in unwant_list:
            entered_unwant = unwant
            entered_unwant = get_name(entered_unwant).lower() if entered_unwant.isdigit() else entered_unwant
            rgx = '[^a-zA-Z0-9]'
            pkmn_match = next((p for p in pkmn_info['pokemon_list'] if re.sub(rgx, '', p) == re.sub(rgx, '', entered_unwant)), None)
            if pkmn_match:
                entered_unwant = pkmn_match
            else:
                entered_unwant = await autocorrect(entered_unwant, message.channel, message.author)
            if not entered_unwant:
                return
            # If user is not already wanting the Pokemon,
            # print a less noisy message
            role = discord.utils.get(guild.roles, name=entered_unwant)
            if role not in message.author.roles:
                await message.add_reaction('☑')
            else:
                await message.author.remove_roles(role)
                unwant_number = pkmn_info['pokemon_list'].index(entered_unwant) + 1
                await message.add_reaction('☑')

@unwant.command(name='all')
@checks.allowwant()
async def unwant_all(ctx):
    """Retirez tous les Pokemon de votre liste de recherche.

     Utilisation:!unwant all
     Tous les rôles Pokemon sont supprimés."""

    """Dans les coulisses, Meowth supprime l'utilisateur du
    rôle de serveur pour les espèces Pokémon."""
    message = ctx.message
    guild = message.guild
    channel = message.channel
    author = message.author
    await channel.trigger_typing()
    count = 0
    roles = author.roles
    remove_roles = []
    for role in roles:
        if role.name in pkmn_info['pokemon_list']:
            remove_roles.append(role)
            count += 1
        continue
    await author.remove_roles(*remove_roles)
    if count == 0:
        await channel.send(content=_('{0}, you have no pokemon in your want list.').format(author.mention, count))
        return
    await channel.send(content=_("{0}, I've removed {1} pokemon from your want list.").format(author.mention, count))
    return

"""
Reporting
"""

@Meowth.command(aliases=['w'])
@checks.allowwildreport()
async def wild(ctx,pokemon,*,location):
    """Signalez un emplacement de spawn Pokemon sauvage.

     Utilisation:!wild <species> <location>
     Miaoussier va insérer les détails (vraiment juste tout après le nom de l'espèce) dans un
     Lien Google Maps et publiez le lien vers le même canal que le rapport a été créé."""
    content = f"{pokemon} {location}"
    await _wild(ctx.message, content)

async def _wild(message, content):
    timestamp = (message.created_at + datetime.timedelta(hours=guild_dict[message.channel.guild.id]['configure_dict']['settings']['offset'])).strftime(_('%I:%M %p (%H:%M)'))
    wild_split = content.split()
    if len(wild_split) <= 1:
        await message.channel.send(_('Meowth! Give more details when reporting! Usage: **!wild <pokemon name> <location>**'))
        return
    rgx = '[^a-zA-Z0-9]'
    content = ' '.join(wild_split)
    entered_wild = content.split(' ', 1)[0]
    entered_wild = get_name(entered_wild).lower() if entered_wild.isdigit() else entered_wild.lower()
    wild_details = content.split(' ', 1)[1]
    pkmn_match = next((p for p in pkmn_info['pokemon_list'] if re.sub(rgx, '', p) == re.sub(rgx, '', entered_wild)), None)
    if (not pkmn_match):
        entered_wild2 = ' '.join([content.split(' ', 2)[0], content.split(' ', 2)[1]]).lower()
        pkmn_match = next((p for p in pkmn_info['pokemon_list'] if re.sub(rgx, '', p) == re.sub(rgx, '', entered_wild2)), None)
        if pkmn_match:
            entered_wild = entered_wild2
            try:
                wild_details = content.split(' ', 2)[2]
            except IndexError:
                await message.channel.send(_('Meowth! Give more details when reporting! Usage: **!wild <pokemon name> <location>**'))
                return
    if pkmn_match:
        entered_wild = pkmn_match
    else:
        entered_wild = await autocorrect(entered_wild, message.channel, message.author)
    if not entered_wild:
        return
    wild = discord.utils.get(message.guild.roles, name=entered_wild)
    if wild is None:
        roletest = ""
    else:
        roletest = _("{pokemon} - ").format(pokemon=wild.mention)
    wild_number = pkmn_info['pokemon_list'].index(entered_wild) + 1
    wild_img_url = 'https://raw.githubusercontent.com/FoglyOgly/Meowth/discordpy-v1/images/pkmn/{0}_.png?cache=0'.format(str(wild_number).zfill(3))
    expiremsg = _('**This {pokemon} has despawned!**').format(pokemon=entered_wild.title())
    wild_gmaps_link = create_gmaps_query(wild_details, message.channel, type="wild")
    wild_embed = discord.Embed(title=_('Meowth! Click here for my directions to the wild {pokemon}!').format(pokemon=entered_wild.title()), description=_("Ask {author} if my directions aren't perfect!").format(author=message.author.name), url=wild_gmaps_link, colour=message.guild.me.colour)
    wild_embed.add_field(name=_('**Details:**'), value=_('{pokemon} ({pokemonnumber}) {type}').format(pokemon=entered_wild.capitalize(), pokemonnumber=str(wild_number), type=''.join(get_type(message.guild, wild_number))), inline=False)
    wild_embed.set_thumbnail(url=wild_img_url)
    wild_embed.add_field(name=_('**Reactions:**'), value=_("{emoji}: I'm on my way!").format(emoji="🏎"))
    wild_embed.add_field(name='\u200b', value=_("{emoji}: The Pokemon despawned!").format(emoji="💨"))
    wild_embed.set_footer(text=_('Reported by @{author} - {timestamp}').format(author=message.author.display_name, timestamp=timestamp), icon_url=message.author.avatar_url_as(format=None, static_format='jpg', size=32))
    wildreportmsg = await message.channel.send(content=_('{roletest}Meowth! Wild {pokemon} reported by {member}! Details: {location_details}').format(roletest=roletest,pokemon=entered_wild.title(), member=message.author.mention, location_details=wild_details), embed=wild_embed)
    await asyncio.sleep(0.25)
    await wildreportmsg.add_reaction('🏎')
    await asyncio.sleep(0.25)
    await wildreportmsg.add_reaction('💨')
    await asyncio.sleep(0.25)
    wild_dict = copy.deepcopy(guild_dict[message.guild.id].get('wildreport_dict',{}))
    wild_dict[wildreportmsg.id] = {
        'exp':time.time() + 3600,
        'expedit': {"content":wildreportmsg.content,"embedcontent":expiremsg},
        'reportmessage':message.id,
        'reportchannel':message.channel.id,
        'reportauthor':message.author.id,
        'location':wild_details,
        'url':wild_gmaps_link,
        'pokemon':entered_wild,
        'omw': []
    }
    guild_dict[message.guild.id]['wildreport_dict'] = wild_dict
    wild_reports = guild_dict[message.guild.id].setdefault('trainers',{}).setdefault(message.author.id,{}).setdefault('wild_reports',0) + 1
    guild_dict[message.guild.id]['trainers'][message.author.id]['wild_reports'] = wild_reports

@Meowth.command(aliases=['r', 're', 'egg', 'regg', 'raidegg'])
@checks.allowraidreport()
async def raid(ctx,pokemon,*,location:commands.clean_content(fix_channel_mentions=True)="", weather=None, timer=None):
    """Signaler un raid en cours ou un œuf de raid.

     Utilisation:!raid <espèce / niveau> <lieu> [météo] [minutes]
     Meowth va insérer <location> dans un
     Lien Google Maps et publiez le lien vers le même canal que le rapport a été créé.
     Le message de Miaouss inclura également les faiblesses de type du boss.

     Enfin, Meowth va créer un canal séparé pour le rapport de raid, dans le but d'organiser le raid."""
    content = f"{pokemon} {location}"
    if pokemon.isdigit():
        new_channel = await _raidegg(ctx.message, content)
    else:
        new_channel = await _raid(ctx.message, content)
    ctx.raid_channel = new_channel

async def _raid(message, content):
    fromegg = False
    if guild_dict[message.channel.guild.id]['raidchannel_dict'].get(message.channel.id,{}).get('type') == "egg":
        fromegg = True
    timestamp = (message.created_at + datetime.timedelta(hours=guild_dict[message.channel.guild.id]['configure_dict']['settings']['offset'])).strftime(_('%I:%M %p (%H:%M)'))
    raid_split = content.split()
    if len(raid_split) == 0:
        await message.channel.send(_('Meowth! Give more details when reporting! Usage: **!raid <pokemon name> <location>**'))
        return
    if raid_split[0] == 'egg':
        await _raidegg(message, content)
        return
    if fromegg == True:
        eggdetails = guild_dict[message.guild.id]['raidchannel_dict'][message.channel.id]
        egglevel = eggdetails['egglevel']
        if raid_split[0].lower() == 'assume':
            if config['allow_assume'][egglevel] == 'False':
                await message.channel.send(_('Meowth! **!raid assume** is not allowed in this level egg.'))
                return
            if guild_dict[message.channel.guild.id]['raidchannel_dict'][message.channel.id]['active'] == False:
                await _eggtoraid(raid_split[1].lower(), message.channel, message.author)
                return
            else:
                await _eggassume(" ".join(raid_split), message.channel, message.author)
                return
        elif guild_dict[message.channel.guild.id]['raidchannel_dict'][message.channel.id]['active'] == False:
            await _eggtoraid(" ".join(raid_split).lower(), message.channel, message.author)
            return
        else:
            await message.channel.send(_('Meowth! Please wait until the egg has hatched before changing it to an open raid!'))
            return
    entered_raid = re.sub('[\\@]', '', raid_split[0].lower())
    entered_raid = get_name(entered_raid).lower() if entered_raid.isdigit() else entered_raid.lower()
    del raid_split[0]
    if len(raid_split) == 0:
        await message.channel.send(_('Meowth! Give more details when reporting! Usage: **!raid <pokemon name> <location>**'))
        return
    if raid_split[(- 1)].isdigit():
        raidexp = int(raid_split[(- 1)])
        del raid_split[(- 1)]
    elif ':' in raid_split[(- 1)]:
        raid_split[(- 1)] = re.sub('[a-zA-Z]', '', raid_split[(- 1)])
        if raid_split[(- 1)].split(':')[0] == '':
            endhours = 0
        else:
            endhours = int(raid_split[(- 1)].split(':')[0])
        if raid_split[(- 1)].split(':')[1] == '':
            endmins = 0
        else:
            endmins = int(raid_split[(- 1)].split(':')[1])
        raidexp = (60 * endhours) + endmins
        del raid_split[(- 1)]
    else:
        raidexp = False
    rgx = '[^a-zA-Z0-9]'
    pkmn_match = next((p for p in pkmn_info['pokemon_list'] if re.sub(rgx, '', p) == re.sub(rgx, '', entered_raid)), None)
    if pkmn_match:
        entered_raid = pkmn_match
    else:
        entered_raid = await autocorrect(entered_raid, message.channel, message.author)
    if not entered_raid:
        return
    raid_match = True if entered_raid in get_raidlist() else False
    if (not raid_match):
        await message.channel.send(_('Meowth! The Pokemon {pokemon} does not appear in raids!').format(pokemon=entered_raid.capitalize()))
        return
    elif get_level(entered_raid) == "EX":
        await message.channel.send(_("Meowth! The Pokemon {pokemon} only appears in EX Raids! Use **!exraid** to report one!").format(pokemon=entered_raid.capitalize()))
        return
    if raidexp is not False:
        if _timercheck(raidexp, raid_info['raid_eggs'][get_level(entered_raid)]['raidtime']):
            await message.channel.send(_("Meowth...that's too long. Level {raidlevel} raids currently last no more than {raidtime} minutes...").format(raidlevel=get_level(entered_raid), raidtime=raid_info['raid_eggs'][get_level(entered_raid)]['raidtime']))
            return
    raid_details = ' '.join(raid_split)
    raid_details = raid_details.strip()
    if raid_details == '':
        await message.channel.send(_('Meowth! Give more details when reporting! Usage: **!raid <pokemon name> <location>**'))
        return
    weather_list = [_('none'), _('extreme'), _('clear'), _('sunny'), _('rainy'),
                    _('partlycloudy'), _('cloudy'), _('windy'), _('snow'), _('fog')]
    weather = next((w for w in weather_list if re.sub(rgx, '', w) in re.sub(rgx, '', raid_details.lower())), None)
    if not weather:
        weather = guild_dict[message.guild.id]['raidchannel_dict'].get(message.channel.id,{}).get('weather', None)
    raid_details = raid_details.replace(str(weather), '', 1)
    if raid_details == '':
        await message.channel.send(_('Meowth! Give more details when reporting! Usage: **!raid <pokemon name> <location>**'))
        return
    gyms = get_gyms(message.guild.id)
    if gyms:
        match = await gym_match_prompt(message.channel, message.author.id, raid_details, gyms)
        if not match:
            return await message.channel.send(_("Meowth! I couldn't find a gym named '{0}'.").format(raid_details))
        gym = gyms[match]
        raid_details = match
        gym_coords = gym['coordinates']
        gym_note = gym.get('notes', _('No notes for this gym.'))
        raid_gmaps_link = create_gmaps_query(gym_coords, message.channel, type="raid")
    else:
        raid_gmaps_link = create_gmaps_query(raid_details, message.channel, type="raid")
    raid_channel_name = (entered_raid + '-') + sanitize_channel_name(raid_details)
    raid_channel_category = get_category(message.channel, get_level(entered_raid), category_type="raid")
    raid_channel = await message.guild.create_text_channel(raid_channel_name, overwrites=dict(message.channel.overwrites), category=raid_channel_category)
    ow = raid_channel.overwrites_for(raid_channel.guild.default_role)
    ow.send_messages = True
    try:
        await raid_channel.set_permissions(raid_channel.guild.default_role, overwrite = ow)
    except (discord.errors.Forbidden, discord.errors.HTTPException, discord.errors.InvalidArgument):
        pass
    raid = discord.utils.get(message.guild.roles, name=entered_raid)
    if raid == None:
        roletest = ""
    else:
        roletest = _("{pokemon} - ").format(pokemon=raid.mention)
    raid_number = pkmn_info['pokemon_list'].index(entered_raid) + 1
    raid_img_url = 'https://raw.githubusercontent.com/FoglyOgly/Meowth/discordpy-v1/images/pkmn/{0}_.png?cache=0'.format(str(raid_number).zfill(3))
    raid_embed = discord.Embed(title=_('Meowth! Click here for directions to the raid!'), url=raid_gmaps_link, colour=message.guild.me.colour)
    if gyms:
        gym_info = _("**Name:** {0}\n**Notes:** {1}").format(raid_details, gym_note)
        raid_embed.add_field(name=_('**Gym:**'), value=gym_info, inline=False)
    raid_embed.add_field(name=_('**Details:**'), value=_('{pokemon} ({pokemonnumber}) {type}').format(pokemon=entered_raid.capitalize(), pokemonnumber=str(raid_number), type=''.join(get_type(message.guild, raid_number)), inline=True))
    raid_embed.add_field(name=_('**Weaknesses:**'), value=_('{weakness_list}').format(weakness_list=weakness_to_str(message.guild, get_weaknesses(entered_raid))), inline=True)
    raid_embed.add_field(name=_('**Next Group:**'), value=_('Set with **!starttime**'), inline=True)
    raid_embed.add_field(name=_('**Expires:**'), value=_('Set with **!timerset**'), inline=True)
    raid_embed.set_footer(text=_('Reported by @{author} - {timestamp}').format(author=message.author.display_name, timestamp=timestamp), icon_url=message.author.avatar_url_as(format=None, static_format='jpg', size=32))
    raid_embed.set_thumbnail(url=raid_img_url)
    report_embed = raid_embed
    raidreport = await message.channel.send(content=_('Meowth! {pokemon} raid reported by {member}! Details: {location_details}. Coordinate in {raid_channel}').format(pokemon=entered_raid.capitalize(), member=message.author.mention, location_details=raid_details, raid_channel=raid_channel.mention), embed=report_embed)
    await asyncio.sleep(1)
    raidmsg = _("{roletest}Meowth! {pokemon} raid reported by {member} in {citychannel}! Details: {location_details}. Coordinate here!\n\nClick the question mark reaction to get help on the commands that work in here.\n\nThis channel will be deleted five minutes after the timer expires.").format(roletest=roletest, pokemon=entered_raid.title(), member=message.author.mention, citychannel=message.channel.mention, location_details=raid_details)
    raidmessage = await raid_channel.send(content=raidmsg, embed=raid_embed)
    await raidmessage.add_reaction('\u2754')
    await raidmessage.pin()
    level = get_level(entered_raid)
    if str(level) in guild_dict[message.guild.id]['configure_dict']['counters']['auto_levels']:
        try:
            ctrs_dict = await _get_generic_counters(message.guild, entered_raid, weather)
            ctrsmsg = _("Here are the best counters for the raid boss in currently known weather conditions! Update weather with **!weather**. If you know the moveset of the boss, you can react to this message with the matching emoji and I will update the counters.")
            ctrsmessage = await raid_channel.send(content=ctrsmsg,embed=ctrs_dict[0]['embed'])
            ctrsmessage_id = ctrsmessage.id
            await ctrsmessage.pin()
            for moveset in ctrs_dict:
                await ctrsmessage.add_reaction(ctrs_dict[moveset]['emoji'])
                await asyncio.sleep(0.25)
        except:
            ctrs_dict = {}
            ctrsmessage_id = None
    else:
        ctrs_dict = {}
        ctrsmessage_id = None
    guild_dict[message.guild.id]['raidchannel_dict'][raid_channel.id] = {
        'reportcity': message.channel.id,
        'trainer_dict': {},
        'exp': time.time() + (60 * raid_info['raid_eggs'][str(level)]['raidtime']),
        'manual_timer': False,
        'active': True,
        'raidmessage': raidmessage.id,
        'raidreport': raidreport.id,
        'ctrsmessage': ctrsmessage_id,
        'address': raid_details,
        'type': 'raid',
        'pokemon': entered_raid,
        'egglevel': '0',
        'ctrs_dict': ctrs_dict,
        'moveset': 0,
        'weather': weather,
    }
    if raidexp is not False:
        await _timerset(raid_channel, raidexp)
    else:
        await raid_channel.send(content=_('Meowth! Hey {member}, if you can, set the time left on the raid using **!timerset <minutes>** so others can check it with **!timer**.').format(member=message.author.mention))
    event_loop.create_task(expiry_check(raid_channel))
    raid_reports = guild_dict[message.guild.id].setdefault('trainers',{}).setdefault(message.author.id,{}).setdefault('raid_reports',0) + 1
    guild_dict[message.guild.id]['trainers'][message.author.id]['raid_reports'] = raid_reports
    return raid_channel

async def _raidegg(message, content):
    timestamp = (message.created_at + datetime.timedelta(hours=guild_dict[message.channel.guild.id]['configure_dict']['settings']['offset'])).strftime(_('%I:%M %p (%H:%M)'))
    raidexp = False
    hourminute = False
    raidegg_split = content.split()
    if raidegg_split[0].lower() == 'egg':
        del raidegg_split[0]
    if len(raidegg_split) <= 1:
        await message.channel.send(_('Meowth! Give more details when reporting! Usage: **!raidegg <level> <location>**'))
        return
    if raidegg_split[0].isdigit():
        egg_level = int(raidegg_split[0])
        del raidegg_split[0]
    else:
        await message.channel.send(_('Meowth! Give more details when reporting! Use at least: **!raidegg <level> <location>**. Type **!help** raidegg for more info.'))
        return
    if raidegg_split[(- 1)].isdigit():
        raidexp = int(raidegg_split[(- 1)])
        del raidegg_split[(- 1)]
    elif ':' in raidegg_split[(- 1)]:
        msg = _("Did you mean egg hatch time {0} or time remaining before hatch {1}?").format("🥚", "⏲")
        question = await message.channel.send(msg)
        try:
            timeout = False
            res, reactuser = await ask(question, message.channel, message.author.id, react_list=['🥚', '⏲'])
        except TypeError:
            timeout = True
        await question.delete()
        if timeout or res.emoji == '⏲':
            hourminute = True
        elif res.emoji == '🥚':
            now = datetime.datetime.utcnow() + datetime.timedelta(hours=guild_dict[message.channel.guild.id]['configure_dict']['settings']['offset'])
            start = dateparser.parse(raidegg_split[(- 1)], settings={'PREFER_DATES_FROM': 'future'})
            if start.day != now.day:
                if "m" not in raidegg_split[(- 1)]:
                    start = start + datetime.timedelta(hours=12)
                start = start.replace(day=now.day)
            timediff = relativedelta(start, now)
            raidexp = (timediff.hours*60) + timediff.minutes + 1
            if raidexp < 0:
                await message.channel.send(_('Meowth! Please enter a time in the future.'))
                return
            del raidegg_split[(- 1)]
    if hourminute:
        (h, m) = re.sub('[a-zA-Z]', '', raidegg_split[(- 1)]).split(':', maxsplit=1)
        if h == '':
            h = '0'
        if m == '':
            m = '0'
        if h.isdigit() and m.isdigit():
            raidexp = (60 * int(h)) + int(m)
        del raidegg_split[(- 1)]
    if raidexp is not False:
        if _timercheck(raidexp, raid_info['raid_eggs'][str(egg_level)]['hatchtime']):
            await message.channel.send(_("Meowth...that's too long. Level {raidlevel} Raid Eggs currently last no more than {hatchtime} minutes...").format(raidlevel=egg_level, hatchtime=raid_info['raid_eggs'][str(egg_level)]['hatchtime']))
            return
    raid_details = ' '.join(raidegg_split)
    raid_details = raid_details.strip()
    if raid_details == '':
        await message.channel.send(_('Meowth! Give more details when reporting! Use at least: **!raidegg <level> <location>**. Type **!help** raidegg for more info.'))
        return
    rgx = '[^a-zA-Z0-9]'
    weather_list = [_('none'), _('extreme'), _('clear'), _('sunny'), _('rainy'),
                    _('partlycloudy'), _('cloudy'), _('windy'), _('snow'), _('fog')]
    weather = next((w for w in weather_list if re.sub(rgx, '', w) in re.sub(rgx, '', raid_details.lower())), None)
    raid_details = raid_details.replace(str(weather), '', 1)
    if not weather:
        weather = guild_dict[message.guild.id]['raidchannel_dict'].get(message.channel.id,{}).get('weather', None)
    if raid_details == '':
        await message.channel.send(_('Meowth! Give more details when reporting! Usage: **!raid <pokemon name> <location>**'))
        return
    gyms = get_gyms(message.guild.id)
    if gyms:
        match = await gym_match_prompt(message.channel, message.author.id, raid_details, gyms)
        if not match:
            return await message.channel.send(_("Meowth! I couldn't find a gym named '{0}'.").format(raid_details))
        gym = gyms[match]
        raid_details = match
        gym_coords = gym['coordinates']
        gym_note = gym.get('notes', _('No notes for this gym.'))
        raid_gmaps_link = create_gmaps_query(gym_coords, message.channel, type="raid")
    else:
        raid_gmaps_link = create_gmaps_query(raid_details, message.channel, type="raid")
    if (egg_level > 5) or (egg_level == 0):
        await message.channel.send(_('Meowth! Raid egg levels are only from 1-5!'))
        return
    else:
        egg_level = str(egg_level)
        egg_info = raid_info['raid_eggs'][egg_level]
        egg_img = egg_info['egg_img']

        # account for psuedo level 6 boosted raids
        pkmn_list = []
        if egg_level == '5':
            try:
                pkmn_list.extend(raid_info['raid_eggs']['6']['pokemon'])
            except KeyError:
                pass
        pkmn_list.extend(egg_info['pokemon'])

        boss_list = []
        for p in pkmn_list:
            p_name = get_name(p).title()
            p_type = get_type(message.guild, p)
            boss_list.append((((p_name + ' (') + str(p)) + ') ') + ''.join(p_type))
        raid_channel_name = _('level-{egg_level}-egg-').format(egg_level=egg_level)
        raid_channel_name += sanitize_channel_name(raid_details)
        raid_channel_category = get_category(message.channel, egg_level, category_type="raid")
        raid_channel = await message.guild.create_text_channel(raid_channel_name, overwrites=dict(message.channel.overwrites), category=raid_channel_category)
        ow = raid_channel.overwrites_for(raid_channel.guild.default_role)
        ow.send_messages = True
        try:
            await raid_channel.set_permissions(raid_channel.guild.default_role, overwrite = ow)
        except (discord.errors.Forbidden, discord.errors.HTTPException, discord.errors.InvalidArgument):
            pass
        raid_img_url = 'https://raw.githubusercontent.com/FoglyOgly/Meowth/discordpy-v1/images/eggs/{}?cache=0'.format(str(egg_img))
        raid_embed = discord.Embed(title=_('Meowth! Click here for directions to the coming raid!'), url=raid_gmaps_link, colour=message.guild.me.colour)
        if gyms:
            gym_info = _("**Name:** {0}\n**Notes:** {1}").format(raid_details, gym_note)
            raid_embed.add_field(name=_('**Gym:**'), value=gym_info, inline=False)
        if len(pkmn_list) > 1:
            raid_embed.add_field(name=_('**Possible Bosses:**'), value=_('{bosslist1}').format(bosslist1='\n'.join(boss_list[::2])), inline=True)
            raid_embed.add_field(name='\u200b', value=_('{bosslist2}').format(bosslist2='\n'.join(boss_list[1::2])), inline=True)
        else:
            raid_embed.add_field(name=_('**Possible Bosses:**'), value=_('{bosslist}').format(bosslist=''.join(boss_list)), inline=True)
            raid_embed.add_field(name='\u200b', value='\u200b', inline=True)
        raid_embed.add_field(name=_('**Next Group:**'), value=_('Set with **!starttime**'), inline=True)
        raid_embed.add_field(name=_('**Hatches:**'), value=_('Set with **!timerset**'), inline=True)
        raid_embed.set_footer(text=_('Reported by @{author} - {timestamp}').format(author=message.author.display_name, timestamp=timestamp), icon_url=message.author.avatar_url_as(format=None, static_format='jpg', size=32))
        raid_embed.set_thumbnail(url=raid_img_url)
        raidreport = await message.channel.send(content=_('Meowth! Level {level} raid egg reported by {member}! Details: {location_details}. Coordinate in {raid_channel}').format(level=egg_level, member=message.author.mention, location_details=raid_details, raid_channel=raid_channel.mention), embed=raid_embed)
        await asyncio.sleep(1)
        raidmsg = _("Meowth! Level {level} raid egg reported by {member} in {citychannel}! Details: {location_details}. Coordinate here!\n\nClick the question mark reaction to get help on the commands that work in here.\n\nThis channel will be deleted five minutes after the timer expires.").format(level=egg_level, member=message.author.mention, citychannel=message.channel.mention, location_details=raid_details)
        raidmessage = await raid_channel.send(content=raidmsg, embed=raid_embed)
        await raidmessage.add_reaction('\u2754')
        await raidmessage.pin()
        guild_dict[message.guild.id]['raidchannel_dict'][raid_channel.id] = {
            'reportcity': message.channel.id,
            'trainer_dict': {

            },
            'exp': time.time() + (60 * raid_info['raid_eggs'][egg_level]['hatchtime']),
            'manual_timer': False,
            'active': True,
            'raidmessage': raidmessage.id,
            'raidreport': raidreport.id,
            'address': raid_details,
            'type': 'egg',
            'pokemon': '',
            'egglevel': egg_level,
            'weather': weather,
            'moveset': 0,
        }
        if raidexp is not False:
            await _timerset(raid_channel, raidexp)
        else:
            await raid_channel.send(content=_('Meowth! Hey {member}, if you can, set the time left until the egg hatches using **!timerset <minutes>** so others can check it with **!timer**.').format(member=message.author.mention))
        if len(raid_info['raid_eggs'][egg_level]['pokemon']) == 1:
            await _eggassume('assume ' + get_name(raid_info['raid_eggs'][egg_level]['pokemon'][0]), raid_channel)
        elif egg_level == "5" and guild_dict[raid_channel.guild.id]['configure_dict']['settings'].get('regional',None) in raid_info['raid_eggs']["5"]['pokemon']:
            await _eggassume('assume ' + get_name(guild_dict[raid_channel.guild.id]['configure_dict']['settings']['regional']), raid_channel)
        event_loop.create_task(expiry_check(raid_channel))
        egg_reports = guild_dict[message.guild.id].setdefault('trainers',{}).setdefault(message.author.id,{}).setdefault('egg_reports',0) + 1
        guild_dict[message.guild.id]['trainers'][message.author.id]['egg_reports'] = egg_reports
        return raid_channel

async def _eggassume(args, raid_channel, author=None):
    eggdetails = guild_dict[raid_channel.guild.id]['raidchannel_dict'][raid_channel.id]
    report_channel = Meowth.get_channel(eggdetails['reportcity'])
    egglevel = eggdetails['egglevel']
    manual_timer = eggdetails['manual_timer']
    weather = eggdetails.get('weather', None)
    egg_report = await report_channel.get_message(eggdetails['raidreport'])
    raid_message = await raid_channel.get_message(eggdetails['raidmessage'])
    entered_raid = re.sub('[\\@]', '', args.lower().lstrip('assume').lstrip(' '))
    entered_raid = get_name(entered_raid).lower() if entered_raid.isdigit() else entered_raid
    rgx = '[^a-zA-Z0-9]'
    pkmn_match = next((p for p in pkmn_info['pokemon_list'] if re.sub(rgx, '', p) == re.sub(rgx, '', entered_raid)), None)
    if pkmn_match:
        entered_raid = pkmn_match
    else:
        entered_raid = await autocorrect(entered_raid, raid_channel, author)
    if not entered_raid:
        return
    raid_match = True if entered_raid in get_raidlist() else False
    if (not raid_match):
        await raid_channel.send(_('Meowth! The Pokemon {pokemon} does not appear in raids!').format(pokemon=entered_raid.capitalize()))
        return
    elif get_number(entered_raid) not in raid_info['raid_eggs'][egglevel]['pokemon']:
        await raid_channel.send(_('Meowth! The Pokemon {pokemon} does not hatch from level {level} raid eggs!').format(pokemon=entered_raid.capitalize(), level=egglevel))
        return
    guild_dict[raid_channel.guild.id]['raidchannel_dict'][raid_channel.id]['pokemon'] = entered_raid
    oldembed = raid_message.embeds[0]
    raid_gmaps_link = oldembed.url
    raidrole = discord.utils.get(raid_channel.guild.roles, name=entered_raid)
    if raidrole == None:
        roletest = ""
    else:
        roletest = _("{pokemon} - ").format(pokemon=raidrole.mention)
    raid_number = pkmn_info['pokemon_list'].index(entered_raid) + 1
    raid_img_url = 'https://raw.githubusercontent.com/FoglyOgly/Meowth/discordpy-v1/images/pkmn/{0}_.png?cache=0'.format(str(raid_number).zfill(3))
    raid_embed = discord.Embed(title=_('Meowth! Click here for directions to the coming raid!'), url=raid_gmaps_link, colour=raid_channel.guild.me.colour)
    raid_embed.add_field(name=_('**Details:**'), value=_('{pokemon} ({pokemonnumber}) {type}').format(pokemon=entered_raid.capitalize(), pokemonnumber=str(raid_number), type=''.join(get_type(raid_channel.guild, raid_number)), inline=True))
    raid_embed.add_field(name=_('**Weaknesses:**'), value=_('{weakness_list}').format(weakness_list=weakness_to_str(raid_channel.guild, get_weaknesses(entered_raid))), inline=True)
    raid_embed.add_field(name=_('**Next Group:**'), value=oldembed.fields[2].value, inline=True)
    raid_embed.add_field(name=_('**Hatches:**'), value=oldembed.fields[3].value, inline=True)
    for field in oldembed.fields:
        t = _('team')
        s = _('status')
        if (t in field.name.lower()) or (s in field.name.lower()):
            raid_embed.add_field(name=field.name, value=field.value, inline=field.inline)
    raid_embed.set_footer(text=oldembed.footer.text, icon_url=oldembed.footer.icon_url)
    raid_embed.set_thumbnail(url=oldembed.thumbnail.url)
    try:
        await raid_message.edit(new_content=raid_message.content, embed=raid_embed, content=raid_message.content)
        raid_message = raid_message.id
    except discord.errors.NotFound:
        raid_message = None
    try:
        await egg_report.edit(new_content=egg_report.content, embed=raid_embed, content=egg_report.content)
        egg_report = egg_report.id
    except discord.errors.NotFound:
        egg_report = None
    await raid_channel.send(_('{roletest}Meowth! This egg will be assumed to be {pokemon} when it hatches!').format(roletest=roletest,pokemon=entered_raid.title()))
    if str(egglevel) in guild_dict[raid_channel.guild.id]['configure_dict']['counters']['auto_levels']:
        ctrs_dict = await _get_generic_counters(raid_channel.guild, entered_raid, weather)
        ctrsmsg = "Here are the best counters for the raid boss in currently known weather conditions! Update weather with **!weather**. If you know the moveset of the boss, you can react to this message with the matching emoji and I will update the counters."
        ctrsmessage = await raid_channel.send(content=ctrsmsg,embed=ctrs_dict[0]['embed'])
        ctrsmessage_id = ctrsmessage.id
        await ctrsmessage.pin()
        for moveset in ctrs_dict:
            await ctrsmessage.add_reaction(ctrs_dict[moveset]['emoji'])
            await asyncio.sleep(0.25)
    else:
        ctrs_dict = {}
        ctrsmessage_id = eggdetails.get('ctrsmessage', None)
    eggdetails['ctrs_dict'] = ctrs_dict
    eggdetails['ctrsmessage'] = ctrsmessage_id
    guild_dict[raid_channel.guild.id]['raidchannel_dict'][raid_channel.id] = eggdetails
    return

async def _eggtoraid(entered_raid, raid_channel, author=None):
    entered_raid = get_name(entered_raid).lower() if entered_raid.isdigit() else entered_raid.lower()
    rgx = '[^a-zA-Z0-9]'
    pkmn_match = next((p for p in pkmn_info['pokemon_list'] if re.sub(rgx, '', p) == re.sub(rgx, '', entered_raid)), None)
    if pkmn_match:
        entered_raid = pkmn_match
    else:
        entered_raid = await autocorrect(entered_raid, raid_channel, author)
    if not entered_raid:
        return
    eggdetails = guild_dict[raid_channel.guild.id]['raidchannel_dict'][raid_channel.id]
    egglevel = eggdetails['egglevel']
    if egglevel == "0":
        egglevel = get_level(entered_raid)
    try:
        reportcitychannel = Meowth.get_channel(eggdetails['reportcity'])
        reportcity = reportcitychannel.name
    except (discord.errors.NotFound, AttributeError):
        reportcity = None
    manual_timer = eggdetails['manual_timer']
    trainer_dict = eggdetails['trainer_dict']
    egg_address = eggdetails['address']
    weather = eggdetails.get('weather', None)
    raid_message = await raid_channel.get_message(eggdetails['raidmessage'])
    if not reportcitychannel:
        async for message in raid_channel.history(limit=500, reverse=True):
            if message.author.id == guild.me.id:
                c = _('Coordinate here')
                if c in message.content:
                    reportcitychannel = message.raw_channel_mentions[0]
                    break
    if reportcitychannel:
        try:
            egg_report = await reportcitychannel.get_message(eggdetails['raidreport'])
        except (discord.errors.NotFound, discord.errors.HTTPException):
            egg_report = None
    starttime = eggdetails.get('starttime',None)
    duplicate = eggdetails.get('duplicate',0)
    archive = eggdetails.get('archive',False)
    meetup = eggdetails.get('meetup',{})
    if not author:
        try:
            raid_messageauthor = raid_message.mentions[0]
        except IndexError:
            raid_messageauthor = ('<@' + raid_message.raw_mentions[0]) + '>'
            logger.info('Hatching Mention Failed - Trying alternative method: channel: {} (id: {}) - server: {} | Attempted mention: {}...'.format(raid_channel.name, raid_channel.id, raid_channel.guild.name, raid_message.content[:125]))
    else:
        raid_messageauthor = author
    raid_match = True if entered_raid in get_raidlist() else False
    if (not raid_match):
        await raid_channel.send(_('Meowth! The Pokemon {pokemon} does not appear in raids!').format(pokemon=entered_raid.capitalize()))
        return
    elif get_number(entered_raid) not in raid_info['raid_eggs'][str(egglevel)]['pokemon']:
        await raid_channel.send(_('Meowth! The Pokemon {pokemon} does not hatch from level {level} raid eggs!').format(pokemon=entered_raid.capitalize(), level=egglevel))
        return
    if (egglevel.isdigit() and int(egglevel) > 0) or egglevel == 'EX':
        raidexp = eggdetails['exp'] + 60 * raid_info['raid_eggs'][str(egglevel)]['raidtime']
    else:
        raidexp = eggdetails['exp']
    end = datetime.datetime.utcfromtimestamp(raidexp) + datetime.timedelta(hours=guild_dict[raid_channel.guild.id]['configure_dict']['settings']['offset'])
    oldembed = raid_message.embeds[0]
    raid_gmaps_link = oldembed.url
    if guild_dict[raid_channel.guild.id].get('raidchannel_dict',{}).get(raid_channel.id,{}).get('meetup',{}):
        guild_dict[raid_channel.guild.id]['raidchannel_dict'][raid_channel.id]['type'] = 'exraid'
        guild_dict[raid_channel.guild.id]['raidchannel_dict'][raid_channel.id]['egglevel'] = '0'
        await raid_channel.send(_("The event has started!"), embed=oldembed)
        await raid_channel.edit(topic="")
        event_loop.create_task(expiry_check(raid_channel))
        return
    if egglevel.isdigit():
        hatchtype = 'raid'
        raidreportcontent = _('Meowth! The egg has hatched into a {pokemon} raid! Details: {location_details}. Coordinate in {raid_channel}').format(pokemon=entered_raid.capitalize(), location_details=egg_address, raid_channel=raid_channel.mention)
        raidmsg = _("Meowth! The egg reported by {member} in {citychannel} hatched into a {pokemon} raid! Details: {location_details}. Coordinate here!\n\nClick the question mark reaction to get help on the commands that work in here.\n\nThis channel will be deleted five minutes after the timer expires.").format(member=raid_messageauthor.mention, citychannel=reportcitychannel.mention, pokemon=entered_raid.capitalize(), location_details=egg_address)
    elif egglevel == 'EX':
        hatchtype = 'exraid'
        if guild_dict[raid_channel.guild.id]['configure_dict']['invite']['enabled']:
            invitemsgstr = _("Use the **!invite** command to gain access and coordinate")
            invitemsgstr2 = _(" after using **!invite** to gain access")
        else:
            invitemsgstr = _("Coordinate")
            invitemsgstr2 = ""
        raidreportcontent = _('Meowth! The EX egg has hatched into a {pokemon} raid! Details: {location_details}. {invitemsgstr} coordinate in {raid_channel}').format(pokemon=entered_raid.capitalize(), location_details=egg_address, invitemsgstr=invitemsgstr,raid_channel=raid_channel.mention)
        raidmsg = _("Meowth! {pokemon} EX raid reported by {member} in {citychannel}! Details: {location_details}. Coordinate here{invitemsgstr2}!\n\nClick the question mark reaction to get help on the commands that work in here.\n\nThis channel will be deleted five minutes after the timer expires.").format(pokemon=entered_raid.capitalize(), member=raid_messageauthor.mention, citychannel=reportcitychannel.mention, location_details=egg_address, invitemsgstr2=invitemsgstr2)
    raid_channel_name = (entered_raid + '-') + sanitize_channel_name(egg_address)
    raid = discord.utils.get(raid_channel.guild.roles, name=entered_raid)
    if raid == None:
        roletest = ""
    else:
        roletest = _("{pokemon} - ").format(pokemon=raid.mention)
    raid_number = pkmn_info['pokemon_list'].index(entered_raid) + 1
    raid_img_url = 'https://raw.githubusercontent.com/FoglyOgly/Meowth/discordpy-v1/images/pkmn/{0}_.png?cache=0'.format(str(raid_number).zfill(3))
    raid_embed = discord.Embed(title=_('Meowth! Click here for directions to the raid!'), url=raid_gmaps_link, colour=raid_channel.guild.me.colour)
    raid_embed.add_field(name=_('**Details:**'), value=_('{pokemon} ({pokemonnumber}) {type}').format(pokemon=entered_raid.capitalize(), pokemonnumber=str(raid_number), type=''.join(get_type(raid_channel.guild, raid_number)), inline=True))
    raid_embed.add_field(name=_('**Weaknesses:**'), value=_('{weakness_list}').format(weakness_list=weakness_to_str(raid_channel.guild, get_weaknesses(entered_raid))), inline=True)
    raid_embed.add_field(name=oldembed.fields[2].name, value=oldembed.fields[2].value, inline=True)
    if meetup:
        raid_embed.add_field(name=oldembed.fields[3].name, value=end.strftime(_('%B %d at %I:%M %p (%H:%M)')), inline=True)
    else:
        raid_embed.add_field(name=_('**Expires:**'), value=end.strftime(_('%B %d at %I:%M %p (%H:%M)')), inline=True)
    raid_embed.set_footer(text=oldembed.footer.text, icon_url=oldembed.footer.icon_url)
    raid_embed.set_thumbnail(url=raid_img_url)
    await raid_channel.edit(name=raid_channel_name, topic=end.strftime(_('Ends on %B %d at %I:%M %p (%H:%M)')))
    trainer_list = []
    trainer_dict = copy.deepcopy(guild_dict[raid_channel.guild.id]['raidchannel_dict'][raid_channel.id]['trainer_dict'])
    for trainer in trainer_dict.keys():
        try:
            user = raid_channel.guild.get_member(trainer)
        except (discord.errors.NotFound, AttributeError):
            continue
        if (trainer_dict[trainer].get('interest',None)) and (entered_raid not in trainer_dict[trainer]['interest']):
            guild_dict[raid_channel.guild.id]['raidchannel_dict'][raid_channel.id]['trainer_dict'][trainer]['status'] = {'maybe':0, 'coming':0, 'here':0, 'lobby':0}
            guild_dict[raid_channel.guild.id]['raidchannel_dict'][raid_channel.id]['trainer_dict'][trainer]['party'] = {'mystic':0, 'valor':0, 'instinct':0, 'unknown':0}
            guild_dict[raid_channel.guild.id]['raidchannel_dict'][raid_channel.id]['trainer_dict'][trainer]['count'] = 1
        else:
            guild_dict[raid_channel.guild.id]['raidchannel_dict'][raid_channel.id]['trainer_dict'][trainer]['interest'] = []
    await asyncio.sleep(1)
    trainer_dict = copy.deepcopy(guild_dict[raid_channel.guild.id]['raidchannel_dict'][raid_channel.id]['trainer_dict'])
    for trainer in trainer_dict.keys():
        if (trainer_dict[trainer]['status']['maybe']) or (trainer_dict[trainer]['status']['coming']) or (trainer_dict[trainer]['status']['here']):
            try:
                user = raid_channel.guild.get_member(trainer)
                trainer_list.append(user.mention)
            except (discord.errors.NotFound, AttributeError):
                continue
    await raid_channel.send(content=_("{roletest}Meowth! Trainers {trainer_list}: The raid egg has just hatched into a {pokemon} raid!\nIf you couldn't before, you're now able to update your status with **!coming** or **!here**. If you've changed your plans, use **!cancel**.").format(roletest=roletest,trainer_list=', '.join(trainer_list), pokemon=entered_raid.title()), embed=raid_embed)
    for field in oldembed.fields:
        t = _('team')
        s = _('status')
        if (t in field.name.lower()) or (s in field.name.lower()):
            raid_embed.add_field(name=field.name, value=field.value, inline=field.inline)
    try:
        await raid_message.edit(new_content=raidmsg, embed=raid_embed, content=raidmsg)
        raid_message = raid_message.id
    except (discord.errors.NotFound, AttributeError):
        raid_message = None
    try:
        await egg_report.edit(new_content=raidreportcontent, embed=raid_embed, content=raidreportcontent)
        egg_report = egg_report.id
    except (discord.errors.NotFound, AttributeError):
        egg_report = None
    if str(egglevel) in guild_dict[raid_channel.guild.id]['configure_dict']['counters']['auto_levels'] and not eggdetails.get('pokemon', None):
        ctrs_dict = await _get_generic_counters(raid_channel.guild, entered_raid, weather)
        ctrsmsg = "Here are the best counters for the raid boss in currently known weather conditions! Update weather with **!weather**. If you know the moveset of the boss, you can react to this message with the matching emoji and I will update the counters."
        ctrsmessage = await raid_channel.send(content=ctrsmsg,embed=ctrs_dict[0]['embed'])
        ctrsmessage_id = ctrsmessage.id
        await ctrsmessage.pin()
        for moveset in ctrs_dict:
            await ctrsmessage.add_reaction(ctrs_dict[moveset]['emoji'])
            await asyncio.sleep(0.25)
    else:
        ctrs_dict = eggdetails.get('ctrs_dict',{})
        ctrsmessage_id = eggdetails.get('ctrsmessage', None)
    guild_dict[raid_channel.guild.id]['raidchannel_dict'][raid_channel.id] = {
        'reportcity': reportcitychannel.id,
        'trainer_dict': trainer_dict,
        'exp': raidexp,
        'manual_timer': manual_timer,
        'active': True,
        'raidmessage': raid_message,
        'raidreport': egg_report,
        'address': egg_address,
        'type': hatchtype,
        'pokemon': entered_raid,
        'egglevel': '0',
        'ctrs_dict': ctrs_dict,
        'ctrsmessage': ctrsmessage_id,
        'moveset': 0,
    }
    guild_dict[raid_channel.guild.id]['raidchannel_dict'][raid_channel.id]['starttime'] = starttime
    guild_dict[raid_channel.guild.id]['raidchannel_dict'][raid_channel.id]['duplicate'] = duplicate
    guild_dict[raid_channel.guild.id]['raidchannel_dict'][raid_channel.id]['archive'] = archive
    if author:
        raid_reports = guild_dict[raid_channel.guild.id].setdefault('trainers',{}).setdefault(author.id,{}).setdefault('raid_reports',0) + 1
        guild_dict[raid_channel.guild.id]['trainers'][author.id]['raid_reports'] = raid_reports
        await _edit_party(raid_channel, author)
    event_loop.create_task(expiry_check(raid_channel))

@Meowth.command(aliases=['ex'])
@checks.allowexraidreport()
async def exraid(ctx, *,location:commands.clean_content(fix_channel_mentions=True)=""):
    """Signaler un raid EX à venir.

     Utilisation:!exraid <emplacement>
     Miaoussier va insérer les détails (vraiment juste tout après le nom de l'espèce) dans un
     Lien Google Maps et publiez le lien vers le même canal que le rapport a été créé.
     Le message de Miaouss inclura également les faiblesses de type du boss.

     Enfin, Meowth va créer un canal séparé pour le rapport de raid, dans le but d'organiser le raid."""
    await _exraid(ctx, location)

async def _exraid(ctx, location):
    message = ctx.message
    channel = message.channel
    timestamp = (message.created_at + datetime.timedelta(hours=guild_dict[message.channel.guild.id]['configure_dict']['settings']['offset'])).strftime(_('%I:%M %p (%H:%M)'))
    fromegg = False
    exraid_split = location.split()
    if len(exraid_split) <= 0:
        await channel.send(_('Meowth! Give more details when reporting! Usage: **!exraid <location>**'))
        return
    rgx = '[^a-zA-Z0-9]'
    pkmn_match = next((p for p in pkmn_info['pokemon_list'] if re.sub(rgx, '', p) == re.sub(rgx, '', exraid_split[0].lower())), None)
    if pkmn_match:
        del exraid_split[0]
    if len(exraid_split) <= 0:
        await channel.send(_('Meowth! Give more details when reporting! Usage: **!exraid <location>**'))
        return
    raid_details = ' '.join(exraid_split)
    raid_details = raid_details.strip()
    gyms = get_gyms(message.guild.id)
    if gyms:
        match = await gym_match_prompt(message.channel, message.author.id, raid_details, gyms)
        if not match:
            return await message.channel.send(_("Meowth! I couldn't find a gym named '{0}'.").format(raid_details))
        gym = gyms[match]
        raid_details = match
        gym_coords = gym['coordinates']
        gym_note = gym.get('notes', _('No notes for this gym.'))
        raid_gmaps_link = create_gmaps_query(gym_coords, message.channel, type="exraid")
    else:
        raid_gmaps_link = create_gmaps_query(raid_details, message.channel, type="exraid")
    egg_info = raid_info['raid_eggs']['EX']
    egg_img = egg_info['egg_img']
    boss_list = []
    for p in egg_info['pokemon']:
        p_name = get_name(p).title()
        p_type = get_type(message.guild, p)
        boss_list.append((((p_name + ' (') + str(p)) + ') ') + ''.join(p_type))
    raid_channel_name = _('ex-raid-egg-')
    raid_channel_name += sanitize_channel_name(raid_details)
    raid_channel_overwrite_list = channel.overwrites
    if guild_dict[channel.guild.id]['configure_dict']['invite']['enabled']:
        if guild_dict[channel.guild.id]['configure_dict']['exraid']['permissions'] == "everyone":
            everyone_overwrite = (channel.guild.default_role, discord.PermissionOverwrite(send_messages=False))
            raid_channel_overwrite_list.append(everyone_overwrite)
        for overwrite in raid_channel_overwrite_list:
            if isinstance(overwrite[0], discord.Role):
                if overwrite[0].permissions.manage_guild or overwrite[0].permissions.manage_channels or overwrite[0].permissions.manage_messages:
                    continue
                overwrite[1].send_messages = False
            elif isinstance(overwrite[0], discord.Member):
                if channel.permissions_for(overwrite[0]).manage_guild or channel.permissions_for(overwrite[0]).manage_channels or channel.permissions_for(overwrite[0]).manage_messages:
                    continue
                overwrite[1].send_messages = False
            if (overwrite[0].name not in channel.guild.me.top_role.name) and (overwrite[0].name not in channel.guild.me.name):
                overwrite[1].send_messages = False
    else:
        if guild_dict[channel.guild.id]['configure_dict']['exraid']['permissions'] == "everyone":
            everyone_overwrite = (channel.guild.default_role, discord.PermissionOverwrite(send_messages=True))
            raid_channel_overwrite_list.append(everyone_overwrite)
    meowth_overwrite = (Meowth.user, discord.PermissionOverwrite(send_messages=True, read_messages=True, manage_roles=True))
    raid_channel_overwrite_list.append(meowth_overwrite)
    raid_channel_overwrites = dict(raid_channel_overwrite_list)
    raid_channel_category = get_category(message.channel,"EX", category_type="exraid")
    raid_channel = await message.guild.create_text_channel(raid_channel_name, overwrites=raid_channel_overwrites,category=raid_channel_category)
    if guild_dict[channel.guild.id]['configure_dict']['invite']['enabled']:
        for role in channel.guild.role_hierarchy:
            if role.permissions.manage_guild or role.permissions.manage_channels or role.permissions.manage_messages:
                try:
                    await raid_channel.set_permissions(role, send_messages=True)
                except (discord.errors.Forbidden, discord.errors.HTTPException, discord.errors.InvalidArgument):
                    pass
    raid_img_url = 'https://raw.githubusercontent.com/FoglyOgly/Meowth/discordpy-v1/images/eggs/{}?cache=0'.format(str(egg_img))
    raid_embed = discord.Embed(title=_('Meowth! Click here for directions to the coming raid!'), url=raid_gmaps_link, colour=message.guild.me.colour)
    if len(egg_info['pokemon']) > 1:
        raid_embed.add_field(name=_('**Possible Bosses:**'), value=_('{bosslist1}').format(bosslist1='\n'.join(boss_list[::2])), inline=True)
        raid_embed.add_field(name='\u200b', value=_('{bosslist2}').format(bosslist2='\n'.join(boss_list[1::2])), inline=True)
    else:
        raid_embed.add_field(name=_('**Possible Bosses:**'), value=_('{bosslist}').format(bosslist=''.join(boss_list)), inline=True)
        raid_embed.add_field(name='\u200b', value='\u200b', inline=True)
    raid_embed.add_field(name=_('**Next Group:**'), value=_('Set with **!starttime**'), inline=True)
    raid_embed.add_field(name=_('**Expires:**'), value=_('Set with **!timerset**'), inline=True)
    raid_embed.set_footer(text=_('Reported by @{author} - {timestamp}').format(author=message.author.display_name, timestamp=timestamp), icon_url=message.author.avatar_url_as(format=None, static_format='jpg', size=32))
    raid_embed.set_thumbnail(url=raid_img_url)
    if guild_dict[channel.guild.id]['configure_dict']['invite']['enabled']:
        invitemsgstr = _("Use the **!invite** command to gain access and coordinate")
        invitemsgstr2 = _(" after using **!invite** to gain access")
    else:
        invitemsgstr = _("Coordinate")
        invitemsgstr2 = ""
    raidreport = await channel.send(content=_('Meowth! EX raid egg reported by {member}! Details: {location_details}. {invitemsgstr} in {raid_channel}').format(member=message.author.mention, location_details=raid_details, invitemsgstr=invitemsgstr,raid_channel=raid_channel.mention), embed=raid_embed)
    await asyncio.sleep(1)
    raidmsg = _("Meowth! EX raid reported by {member} in {citychannel}! Details: {location_details}. Coordinate here{invitemsgstr2}!\n\nClick the question mark reaction to get help on the commands that work in here.\n\nThis channel will be deleted five minutes after the timer expires.").format(member=message.author.mention, citychannel=message.channel.mention, location_details=raid_details, invitemsgstr2=invitemsgstr2)
    raidmessage = await raid_channel.send(content=raidmsg, embed=raid_embed)
    await raidmessage.add_reaction('\u2754')
    await raidmessage.pin()
    guild_dict[message.guild.id]['raidchannel_dict'][raid_channel.id] = {
        'reportcity': channel.id,
        'trainer_dict': {

        },
        'exp': time.time() + (((60 * 60) * 24) * raid_info['raid_eggs']['EX']['hatchtime']),
        'manual_timer': False,
        'active': True,
        'raidmessage': raidmessage.id,
        'raidreport': raidreport.id,
        'address': raid_details,
        'type': 'egg',
        'pokemon': '',
        'egglevel': 'EX'
    }
    if len(raid_info['raid_eggs']['EX']['pokemon']) == 1:
        await _eggassume('assume ' + get_name(raid_info['raid_eggs']['EX']['pokemon'][0]), raid_channel)
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=guild_dict[raid_channel.guild.id]['configure_dict']['settings']['offset'])
    await raid_channel.send(content=_('Meowth! Hey {member}, if you can, set the time left until the egg hatches using **!timerset <date and time>** so others can check it with **!timer**. **<date and time>** can just be written exactly how it appears on your EX Raid Pass.').format(member=message.author.mention))
    ex_reports = guild_dict[message.guild.id].setdefault('trainers',{}).setdefault(message.author.id,{}).setdefault('ex_reports',0) + 1
    guild_dict[message.guild.id]['trainers'][message.author.id]['ex_reports'] = ex_reports
    event_loop.create_task(expiry_check(raid_channel))

@Meowth.command()
@checks.allowinvite()
async def invite(ctx):
    """Rejoignez un raid EX.

     Utilisation:!invite"""
    await _invite(ctx)

async def _invite(ctx):
    bot = ctx.bot
    channel = ctx.channel
    author = ctx.author
    guild = ctx.guild
    await channel.trigger_typing()
    exraidlist = ''
    exraid_dict = {

    }
    exraidcount = 0
    rc_dict = bot.guild_dict[guild.id]['raidchannel_dict']
    for channelid in rc_dict:
        if (not discord.utils.get(guild.text_channels, id=channelid)) or rc_dict[channelid].get('meetup',{}):
            continue
        if (rc_dict[channelid]['egglevel'] == 'EX') or (rc_dict[channelid]['type'] == 'exraid'):
            if guild_dict[guild.id]['configure_dict']['exraid']['permissions'] == "everyone" or (guild_dict[guild.id]['configure_dict']['exraid']['permissions'] == "same" and rc_dict[channelid]['reportcity'] == channel.id):
                exraid_channel = bot.get_channel(channelid)
                if exraid_channel.mention != '#deleted-channel':
                    exraidcount += 1
                    exraidlist += (('\n**' + str(exraidcount)) + '.**   ') + exraid_channel.mention
                    exraid_dict[str(exraidcount)] = exraid_channel
    if exraidcount == 0:
        await channel.send(_('Meowth! No EX Raids have been reported in this server! Use **!exraid** to report one!'))
        return
    exraidchoice = await channel.send(_("Meowth! {0}, you've told me you have an invite to an EX Raid, and I'm just going to take your word for it! The following {1} EX Raids have been reported:\n{2}\nReply with **the number** (1, 2, etc) of the EX Raid you have been invited to. If none of them match your invite, type 'N' and report it with **!exraid**").format(author.mention, str(exraidcount), exraidlist))
    reply = await bot.wait_for('message', check=(lambda message: (message.author == author)))
    if reply.content.lower() == 'n':
        await exraidchoice.delete()
        exraidmsg = await channel.send(_('Meowth! Be sure to report your EX Raid with **!exraid**!'))
    elif (not reply.content.isdigit()) or (int(reply.content) > exraidcount):
        await exraidchoice.delete()
        exraidmsg = await channel.send(_("Meowth! I couldn't tell which EX Raid you meant! Try the **!invite** command again, and make sure you respond with the number of the channel that matches!"))
    elif (int(reply.content) <= exraidcount) and (int(reply.content) > 0):
        await exraidchoice.delete()
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = True
        overwrite.read_messages = True
        exraid_channel = exraid_dict[str(int(reply.content))]
        try:
            await exraid_channel.set_permissions(author, overwrite=overwrite)
        except (discord.errors.Forbidden, discord.errors.HTTPException, discord.errors.InvalidArgument):
            pass
        exraidmsg = await channel.send(_('Meowth! Alright {0}, you can now send messages in {1}! Make sure you let the trainers in there know if you can make it to the EX Raid!').format(author.mention, exraid_channel.mention))
        await _maybe(exraid_channel, author, 1, party=None)
    else:
        await exraidchoice.delete()
        exraidmsg = await channel.send(_("Meowth! I couldn't understand your reply! Try the **!invite** command again!"))
    await asyncio.sleep(30)
    await ctx.message.delete()
    await reply.delete()
    await exraidmsg.delete()

@Meowth.command(aliases=['res'])
@checks.allowresearchreport()
async def research(ctx, *, details = None):
    """Rapport de recherche sur le terrain
     Méthode de rapport guidé avec juste! Si vous fournissez des arguments dans un
     évitez les virgules, sauf vos séparations entre pokestop,
     quête, récompense. L'ordre compte si vous fournissez des arguments. Si un nom de pokemon
     est inclus dans la récompense, un @mention sera utilisé si le rôle existe.

     Utilisation:!research [nom du pokestop [URL optionnelle], quête, récompense]"""
    message = ctx.message
    channel = message.channel
    author = message.author
    guild = message.guild
    timestamp = (message.created_at + datetime.timedelta(hours=guild_dict[message.channel.guild.id]['configure_dict']['settings']['offset']))
    to_midnight = 24*60*60 - ((timestamp-timestamp.replace(hour=0, minute=0, second=0, microsecond=0)).seconds)
    error = False
    loc_url = create_gmaps_query("", message.channel, type="research")
    research_embed = discord.Embed(colour=message.guild.me.colour).set_thumbnail(url='https://raw.githubusercontent.com/FoglyOgly/Meowth/discordpy-v1/images/misc/field-research.png?cache=0')
    research_embed.set_footer(text=_('Reported by @{author} - {timestamp}').format(author=author.display_name, timestamp=timestamp.strftime(_('%I:%M %p (%H:%M)'))), icon_url=author.avatar_url_as(format=None, static_format='jpg', size=32))
    while True:
        if details:
            research_split = details.rsplit(",", 2)
            if len(research_split) != 3:
                error = _("entered an incorrect amount of arguments.\n\nUsage: **!research** or **!research <pokestop>, <quest>, <reward>**")
                break
            location, quest, reward = research_split
            loc_url = create_gmaps_query(location, message.channel, type="research")
            location = location.replace(loc_url,"").strip()
            research_embed.add_field(name=_("**Pokestop:**"),value='\n'.join(textwrap.wrap(location.title(), width=30)),inline=True)
            research_embed.add_field(name=_("**Quest:**"),value='\n'.join(textwrap.wrap(quest.title(), width=30)),inline=True)
            research_embed.add_field(name=_("**Reward:**"),value='\n'.join(textwrap.wrap(reward.title(), width=30)),inline=True)
            break
        else:
            research_embed.add_field(name=_('**New Research Report**'), value=_("Meowth! I'll help you report a research quest!\n\nFirst, I'll need to know what **pokestop** you received the quest from. Reply with the name of the **pokestop**. You can reply with **cancel** to stop anytime."), inline=False)
            pokestopwait = await channel.send(embed=research_embed)
            try:
                pokestopmsg = await Meowth.wait_for('message', timeout=60, check=(lambda reply: reply.author == message.author))
            except asyncio.TimeoutError:
                pokestopmsg = None
            await pokestopwait.delete()
            if not pokestopmsg:
                error = _("took too long to respond")
                break
            elif pokestopmsg.clean_content.lower() == "cancel":
                error = _("cancelled the report")
                await pokestopmsg.delete()
                break
            elif pokestopmsg:
                location = pokestopmsg.clean_content
                loc_url = create_gmaps_query(location, message.channel, type="research")
                location = location.replace(loc_url,"").strip()
            await pokestopmsg.delete()
            research_embed.add_field(name=_("**Pokestop:**"),value='\n'.join(textwrap.wrap(location.title(), width=30)),inline=True)
            research_embed.set_field_at(0, name=research_embed.fields[0].name, value=_("Great! Now, reply with the **quest** that you received from **{location}**. You can reply with **cancel** to stop anytime.\n\nHere's what I have so far:").format(location=location), inline=False)
            questwait = await channel.send(embed=research_embed)
            try:
                questmsg = await Meowth.wait_for('message', timeout=60, check=(lambda reply: reply.author == message.author))
            except asyncio.TimeoutError:
                questmsg = None
            await questwait.delete()
            if not questmsg:
                error = _("took too long to respond")
                break
            elif questmsg.clean_content.lower() == "cancel":
                error = _("cancelled the report")
                await questmsg.delete()
                break
            elif questmsg:
                quest = questmsg.clean_content
            await questmsg.delete()
            research_embed.add_field(name=_("**Quest:**"),value='\n'.join(textwrap.wrap(quest.title(), width=30)),inline=True)
            research_embed.set_field_at(0, name=research_embed.fields[0].name, value=_("Fantastic! Now, reply with the **reward** for the **{quest}** quest that you received from **{location}**. You can reply with **cancel** to stop anytime.\n\nHere's what I have so far:").format(quest=quest, location=location), inline=False)
            rewardwait = await channel.send(embed=research_embed)
            try:
                rewardmsg = await Meowth.wait_for('message', timeout=60, check=(lambda reply: reply.author == message.author))
            except asyncio.TimeoutError:
                rewardmsg = None
            await rewardwait.delete()
            if not rewardmsg:
                error = _("took too long to respond")
                break
            elif rewardmsg.clean_content.lower() == "cancel":
                error = _("cancelled the report")
                await rewardmsg.delete()
                break
            elif rewardmsg:
                reward = rewardmsg.clean_content
            await rewardmsg.delete()
            research_embed.add_field(name=_("**Reward:**"),value='\n'.join(textwrap.wrap(reward.title(), width=30)),inline=True)
            research_embed.remove_field(0)
            break
    if not error:
        pkmn_match = next((p for p in pkmn_info['pokemon_list'] if re.sub('[^a-zA-Z0-9]', '', p) == re.sub('[^a-zA-Z0-9]', '', reward.lower())), None)
        roletest = ""
        if pkmn_match:
            role = discord.utils.get(guild.roles, name=pkmn_match)
            if role:
                roletest = _("{pokemon} - ").format(pokemon=role.mention)
        research_msg = _("{roletest}Field Research reported by {author}").format(roletest=roletest,author=author.mention)
        research_embed.title = _('Meowth! Click here for my directions to the research!')
        research_embed.description = _("Ask {author} if my directions aren't perfect!").format(author=author.name)
        research_embed.url = loc_url
        confirmation = await channel.send(research_msg,embed=research_embed)
        research_dict = copy.deepcopy(guild_dict[guild.id].get('questreport_dict',{}))
        research_dict[confirmation.id] = {
            'exp':time.time() + to_midnight,
            'expedit':"delete",
            'reportmessage':message.id,
            'reportchannel':channel.id,
            'reportauthor':author.id,
            'location':location,
            'url':loc_url,
            'quest':quest,
            'reward':reward
        }
        guild_dict[guild.id]['questreport_dict'] = research_dict
        research_reports = guild_dict[ctx.guild.id].setdefault('trainers',{}).setdefault(author.id,{}).setdefault('research_reports',0) + 1
        guild_dict[ctx.guild.id]['trainers'][author.id]['research_reports'] = research_reports
    else:
        research_embed.clear_fields()
        research_embed.add_field(name=_('**Research Report Cancelled**'), value=_("Meowth! Your report has been cancelled because you {error}! Retry when you're ready.").format(error=error), inline=False)
        confirmation = await channel.send(embed=research_embed)
        await asyncio.sleep(10)
        await confirmation.delete()
        await message.delete()

@Meowth.command(aliases=['event'])
@checks.allowmeetupreport()
async def meetup(ctx, *,location:commands.clean_content(fix_channel_mentions=True)=""):
    """Signaler un événement à venir

     Utilisation:!meetup <emplacement>
     Miaoussier va insérer les détails (vraiment juste tout après le nom de l'espèce) dans un
     Lien Google Maps et publiez le lien vers le même canal que le rapport a été créé.

     Enfin, Meowth créera un canal séparé pour le rapport, dans le but d'organiser l'événement."""
    await _meetup(ctx, location)

async def _meetup(ctx, location):
    message = ctx.message
    channel = message.channel
    timestamp = (message.created_at + datetime.timedelta(hours=guild_dict[message.channel.guild.id]['configure_dict']['settings']['offset'])).strftime(_('%I:%M %p (%H:%M)'))
    event_split = location.split()
    if len(event_split) <= 0:
        await channel.send(_('Meowth! Give more details when reporting! Usage: **!meetup <location>**'))
        return
    raid_details = ' '.join(event_split)
    raid_details = raid_details.strip()
    raid_gmaps_link = create_gmaps_query(raid_details, message.channel, type="meetup")
    egg_info = raid_info['raid_eggs']['EX']
    raid_channel_name = _('meetup-')
    raid_channel_name += sanitize_channel_name(raid_details)
    raid_channel_category = get_category(message.channel,"EX", category_type="meetup")
    raid_channel = await message.guild.create_text_channel(raid_channel_name, overwrites=dict(message.channel.overwrites), category=raid_channel_category)
    ow = raid_channel.overwrites_for(raid_channel.guild.default_role)
    ow.send_messages = True
    try:
        await raid_channel.set_permissions(raid_channel.guild.default_role, overwrite = ow)
    except (discord.errors.Forbidden, discord.errors.HTTPException, discord.errors.InvalidArgument):
        pass
    raid_img_url = 'https://raw.githubusercontent.com/FoglyOgly/Meowth/discordpy-v1/images/misc/meetup.png?cache=0'
    raid_embed = discord.Embed(title=_('Meowth! Click here for directions to the event!'), url=raid_gmaps_link, colour=message.guild.me.colour)
    raid_embed.add_field(name=_('**Event Location:**'), value=raid_details, inline=True)
    raid_embed.add_field(name='\u200b', value='\u200b', inline=True)
    raid_embed.add_field(name=_('**Event Starts:**'), value=_('Set with **!starttime**'), inline=True)
    raid_embed.add_field(name=_('**Event Ends:**'), value=_('Set with **!timerset**'), inline=True)
    raid_embed.set_footer(text=_('Reported by @{author} - {timestamp}').format(author=message.author.display_name, timestamp=timestamp), icon_url=message.author.avatar_url_as(format=None, static_format='jpg', size=32))
    raid_embed.set_thumbnail(url=raid_img_url)
    raidreport = await channel.send(content=_('Meowth! Meetup reported by {member}! Details: {location_details}. Coordinate in {raid_channel}').format(member=message.author.mention, location_details=raid_details, raid_channel=raid_channel.mention), embed=raid_embed)
    await asyncio.sleep(1)
    raidmsg = _("Meowth! Meetup reported by {member} in {citychannel}! Details: {location_details}. Coordinate here!\n\nTo update your status, choose from the following commands: **!maybe**, **!coming**, **!here**, **!cancel**. If you are bringing more than one trainer/account, add in the number of accounts total, teams optional, on your first status update.\nExample: `!coming 5 2m 2v 1i`\n\nTo see the list of trainers who have given their status:\n**!list interested**, **!list coming**, **!list here** or use just **!list** to see all lists. Use **!list teams** to see team distribution.\n\nSometimes I'm not great at directions, but I'll correct my directions if anybody sends me a maps link or uses **!location new <address>**. You can see the location of the event by using **!location**\n\nYou can set the start time with **!starttime <MM/DD HH:MM AM/PM>** (you can also omit AM/PM and use 24-hour time) and access this with **!starttime**.\nYou can set the end time with **!timerset <MM/DD HH:MM AM/PM>** and access this with **!timer**.\n\nThis channel will be deleted five minutes after the timer expires.").format(member=message.author.mention, citychannel=message.channel.mention, location_details=raid_details)
    raidmessage = await raid_channel.send(content=raidmsg, embed=raid_embed)
    await raidmessage.pin()
    guild_dict[message.guild.id]['raidchannel_dict'][raid_channel.id] = {
        'reportcity': channel.id,
        'trainer_dict': {},
        'exp': time.time() + (((60 * 60) * 24) * raid_info['raid_eggs']['EX']['hatchtime']),
        'manual_timer': False,
        'active': True,
        'raidmessage': raidmessage.id,
        'raidreport': raidreport.id,
        'address': raid_details,
        'type': 'egg',
        'pokemon': '',
        'egglevel': 'EX',
        'meetup': {'start':None, 'end':None}
    }
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=guild_dict[raid_channel.guild.id]['configure_dict']['settings']['offset'])
    await raid_channel.send(content=_('Meowth! Hey {member}, if you can, set the time that the event starts with **!starttime <date and time>** and also set the time that the event ends using **!timerset <date and time>**.').format(member=message.author.mention))
    event_loop.create_task(expiry_check(raid_channel))

"""
Raid Channel Management
"""

async def print_raid_timer(channel):
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=guild_dict[channel.guild.id]['configure_dict']['settings']['offset'])
    end = now + datetime.timedelta(seconds=guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['exp'] - time.time())
    timerstr = ' '
    if guild_dict[channel.guild.id]['raidchannel_dict'][channel.id].get('meetup',{}):
        end = guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['meetup']['end']
        start = guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['meetup']['start']
        if guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['type'] == 'egg':
            if start:
                timerstr += _("This event will start at {expiry_time}").format(expiry_time=start.strftime(_('%B %d at %I:%M %p (%H:%M)')))
            else:
                timerstr += _("Nobody has told me a start time! Set it with **!starttime**")
            if end:
                timerstr += _(" | This event will end at {expiry_time}").format(expiry_time=end.strftime(_('%B %d at %I:%M %p (%H:%M)')))
        if guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['type'] == 'exraid':
            if end:
                timerstr += _("This event will end at {expiry_time}").format(expiry_time=end.strftime(_('%B %d at %I:%M %p (%H:%M)')))
            else:
                timerstr += _("Nobody has told me a end time! Set it with **!timerset**")
        return timerstr
    if guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['type'] == 'egg':
        raidtype = _('egg')
        raidaction = _('hatch')
    else:
        raidtype = _('raid')
        raidaction = _('end')
    if (not guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['active']):
        timerstr += _("This {raidtype}'s timer has already expired as of {expiry_time}!").format(raidtype=raidtype, expiry_time=end.strftime(_('%I:%M %p (%H:%M)')))
    elif (guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['egglevel'] == 'EX') or (guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['type'] == 'exraid'):
        if guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['manual_timer']:
            timerstr += _('This {raidtype} will {raidaction} on {expiry}!').format(raidtype=raidtype, raidaction=raidaction, expiry=end.strftime(_('%B %d at %I:%M %p (%H:%M)')))
        else:
            timerstr += _("No one told me when the {raidtype} will {raidaction}, so I'm assuming it will {raidaction} on {expiry}!").format(raidtype=raidtype, raidaction=raidaction, expiry=end.strftime(_('%B %d at %I:%M %p (%H:%M)')))
    elif guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['manual_timer']:
        timerstr += _('This {raidtype} will {raidaction} at {expiry_time}!').format(raidtype=raidtype, raidaction=raidaction, expiry_time=end.strftime(_('%I:%M %p (%H:%M)')))
    else:
        timerstr += _("No one told me when the {raidtype} will {raidaction}, so I'm assuming it will {raidaction} at {expiry_time}!").format(raidtype=raidtype, raidaction=raidaction, expiry_time=end.strftime(_('%I:%M %p (%H:%M)')))
    return timerstr

@Meowth.command()
@checks.raidchannel()
async def timerset(ctx, *,timer):
    """Définissez la durée restante sur un raid.

     Utilisation:!timerset <minutes>
     Fonctionne uniquement dans les canaux de raid, peut être défini ou remplacé par n'importe qui.
     Miaouss affiche l'heure de fin en HH: MM heure locale."""
    message = ctx.message
    channel = message.channel
    guild = message.guild
    hourminute = False
    type = guild_dict[guild.id]['raidchannel_dict'][channel.id]['type']
    if (not checks.check_exraidchannel(ctx)) and not (checks.check_meetupchannel(ctx)):
        if type == 'egg':
            raidlevel = guild_dict[guild.id]['raidchannel_dict'][channel.id]['egglevel']
            raidtype = _('Raid Egg')
            maxtime = raid_info['raid_eggs'][raidlevel]['hatchtime']
        else:
            raidlevel = get_level(guild_dict[guild.id]['raidchannel_dict'][channel.id]['pokemon'])
            raidtype = _('Raid')
            maxtime = raid_info['raid_eggs'][raidlevel]['raidtime']
        if timer.isdigit():
            raidexp = int(timer)
        elif type == 'egg' and ':' in timer:
            msg = _("Did you mean egg hatch time {0} or time remaining before hatch {1}?").format("🥚", "⏲")
            question = await ctx.channel.send(msg)
            try:
                timeout = False
                res, reactuser = await ask(question, ctx.message.channel, ctx.message.author.id, react_list=['🥚', '⏲'])
            except TypeError:
                timeout = True
            await question.delete()
            if timeout or res.emoji == '⏲':
                hourminute = True
            elif res.emoji == '🥚':
                now = datetime.datetime.utcnow() + datetime.timedelta(hours=guild_dict[channel.guild.id]['configure_dict']['settings']['offset'])
                start = dateparser.parse(timer, settings={'PREFER_DATES_FROM': 'future'})
                if now.hour > 12 and start.hour < 12 and "m" not in timer:
                    start = start + datetime.timedelta(hours=12)
                start = start.replace(day=now.day)
                timediff = relativedelta(start, now)
                raidexp = (timediff.hours*60) + timediff.minutes + 1
                if raidexp < 0:
                    await channel.send(_('Meowth! Please enter a time in the future.'))
                    return
            else:
                await channel.send(_("Meowth! I couldn't understand your time format. Try again like this: **!timerset <minutes>**"))
                return
        elif ':' in timer:
            hourminute = True
        else:
            await channel.send(_("Meowth! I couldn't understand your time format. Try again like this: **!timerset <minutes>**"))
            return
        if hourminute:
            (h, m) = re.sub('[a-zA-Z]', '', timer).split(':', maxsplit=1)
            if h == '':
                h = '0'
            if m == '':
                m = '0'
            if h.isdigit() and m.isdigit():
                raidexp = (60 * int(h)) + int(m)
            else:
                await channel.send(_("Meowth! I couldn't understand your time format. Try again like this: **!timerset <minutes>**"))
                return
        if _timercheck(raidexp, maxtime):
            await channel.send(_("Meowth...that's too long. Level {raidlevel} {raidtype}s currently last no more than {maxtime} minutes...").format(raidlevel=str(raidlevel), raidtype=raidtype.capitalize(), maxtime=str(maxtime)))
            return
        await _timerset(channel, raidexp)
    if checks.check_exraidchannel(ctx):
        if checks.check_eggchannel(ctx) or checks.check_meetupchannel(ctx):
            now = datetime.datetime.utcnow() + datetime.timedelta(hours=guild_dict[channel.guild.id]['configure_dict']['settings']['offset'])
            timer_split = timer.lower().split()
            try:
                start = dateparser.parse(' '.join(timer_split).lower(), settings={'DATE_ORDER': 'MDY'})
            except:
                if ('am' in ' '.join(timer_split).lower()) or ('pm' in ' '.join(timer_split).lower()):
                    try:
                        start = datetime.datetime.strptime((' '.join(timer_split) + ' ') + str(now.year), '%m/%d %I:%M %p %Y')
                        if start.month < now.month:
                            start = start.replace(year=now.year + 1)
                    except ValueError:
                        await channel.send(_("Meowth! Your timer wasn't formatted correctly. Change your **!timerset** to match this format: **MM/DD HH:MM AM/PM** (You can also omit AM/PM and use 24-hour time!)"))
                        return
                else:
                    try:
                        start = datetime.datetime.strptime((' '.join(timer_split) + ' ') + str(now.year), '%m/%d %H:%M %Y')
                        if start.month < now.month:
                            start = start.replace(year=now.year + 1)
                    except ValueError:
                        await channel.send(_("Meowth! Your timer wasn't formatted correctly. Change your **!timerset** to match this format: **MM/DD HH:MM AM/PM** (You can also omit AM/PM and use 24-hour time!)"))
                        return
            if checks.check_meetupchannel(ctx):
                starttime = guild_dict[guild.id]['raidchannel_dict'][channel.id]['meetup'].get('start',False)
                if starttime and start < starttime:
                    await channel.send(_('Meowth! Please enter a time after your start time.'))
                    return
            diff = start - now
            total = diff.total_seconds() / 60
            if now <= start:
                await _timerset(channel, total)
            elif now > start:
                await channel.send(_('Meowth! Please enter a time in the future.'))
        else:
            await channel.send(_("Meowth! Timerset isn't supported for EX Raids after they have hatched."))

def _timercheck(time, maxtime):
    return time > maxtime

async def _timerset(raidchannel, exptime):
    guild = raidchannel.guild
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=guild_dict[guild.id]['configure_dict']['settings']['offset'])
    end = now + datetime.timedelta(minutes=exptime)
    guild_dict[guild.id]['raidchannel_dict'][raidchannel.id]['exp'] = time.time() + (exptime * 60)
    if (not guild_dict[guild.id]['raidchannel_dict'][raidchannel.id]['active']):
        await raidchannel.send(_('The channel has been reactivated.'))
    guild_dict[guild.id]['raidchannel_dict'][raidchannel.id]['active'] = True
    guild_dict[guild.id]['raidchannel_dict'][raidchannel.id]['manual_timer'] = True
    topicstr = ''
    if guild_dict[guild.id]['raidchannel_dict'][raidchannel.id].get('meetup',{}):
        guild_dict[guild.id]['raidchannel_dict'][raidchannel.id]['meetup']['end'] = end
        topicstr += _('Ends on {end}').format(end=end.strftime(_('%B %d at %I:%M %p (%H:%M)')))
        endtime = end.strftime(_('%B %d at %I:%M %p (%H:%M)'))
    elif guild_dict[guild.id]['raidchannel_dict'][raidchannel.id]['type'] == 'egg':
        egglevel = guild_dict[guild.id]['raidchannel_dict'][raidchannel.id]['egglevel']
        hatch = end
        end = hatch + datetime.timedelta(minutes=raid_info['raid_eggs'][egglevel]['raidtime'])
        topicstr += _('Hatches on {expiry}').format(expiry=hatch.strftime(_('%B %d at %I:%M %p (%H:%M) | ')))
        topicstr += _('Ends on {end}').format(end=end.strftime(_('%B %d at %I:%M %p (%H:%M)')))
        endtime = hatch.strftime(_('%B %d at %I:%M %p (%H:%M)'))
    else:
        topicstr += _('Ends on {end}').format(end=end.strftime(_('%B %d at %I:%M %p (%H:%M)')))
        endtime = end.strftime(_('%B %d at %I:%M %p (%H:%M)'))
    timerstr = await print_raid_timer(raidchannel)
    await raidchannel.send(timerstr)
    await raidchannel.edit(topic=topicstr)
    report_channel = Meowth.get_channel(guild_dict[guild.id]['raidchannel_dict'][raidchannel.id]['reportcity'])
    raidmsg = await raidchannel.get_message(guild_dict[guild.id]['raidchannel_dict'][raidchannel.id]['raidmessage'])
    reportmsg = await report_channel.get_message(guild_dict[guild.id]['raidchannel_dict'][raidchannel.id]['raidreport'])
    embed = raidmsg.embeds[0]
    embed.set_field_at(3, name=embed.fields[3].name, value=endtime, inline=True)
    try:
        await raidmsg.edit(content=raidmsg.content,embed=embed)
    except discord.errors.NotFound:
        pass
    try:
        await reportmsg.edit(content=reportmsg.content,embed=embed)
    except discord.errors.NotFound:
        pass
    raidchannel = Meowth.get_channel(raidchannel.id)
    event_loop.create_task(expiry_check(raidchannel))

@Meowth.command()
@checks.raidchannel()
async def timer(ctx):
    """Avoir Meowth renvoyer le message d'expiration d'un raid.

     Utilisation:!timer
     L'heure d'expiration doit avoir été préalablement définie avec !timerset."""
    timerstr = _('Meowth!')
    timerstr += await print_raid_timer(ctx.channel)
    await ctx.channel.send(timerstr)

@Meowth.command()
@checks.activechannel()
async def starttime(ctx,*,start_time=""):
    """Définir une heure pour un groupe pour lancer un raid

     Utilisation:!starttime [HH:MM AM/PM]
     (Vous pouvez également omettre AM/PM et utiliser l'heure de 24 heures!)
     Fonctionne uniquement dans les canaux de raid. Envoie un message et définit une heure de début de groupe
     peut être vu en utilisant! starttime (sans temps). Une heure de début est autorisée à
     une fois et est visible dans! liste de sortie. Effacé avec !starting."""
    message = ctx.message
    guild = message.guild
    channel = message.channel
    author = message.author
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=guild_dict[guild.id]['configure_dict']['settings']['offset'])
    start_split = start_time.lower().split()
    rc_d = guild_dict[guild.id]['raidchannel_dict'][channel.id]
    timeset = False
    start = None
    if rc_d.get('meetup',{}):
        try:
            start = dateparser.parse(' '.join(start_split).lower(), settings={'DATE_ORDER': 'MDY'})
            endtime = guild_dict[guild.id]['raidchannel_dict'][channel.id]['meetup'].get('end',False)
            if start < now:
                await channel.send(_('Meowth! Please enter a time in the future.'))
                return
            if endtime and start > endtime:
                await channel.send(_('Meowth! Please enter a time before your end time.'))
                return
            timeset = True
            rc_d['meetup']['start'] = start
        except:
            pass
    if not timeset:
        if rc_d['type'] == 'egg':
            egglevel = rc_d['egglevel']
            mintime = (rc_d['exp'] - time.time()) / 60
            maxtime = mintime + raid_info['raid_eggs'][egglevel]['raidtime']
        elif (rc_d['type'] == 'raid') or (rc_d['type'] == 'exraid'):
            egglevel = get_level(rc_d['pokemon'])
            mintime = 0
            maxtime = (rc_d['exp'] - time.time()) / 60
        if len(start_split) > 0:
            alreadyset = rc_d.get('starttime',False)
            if ('am' in ' '.join(start_split).lower()) or ('pm' in ' '.join(start_split).lower()):
                try:
                    start = datetime.datetime.strptime(' '.join(start_split), '%I:%M %p').replace(year=now.year, month=now.month, day=now.day)
                except ValueError:
                    await channel.send(_("Meowth! Your start time wasn't formatted correctly. Change your **!starttime** to match this format: **HH:MM AM/PM** (You can also omit AM/PM and use 24-hour time!)"))
                    return
            else:
                try:
                    start = datetime.datetime.strptime(' '.join(start_split), '%H:%M').replace(year=now.year, month=now.month, day=now.day)
                except ValueError:
                    await channel.send(_("Meowth! Your start time wasn't formatted correctly. Change your **!starttime** to match this format: **HH:MM AM/PM** (You can also omit AM/PM and use 24-hour time!)"))
                    return
            if egglevel == 'EX':
                hatch = datetime.datetime.utcfromtimestamp(rc_d['exp']) + datetime.timedelta(hours=guild_dict[guild.id]['configure_dict']['settings']['offset'])
                start = start.replace(year=hatch.year, month=hatch.month, day=hatch.day)
            diff = start - now
            total = diff.total_seconds() / 60
            if total > maxtime and egglevel != 'EX':
                await channel.send(_('Meowth! The raid will be over before that....'))
                return
            if now > start and egglevel != 'EX':
                await channel.send(_('Meowth! Please enter a time in the future.'))
                return
            if int(total) < int(mintime) and egglevel != 'EX':
                await channel.send(_('Meowth! The egg will not hatch by then!'))
                return
            if alreadyset:
                rusure = await channel.send(_('Meowth! There is already a start time of **{start}** set! Do you want to change it?').format(start=alreadyset.strftime(_('%I:%M %p (%H:%M)'))))
                try:
                    timeout = False
                    res, reactuser = await ask(rusure, channel, author.id)
                except TypeError:
                    timeout = True
                if timeout or res.emoji == '❎':
                    await rusure.delete()
                    confirmation = await channel.send(_('Start time change cancelled.'))
                    await asyncio.sleep(10)
                    await confirmation.delete()
                    return
                elif res.emoji == '✅':
                    await rusure.delete()
                    if now <= start:
                        timeset = True
                else:
                    return
    if (start and now <= start) or timeset:
        rc_d['starttime'] = start
        nextgroup = start.strftime(_('%I:%M %p (%H:%M)'))
        if rc_d.get('meetup',{}):
            nextgroup = start.strftime(_('%B %d at %I:%M %p (%H:%M)'))
        await channel.send(_('Meowth! The current start time has been set to: **{starttime}**').format(starttime=nextgroup))
        report_channel = Meowth.get_channel(rc_d['reportcity'])
        raidmsg = await channel.get_message(rc_d['raidmessage'])
        reportmsg = await report_channel.get_message(rc_d['raidreport'])
        embed = raidmsg.embeds[0]
        embed.set_field_at(2, name=embed.fields[2].name, value=nextgroup, inline=True)
        try:
            await raidmsg.edit(content=raidmsg.content,embed=embed)
        except discord.errors.NotFound:
            pass
        try:
            await reportmsg.edit(content=reportmsg.content,embed=embed)
        except discord.errors.NotFound:
            pass
        return
    else:
        starttime = rc_d.get('starttime',None)
        if starttime and starttime < now:
            rc_d['starttime'] = None
            starttime = None
        if starttime:
            await channel.send(_('Meowth! The current start time is: **{starttime}**').format(starttime=starttime.strftime(_('%I:%M %p (%H:%M)'))))
        elif not starttime:
            await channel.send(_('Meowth! No start time has been set, set one with **!starttime HH:MM AM/PM**! (You can also omit AM/PM and use 24-hour time!)'))

@Meowth.group(case_insensitive=True)
@checks.activechannel()
async def location(ctx):
    """Obtenez l'emplacement de raid.

     Utilisation:!location
     Fonctionne uniquement dans les canaux de raid. Donne le lien d'emplacement de raid."""
    if ctx.invoked_subcommand == None:
        message = ctx.message
        guild = message.guild
        channel = message.channel
        rc_d = guild_dict[guild.id]['raidchannel_dict']
        raidmsg = await channel.get_message(rc_d[channel.id]['raidmessage'])
        location = rc_d[channel.id]['address']
        report_channel = Meowth.get_channel(rc_d[channel.id]['reportcity'])
        oldembed = raidmsg.embeds[0]
        locurl = oldembed.url
        newembed = discord.Embed(title=oldembed.title, url=locurl, colour=guild.me.colour)
        for field in oldembed.fields:
            newembed.add_field(name=field.name, value=field.value, inline=field.inline)
        newembed.set_footer(text=oldembed.footer.text, icon_url=oldembed.footer.icon_url)
        newembed.set_thumbnail(url=oldembed.thumbnail.url)
        locationmsg = await channel.send(content=_("Meowth! Here's the current location for the raid!\nDetails: {location}").format(location=location), embed=newembed)
        await asyncio.sleep(60)
        await locationmsg.delete()

@location.command()
@checks.activechannel()
async def new(ctx,*,content):
    """Changer l'emplacement du raid.

     Utilisation:!location new <nouvelle adresse>
     Fonctionne uniquement dans les canaux de raid. Change les liens de Google Maps."""
    message = ctx.message
    location_split = content.lower().split()
    if len(location_split) < 1:
        await message.channel.send(_("Meowth! We're missing the new location details! Usage: **!location new <new address>**"))
        return
    else:
        report_channel = Meowth.get_channel(guild_dict[message.guild.id]['raidchannel_dict'][message.channel.id]['reportcity'])
        if not report_channel:
            async for m in message.channel.history(limit=500, reverse=True):
                if m.author.id == guild.me.id:
                    c = _('Coordinate here')
                    if c in m.content:
                        report_channel = m.raw_channel_mentions[0]
                        break
        report_city = report_channel.name
        details = ' '.join(location_split)
        newloc = create_gmaps_query(details, report_channel, type=guild_dict[message.guild.id]['raidchannel_dict'][message.channel.id]['type'])
        oldraidmsg = await message.channel.get_message(guild_dict[message.guild.id]['raidchannel_dict'][message.channel.id]['raidmessage'])
        oldreportmsg = await report_channel.get_message(guild_dict[message.guild.id]['raidchannel_dict'][message.channel.id]['raidreport'])
        oldembed = oldraidmsg.embeds[0]
        newembed = discord.Embed(title=oldembed.title, url=newloc, colour=message.guild.me.colour)
        for field in oldembed.fields:
            t = _('team')
            s = _('status')
            if (t not in field.name.lower()) and (s not in field.name.lower()):
                newembed.add_field(name=field.name, value=field.value, inline=field.inline)
        newembed.set_footer(text=oldembed.footer.text, icon_url=oldembed.footer.icon_url)
        newembed.set_thumbnail(url=oldembed.thumbnail.url)
        otw_list = []
        trainer_dict = copy.deepcopy(guild_dict[message.guild.id]['raidchannel_dict'][message.channel.id]['trainer_dict'])
        for trainer in trainer_dict.keys():
            if trainer_dict[trainer]['status']['coming']:
                user = message.guild.get_member(trainer)
                otw_list.append(user.mention)
        await message.channel.send(content=_('Meowth! Someone has suggested a different location for the raid! Trainers {trainer_list}: make sure you are headed to the right place!').format(trainer_list=', '.join(otw_list)), embed=newembed)
        for field in oldembed.fields:
            t = _('team')
            s = _('status')
            if (t in field.name.lower()) or (s in field.name.lower()):
                newembed.add_field(name=field.name, value=field.value, inline=field.inline)
        try:
            await oldraidmsg.edit(new_content=oldraidmsg.content, embed=newembed, content=oldraidmsg.content)
        except:
            pass
        try:
            await oldreportmsg.edit(new_content=oldreportmsg.content, embed=newembed, content=oldreportmsg.content)
        except:
            pass
        guild_dict[message.guild.id]['raidchannel_dict'][message.channel.id]['raidmessage'] = oldraidmsg.id
        guild_dict[message.guild.id]['raidchannel_dict'][message.channel.id]['raidreport'] = oldreportmsg.id
        return

@Meowth.command()
async def recover(ctx):
    """Récupérer un canal RAID s'il ne répond plus aux commandes

     Utilisation:!recover
     Seulement nécessaire après un accident."""
    if (checks.check_wantchannel(ctx) or checks.check_citychannel(ctx) or checks.check_raidchannel(ctx) or checks.check_eggchannel(ctx) or checks.check_exraidchannel(ctx)):
        await ctx.channel.send(_("Meowth! I can't recover this channel because I know about it already!"))
    else:
        channel = ctx.channel
        guild = channel.guild
        name = channel.name
        topic = channel.topic
        h = _('hatched-')
        e = _('expired-')
        while h in name or e in name:
            name = name.replace(h,'')
            name = name.replace(e,'')
        egg = re.match(_('level-[1-5]-egg'), name)
        meetup = re.match(_('meetup'), name)
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=guild_dict[guild.id]['configure_dict']['settings']['offset'])
        reportchannel = None
        raidmessage = None
        trainer_dict = {

        }
        async for message in channel.history(limit=500, reverse=True):
            if message.author.id == guild.me.id:
                c = _('Coordinate here')
                if c in message.content:
                    reportchannel = message.raw_channel_mentions[0]
                    raidmessage = message
                    break
        if egg:
            raidtype = 'egg'
            chsplit = egg.string.split('-')
            del chsplit[0]
            egglevel = chsplit[0]
            del chsplit[0]
            del chsplit[0]
            raid_details = ' '.join(chsplit)
            raid_details = raid_details.strip()
            if (not topic):
                exp = raidmessage.created_at.replace(tzinfo=datetime.timezone.utc).timestamp() + (60 * raid_info['raid_eggs'][egglevel]['hatchtime'])
                manual_timer = False
            else:
                topicsplit = topic.split('|')
                localhatch = datetime.datetime.strptime(topicsplit[0][:(- 9)], 'Hatches on %B %d at %I:%M %p')
                utchatch = localhatch - datetime.timedelta(hours=guild_dict[guild.id]['configure_dict']['settings']['offset'])
                exp = utchatch.replace(year=now.year, tzinfo=datetime.timezone.utc).timestamp()
                manual_timer = True
            pokemon = ''
            if len(raid_info['raid_eggs'][egglevel]['pokemon']) == 1:
                pokemon = get_name(raid_info['raid_eggs'][egglevel]['pokemon'][0])
        elif name.split('-')[0] in get_raidlist():
            raidtype = 'raid'
            egglevel = '0'
            chsplit = name.split('-')
            pokemon = chsplit[0]
            del chsplit[0]
            raid_details = ' '.join(chsplit)
            raid_details = raid_details.strip()
            if (not topic):
                exp = raidmessage.created_at.replace(tzinfo=datetime.timezone.utc).timestamp() + (60 * raid_info['raid_eggs'][get_level(pokemon)]['raidtime'])
                manual_timer = False
            else:
                localend = datetime.datetime.strptime(topic[:(- 8)], _('Ends on %B %d at %I:%M %p'))
                utcend = localend - datetime.timedelta(hours=guild_dict[guild.id]['configure_dict']['settings']['offset'])
                exp = utcend.replace(year=now.year, tzinfo=datetime.timezone.utc).timestamp()
                manual_timer = True
        elif name.split('-')[0] == 'ex':
            raidtype = 'egg'
            egglevel = 'EX'
            chsplit = name.split('-')
            del chsplit[0]
            del chsplit[0]
            del chsplit[0]
            raid_details = ' '.join(chsplit)
            raid_details = raid_details.strip()
            if (not topic):
                exp = raidmessage.created_at.replace(tzinfo=datetime.timezone.utc).timestamp() + (((60 * 60) * 24) * 14)
                manual_timer = False
            else:
                topicsplit = topic.split('|')
                localhatch = datetime.datetime.strptime(topicsplit[0][:(- 9)], 'Hatches on %B %d at %I:%M %p')
                utchatch = localhatch - datetime.timedelta(hours=guild_dict[guild.id]['configure_dict']['settings']['offset'])
                exp = utchatch.replace(year=now.year, tzinfo=datetime.timezone.utc).timestamp()
                manual_timer = True
            pokemon = ''
            if len(raid_info['raid_eggs']['EX']['pokemon']) == 1:
                pokemon = get_name(raid_info['raid_eggs']['EX']['pokemon'][0])
        elif meetup:
            raidtype = 'egg'
            egglevel = 'EX'
            chsplit = name.split('-')
            del chsplit[0]
            raid_details = ' '.join(chsplit)
            raid_details = raid_details.strip()
            if (not topic):
                exp = raidmessage.created_at.replace(tzinfo=datetime.timezone.utc).timestamp() + (((60 * 60) * 24) * 14)
                manual_timer = False
            else:
                topicsplit = topic.split('|')
                localhatch = datetime.datetime.strptime(topicsplit[0][:(- 9)], 'Hatches on %B %d at %I:%M %p')
                utchatch = localhatch - datetime.timedelta(hours=guild_dict[guild.id]['configure_dict']['settings']['offset'])
                exp = utchatch.replace(year=now.year, tzinfo=datetime.timezone.utc).timestamp()
                manual_timer = True
            pokemon = ''
        else:
            await channel.send(_("Meowth! I couldn't recognize this as a raid channel!"))
            return
        async for message in channel.history(limit=500):
            if message.author.id == guild.me.id:
                if (_('is interested') in message.content) or (_('on the way') in message.content) or (_('at the raid') in message.content) or (_('no longer') in message.content) or (_('left the raid') in message.content):
                    if message.raw_mentions:
                        if message.raw_mentions[0] not in trainer_dict:
                            trainerid = message.raw_mentions[0]
                            status = {'maybe':0, 'coming':0, 'here':0, 'lobby':0}
                            trainerstatus = None
                            if _('is interested') in message.content:
                                trainerstatus = 'maybe'
                            if _('on the way') in message.content:
                                trainerstatus = 'coming'
                            if _('at the raid') in message.content:
                                trainerstatus = 'here'
                            if (_('no longer') in message.content) or (_('left the raid') in message.content):
                                trainerstatus = None
                            if _('trainers') in message.content:
                                messagesplit = message.content.split()
                                if messagesplit[-1].isdigit():
                                    count = int(messagesplit[-13])
                                    party = {'mystic':int(messagesplit[-10]), 'valor':int(messagesplit[-7]), 'instinct':int(messagesplit[-4]), 'unknown':int(messagesplit[-1])}
                                else:
                                    count = 1
                                    party = {'mystic':0, 'valor':0, 'instinct':0, 'unknown':count}
                            else:
                                count = 1
                                user = ctx.guild.get_member(trainerid)
                                for role in user.roles:
                                    if role.name.lower() == 'mystic':
                                        party = {'mystic':1, 'valor':0, 'instinct':0, 'unknown':0}
                                        break
                                    elif role.name.lower() == 'valor':
                                        party = {'mystic':0, 'valor':1, 'instinct':0, 'unknown':0}
                                        break
                                    elif role.name.lower() == 'instinct':
                                        party = {'mystic':0, 'valor':0, 'instinct':1, 'unknown':0}
                                        break
                                    else:
                                        party = {'mystic':0, 'valor':0, 'instinct':0, 'unknown':1}
                            if trainerstatus:
                                status[trainerstatus] = count
                            trainer_dict[trainerid] = {
                                'status': status,
                                'count': count,
                                'party': party
                            }
                        else:
                            continue
                    else:
                        continue
        guild_dict[channel.guild.id]['raidchannel_dict'][channel.id] = {
            'reportcity': reportchannel,
            'trainer_dict': trainer_dict,
            'exp': exp,
            'manual_timer': manual_timer,
            'active': True,
            'raidmessage': raidmessage.id,
            'raidreport': None,
            'address': raid_details,
            'type': raidtype,
            'pokemon': pokemon,
            'egglevel': egglevel
        }
        await _edit_party(channel, message.author)
        recovermsg = _("Meowth! This channel has been recovered! However, there may be some inaccuracies in what I remembered! Here's what I have:")
        bulletpoint = '🔹'
        recovermsg += ('\n' + bulletpoint) + (await _interest(ctx))
        recovermsg += ('\n' + bulletpoint) + (await _otw(ctx))
        recovermsg += ('\n' + bulletpoint) + (await _waiting(ctx))
        if (not manual_timer):
            if raidtype == 'egg':
                action = _('hatch')
                type = _('egg')
            elif raidtype == 'raid':
                action = _('end')
                type = _('raid')
            recovermsg += _("\nI'm not sure when this {raidtype} will {action}, so please use **!timerset** if you can!").format(raidtype=type, action=action)
        else:
            recovermsg += ('\n' + bulletpoint) + (await print_raid_timer(channel))
        await _edit_party(channel, ctx.message.author)
        await channel.send(recovermsg)
        event_loop.create_task(expiry_check(channel))

@Meowth.command()
@checks.activechannel()
async def duplicate(ctx):
    """Une commande pour signaler un canal RAID en tant que doublon.

     Utilisation:!duplicate
     Fonctionne uniquement dans les canaux de raid. Lorsque trois utilisateurs signalent un canal en double,
     Miaou désactive le canal et le marque pour suppression."""
    channel = ctx.channel
    author = ctx.author
    guild = ctx.guild
    rc_d = guild_dict[guild.id]['raidchannel_dict'][channel.id]
    t_dict = rc_d['trainer_dict']
    can_manage = channel.permissions_for(author).manage_channels
    raidtype = _("event") if guild_dict[guild.id]['raidchannel_dict'][channel.id].get('meetup',False) else _("raid")
    if can_manage:
        dupecount = 2
        rc_d['duplicate'] = dupecount
    else:
        if author.id in t_dict:
            try:
                if t_dict[author.id]['dupereporter']:
                    dupeauthmsg = await channel.send(_("Meowth! You've already made a duplicate report for this {raidtype}!").format(raidtype=raidtype))
                    await asyncio.sleep(10)
                    await dupeauthmsg.delete()
                    return
                else:
                    t_dict[author.id]['dupereporter'] = True
            except KeyError:
                t_dict[author.id]['dupereporter'] = True
        else:
            t_dict[author.id] = {
                'status': {'maybe':0, 'coming':0, 'here':0, 'lobby':0},
                'dupereporter': True,
            }
        try:
            dupecount = rc_d['duplicate']
        except KeyError:
            dupecount = 0
            rc_d['duplicate'] = dupecount
    dupecount += 1
    rc_d['duplicate'] = dupecount
    if dupecount >= 3:
        rusure = await channel.send(_('Meowth! Are you sure you wish to remove this {raidtype}?').format(raidtype=raidtype))
        try:
            timeout = False
            res, reactuser = await ask(rusure, channel, author.id)
        except TypeError:
            timeout = True
        if not timeout:
            if res.emoji == '❎':
                await rusure.delete()
                confirmation = await channel.send(_('Duplicate Report cancelled.'))
                logger.info((('Duplicate Report - Cancelled - ' + channel.name) + ' - Report by ') + author.name)
                dupecount = 2
                guild_dict[guild.id]['raidchannel_dict'][channel.id]['duplicate'] = dupecount
                await asyncio.sleep(10)
                await confirmation.delete()
                return
            elif res.emoji == '✅':
                await rusure.delete()
                await channel.send(_('Duplicate Confirmed'))
                logger.info((('Duplicate Report - Channel Expired - ' + channel.name) + ' - Last Report by ') + author.name)
                raidmsg = await channel.get_message(rc_d['raidmessage'])
                reporter = raidmsg.mentions[0]
                if 'egg' in raidmsg.content:
                    egg_reports = guild_dict[guild.id]['trainers'][reporter.id]['egg_reports']
                    guild_dict[guild.id]['trainers'][reporter.id]['egg_reports'] = egg_reports - 1
                elif 'EX' in raidmsg.content:
                    ex_reports = guild_dict[guild.id]['trainers'][reporter.id]['ex_reports']
                    guild_dict[guild.id]['trainers'][reporter.id]['ex_reports'] = ex_reports - 1
                else:
                    raid_reports = guild_dict[guild.id]['trainers'][reporter.id]['raid_reports']
                    guild_dict[guild.id]['trainers'][reporter.id]['raid_reports'] = raid_reports - 1
                await expire_channel(channel)
                return
        else:
            await rusure.delete()
            confirmation = await channel.send(_('Duplicate Report Timed Out.'))
            logger.info((('Duplicate Report - Timeout - ' + channel.name) + ' - Report by ') + author.name)
            dupecount = 2
            guild_dict[guild.id]['raidchannel_dict'][channel.id]['duplicate'] = dupecount
            await asyncio.sleep(10)
            await confirmation.delete()
    else:
        rc_d['duplicate'] = dupecount
        confirmation = await channel.send(_('Duplicate report #{duplicate_report_count} received.').format(duplicate_report_count=str(dupecount)))
        logger.info((((('Duplicate Report - ' + channel.name) + ' - Report #') + str(dupecount)) + '- Report by ') + author.name)
        return

@Meowth.command()
async def counters(ctx, *, args = None):
    """Simulez une bataille de Raid avec Pokebattler.

     Utilisation:!counters [pokemon] [météo] [utilisateur]
     Voir! Aidez le temps pour des valeurs acceptables pour la météo.
     Si [utilisateur] est un identifiant d'utilisateur Pokebattler valide, Miaouss simulera le Raid avec la Pokebox de cet utilisateur.
     Utilise le boss actuel et la météo par défaut si disponible.
    """
    rgx = '[^a-zA-Z0-9]'
    channel = ctx.channel
    guild = channel.guild
    user = guild_dict[ctx.guild.id].get('trainers',{}).get(ctx.author.id,{}).get('pokebattlerid', None)
    if checks.check_raidchannel(ctx) and not checks.check_meetupchannel(ctx):
        if args:
            args_split = args.split()
            for arg in args_split:
                if arg.isdigit():
                    user = arg
                    break
        try:
            ctrsmessage = await channel.get_message(guild_dict[guild.id]['raidchannel_dict'][channel.id].get('ctrsmessage',None))
        except (discord.errors.NotFound, discord.errors.Forbidden, discord.errors.HTTPException):
            pass
        pkmn = guild_dict[guild.id]['raidchannel_dict'][channel.id].get('pokemon', None)
        if pkmn:
            if not user:
                try:
                    ctrsmessage = await channel.get_message(guild_dict[guild.id]['raidchannel_dict'][channel.id].get('ctrsmessage',None))
                    ctrsembed = ctrsmessage.embeds[0]
                    ctrsembed.remove_field(6)
                    ctrsembed.remove_field(6)
                    await channel.send(content=ctrsmessage.content,embed=ctrsembed)
                    return
                except (discord.errors.NotFound, discord.errors.Forbidden, discord.errors.HTTPException):
                    pass
            moveset = guild_dict[guild.id]['raidchannel_dict'][channel.id].get('moveset', 0)
            movesetstr = guild_dict[guild.id]['raidchannel_dict'][channel.id]['ctrs_dict'].get(moveset,{}).get('moveset',"Unknown Moveset")
            weather = guild_dict[guild.id]['raidchannel_dict'][channel.id].get('weather', None)
        else:
            pkmn = next((str(p) for p in get_raidlist() if not str(p).isdigit() and re.sub(rgx, '', str(p)) in re.sub(rgx, '', args.lower())), None)
            if not pkmn:
                await ctx.channel.send(_("Meowth! You're missing some details! Be sure to enter a pokemon that appears in raids! Usage: **!counters <pkmn> [weather] [user ID]**"))
                return
        if not weather:
            if args:
                weather_list = [_('none'), _('extreme'), _('clear'), _('sunny'), _('rainy'),
                                _('partlycloudy'), _('cloudy'), _('windy'), _('snow'), _('fog')]
                weather = next((w for w in weather_list if re.sub(rgx, '', w) in re.sub(rgx, '', args.lower())), None)
        return await _counters(ctx, pkmn, user, weather, movesetstr)
    if args:
        args_split = args.split()
        for arg in args_split:
            if arg.isdigit():
                user = arg
                break
        rgx = '[^a-zA-Z0-9]'
        pkmn = next((str(p) for p in get_raidlist() if not str(p).isdigit() and re.sub(rgx, '', str(p)) in re.sub(rgx, '', args.lower())), None)
        if not pkmn:
            pkmn = guild_dict[guild.id]['raidchannel_dict'].get(channel.id,{}).get('pokemon', None)
        weather_list = [_('none'), _('extreme'), _('clear'), _('sunny'), _('rainy'),
                        _('partlycloudy'), _('cloudy'), _('windy'), _('snow'), _('fog')]
        weather = next((w for w in weather_list if re.sub(rgx, '', w) in re.sub(rgx, '', args.lower())), None)
        if not weather:
            weather = guild_dict[guild.id]['raidchannel_dict'].get(channel.id,{}).get('weather', None)
    else:
        pkmn = guild_dict[guild.id]['raidchannel_dict'].get(channel.id,{}).get('pokemon', None)
        weather = guild_dict[guild.id]['raidchannel_dict'].get(channel.id,{}).get('weather', None)
    if not pkmn:
        await ctx.channel.send(_("Meowth! You're missing some details! Be sure to enter a pokemon that appears in raids! Usage: **!counters <pkmn> [weather] [user ID]**"))
        return
    await _counters(ctx, pkmn, user, weather, "Unknown Moveset")

async def _counters(ctx, pkmn, user = None, weather = None, movesetstr = "Unknown Moveset"):
    pokemon_index = pkmn_info['pokemon_list'].index(pkmn)
    pkmn_reference = pkmn_info_reference['pokemon_list'][pokemon_index]
    img_url = 'https://raw.githubusercontent.com/FoglyOgly/Meowth/discordpy-v1/images/pkmn/{0}_.png?cache=4'.format(str(get_number(pkmn)).zfill(3))
    level = get_level(pkmn) if get_level(pkmn).isdigit() else "5"
    url = "https://fight.pokebattler.com/raids/defenders/{pkmn}/levels/RAID_LEVEL_{level}/attackers/".format(pkmn=pkmn_reference.replace('-','_').upper(),level=level)
    if user:
        url += "users/{user}/".format(user=user)
        userstr = _("user #{user}'s").format(user=user)
    else:
        url += "levels/30/"
        userstr = _("Level 30")
    weather_list = [_('none'), _('extreme'), _('clear'), _('sunny'), _('rainy'),
                    _('partlycloudy'), _('cloudy'), _('windy'), _('snow'), _('fog')]
    match_list = ['NO_WEATHER','NO_WEATHER','CLEAR','CLEAR','RAINY',
                        'PARTLY_CLOUDY','OVERCAST','WINDY','SNOW','FOG']
    if not weather:
        index = 0
    else:
        index = weather_list.index(weather)
    weather = match_list[index]
    url += "strategies/CINEMATIC_ATTACK_WHEN_POSSIBLE/DEFENSE_RANDOM_MC?sort=OVERALL&"
    url += "weatherCondition={weather}&dodgeStrategy=DODGE_REACTION_TIME&aggregation=AVERAGE".format(weather=weather)
    async with ctx.typing():
        async with aiohttp.ClientSession() as sess:
            async with sess.get(url) as resp:
                data = await resp.json()

        title_url = url.replace('https://fight', 'https://www')
        colour = ctx.guild.me.colour
        hyperlink_icon = 'https://i.imgur.com/fn9E5nb.png'
        pbtlr_icon = 'https://www.pokebattler.com/favicon-32x32.png'
        data = data['attackers'][0]
        raid_cp = data['cp']
        atk_levels = '30'
        if movesetstr == "Unknown Moveset":
            ctrs = data['randomMove']['defenders'][-6:]
            est = data['randomMove']['total']['estimator']
        else:
            for moveset in data['byMove']:
                move1 = moveset['move1'][:-5].lower().title().replace('_', ' ')
                move2 = moveset['move2'].lower().title().replace('_', ' ')
                moveset_str = f'{move1} | {move2}'
                if moveset_str == movesetstr:
                    ctrs = moveset['defenders'][-6:]
                    est = moveset['total']['estimator']
                    break
            else:
                movesetstr = "Unknown Moveset"
                ctrs = data['randomMove']['defenders'][-6:]
                est = data['randomMove']['total']['estimator']
        def clean(txt):
            return txt.replace('_', ' ').title()
        title = _('{pkmn} | {weather} | {movesetstr}').format(pkmn=pkmn.title(),weather=weather_list[index].title(),movesetstr=movesetstr)
        stats_msg = _("**CP:** {raid_cp}\n").format(raid_cp=raid_cp)
        stats_msg += _("**Weather:** {weather}\n").format(weather=clean(weather))
        stats_msg += _("**Attacker Level:** {atk_levels}").format(atk_levels=atk_levels)
        ctrs_embed = discord.Embed(colour=colour)
        ctrs_embed.set_author(name=title,url=title_url,icon_url=hyperlink_icon)
        ctrs_embed.set_thumbnail(url=img_url)
        ctrs_embed.set_footer(text=_('Results courtesy of Pokebattler'), icon_url=pbtlr_icon)
        index = 1
        for ctr in reversed(ctrs):
            ctr_name = clean(ctr['pokemonId'])
            ctr_nick = clean(ctr.get('name',''))
            ctr_cp = ctr['cp']
            moveset = ctr['byMove'][-1]
            moves = _("{move1} | {move2}").format(move1=clean(moveset['move1'])[:-5], move2=clean(moveset['move2']))
            name = _("#{index} - {ctr_name}").format(index=index, ctr_name=(ctr_nick or ctr_name))
            cpstr = _("CP")
            ctrs_embed.add_field(name=name,value=f"{cpstr}: {ctr_cp}\n{moves}")
            index += 1
        ctrs_embed.add_field(name=_("Results with {userstr} attackers").format(userstr=userstr), value=_("[See your personalized results!](https://www.pokebattler.com/raids/{pkmn})").format(pkmn=pkmn.replace('-','_').upper()))
        if user:
            ctrs_embed.add_field(name=_("Pokebattler Estimator:"), value=_("Difficulty rating: {est}").format(est=est))
            await ctx.author.send(embed=ctrs_embed)
            return
        await ctx.channel.send(embed=ctrs_embed)

async def _get_generic_counters(guild, pkmn, weather=None):
    emoji_dict = {0: '0\u20e3', 1: '1\u20e3', 2: '2\u20e3', 3: '3\u20e3', 4: '4\u20e3', 5: '5\u20e3', 6: '6\u20e3', 7: '7\u20e3', 8: '8\u20e3', 9: '9\u20e3', 10: '10\u20e3'}
    ctrs_dict = {}
    ctrs_index = 0
    ctrs_dict[ctrs_index] = {}
    ctrs_dict[ctrs_index]['moveset'] = "Unknown Moveset"
    ctrs_dict[ctrs_index]['emoji'] = '0\u20e3'
    img_url = 'https://raw.githubusercontent.com/FoglyOgly/Meowth/discordpy-v1/images/pkmn/{0}_.png?cache=4'.format(str(get_number(pkmn)).zfill(3))
    level = get_level(pkmn) if get_level(pkmn).isdigit() else "5"
    pokemon_index = pkmn_info['pokemon_list'].index(pkmn)
    pkmn_reference = pkmn_info_reference['pokemon_list'][pokemon_index]
    url = "https://fight.pokebattler.com/raids/defenders/{pkmn}/levels/RAID_LEVEL_{level}/attackers/".format(pkmn=pkmn_reference.replace('-','_').upper(),level=level)
    url += "levels/30/"
    weather_list = [_('none'), _('extreme'), _('clear'), _('sunny'), _('rainy'),
                    _('partlycloudy'), _('cloudy'), _('windy'), _('snow'), _('fog')]
    match_list = ['NO_WEATHER','NO_WEATHER','CLEAR','CLEAR','RAINY',
                        'PARTLY_CLOUDY','OVERCAST','WINDY','SNOW','FOG']
    if not weather:
        index = 0
    else:
        index = weather_list.index(weather)
    weather = match_list[index]
    url += "strategies/CINEMATIC_ATTACK_WHEN_POSSIBLE/DEFENSE_RANDOM_MC?sort=OVERALL&"
    url += "weatherCondition={weather}&dodgeStrategy=DODGE_REACTION_TIME&aggregation=AVERAGE".format(weather=weather)
    title_url = url.replace('https://fight', 'https://www')
    hyperlink_icon = 'https://i.imgur.com/fn9E5nb.png'
    pbtlr_icon = 'https://www.pokebattler.com/favicon-32x32.png'
    async with aiohttp.ClientSession() as sess:
        async with sess.get(url) as resp:
            data = await resp.json()
    data = data['attackers'][0]
    raid_cp = data['cp']
    atk_levels = '30'
    ctrs = data['randomMove']['defenders'][-6:]
    def clean(txt):
        return txt.replace('_', ' ').title()
    title = _('{pkmn} | {weather} | Unknown Moveset').format(pkmn=pkmn.title(),weather=weather_list[index].title())
    stats_msg = _("**CP:** {raid_cp}\n").format(raid_cp=raid_cp)
    stats_msg += _("**Weather:** {weather}\n").format(weather=clean(weather))
    stats_msg += _("**Attacker Level:** {atk_levels}").format(atk_levels=atk_levels)
    ctrs_embed = discord.Embed(colour=guild.me.colour)
    ctrs_embed.set_author(name=title,url=title_url,icon_url=hyperlink_icon)
    ctrs_embed.set_thumbnail(url=img_url)
    ctrs_embed.set_footer(text=_('Results courtesy of Pokebattler'), icon_url=pbtlr_icon)
    ctrindex = 1
    for ctr in reversed(ctrs):
        ctr_name = clean(ctr['pokemonId'])
        moveset = ctr['byMove'][-1]
        moves = _("{move1} | {move2}").format(move1=clean(moveset['move1'])[:-5], move2=clean(moveset['move2']))
        name = _("#{index} - {ctr_name}").format(index=ctrindex, ctr_name=ctr_name)
        ctrs_embed.add_field(name=name,value=moves)
        ctrindex += 1
    ctrs_dict[ctrs_index]['embed'] = ctrs_embed
    for moveset in data['byMove']:
        ctrs_index += 1
        move1 = moveset['move1'][:-5].lower().title().replace('_', ' ')
        move2 = moveset['move2'].lower().title().replace('_', ' ')
        movesetstr = f'{move1} | {move2}'
        ctrs = moveset['defenders'][-6:]
        title = _('{pkmn} | {weather} | {movesetstr}').format(pkmn=pkmn.title(), weather=weather_list[index].title(), movesetstr=movesetstr)
        ctrs_embed = discord.Embed(colour=guild.me.colour)
        ctrs_embed.set_author(name=title,url=title_url,icon_url=hyperlink_icon)
        ctrs_embed.set_thumbnail(url=img_url)
        ctrs_embed.set_footer(text=_('Results courtesy of Pokebattler'), icon_url=pbtlr_icon)
        ctrindex = 1
        for ctr in reversed(ctrs):
            ctr_name = clean(ctr['pokemonId'])
            moveset = ctr['byMove'][-1]
            moves = _("{move1} | {move2}").format(move1=clean(moveset['move1'])[:-5], move2=clean(moveset['move2']))
            name = _("#{index} - {ctr_name}").format(index=ctrindex, ctr_name=ctr_name)
            ctrs_embed.add_field(name=name,value=moves)
            ctrindex += 1
        ctrs_dict[ctrs_index] = {'moveset': movesetstr, 'embed': ctrs_embed, 'emoji': emoji_dict[ctrs_index]}
    moveset_list = []
    for moveset in ctrs_dict:
        moveset_list.append(f"{ctrs_dict[moveset]['emoji']}: {ctrs_dict[moveset]['moveset']}\n")
    for moveset in ctrs_dict:
        ctrs_split = int(round(len(moveset_list)/2+0.1))
        ctrs_dict[moveset]['embed'].add_field(name=_("**Possible Movesets:**"), value=f"{''.join(moveset_list[:ctrs_split])}", inline=True)
        ctrs_dict[moveset]['embed'].add_field(name="\u200b", value=f"{''.join(moveset_list[ctrs_split:])}",inline=True)
        ctrs_dict[moveset]['embed'].add_field(name=_("Results with Level 30 attackers"), value=_("[See your personalized results!](https://www.pokebattler.com/raids/{pkmn})").format(pkmn=pkmn.replace('-','_').upper()),inline=False)

    return ctrs_dict

@Meowth.command()
@checks.activechannel()
async def weather(ctx, *, weather):
    """Définit la météo pour le raid.
    Utilisation: !weather <weather>
    Uniquement utilisable dans les canaux raid.
    Acceptable options: aucun, tempête, dégagé, ensoleillé, pluvieux, couvert, nuageux, venteux, neige, brouillard"""
    weather_list = [_('none'), _('extreme'), _('clear'), _('sunny'), _('rainy'),
                    _('partlycloudy'), _('cloudy'), _('windy'), _('snow'), _('fog')]
    if weather.lower() not in weather_list:
        return await ctx.channel.send(_("Meowth! Enter one of the following weather conditions: {}").format(", ".join(weather_list)))
    else:
        guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['weather'] = weather.lower()
        pkmn = guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id].get('pokemon', None)
        if pkmn:
            if str(get_level(pkmn)) in guild_dict[ctx.guild.id]['configure_dict']['counters']['auto_levels']:
                ctrs_dict = await _get_generic_counters(ctx.guild,pkmn,weather.lower())
                try:
                    ctrsmessage = await ctx.channel.get_message(guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['ctrsmessage'])
                    moveset = guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['moveset']
                    newembed = ctrs_dict[moveset]['embed']
                    await ctrsmessage.edit(embed=newembed)
                except (discord.errors.NotFound, discord.errors.Forbidden, discord.errors.HTTPException):
                    pass
                guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['ctrs_dict'] = ctrs_dict
        return await ctx.channel.send(_("Meowth! Weather set to {}!").format(weather.lower()))

"""
Status Management
"""

@Meowth.command(aliases=['i', 'maybe'])
@checks.activechannel()
async def interested(ctx, *, teamcounts: str=None):
    """Indiquez que vous êtes intéressé par le raid.

     Utilisation:!interest [nb total] [nb par équipe]
     Fonctionne uniquement dans les chaînes de raid. Si count est omis, suppose que vous êtes un groupe de 1.
     Sinon, cette commande s'attend à ce qu'au moins un mot de votre message soit un nombre,
     et supposera que vous êtes un groupe avec autant de gens.

     La participation est également facultative. Le format est #m #v #i #u pour informer les équipes de votre groupe."""
    trainer_dict = guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['trainer_dict']
    entered_interest = trainer_dict.get(ctx.author.id, {}).get('interest', [])
    egglevel = guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['egglevel']
    if (not teamcounts):
        if ctx.author.id in trainer_dict:
            bluecount = str(trainer_dict[ctx.author.id]['party']['mystic']) + 'm '
            redcount = str(trainer_dict[ctx.author.id]['party']['valor']) + 'v '
            yellowcount = str(trainer_dict[ctx.author.id]['party']['instinct']) + 'i '
            unknowncount = str(trainer_dict[ctx.author.id]['party']['unknown']) + 'u '
            teamcounts = ((((str(trainer_dict[ctx.author.id]['count']) + ' ') + bluecount) + redcount) + yellowcount) + unknowncount
        else:
            teamcounts = '1'
    rgx = '[^a-zA-Z0-9]'
    if teamcounts:
        if "all" in teamcounts.lower():
            # What a hack
            teamcounts = "{teamcounts} {bosslist}".format(teamcounts=teamcounts,bosslist=" ".join([get_name(s).title() for s in raid_info['raid_eggs'][egglevel]['pokemon']]))
            teamcounts = teamcounts.lower().replace("all","").strip()
        pkmn_match = next((p for p in pkmn_info['pokemon_list'] if re.sub(rgx, '', p) in re.sub(rgx, '', teamcounts.lower())), None)
    if pkmn_match and guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['type'] == "egg":
        entered_interest = []
        for word in re.split(' |,', teamcounts.lower()):
            if word.lower() in pkmn_info['pokemon_list']:
                if get_number(word.lower()) in raid_info['raid_eggs'][egglevel]['pokemon']:
                    if word.lower() not in entered_interest:
                        entered_interest.append(word.lower())
                else:
                    await ctx.message.channel.send(_("{word} doesn't appear in level {egglevel} raids! Please try again.").format(word=word.title(),egglevel=egglevel))
                    return
                teamcounts = teamcounts.lower().replace(word.lower(),"").replace(",","").strip()
    elif not pkmn_match and guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['type'] == 'egg':
        entered_interest = [get_name(p) for p in raid_info['raid_eggs'][egglevel]['pokemon']]
    if teamcounts and teamcounts.split()[0].isdigit():
        total = int(teamcounts.split()[0])
    elif (ctx.author.id in trainer_dict) and (sum(trainer_dict[ctx.author.id]['status'].values()) > 0):
        total = trainer_dict[ctx.author.id]['count']
    elif teamcounts:
        total = re.sub('[^0-9 ]','', teamcounts)
        total = sum([int(x) for x in total.split()])
    else:
        total = 1
    result = await _party_status(ctx, total, teamcounts)
    if isinstance(result, __builtins__.list):
        count = result[0]
        partylist = result[1]
        await _maybe(ctx.channel, ctx.author, count, partylist, entered_interest)

async def _maybe(channel, author, count, party, entered_interest=None):
    trainer_dict = guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['trainer_dict']
    allblue = 0
    allred = 0
    allyellow = 0
    allunknown = 0
    if (not party):
        for role in author.roles:
            if role.name.lower() == 'mystic':
                allblue = count
                break
            elif role.name.lower() == 'valor':
                allred = count
                break
            elif role.name.lower() == 'instinct':
                allyellow = count
                break
        else:
            allunknown = count
        party = {'mystic':allblue, 'valor':allred, 'instinct':allyellow, 'unknown':allunknown}
    if count == 1:
        team_emoji = max(party, key=lambda key: party[key])
        if team_emoji == "unknown":
            team_emoji = "❔"
        else:
            team_emoji = parse_emoji(channel.guild, config['team_dict'][team_emoji])
        await channel.send(_('Meowth! {member} is interested! {emoji}: 1').format(member=author.mention, emoji=team_emoji))
    else:
        msg = _('Meowth! {member} is interested with a total of {trainer_count} trainers!').format(member=author.mention, trainer_count=count)
        await channel.send('{msg} {blue_emoji}: {mystic} | {red_emoji}: {valor} | {yellow_emoji}: {instinct} | ❔: {unknown}'.format(msg=msg, blue_emoji=parse_emoji(channel.guild, config['team_dict']['mystic']), mystic=party['mystic'], red_emoji=parse_emoji(channel.guild, config['team_dict']['valor']), valor=party['valor'], instinct=party['instinct'], yellow_emoji=parse_emoji(channel.guild, config['team_dict']['instinct']), unknown=party['unknown']))
    if author.id not in guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['trainer_dict']:
        trainer_dict[author.id] = {

        }
    trainer_dict[author.id]['status'] = {'maybe':count, 'coming':0, 'here':0, 'lobby':0}
    if entered_interest:
        trainer_dict[author.id]['interest'] = entered_interest
    trainer_dict[author.id]['count'] = count
    trainer_dict[author.id]['party'] = party
    await _edit_party(channel, author)
    guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['trainer_dict'] = trainer_dict

@Meowth.command(aliases=['c'])
@checks.activechannel()
async def coming(ctx, *, teamcounts: str=None):
    """Indiquez que vous êtes sur le chemin d'un raid.

     Utilisation:!coming [nb total] [nb par équipe]
     Fonctionne uniquement dans les chaînes de raid. Si count est omis, vérifie s'il y a déjà eu!
     commande et prend le compte de cela. S'il n'en trouve aucun, suppose que vous êtes un groupe
     de 1.
     Sinon, cette commande s'attend à ce qu'au moins un mot de votre message soit un nombre,
     et supposera que vous êtes un groupe avec autant de gens.

     La participation est également facultative. Le format est #m #v #i #u pour informer les équipes de votre groupe."""
    trainer_dict = guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['trainer_dict']
    rgx = '[^a-zA-Z0-9]'
    entered_interest = trainer_dict.get(ctx.author.id, {}).get('interest', [])
    egglevel = guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['egglevel']
    pkmn_match = None
    if teamcounts:
        if "all" in teamcounts.lower():
            teamcounts = "{teamcounts} {bosslist}".format(teamcounts=teamcounts,bosslist=" ".join([get_name(s).title() for s in raid_info['raid_eggs'][egglevel]['pokemon']]))
            teamcounts = teamcounts.lower().replace("all","").strip()
        pkmn_match = next((p for p in pkmn_info['pokemon_list'] if re.sub(rgx, '', p) in re.sub(rgx, '', teamcounts.lower())), None)
    if pkmn_match and guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['type'] == "egg":
        entered_interest = []
        unmatched_mons = False
        for word in re.split(' |,', teamcounts.lower()):
            if word.lower() in pkmn_info['pokemon_list']:
                if word.lower() not in entered_interest:
                    entered_interest.append(word.lower())
                    if not get_number(word.lower()) in raid_info['raid_eggs'][egglevel]['pokemon']:
                        await ctx.message.channel.send(_("{word} doesn't appear in level {egglevel} raids!").format(word=word.title(),egglevel=egglevel))
                        unmatched_mons = True
                teamcounts = teamcounts.lower().replace(word.lower(),"").replace(",","").strip()
        if unmatched_mons:
            await ctx.message.channel.send(_("Invalid Pokemon detected. Please check the pinned message for the list of possible bosses and try again."))
            return
    elif not pkmn_match and guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['type'] == 'egg':
        entered_interest = [get_name(p) for p in raid_info['raid_eggs'][egglevel]['pokemon']]
    trainer_dict = guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['trainer_dict']
    if (not teamcounts):
        if ctx.author.id in trainer_dict:
            bluecount = str(trainer_dict[ctx.author.id]['party']['mystic']) + 'm '
            redcount = str(trainer_dict[ctx.author.id]['party']['valor']) + 'v '
            yellowcount = str(trainer_dict[ctx.author.id]['party']['instinct']) + 'i '
            unknowncount = str(trainer_dict[ctx.author.id]['party']['unknown']) + 'u '
            teamcounts = ((((str(trainer_dict[ctx.author.id]['count']) + ' ') + bluecount) + redcount) + yellowcount) + unknowncount
        else:
            teamcounts = '1'

    if teamcounts and teamcounts.split()[0].isdigit():
        total = int(teamcounts.split()[0])
    elif (ctx.author.id in trainer_dict) and (sum(trainer_dict[ctx.author.id]['status'].values()) > 0):
        total = trainer_dict[ctx.author.id]['count']
    elif teamcounts:
        total = re.sub('[^0-9 ]','', teamcounts)
        total = sum([int(x) for x in total.split()])
    else:
        total = 1
    result = await _party_status(ctx, total, teamcounts)
    if isinstance(result, __builtins__.list):
        count = result[0]
        partylist = result[1]
        await _coming(ctx.channel, ctx.author, count, partylist, entered_interest)

async def _coming(channel, author, count, party, entered_interest=None):
    allblue = 0
    allred = 0
    allyellow = 0
    allunknown = 0
    trainer_dict = guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['trainer_dict']
    if (not party):
        for role in author.roles:
            if role.name.lower() == 'mystic':
                allblue = count
                break
            elif role.name.lower() == 'valor':
                allred = count
                break
            elif role.name.lower() == 'instinct':
                allyellow = count
                break
        else:
            allunknown = count
        party = {'mystic':allblue, 'valor':allred, 'instinct':allyellow, 'unknown':allunknown}
    if count == 1:
        team_emoji = max(party, key=lambda key: party[key])
        if team_emoji == "unknown":
            team_emoji = "❔"
        else:
            team_emoji = parse_emoji(channel.guild, config['team_dict'][team_emoji])
        await channel.send(_('Meowth! {member} is on the way! {emoji}: 1').format(member=author.mention, emoji=team_emoji))
    else:
        msg = _('Meowth! {member} is on the way with a total of {trainer_count} trainers!').format(member=author.mention, trainer_count=count)
        await channel.send('{msg} {blue_emoji}: {mystic} | {red_emoji}: {valor} | {yellow_emoji}: {instinct} | ❔: {unknown}'.format(msg=msg, blue_emoji=parse_emoji(channel.guild, config['team_dict']['mystic']), mystic=party['mystic'], red_emoji=parse_emoji(channel.guild, config['team_dict']['valor']), valor=party['valor'], instinct=party['instinct'], yellow_emoji=parse_emoji(channel.guild, config['team_dict']['instinct']), unknown=party['unknown']))
    if author.id not in trainer_dict:
        trainer_dict[author.id] = {

        }
    trainer_dict[author.id]['status'] = {'maybe':0, 'coming':count, 'here':0, 'lobby':0}
    trainer_dict[author.id]['count'] = count
    trainer_dict[author.id]['party'] = party
    if entered_interest:
        trainer_dict[author.id]['interest'] = entered_interest
    await _edit_party(channel, author)
    guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['trainer_dict'] = trainer_dict

@Meowth.command(aliases=['h'])
@checks.activechannel()
async def here(ctx, *, teamcounts: str=None):
    """Indiquez que vous êtes arrivé au raid.

     Utilisation:!here [nb total] [nb par équipe]
     Fonctionne uniquement dans les chaînes de raid. Si le message est omis, et
     vous avez déjà émis! à venir, puis préserve le compte
     de cette commande. Sinon, suppose que vous êtes un groupe de 1.
     Sinon, cette commande s'attend à ce qu'au moins un mot de votre message soit un nombre,
     et supposera que vous êtes un groupe avec autant de gens.

     La participation est également facultative. Le format est #m #v #i #u pour informer les équipes de votre groupe."""
    trainer_dict = guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['trainer_dict']
    rgx = '[^a-zA-Z0-9]'
    entered_interest = trainer_dict.get(ctx.author.id, {}).get('interest', [])
    egglevel = guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['egglevel']
    pkmn_match = None
    if teamcounts:
        if "all" in teamcounts.lower():
            teamcounts = "{teamcounts} {bosslist}".format(teamcounts=teamcounts,bosslist=" ".join([get_name(s).title() for s in raid_info['raid_eggs'][egglevel]['pokemon']]))
            teamcounts = teamcounts.lower().replace("all","").strip()
        pkmn_match = next((p for p in pkmn_info['pokemon_list'] if re.sub(rgx, '', p) in re.sub(rgx, '', teamcounts.lower())), None)
    if pkmn_match and guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['type'] == "egg":
        entered_interest = []
        for word in re.split(' |,', teamcounts.lower()):
            if word.lower() in pkmn_info['pokemon_list']:
                if get_number(word.lower()) in raid_info['raid_eggs'][egglevel]['pokemon']:
                    if word.lower() not in entered_interest:
                        entered_interest.append(word.lower())
                else:
                    await ctx.message.channel.send(_("{word} doesn't appear in level {egglevel} raids! Please try again.").format(word=word.title(),egglevel=egglevel))
                    return
                teamcounts = teamcounts.lower().replace(word.lower(),"").replace(",","").strip()
    elif not pkmn_match and guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['type'] == 'egg':
        entered_interest = [get_name(p) for p in raid_info['raid_eggs'][egglevel]['pokemon']]

    if (not teamcounts):
        if ctx.author.id in trainer_dict:
            bluecount = str(trainer_dict[ctx.author.id]['party']['mystic']) + 'm '
            redcount = str(trainer_dict[ctx.author.id]['party']['valor']) + 'v '
            yellowcount = str(trainer_dict[ctx.author.id]['party']['instinct']) + 'i '
            unknowncount = str(trainer_dict[ctx.author.id]['party']['unknown']) + 'u '
            teamcounts = ((((str(trainer_dict[ctx.author.id]['count']) + ' ') + bluecount) + redcount) + yellowcount) + unknowncount
        else:
            teamcounts = '1'
    if teamcounts and teamcounts.split()[0].isdigit():
        total = int(teamcounts.split()[0])
    elif (ctx.author.id in trainer_dict) and (sum(trainer_dict[ctx.author.id]['status'].values()) > 0):
        total = trainer_dict[ctx.author.id]['count']
    elif teamcounts:
        total = re.sub('[^0-9 ]','', teamcounts)
        total = sum([int(x) for x in total.split()])
    else:
        total = 1
    result = await _party_status(ctx, total, teamcounts)
    if isinstance(result, __builtins__.list):
        count = result[0]
        partylist = result[1]
        await _here(ctx.channel, ctx.author, count, partylist, entered_interest)

async def _here(channel, author, count, party, entered_interest=None):
    lobbymsg = ''
    allblue = 0
    allred = 0
    allyellow = 0
    allunknown = 0
    trainer_dict = guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['trainer_dict']
    raidtype = _("event") if guild_dict[channel.guild.id]['raidchannel_dict'][channel.id].get('meetup',False) else _("raid")
    try:
        if guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['lobby']:
            lobbymsg += _('\nThere is a group already in the lobby! Use **!lobby** to join them or **!backout** to request a backout! Otherwise, you may have to wait for the next group!')
    except KeyError:
        pass
    if (not party):
        for role in author.roles:
            if role.name.lower() == 'mystic':
                allblue = count
                break
            elif role.name.lower() == 'valor':
                allred = count
                break
            elif role.name.lower() == 'instinct':
                allyellow = count
                break
        else:
            allunknown = count
        party = {'mystic':allblue, 'valor':allred, 'instinct':allyellow, 'unknown':allunknown}
    if count == 1:
        team_emoji = max(party, key=lambda key: party[key])
        if team_emoji == "unknown":
            team_emoji = "❔"
        else:
            team_emoji = parse_emoji(channel.guild, config['team_dict'][team_emoji])
        msg = _('Meowth! {member} is at the {raidtype}! {emoji}: 1').format(member=author.mention, emoji=team_emoji, raidtype=raidtype)
        await channel.send(msg + lobbymsg)
    else:
        msg = _('Meowth! {member} is at the {raidtype} with a total of {trainer_count} trainers!').format(member=author.mention, trainer_count=count, raidtype=raidtype)
        msg += ' {blue_emoji}: {mystic} | {red_emoji}: {valor} | {yellow_emoji}: {instinct} | ❔: {unknown}'.format(blue_emoji=parse_emoji(channel.guild, config['team_dict']['mystic']), mystic=party['mystic'], red_emoji=parse_emoji(channel.guild, config['team_dict']['valor']), valor=party['valor'], instinct=party['instinct'], yellow_emoji=parse_emoji(channel.guild, config['team_dict']['instinct']), unknown=party['unknown'])
        await channel.send(msg + lobbymsg)
    if author.id not in trainer_dict:
        trainer_dict[author.id] = {

        }
    trainer_dict[author.id]['status'] = {'maybe':0, 'coming':0, 'here':count, 'lobby':0}
    trainer_dict[author.id]['count'] = count
    trainer_dict[author.id]['party'] = party
    if entered_interest:
        trainer_dict[author.id]['interest'] = entered_interest
    await _edit_party(channel, author)
    guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['trainer_dict'] = trainer_dict

async def _party_status(ctx, total, teamcounts):
    channel = ctx.channel
    author = ctx.author
    for role in ctx.author.roles:
        if role.name.lower() == 'mystic':
            my_team = 'mystic'
            break
        elif role.name.lower() == 'valor':
            my_team = 'valor'
            break
        elif role.name.lower() == 'instinct':
            my_team = 'instinct'
            break
    else:
        my_team = 'unknown'
    if not teamcounts:
        teamcounts = "1"
    teamcounts = teamcounts.lower().split()
    if total and teamcounts[0].isdigit():
        del teamcounts[0]
    mystic = ['mystic', 0]
    instinct = ['instinct', 0]
    valor = ['valor', 0]
    unknown = ['unknown', 0]
    team_aliases = {
        'mystic': mystic,
        'blue': mystic,
        'm': mystic,
        'b': mystic,
        'instinct': instinct,
        'yellow': instinct,
        'i': instinct,
        'y': instinct,
        'valor': valor,
        'red': valor,
        'v': valor,
        'r': valor,
        'unknown': unknown,
        'grey': unknown,
        'gray': unknown,
        'u': unknown,
        'g': unknown,
    }
    regx = re.compile('([a-zA-Z]+)([0-9]+)|([0-9]+)([a-zA-Z]+)')
    for count in teamcounts:
        if count.isdigit():
            if total:
                return await channel.send(_('Only one non-team count can be accepted.'))
            else:
                total = int(count)
        else:
            match = regx.match(count)
            if match:
                match = regx.match(count).groups()
                str_match = match[0] or match[3]
                int_match = match[1] or match[2]
                if str_match in team_aliases.keys():
                    if int_match:
                        if team_aliases[str_match][1]:
                            return await channel.send(_('Only one count per team accepted.'))
                        else:
                            team_aliases[str_match][1] = int(int_match)
                            continue
            return await channel.send(_('Invalid format, please check and try again.'))
    team_total = ((mystic[1] + instinct[1]) + valor[1]) + unknown[1]
    if total:
        if int(team_total) > int(total):
            a = _('Team counts are higher than the total, double check your counts and try again. You entered **')
            b = _('** total and **')
            c = _('** in your party.')
            return await channel.send(((( a + str(total)) + b) + str(team_total)) + c)
        if int(total) > int(team_total):
            if team_aliases[my_team][1]:
                if unknown[1]:
                    return await channel.send(_('Meowth! Something is not adding up! Try making sure your total matches what each team adds up to!'))
                unknown[1] = total - team_total
            else:
                team_aliases[my_team][1] = total - team_total
    partylist = {'mystic':mystic[1], 'valor':valor[1], 'instinct':instinct[1], 'unknown':unknown[1]}
    result = [total, partylist]
    return result

async def _edit_party(channel, author=None):
    egglevel = guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['egglevel']
    if egglevel != "0":
        boss_dict = {}
        boss_list = []
        display_list = []
        for p in raid_info['raid_eggs'][egglevel]['pokemon']:
            p_name = get_name(p).title()
            boss_list.append(p_name.lower())
            p_type = get_type(channel.guild,p)
            boss_dict[p_name.lower()] = {"type": "{}".format(''.join(p_type)), "total": 0}
    channel_dict = {"mystic":0,"valor":0,"instinct":0,"unknown":0,"maybe":0,"coming":0,"here":0,"total":0,"boss":0}
    team_list = ["mystic","valor","instinct","unknown"]
    status_list = ["maybe","coming","here"]
    trainer_dict = copy.deepcopy(guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['trainer_dict'])
    for trainer in trainer_dict:
        for team in team_list:
            channel_dict[team] += int(trainer_dict[trainer]['party'][team])
        for status in status_list:
            if trainer_dict[trainer]['status'][status]:
                channel_dict[status] += int(trainer_dict[trainer]['count'])
        if egglevel != "0":
            for boss in boss_list:
                if boss.lower() in trainer_dict[trainer].get('interest',[]):
                    boss_dict[boss]['total'] += int(trainer_dict[trainer]['count'])
                    channel_dict["boss"] += int(trainer_dict[trainer]['count'])
    if egglevel != "0":
        for boss in boss_list:
            if boss_dict[boss]['total'] > 0:
                bossstr = "{name} ({number}) {types} : **{count}**".format(name=boss.title(),number=get_number(boss),types=boss_dict[boss]['type'],count=boss_dict[boss]['total'])
                display_list.append(bossstr)
            elif boss_dict[boss]['total'] == 0:
                bossstr = "{name} ({number}) {types}".format(name=boss.title(),number=get_number(boss),types=boss_dict[boss]['type'])
                display_list.append(bossstr)
    channel_dict["total"] = channel_dict["maybe"] + channel_dict["coming"] + channel_dict["here"]
    reportchannel = Meowth.get_channel(guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['reportcity'])
    try:
        reportmsg = await reportchannel.get_message(guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['raidreport'])
    except:
        pass
    try:
        raidmsg = await channel.get_message(guild_dict[channel.guild.id]['raidchannel_dict'][channel.id]['raidmessage'])
    except:
        async for message in channel.history(limit=500, reverse=True):
            if author and message.author.id == channel.guild.me.id:
                c = _('Coordinate here')
                if c in message.content:
                    reportchannel = message.raw_channel_mentions[0]
                    raidmsg = message
                    break
    reportembed = raidmsg.embeds[0]
    newembed = discord.Embed(title=reportembed.title, url=reportembed.url, colour=channel.guild.me.colour)
    for field in reportembed.fields:
        t = _('team')
        s = _('status')
        if (t not in field.name.lower()) and (s not in field.name.lower()):
            newembed.add_field(name=field.name, value=field.value, inline=field.inline)
    if egglevel != "0" and not guild_dict[channel.guild.id].get('raidchannel_dict',{}).get(channel.id,{}).get('meetup',{}):
        if len(boss_list) > 1:
            newembed.set_field_at(0, name=_("**Boss Interest:**") if channel_dict["boss"] > 0 else _("**Possible Bosses:**"), value=_('{bosslist1}').format(bosslist1='\n'.join(display_list[::2])), inline=True)
            newembed.set_field_at(1, name='\u200b', value=_('{bosslist2}').format(bosslist2='\n'.join(display_list[1::2])), inline=True)
        else:
            newembed.set_field_at(0, name=_("**Boss Interest:**") if channel_dict["boss"] > 0 else _("**Possible Bosses:**"), value=_('{bosslist}').format(bosslist=''.join(display_list)), inline=True)
            newembed.set_field_at(1, name='\u200b', value='\u200b', inline=True)
    if channel_dict["total"] > 0:
        newembed.add_field(name=_('**Status List**'), value=_('Maybe: **{channelmaybe}** | Coming: **{channelcoming}** | Here: **{channelhere}**').format(channelmaybe=channel_dict["maybe"], channelcoming=channel_dict["coming"], channelhere=channel_dict["here"]), inline=True)
        newembed.add_field(name=_('**Team List**'), value='{blue_emoji}: **{channelblue}** | {red_emoji}: **{channelred}** | {yellow_emoji}: **{channelyellow}** | ❔: **{channelunknown}**'.format(blue_emoji=parse_emoji(channel.guild, config['team_dict']['mystic']), channelblue=channel_dict["mystic"], red_emoji=parse_emoji(channel.guild, config['team_dict']['valor']), channelred=channel_dict["valor"], yellow_emoji=parse_emoji(channel.guild, config['team_dict']['instinct']), channelyellow=channel_dict["instinct"], channelunknown=channel_dict["unknown"]), inline=True)
    newembed.set_footer(text=reportembed.footer.text, icon_url=reportembed.footer.icon_url)
    newembed.set_thumbnail(url=reportembed.thumbnail.url)
    try:
        await reportmsg.edit(embed=newembed)
    except:
        pass
    try:
        await raidmsg.edit(embed=newembed)
    except:
        pass

@Meowth.command(aliases=['l'])
@checks.activeraidchannel()
async def lobby(ctx, *, count: str=None):
    """Indiquez que vous entrez dans le lobby du raid.

     Utilisation:!lobby [message]
     Fonctionne uniquement dans les canaux de raid. Si le message est omis, et
     vous avez déjà émis! à venir, puis préserve le compte
     de cette commande. Sinon, suppose que vous êtes un groupe de 1.
     Sinon, cette commande s'attend à ce qu'au moins un mot de votre message soit un nombre,
     et supposera que vous êtes un groupe avec autant de gens."""
    try:
        if guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['type'] == 'egg':
            if guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['pokemon'] == '':
                await ctx.channel.send(_("Meowth! Please wait until the raid egg has hatched before announcing you're coming or present."))
                return
    except:
        pass
    trainer_dict = guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['trainer_dict']
    if count:
        if count.isdigit():
            count = int(count)
        else:
            await ctx.channel.send(_("Meowth! I can't understand how many are in your group. Just say **!here** if you're by yourself, or **!coming 5** for example if there are 5 in your group."))
            return
    elif (ctx.author.id in trainer_dict) and (sum(trainer_dict[ctx.author.id]['status'].values()) > 0):
        count = trainer_dict[ctx.author.id]['count']
    else:
        count = 1
    await _lobby(ctx.message, count)

async def _lobby(message, count):
    if 'lobby' not in guild_dict[message.guild.id]['raidchannel_dict'][message.channel.id]:
        await message.channel.send(_('Meowth! There is no group in the lobby for you to join! Use **!starting** if the group waiting at the raid is entering the lobby!'))
        return
    trainer_dict = guild_dict[message.guild.id]['raidchannel_dict'][message.channel.id]['trainer_dict']
    if count == 1:
        await message.channel.send(_('Meowth! {member} is entering the lobby!').format(member=message.author.mention))
    else:
        await message.channel.send(_('Meowth! {member} is entering the lobby with a total of {trainer_count} trainers!').format(member=message.author.mention, trainer_count=count))
    if message.author.id not in trainer_dict:
        trainer_dict[message.author.id] = {

        }
    trainer_dict[message.author.id]['status'] = {'maybe':0, 'coming':0, 'here':0, 'lobby':count}
    trainer_dict[message.author.id]['count'] = count
    guild_dict[message.guild.id]['raidchannel_dict'][message.channel.id]['trainer_dict'] = trainer_dict

@Meowth.command(aliases=['x'])
@checks.raidchannel()
async def cancel(ctx):
    """Indiquez que vous n'êtes plus intéressé par un raid.

     Utilisation:!cancel
     Fonctionne uniquement dans les canaux de raid. Supprime vous et votre fête
     de la liste des formateurs qui sont "otw" ou "here"."""
    await _cancel(ctx.channel, ctx.author)

async def _cancel(channel, author):
    guild = channel.guild
    raidtype = _("event") if guild_dict[guild.id]['raidchannel_dict'][channel.id].get('meetup',False) else _("raid")
    try:
        t_dict = guild_dict[guild.id]['raidchannel_dict'][channel.id]['trainer_dict'][author.id]
    except KeyError:
        await channel.send(_('Meowth! {member} has no status to cancel!').format(member=author.mention))
        return
    if t_dict['status']['maybe']:
        if t_dict['count'] == 1:
            await channel.send(_('Meowth! {member} is no longer interested!').format(member=author.mention))
        else:
            await channel.send(_('Meowth! {member} and their total of {trainer_count} trainers are no longer interested!').format(member=author.mention, trainer_count=t_dict['count']))
    if t_dict['status']['here']:
        if t_dict['count'] == 1:
            await channel.send(_('Meowth! {member} has left the {raidtype}!').format(member=author.mention, raidtype=raidtype))
        else:
            await channel.send(_('Meowth! {member} and their total of {trainer_count} trainers have left the {raidtype}!').format(member=author.mention, trainer_count=t_dict['count'], raidtype=raidtype))
    if t_dict['status']['coming']:
        if t_dict['count'] == 1:
            await channel.send(_('Meowth! {member} is no longer on their way!').format(member=author.mention))
        else:
            await channel.send(_('Meowth! {member} and their total of {trainer_count} trainers are no longer on their way!').format(member=author.mention, trainer_count=t_dict['count']))
    if t_dict['status']['lobby']:
        if t_dict['count'] == 1:
            await channel.send(_('Meowth! {member} has backed out of the lobby!').format(member=author.mention))
        else:
            await channel.send(_('Meowth! {member} and their total of {trainer_count} trainers have backed out of the lobby!').format(member=author.mention, trainer_count=t_dict['count']))
    t_dict['status'] = {'maybe':0, 'coming':0, 'here':0, 'lobby':0}
    t_dict['party'] = {'mystic':0, 'valor':0, 'instinct':0, 'unknown':0}
    t_dict['interest'] = []
    t_dict['count'] = 1
    await _edit_party(channel, author)

async def lobby_countdown(ctx):
    await asyncio.sleep(120)
    if ('lobby' not in guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]) or (time.time() < guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['lobby']['exp']):
        return
    ctx_lobbycount = 0
    trainer_delete_list = []
    for trainer in ctx.trainer_dict:
        if ctx.trainer_dict[trainer]['status']['lobby']:
            ctx_lobbycount += ctx.trainer_dict[trainer]['status']['lobby']
            trainer_delete_list.append(trainer)
    if ctx_lobbycount > 0:
        await ctx.channel.send(_('Meowth! The group of {count} in the lobby has entered the raid! Wish them luck!').format(count=str(ctx_lobbycount)))
    for trainer in trainer_delete_list:
        if team in ctx.team_names:
            ctx.trainer_dict[trainer]['status'] = {'maybe':0, 'coming':0, 'here':herecount - teamcount, 'lobby': lobbycount}
            ctx.trainer_dict[trainer]['party'][team] = 0
            ctx.trainer_dict[trainer]['count'] = ctx.trainer_dict[trainer]['count'] - teamcount
        else:
            del ctx.trainer_dict[trainer]
    try:
        del guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['lobby']
    except KeyError:
        pass
    await _edit_party(ctx.channel, ctx.author)
    guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['trainer_dict'] = ctx.trainer_dict

@Meowth.command()
@checks.activeraidchannel()
async def starting(ctx, team: str = ''):
    """Signaler qu'un raid commence.

     Utilisation:!starting [équipe]
     Fonctionne uniquement dans les canaux de raid. Envoie un message et efface la liste d'attente. Les utilisateurs qui attendent
     pour un deuxième groupe doit se relire avec le :here: emoji or !here."""
    ctx_startinglist = []
    id_startinglist = []
    name_startinglist = []
    team_list = []
    ctx.team_names = ["mystic", "valor", "instinct", "unknown"]
    team = team if team and team.lower() in ctx.team_names else "all"
    ctx.trainer_dict = copy.deepcopy(guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['trainer_dict'])
    if guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id].get('type',None) == 'egg':
        starting_str = _("Meowth! How can you start when the egg hasn't hatched!?")
        await ctx.channel.send(starting_str)
        return
    if guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id].get('lobby',False):
        starting_str = _("Meowth! Please wait for the group in the lobby to enter the raid.")
        await ctx.channel.send(starting_str)
        return
    for trainer in ctx.trainer_dict:
        count = ctx.trainer_dict[trainer]['count']
        user = ctx.guild.get_member(trainer)
        if team in ctx.team_names:
            if ctx.trainer_dict[trainer]['party'][team]:
                team_list.append(user.id)
            teamcount = ctx.trainer_dict[trainer]['party'][team]
            herecount = ctx.trainer_dict[trainer]['status']['here']
            lobbycount = ctx.trainer_dict[trainer]['status']['lobby']
            if ctx.trainer_dict[trainer]['status']['here'] and (user.id in team_list):
                ctx.trainer_dict[trainer]['status'] = {'maybe':0, 'coming':0, 'here':herecount - teamcount, 'lobby':lobbycount + teamcount}
                ctx_startinglist.append(user.mention)
                name_startinglist.append('**'+user.display_name+'**')
                id_startinglist.append(trainer)
        else:
            if ctx.trainer_dict[trainer]['status']['here'] and (user.id in team_list or team == "all"):
                ctx.trainer_dict[trainer]['status'] = {'maybe':0, 'coming':0, 'here':0, 'lobby':count}
                ctx_startinglist.append(user.mention)
                name_startinglist.append('**'+user.display_name+'**')
                id_startinglist.append(trainer)
    if len(ctx_startinglist) == 0:
        starting_str = _("Meowth! How can you start when there's no one waiting at this raid!?")
        await ctx.channel.send(starting_str)
        return
    guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['trainer_dict'] = ctx.trainer_dict
    starttime = guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id].get('starttime',None)
    if starttime:
        timestr = _(' to start at **{}** ').format(starttime.strftime(_('%I:%M %p (%H:%M)')))
        guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['starttime'] = None
    else:
        timestr = ' '
    starting_str = _('Starting - Meowth! The group that was waiting{timestr}is starting the raid! Trainers {trainer_list}, if you are not in this group and are waiting for the next group, please respond with {here_emoji} or **!here**. If you need to ask those that just started to back out of their lobby, use **!backout**').format(timestr=timestr, trainer_list=', '.join(ctx_startinglist), here_emoji=parse_emoji(ctx.guild, config['here_id']))
    guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['lobby'] = {"exp":time.time() + 120, "team":team}
    if starttime:
        starting_str += '\n\nThe start time has also been cleared, new groups can set a new start time wtih **!starttime HH:MM AM/PM** (You can also omit AM/PM and use 24-hour time!).'
        report_channel = Meowth.get_channel(guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['reportcity'])
        raidmsg = await ctx.channel.get_message(guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['raidmessage'])
        reportmsg = await report_channel.get_message(guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['raidreport'])
        embed = raidmsg.embeds[0]
        embed.set_field_at(2, name=_("**Next Group**"), value=_("Set with **!starttime**"), inline=True)
        try:
            await raidmsg.edit(content=raidmsg.content,embed=embed)
        except discord.errors.NotFound:
            pass
        try:
            await reportmsg.edit(content=reportmsg.content,embed=embed)
        except discord.errors.NotFound:
            pass
    await ctx.channel.send(starting_str)
    ctx.bot.loop.create_task(lobby_countdown(ctx))

@Meowth.command()
@checks.activeraidchannel()
async def backout(ctx):
    """Demander aux joueurs du lobby de se retirer

     Utilisation:!backout
     Alertera tous les dresseurs dans le lobby qu'un backout est demandé."""
    message = ctx.message
    channel = message.channel
    author = message.author
    guild = channel.guild
    trainer_dict = guild_dict[guild.id]['raidchannel_dict'][channel.id]['trainer_dict']
    if (author.id in trainer_dict) and (trainer_dict[author.id]['status']['lobby']):
        count = trainer_dict[author.id]['count']
        trainer_dict[author.id]['status'] = {'maybe':0, 'coming':0,'here':count,'lobby':0}
        lobby_list = []
        for trainer in trainer_dict:
            count = trainer_dict[trainer]['count']
            if trainer_dict[trainer]['status']['lobby']:
                user = guild.get_member(trainer)
                lobby_list.append(user.mention)
                trainer_dict[trainer]['status'] = {'maybe':0, 'coming':0, 'here':count, 'lobby':0}
        if (not lobby_list):
            await channel.send(_("Meowth! There's no one else in the lobby for this raid!"))
            try:
                del guild_dict[guild.id]['raidchannel_dict'][channel.id]['lobby']
            except KeyError:
                pass
            return
        await channel.send(_('Backout - Meowth! {author} has indicated that the group consisting of {lobby_list} and the people with them has backed out of the lobby! If this is inaccurate, please use **!lobby** or **!cancel** to help me keep my lists accurate!').format(author=author.mention, lobby_list=', '.join(lobby_list)))
        try:
            del guild_dict[guild.id]['raidchannel_dict'][channel.id]['lobby']
        except KeyError:
            pass
    else:
        lobby_list = []
        trainer_list = []
        for trainer in trainer_dict:
            if trainer_dict[trainer]['status']['lobby']:
                user = guild.get_member(trainer)
                lobby_list.append(user.mention)
                trainer_list.append(trainer)
        if (not lobby_list):
            await channel.send(_("Meowth! There's no one in the lobby for this raid!"))
            return

        backoutmsg = await channel.send(_('Backout - Meowth! {author} has requested a backout! If one of the following trainers reacts with the check mark, I will assume the group is backing out of the raid lobby as requested! {lobby_list}').format(author=author.mention, lobby_list=', '.join(lobby_list)))
        try:
            timeout = False
            res, reactuser = await ask(backoutmsg, channel, trainer_list, react_list=['✅'])
        except TypeError:
            timeout = True
        if not timeout and res.emoji == '✅':
            for trainer in trainer_list:
                count = trainer_dict[trainer]['count']
                if trainer in trainer_dict:
                    trainer_dict[trainer]['status'] = {'maybe':0, 'coming':0, 'here':count, 'lobby':0}
            await channel.send(_('Meowth! {user} confirmed the group is backing out!').format(user=reactuser.mention))
            try:
                del guild_dict[guild.id]['raidchannel_dict'][channel.id]['lobby']
            except KeyError:
                pass
        else:
            return

"""
List Commands
"""

@Meowth.group(name="list", aliases=['lists'], case_insensitive=True)
async def _list(ctx):
    """Répertorie toutes les informations de raid pour le canal actuel.

     Utilisation:!list
     Fonctionne uniquement dans les raids ou les canaux de la ville. Appelle les listes intéressées, en attente et ici. Imprime également
     le minuteur du raid. Dans les canaux de la ville, liste tous les raids actifs."""
    if ctx.invoked_subcommand == None:
        listmsg = _('**Meowth!** ')
        guild = ctx.guild
        channel = ctx.channel
        now = datetime.datetime.utcnow() + datetime.timedelta(hours=guild_dict[guild.id]['configure_dict']['settings']['offset'])
        if checks.check_raidreport(ctx) or checks.check_exraidreport(ctx):
            activeraidnum = 0
            cty = channel.name
            rc_d = guild_dict[guild.id]['raidchannel_dict']
            raid_dict = {

            }
            egg_dict = {

            }
            exraid_list = []
            event_list = []
            for r in rc_d:
                reportcity = Meowth.get_channel(rc_d[r]['reportcity'])
                if not reportcity:
                    continue
                if (reportcity.name == cty) and rc_d[r]['active'] and discord.utils.get(guild.text_channels, id=r):
                    exp = rc_d[r]['exp']
                    type = rc_d[r]['type']
                    level = rc_d[r]['egglevel']
                    if (type == 'egg') and level.isdigit():
                        egg_dict[r] = exp
                    elif rc_d[r].get('meetup',{}):
                        event_list.append(r)
                    elif ((type == 'exraid') or (level == 'EX')):
                        exraid_list.append(r)
                    else:
                        raid_dict[r] = exp
                    activeraidnum += 1

            def list_output(r):
                trainer_dict = rc_d[r]['trainer_dict']
                rchan = Meowth.get_channel(r)
                end = now + datetime.timedelta(seconds=rc_d[r]['exp'] - time.time())
                output = ''
                start_str = ''
                ctx_herecount = 0
                ctx_comingcount = 0
                ctx_maybecount = 0
                ctx_lobbycount = 0
                for trainer in rc_d[r]['trainer_dict'].keys():
                    if not ctx.guild.get_member(trainer):
                        continue
                    if trainer_dict[trainer]['status']['here']:
                        ctx_herecount += trainer_dict[trainer]['count']
                    elif trainer_dict[trainer]['status']['coming']:
                        ctx_comingcount += trainer_dict[trainer]['count']
                    elif trainer_dict[trainer]['status']['maybe']:
                        ctx_maybecount += trainer_dict[trainer]['count']
                    elif trainer_dict[trainer]['status']['lobby']:
                        ctx_lobbycount += trainer_dict[trainer]['count']
                if rc_d[r]['manual_timer'] == False:
                    assumed_str = _(' (assumed)')
                else:
                    assumed_str = ''
                starttime = rc_d[r].get('starttime',None)
                meetup = rc_d[r].get('meetup',{})
                if starttime and starttime > now and not meetup:
                    start_str = _(' Next group: **{}**').format(starttime.strftime(_('%I:%M %p (%H:%M)')))
                else:
                    starttime = False
                if rc_d[r]['egglevel'].isdigit() and (int(rc_d[r]['egglevel']) > 0):
                    expirytext = _(' - Hatches: {expiry}{is_assumed}').format(expiry=end.strftime(_('%I:%M %p (%H:%M)')), is_assumed=assumed_str)
                elif ((rc_d[r]['egglevel'] == 'EX') or (rc_d[r]['type'] == 'exraid')) and not meetup:
                    expirytext = _(' - Hatches: {expiry}{is_assumed}').format(expiry=end.strftime(_('%B %d at %I:%M %p (%H:%M)')), is_assumed=assumed_str)
                elif meetup:
                    meetupstart = meetup['start']
                    meetupend = meetup['end']
                    expirytext = ""
                    if meetupstart:
                        expirytext += _(' - Starts: {expiry}{is_assumed}').format(expiry=meetupstart.strftime(_('%B %d at %I:%M %p (%H:%M)')), is_assumed=assumed_str)
                    if meetupend:
                        expirytext += _(" - Ends: {expiry}{is_assumed}").format(expiry=meetupend.strftime(_('%B %d at %I:%M %p (%H:%M)')), is_assumed=assumed_str)
                    if not meetupstart and not meetupend:
                        expirytext = _(' - Starts: {expiry}{is_assumed}').format(expiry=end.strftime(_('%B %d at %I:%M %p (%H:%M)')), is_assumed=assumed_str)
                else:
                    expirytext = _(' - Expiry: {expiry}{is_assumed}').format(expiry=end.strftime(_('%I:%M %p (%H:%M)')), is_assumed=assumed_str)
                output += _('    {raidchannel}{expiry_text}\n').format(raidchannel=rchan.mention, expiry_text=expirytext)
                output += _('    {interestcount} interested, {comingcount} coming, {herecount} here, {lobbycount} in the lobby.{start_str}\n').format(raidchannel=rchan.mention, interestcount=ctx_maybecount, comingcount=ctx_comingcount, herecount=ctx_herecount, lobbycount=ctx_lobbycount, start_str=start_str)
                return output
            if activeraidnum:
                listmsg += _("**Here's the current channels for {0}**\n\n").format(cty.capitalize())
            if raid_dict:
                listmsg += _('**Active Raids:**\n')
                for (r, e) in sorted(raid_dict.items(), key=itemgetter(1)):
                    if len(listmsg) < 1800:
                        listmsg += list_output(r)
                    else:
                        await channel.send(listmsg)
                        listmsg = _('**Active Raids:** (continued)\n')
                        listmsg += list_output(r)
                listmsg += '\n'
            if egg_dict:
                listmsg += _('**Raid Eggs:**\n')
                for (r, e) in sorted(egg_dict.items(), key=itemgetter(1)):
                    if len(listmsg) < 1800:
                        listmsg += list_output(r)
                    else:
                        await channel.send(listmsg)
                        listmsg = _('**Raid Eggs:** (continued)\n')
                        listmsg += list_output(r)
                listmsg += '\n'
            if exraid_list:
                listmsg += _('**EX Raids:**\n')
                for r in exraid_list:
                    if len(listmsg) < 1800:
                        listmsg += list_output(r)
                    else:
                        await channel.send(listmsg)
                        listmsg = _('**EX Raids:** (continued)\n')
                        listmsg += list_output(r)
            if event_list:
                listmsg += _('**Meetups:**\n')
                for r in event_list:
                    if len(listmsg) < 1800:
                        listmsg += list_output(r)
                    else:
                        await channel.send(listmsg)
                        listmsg = _('**Meetups:** (continued)\n')
                        listmsg += list_output(r)
            if activeraidnum == 0:
                await channel.send(_('Meowth! No active raids! Report one with **!raid <name> <location> [weather] [timer]**.'))
                return
            else:
                await channel.send(listmsg)
                return
        elif checks.check_raidactive(ctx):
            team_list = ["mystic","valor","instinct","unknown"]
            tag = False
            team = False
            starttime = guild_dict[guild.id]['raidchannel_dict'][channel.id].get('starttime',None)
            meetup = guild_dict[guild.id]['raidchannel_dict'][channel.id].get('meetup',{})
            rc_d = guild_dict[guild.id]['raidchannel_dict'][channel.id]
            list_split = ctx.message.clean_content.lower().split()
            if "tags" in list_split or "tag" in list_split:
                tag = True
            for word in list_split:
                if word in team_list:
                    team = word.lower()
                    break
            if team == "mystic" or team == "valor" or team == "instinct":
                bulletpoint = parse_emoji(ctx.guild, config['team_dict'][team])
            elif team == "unknown":
                bulletpoint = '❔'
            else:
                bulletpoint = '🔹'
            if " 0 interested!" not in await _interest(ctx, tag, team):
                listmsg += ('\n' + bulletpoint) + (await _interest(ctx, tag, team))
            if " 0 on the way!" not in await _otw(ctx, tag, team):
                listmsg += ('\n' + bulletpoint) + (await _otw(ctx, tag, team))
            if " 0 waiting at the raid!" not in await _waiting(ctx, tag, team):
                listmsg += ('\n' + bulletpoint) + (await _waiting(ctx, tag, team))
            if " 0 in the lobby!" not in await _lobbylist(ctx, tag, team):
                listmsg += ('\n' + bulletpoint) + (await _lobbylist(ctx, tag, team))
            if (len(listmsg.splitlines()) <= 1):
                listmsg +=  ('\n' + bulletpoint) + (_(" Nobody has updated their status yet!"))
            listmsg += ('\n' + bulletpoint) + (await print_raid_timer(channel))
            if starttime and (starttime > now) and not meetup:
                listmsg += _('\nThe next group will be starting at **{}**').format(starttime.strftime(_('%I:%M %p (%H:%M)')))
            await channel.send(listmsg)
            return
        else:
            raise checks.errors.CityRaidChannelCheckFail()

@_list.command()
@checks.activechannel()
async def interested(ctx, tags: str = ''):
    """Lists the number and users who are interested in the raid.

    Usage: !list interested
    Works only in raid channels."""
    listmsg = _('**Meowth!**')
    if tags and tags.lower() == "tags" or tags.lower() == "tag":
        tags = True
    listmsg += await _interest(ctx, tags)
    await ctx.channel.send(listmsg)

async def _interest(ctx, tag=False, team=False):
    ctx_maybecount = 0
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=guild_dict[ctx.channel.guild.id]['configure_dict']['settings']['offset'])
    trainer_dict = copy.deepcopy(guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['trainer_dict'])
    maybe_exstr = ''
    maybe_list = []
    name_list = []
    for trainer in trainer_dict.keys():
        user = ctx.guild.get_member(trainer)
        if (trainer_dict[trainer]['status']['maybe']) and user and team == False:
            ctx_maybecount += trainer_dict[trainer]['status']['maybe']
            if trainer_dict[trainer]['status']['maybe'] == 1:
                name_list.append(_('**{name}**').format(name=user.display_name))
                maybe_list.append(user.mention)
            else:
                name_list.append(_('**{name} ({count})**').format(name=user.display_name, count=trainer_dict[trainer]['status']['maybe']))
                maybe_list.append(_('{name} **({count})**').format(name=user.mention, count=trainer_dict[trainer]['status']['maybe']))
        elif (trainer_dict[trainer]['status']['maybe']) and user and team and trainer_dict[trainer]['party'][team]:
            if trainer_dict[trainer]['status']['maybe'] == 1:
                name_list.append(_('**{name}**').format(name=user.display_name))
                maybe_list.append(user.mention)
            else:
                name_list.append(_('**{name} ({count})**').format(name=user.display_name, count=trainer_dict[trainer]['party'][team]))
                maybe_list.append(_('{name} **({count})**').format(name=user.mention, count=trainer_dict[trainer]['party'][team]))
            ctx_maybecount += trainer_dict[trainer]['party'][team]

    if ctx_maybecount > 0:
        if (now.time() >= datetime.time(5, 0)) and (now.time() <= datetime.time(21, 0)) and (tag == True):
            maybe_exstr = _(' including {trainer_list} and the people with them! Let them know if there is a group forming').format(trainer_list=', '.join(maybe_list))
        else:
            maybe_exstr = _(' including {trainer_list} and the people with them! Let them know if there is a group forming').format(trainer_list=', '.join(name_list))
    listmsg = _(' {trainer_count} interested{including_string}!').format(trainer_count=str(ctx_maybecount), including_string=maybe_exstr)
    return listmsg

@_list.command()
@checks.activechannel()
async def coming(ctx, tags: str = ''):
    """Liste le nombre et les utilisateurs qui viennent à un raid.

     Utilisation:!list coming
     Fonctionne uniquement dans les canaux de raid."""
    listmsg = _('**Meowth!**')
    if tags and tags.lower() == "tags" or tags.lower() == "tag":
        tags = True
    listmsg += await _otw(ctx, tags)
    await ctx.channel.send(listmsg)

async def _otw(ctx, tag=False, team=False):
    ctx_comingcount = 0
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=guild_dict[ctx.channel.guild.id]['configure_dict']['settings']['offset'])
    trainer_dict = copy.deepcopy(guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['trainer_dict'])
    otw_exstr = ''
    otw_list = []
    name_list = []
    for trainer in trainer_dict.keys():
        user = ctx.guild.get_member(trainer)
        if (trainer_dict[trainer]['status']['coming']) and user and team == False:
            ctx_comingcount += trainer_dict[trainer]['status']['coming']
            if trainer_dict[trainer]['status']['coming'] == 1:
                name_list.append(_('**{name}**').format(name=user.display_name))
                otw_list.append(user.mention)
            else:
                name_list.append(_('**{name} ({count})**').format(name=user.display_name, count=trainer_dict[trainer]['status']['coming']))
                otw_list.append(_('{name} **({count})**').format(name=user.mention, count=trainer_dict[trainer]['status']['coming']))
        elif (trainer_dict[trainer]['status']['coming']) and user and team and trainer_dict[trainer]['party'][team]:
            if trainer_dict[trainer]['status']['coming'] == 1:
                name_list.append(_('**{name}**').format(name=user.display_name))
                otw_list.append(user.mention)
            else:
                name_list.append(_('**{name} ({count})**').format(name=user.display_name, count=trainer_dict[trainer]['party'][team]))
                otw_list.append(_('{name} **({count})**').format(name=user.mention, count=trainer_dict[trainer]['party'][team]))
            ctx_comingcount += trainer_dict[trainer]['party'][team]

    if ctx_comingcount > 0:
        if (now.time() >= datetime.time(5, 0)) and (now.time() <= datetime.time(21, 0)) and (tag == True):
            otw_exstr = _(' including {trainer_list} and the people with them! Be considerate and wait for them if possible').format(trainer_list=', '.join(otw_list))
        else:
            otw_exstr = _(' including {trainer_list} and the people with them! Be considerate and wait for them if possible').format(trainer_list=', '.join(name_list))
    listmsg = _(' {trainer_count} on the way{including_string}!').format(trainer_count=str(ctx_comingcount), including_string=otw_exstr)
    return listmsg

@_list.command()
@checks.activechannel()
async def here(ctx, tags: str = ''):
    """Liste le nombre et les utilisateurs qui sont présents lors d'un raid.

     Utilisation:!list here
     Fonctionne uniquement dans les canaux de raid."""
    listmsg = _('**Meowth!**')
    if tags and tags.lower() == "tags" or tags.lower() == "tag":
        tags = True
    listmsg += await _waiting(ctx, tags)
    await ctx.channel.send(listmsg)

async def _waiting(ctx, tag=False, team=False):
    ctx_herecount = 0
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=guild_dict[ctx.channel.guild.id]['configure_dict']['settings']['offset'])
    raid_dict = copy.deepcopy(guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id])
    trainer_dict = copy.deepcopy(guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['trainer_dict'])
    here_exstr = ''
    here_list = []
    name_list = []
    for trainer in trainer_dict.keys():
        user = ctx.guild.get_member(trainer)
        if (trainer_dict[trainer]['status']['here']) and user and team == False:
            ctx_herecount += trainer_dict[trainer]['status']['here']
            if trainer_dict[trainer]['status']['here'] == 1:
                name_list.append(_('**{name}**').format(name=user.display_name))
                here_list.append(user.mention)
            else:
                name_list.append(_('**{name} ({count})**').format(name=user.display_name, count=trainer_dict[trainer]['status']['here']))
                here_list.append(_('{name} **({count})**').format(name=user.mention, count=trainer_dict[trainer]['status']['here']))
        elif (trainer_dict[trainer]['status']['here']) and user and team and trainer_dict[trainer]['party'][team]:
            if trainer_dict[trainer]['status']['here'] == 1:
                name_list.append(_('**{name}**').format(name=user.display_name))
                here_list.append(user.mention)
            else:
                name_list.append(_('**{name} ({count})**').format(name=user.display_name, count=trainer_dict[trainer]['party'][team]))
                here_list.append(_('{name} **({count})**').format(name=user.mention, count=trainer_dict[trainer]['party'][team]))
            ctx_herecount += trainer_dict[trainer]['party'][team]
            if raid_dict.get('lobby',{"team":"all"})['team'] == team or raid_dict.get('lobby',{"team":"all"})['team'] == "all":
                ctx_herecount -= trainer_dict[trainer]['status']['lobby']
    raidtype = _("event") if guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id].get('meetup',False) else _("raid")
    if ctx_herecount > 0:
        if (now.time() >= datetime.time(5, 0)) and (now.time() <= datetime.time(21, 0)) and (tag == True):
            here_exstr = _(" including {trainer_list} and the people with them! Be considerate and let them know if and when you'll be there").format(trainer_list=', '.join(here_list))
        else:
            here_exstr = _(" including {trainer_list} and the people with them! Be considerate and let them know if and when you'll be there").format(trainer_list=', '.join(name_list))
    listmsg = _(' {trainer_count} waiting at the {raidtype}{including_string}!').format(trainer_count=str(ctx_herecount), raidtype=raidtype, including_string=here_exstr)
    return listmsg

@_list.command()
@checks.activeraidchannel()
async def lobby(ctx, tag=False):
    """Liste le nombre et les utilisateurs qui sont dans le lobby RAID.

     Utilisation:!list lobby
     Fonctionne uniquement dans les canaux de raid."""
    listmsg = _('**Meowth!**')
    listmsg += await _lobbylist(ctx)
    await ctx.channel.send(listmsg)

async def _lobbylist(ctx, tag=False, team=False):
    ctx_lobbycount = 0
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=guild_dict[ctx.channel.guild.id]['configure_dict']['settings']['offset'])
    raid_dict = copy.deepcopy(guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id])
    trainer_dict = copy.deepcopy(guild_dict[ctx.guild.id]['raidchannel_dict'][ctx.channel.id]['trainer_dict'])
    lobby_exstr = ''
    lobby_list = []
    name_list = []
    for trainer in trainer_dict.keys():
        user = ctx.guild.get_member(trainer)
        if (trainer_dict[trainer]['status']['lobby']) and user and team == False:
            ctx_lobbycount += trainer_dict[trainer]['status']['lobby']
            if trainer_dict[trainer]['status']['lobby'] == 1:
                name_list.append(_('**{name}**').format(name=user.display_name))
                lobby_list.append(user.mention)
            else:
                name_list.append(_('**{name} ({count})**').format(name=user.display_name, count=trainer_dict[trainer]['status']['lobby']))
                lobby_list.append(_('{name} **({count})**').format(name=user.mention, count=trainer_dict[trainer]['status']['lobby']))
        elif (trainer_dict[trainer]['status']['lobby']) and user and team and trainer_dict[trainer]['party'][team]:
            if trainer_dict[trainer]['status']['lobby'] == 1:
                name_list.append(_('**{name}**').format(name=user.display_name))
                lobby_list.append(user.mention)
            else:
                name_list.append(_('**{name} ({count})**').format(name=user.display_name, count=trainer_dict[trainer]['party'][team]))
                lobby_list.append(_('{name} **({count})**').format(name=user.mention, count=trainer_dict[trainer]['party'][team]))
            if raid_dict.get('lobby',{"team":"all"})['team'] == team or raid_dict.get('lobby',{"team":"all"})['team'] == "all":
                ctx_lobbycount += trainer_dict[trainer]['party'][team]

    if ctx_lobbycount > 0:
        if (now.time() >= datetime.time(5, 0)) and (now.time() <= datetime.time(21, 0)) and (tag == True):
            lobby_exstr = _(' including {trainer_list} and the people with them! Use **!lobby** if you are joining them or **!backout** to request a backout').format(trainer_list=', '.join(lobby_list))
        else:
            lobby_exstr = _(' including {trainer_list} and the people with them! Use **!lobby** if you are joining them or **!backout** to request a backout').format(trainer_list=', '.join(name_list))
    listmsg = _(' {trainer_count} in the lobby{including_string}!').format(trainer_count=str(ctx_lobbycount), including_string=lobby_exstr)
    return listmsg

@_list.command()
@checks.activeraidchannel()
async def bosses(ctx):
    """Dressez la liste de chaque boss possible et du nombre d'utilisateurs qui ont répondu à cet appel.

     Utilisation:!list bosses
     Fonctionne uniquement dans les canaux de raid."""
    listmsg = _('**Meowth!**')
    listmsg += await _bosslist(ctx)
    await ctx.channel.send(listmsg)

async def _bosslist(ctx):
    message = ctx.message
    channel = ctx.channel
    egglevel = guild_dict[message.guild.id]['raidchannel_dict'][channel.id]['egglevel']
    egg_level = str(egglevel)
    egg_info = raid_info['raid_eggs'][egg_level]
    egg_img = egg_info['egg_img']
    boss_dict = {}
    boss_list = []
    boss_dict["unspecified"] = {"type": "❔", "total": 0, "maybe": 0, "coming": 0, "here": 0}

    # account for psuedo level 6 boosted raids
    pkmn_list = []
    if egg_level == '5':
        try:
            pkmn_list.extend(raid_info['raid_eggs']['6']['pokemon'])
        except KeyError:
            pass
    pkmn_list.extend(egg_info['pokemon'])

    for p in pkmn_list:
        p_name = get_name(p).title()
        boss_list.append(p_name.lower())
        p_type = get_type(message.guild,p)
        boss_dict[p_name.lower()] = {"type": "{}".format(''.join(p_type)), "total": 0, "maybe": 0, "coming": 0, "here": 0}
    boss_list.append('unspecified')
    trainer_dict = copy.deepcopy(guild_dict[message.guild.id]['raidchannel_dict'][channel.id]['trainer_dict'])
    for trainer in trainer_dict:
        if not ctx.guild.get_member(trainer):
            continue
        interest = trainer_dict[trainer].get('interest', ['unspecified'])
        for item in interest:
            status = max(trainer_dict[trainer]['status'], key=lambda key: trainer_dict[trainer]['status'][key])
            count = trainer_dict[trainer]['count']
            boss_dict[item][status] += count
            boss_dict[item]['total'] += count
    bossliststr = ''
    for boss in boss_list:
        if boss_dict[boss]['total'] > 0:
            bossliststr += _('{type}{name}: **{total} total,** {interested} interested, {coming} coming, {here} waiting{type}\n').format(type=boss_dict[boss]['type'],name=boss.capitalize(), total=boss_dict[boss]['total'], interested=boss_dict[boss]['maybe'], coming=boss_dict[boss]['coming'], here=boss_dict[boss]['here'])
    if bossliststr:
        listmsg = _(' Boss numbers for the raid:\n{}').format(bossliststr)
    else:
        listmsg = _(' Nobody has told me what boss they want!')
    return listmsg

@_list.command()
@checks.activechannel()
async def teams(ctx):
    """Liste les équipes pour les utilisateurs qui ont RSVP'd à un raid.

     Utilisation:!list teams
     Fonctionne uniquement dans les canaux de raid."""
    listmsg = _('**Meowth!**')
    listmsg += await _teamlist(ctx)
    await ctx.channel.send(listmsg)

async def _teamlist(ctx):
    message = ctx.message
    team_dict = {}
    team_dict["mystic"] = {"total":0,"maybe":0,"coming":0,"here":0}
    team_dict["valor"] = {"total":0,"maybe":0,"coming":0,"here":0}
    team_dict["instinct"] = {"total":0,"maybe":0,"coming":0,"here":0}
    team_dict["unknown"] = {"total":0,"maybe":0,"coming":0,"here":0}
    status_list = ["here","coming","maybe"]
    team_list = ["mystic","valor","instinct","unknown"]
    teamliststr = ''
    trainer_dict = copy.deepcopy(guild_dict[message.guild.id]['raidchannel_dict'][message.channel.id]['trainer_dict'])
    for trainer in trainer_dict.keys():
        if not ctx.guild.get_member(trainer):
            continue
        for team in team_list:
            team_dict[team]["total"] += int(trainer_dict[trainer]['party'][team])
            for status in status_list:
                if max(trainer_dict[trainer]['status'], key=lambda key: trainer_dict[trainer]['status'][key]) == status:
                    team_dict[team][status] += int(trainer_dict[trainer]['party'][team])
    for team in team_list[:-1]:
        if team_dict[team]['total'] > 0:
            teamliststr += _('{emoji} **{total} total,** {interested} interested, {coming} coming, {here} waiting {emoji}\n').format(emoji=parse_emoji(ctx.guild, config['team_dict'][team]), total=team_dict[team]['total'], interested=team_dict[team]['maybe'], coming=team_dict[team]['coming'], here=team_dict[team]['here'])
    if team_dict["unknown"]['total'] > 0:
        teamliststr += '❔ '
        teamliststr += _('**{grey_number} total,** {greymaybe} interested, {greycoming} coming, {greyhere} waiting')
        teamliststr += ' ❔'
        teamliststr = teamliststr.format(grey_number=team_dict['unknown']['total'], greymaybe=team_dict['unknown']['maybe'], greycoming=team_dict['unknown']['coming'], greyhere=team_dict['unknown']['here'])
    if teamliststr:
        listmsg = _(' Team numbers for the raid:\n{}').format(teamliststr)
    else:
        listmsg = _(' Nobody has updated their status!')
    return listmsg

@_list.command()
@checks.allowwant()
async def wants(ctx):
    """Liste les désirs pour l'utilisateur

     Utilisation:!list wants
     Fonctionne uniquement dans le canal de recherche."""
    listmsg = _('**Meowth!**')
    listmsg += await _wantlist(ctx)
    await ctx.channel.send(listmsg)

async def _wantlist(ctx):
    wantlist = []
    for role in ctx.author.roles:
        if role.name in pkmn_info['pokemon_list']:
            wantlist.append(role.name.title())
    if len(wantlist) > 0:
        listmsg = _(' Your current **!want** list is: ```{wantlist}```').format(wantlist=', '.join(wantlist))
    else:
        listmsg = _(" You don\'t have any wants! use **!want** to add some.")
    return listmsg

@_list.command()
@checks.allowresearchreport()
async def research(ctx):
    """Liste les quêtes pour la chaîne

     Utilisation:!list research"""
    listmsg = _('**Meowth!**')
    listmsg += await _researchlist(ctx)
    await ctx.channel.send(embed=discord.Embed(colour=ctx.guild.me.colour, description=listmsg))

async def _researchlist(ctx):
    research_dict = copy.deepcopy(guild_dict[ctx.guild.id].get('questreport_dict',{}))
    questmsg = ""
    for questid in research_dict:
        if research_dict[questid]['reportchannel'] == ctx.message.channel.id:
            try:
                questreportmsg = await ctx.message.channel.get_message(questid)
                questauthor = ctx.channel.guild.get_member(research_dict[questid]['reportauthor'])
                if questauthor:
                    if len(questmsg) < 1500:
                        questmsg += ('\n🔹')
                        questmsg += _("**Reward**: {reward}, **Pokestop**: [{location}]({url}), **Quest**: {quest}, **Reported By**: {author}").format(location=research_dict[questid]['location'].title(),quest=research_dict[questid]['quest'].title(),reward=research_dict[questid]['reward'].title(), author=questauthor.display_name, url=research_dict[questid].get('url',None))
                    else:
                        listmsg = _('Meowth! **Here\'s the current research reports for {channel}**\n{questmsg}').format(channel=ctx.message.channel.name.capitalize(),questmsg=questmsg)
                        await ctx.channel.send(embed=discord.Embed(colour=ctx.guild.me.colour, description=listmsg))
                        questmsg = ""
                        questmsg += ('\n🔹')
                        questmsg += _("**Reward**: {reward}, **Pokestop**: [{location}]({url}), **Quest**: {quest}, **Reported By**: {author}").format(location=research_dict[questid]['location'].title(),quest=research_dict[questid]['quest'].title(),reward=research_dict[questid]['reward'].title(), author=questauthor.display_name, url=research_dict[questid].get('url',None))
            except discord.errors.NotFound:
                continue
    if questmsg:
        listmsg = _(' **Here\'s the current research reports for {channel}**\n{questmsg}').format(channel=ctx.message.channel.name.capitalize(),questmsg=questmsg)
    else:
        listmsg = _(" There are no reported research reports. Report one with **!research**")
    return listmsg

@_list.command()
@checks.allowwildreport()
async def wilds(ctx):
    """Liste les wilds pour la chaîne

     Utilisation:!list wilds"""
    listmsg = _('**Meowth!**')
    listmsg += await _wildlist(ctx)
    await ctx.channel.send(embed=discord.Embed(colour=ctx.guild.me.colour, description=listmsg))

async def _wildlist(ctx):
    wild_dict = copy.deepcopy(guild_dict[ctx.guild.id].get('wildreport_dict',{}))
    wildmsg = ""
    for wildid in wild_dict:
        if wild_dict[wildid]['reportchannel'] == ctx.message.channel.id:
            try:
                wildreportmsg = await ctx.message.channel.get_message(wildid)
                wildauthor = ctx.channel.guild.get_member(wild_dict[wildid]['reportauthor'])
                if wildauthor:
                    if len(wildmsg) < 1500:
                        wildmsg += ('\n🔹')
                        wildmsg += _("**Pokemon**: {pokemon}, **Location**: [{location}]({url}), **Reported By**: {author}").format(pokemon=wild_dict[wildid]['pokemon'].title(),location=wild_dict[wildid]['location'].title(),author=wildauthor.display_name,url=wild_dict[wildid].get('url',None))
                    else:
                        listmsg = _('Meowth! **Here\'s the current wild reports for {channel}**\n{wildmsg}').format(channel=ctx.message.channel.name.capitalize(),wildmsg=wildmsg)
                        await ctx.channel.send(embed=discord.Embed(colour=ctx.guild.me.colour, description=listmsg))
                        wildmsg = ""
                        wildmsg += ('\n🔹')
                        wildmsg += _("**Pokemon**: {pokemon}, **Location**: [{location}]({url}), **Reported By**: {author}\n**Location**: <{url}>").format(pokemon=wild_dict[wildid]['pokemon'].title(),location=wild_dict[wildid]['location'].title(),author=wildauthor.display_name,url=wild_dict[wildid].get('url',None))
            except discord.errors.NotFound:
                continue
    if wildmsg:
        listmsg = _(' **Here\'s the current wild reports for {channel}**\n{wildmsg}').format(channel=ctx.message.channel.name.capitalize(),wildmsg=wildmsg)
    else:
        listmsg = _(" There are no reported wild pokemon. Report one with **!wild <pokemon> <location>**")
    return listmsg

try:
    event_loop.run_until_complete(Meowth.start(config['bot_token']))
except discord.LoginFailure:
    logger.critical('Invalid token')
    event_loop.run_until_complete(Meowth.logout())
    Meowth._shutdown_mode = 0
except KeyboardInterrupt:
    logger.info('Keyboard interrupt detected. Quitting...')
    event_loop.run_until_complete(Meowth.logout())
    Meowth._shutdown_mode = 0
except Exception as e:
    logger.critical('Fatal exception', exc_info=e)
    event_loop.run_until_complete(Meowth.logout())
finally:
    pass
sys.exit(Meowth._shutdown_mode)
