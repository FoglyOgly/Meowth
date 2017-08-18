import os
import asyncio
import gettext
import re
import pickle
import json
import time
from time import strftime

import discord
from discord.ext.commands import Bot

import spelling


Meowth = Bot(command_prefix="!")


config = {}
pkmn_info = {}
type_chart = {}
type_list = []

# Append path of this script to the path of
# config files which we're loading.
# Assumes that config files will always live in the same directory.
script_path = os.path.dirname(os.path.realpath(__file__))

def load_config():
    global config
    global pkmn_info
    global type_chart
    global type_list
    
    # Load configuration
    with open(os.path.join(script_path, "config.json"), "r") as fd:
        config = json.load(fd)

    # Set up message catalog access
    language = gettext.translation('meowth', localedir='locale', languages=[config['language']])
    language.install()
    pokemon_path_source = "locale/{0}/pkmn.json".format(config['language'])
    
    # Load Pokemon list and raid info
    with open(os.path.join(script_path, pokemon_path_source), "r") as fd:
        pkmn_info = json.load(fd)
    
    # Load type information
    with open(os.path.join(script_path, "type_chart.json"), "r") as fd:
        type_chart = json.load(fd)
    with open(os.path.join(script_path, "type_list.json"), "r") as fd:
        type_list = json.load(fd)
    
    # Set spelling dictionary to our list of Pokemon
    spelling.set_dictionary(pkmn_info['pokemon_list'])

load_config()



"""

======================

Helper functions

======================

"""

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
    
    # Summarize into a list of weaknesses,
    # sorting double weaknesses to the front and marking them with 'x2'.
    ret = []
    for type, effectiveness in sorted(type_eff.items(), key=lambda x: x[1], reverse=True):
        if effectiveness == 1:
            ret.append(type.lower())
        elif effectiveness == 2:
            ret.append(type.lower() + "x2")
    
    return ret


# Given a list of weaknesses, return a
# space-separated string of their type IDs,
# as defined in the type_id_dict
def weakness_to_str(server, weak_list):
    ret = ""
    for weakness in weak_list:
        # Handle an "x2" postfix defining a double weakness
        x2 = ""
        if weakness[-2:] == "x2":
            weakness = weakness[:-2]
            x2 = "x2"
        
        # Append to string
        ret += parse_emoji(server, config['type_id_dict'][weakness]) + x2 + " "
    
    return ret


# Convert an arbitrary string into something which
# is acceptable as a Discord channel name.
def sanitize_channel_name(name):
    # Remove all characters other than alphanumerics,
    # dashes, underscores, and spaces
    ret = re.sub(r"[^a-zA-Z0-9 _\-]", "", name)
    # Replace spaces with dashes
    ret = ret.replace(" ", "-")
    
    return ret

# Given the name of the admin role, return a human-readable
# string pointing to the admin role. If the admin role is
# not defined, print the generic message "an admin"
def get_admin_str(admin):
    return _("a member of {0}".format(admin.mention)) if admin else _("an admin")

# Given a string, if it fits the pattern :emoji name:,
# and <emoji_name> is in the server's emoji list, then
# return the string <:emoji name:emoji id>. Otherwise,
# just return the string unmodified.
def parse_emoji(server, emoji_string):
    if emoji_string[0] == ':' and emoji_string[-1] == ':':
        emoji = discord.utils.get(server.emojis, name=emoji_string.strip(':'))
        if emoji:
            emoji_string = "<:{0}:{1}>".format(emoji.name, emoji.id)
    
    return emoji_string

def print_emoji_name(server, emoji_string):
    # By default, just print the emoji_string
    ret = "`" + emoji_string + "`"
    
    emoji = parse_emoji(server, emoji_string)
    # If the string was transformed by the parse_emoji
    # call, then it really was an emoji and we should
    # add the raw string so people know what to write.
    if emoji != emoji_string:
        ret = emoji + " (`" + emoji_string + "`)"
    
    return ret

# Given an arbitrary string, create a Google Maps
# query using the configured hints
def create_gmaps_query(details):
    details_list = details.split()
    return "https://www.google.com/maps/search/?api=1&query={0}+{1}+{2}".format('+'.join(details_list), config['yourtown'], config['yourstate'])

# Given a User, check that it is Meowth's master
def check_master(user):
    return str(user) == config['master']

# Given a violating message, raise an exception
# reporting unauthorized use of admin commands
def raise_admin_violation(message):
    raise Exception(_("Received admin command {0} from unauthorized user {1}!").format(message.content, message.author))

def spellcheck(word):
    suggestion = spelling.correction(word)
    
    # If we have a spellcheck suggestion
    if suggestion != word:
        return _("Meowth! \"{0}\" is not a Pokemon! Did you mean \"{1}\"?").format(word, spelling.correction(word))
    else:
        return _("Meowth! \"{0}\" is not a Pokemon! Check your spelling!").format(word)

"""

======================

End helper functions

======================

"""


"""
Meowth tracks raiding commands through the raidchannel_dict.
Each channel contains the following fields:
'trainer_dict' : a dictionary of all trainers interested in the raid.
'exp'          : a message indicating the expiry time of the raid.

The trainer_dict contains "trainer" elements, which have the following fields:
'status' : a string indicating either "omw" or "waiting"
'count'  : the number of trainers in the party
"""

raidchannel_dict = {}


team_msg = " or ".join(["'!team {0}'".format(team) for team in config['team_dict'].keys()])


@Meowth.event
async def on_ready():
    print(_("Meowth! That's right!")) #prints to the terminal or cmd prompt window upon successful connection to Discord


"""Welcome message to the server and some basic instructions."""

@Meowth.event
async def on_member_join(member):
    server = member.server
    admin = discord.utils.get(server.roles, name=config['admin_role'])
    announcements = discord.utils.get(server.channels, name=config['welcome_channel'])
    
    # Build welcome message
    ann_message = _(" Then head over to {3.mention} to get caught up on what's happening!")
    admin_message = _(" If you have any questions just ask {4}.")
    
    message = _("Meowth! Welcome to {0.name}, {1.mention}! Set your team by typing {2} without quotations.")
    if announcements:
        message += ann_message
    if admin:
        message += admin_message
    
    # Figure out which channel to send the message to
    
    # If default channel is not configured in Meowth,
    # AND Discord doesn't have it configured, give up and print a warning
    default = discord.utils.get(server.channels, name=config['default_channel']) or server.default_channel
    if not default:
        print(_("WARNING: no default channel configured. Unable to send welcome message."))
    else:
        await Meowth.send_message(default, message.format(server, member, team_msg, announcements, get_admin_str(admin)))


"""

Admin commands

"""

@Meowth.command(pass_context=True, hidden=True)
async def welcome(ctx):
    """Print the welcome message (used for testing).
    
    Usage: !welcome [user]
    Optionally takes an argument welcoming a specific user.
    If omitted, welcomes the message author."""
    member = ctx.message.author
    if check_master(member):
        space1 = ctx.message.content.find(" ")
        if space1 != -1:
            member = discord.utils.get(ctx.message.server.members, name=ctx.message.content[9:])
            if not member:
                await Meowth.send_message(ctx.message.channel, _("Meowth! No member named \"{0}\"!").format(ctx.message.content[9:]))
        
        if member:
            await on_member_join(member)
    else:
        raise_admin_violation(ctx.message)


@Meowth.command(pass_context=True, hidden=True)
async def save(ctx):
    """Save persistent state to file.
    
    Usage: !save [filename]
    File path is relative to current directory."""
    member = ctx.message.author
    if check_master(member):
        space1 = ctx.message.content.find(" ")
        if space1 == -1:
            print(_("Needs filename!"))
        else:
            filename = ctx.message.content[6:]
            try:
                fd = open(ctx.message.content[6:], "wb")
                pickle.dump(raidchannel_dict, fd)
                fd.close()
                print("Successfully saved state to {0}!".format(filename))
            except Exception as err:
                print(_("Error occured while trying to write file {0}!").format(filename))
                print(err)
    else:
        raise_admin_violation(ctx.message)

@Meowth.command(pass_context=True, hidden=True)
async def load(ctx):
    """Load persistent state from file.
    
    Usage: !load [filename]
    File path is relative to current directory."""
    global raidchannel_dict
    
    member = ctx.message.author
    if check_master(member):
        space1 = ctx.message.content.find(" ")
        if space1 == -1:
            print(_("Needs filename!"))
        else:
            filename = ctx.message.content[6:]
            try:
                fd = open(ctx.message.content[6:], "rb")
                raidchannel_dict = pickle.load(fd)
                fd.close()
                print("Successfully loaded state from {0}!".format(filename))
            except Exception as err:
                print(_("Error occured while trying to read file {0}!").format(filename))
                print(err)
    else:
        raise_admin_violation(ctx.message)

@Meowth.command(pass_context=True, hidden=True)
async def configure(ctx):
    """Load persistent state from file.
    
    Usage: !load [filename]
    File path is relative to current directory."""
    member = ctx.message.author
    if check_master(member):
        load_config()
    else:
        raise_admin_violation(ctx.message)

"""

End admin commands

"""


@Meowth.command(pass_context = True)
async def team(ctx):
    """Set your team role.
    
    Usage: !team <team name>
    The team roles have to be created manually beforehand by the server administrator."""
    
    role = None
    entered_team = ctx.message.content[6:]
    role = discord.utils.get(ctx.message.server.roles, name=entered_team)
    
    # Check if user already belongs to a team role by
    # getting the role objects of all teams in team_dict and
    # checking if the message author has any of them.
    for team in config['team_dict'].keys():
        temp_role = discord.utils.get(ctx.message.server.roles, name=team)
        # If the role is valid,
        if temp_role:
            # and the user has this role,
            if temp_role in ctx.message.author.roles:
                # then report that a role is already assigned
                await Meowth.send_message(ctx.message.channel, _("Meowth! You already have a team role!"))
                return
        # If the role isn't valid, something is misconfigured, so fire a warning.
        else:
            print(_("WARNING: Role {0} in team_dict not configured as a role on the server!").format(team))
    # Check if team is one of the three defined in the team_dict

    if entered_team not in list(config['team_dict'].keys()):
        await Meowth.send_message(ctx.message.channel, "Meowth! \"{0}\" isn't a valid team! Try {1}".format(entered_team, team_msg))
        return
    # Check if the role is configured on the server
    elif role is None:
        admin = discord.utils.get(ctx.message.server.roles, name=config['admin_role'])
        await Meowth.send_message(ctx.message.channel, _("Meowth! The \"{0}\" role isn't configured on this server! Contact {1}!").format(entered_team, get_admin_str(admin)))
    else:
        try:
            await Meowth.add_roles(ctx.message.author, role)
            await Meowth.send_message(ctx.message.channel, "Meowth! Added {0} to Team {1}! {2}".format(ctx.message.author.mention, role.name.capitalize(), parse_emoji(ctx.message.server, config['team_dict'][entered_team])))
        except discord.Forbidden:
            await Meowth.send_message(ctx.message.channel, _("Meowth! I can't add roles!"))

@Meowth.command(pass_context = True)                
async def want(ctx):
    """A command for declaring a Pokemon species the user wants.
    
    Usage: !want <species>
    Meowth will mention you if anyone reports seeing
    this species in their !wild or !raid command."""
    
    """Behind the scenes, Meowth tracks user !wants by
    creating a server role for the Pokemon species, and
    assigning it to the user."""
    
    entered_want = ctx.message.content[6:].lower()
    if entered_want not in pkmn_info['pokemon_list']:
        await Meowth.send_message(ctx.message.channel, spellcheck(entered_want))
        return
    else:
        role = discord.utils.get(ctx.message.server.roles, name=entered_want)
        # Create role if it doesn't exist yet
        if role is None:
            role = await Meowth.create_role(server = ctx.message.server, name = entered_want, hoist = False, mentionable = True)
            await asyncio.sleep(0.5)
        
        # If user is already wanting the Pokemon,
        # print a less noisy message
        if role in ctx.message.author.roles:
            await Meowth.send_message(ctx.message.channel, content=_("Meowth! {0}, I already know you want {1}!").format(ctx.message.author.mention, entered_want.capitalize()))
        else:
            await Meowth.add_roles(ctx.message.author, role)
            want_number = pkmn_info['pokemon_list'].index(entered_want) + 1
            want_img_url = "http://floatzel.net/pokemon/black-white/sprites/images/{0}.png".format(str(want_number)) #This part embeds the sprite
            want_embed = discord.Embed(colour=discord.Colour(0x2ecc71))
            want_embed.set_thumbnail(url=want_img_url)
            await Meowth.send_message(ctx.message.channel, content=_("Meowth! Got it! {0} wants {1}").format(ctx.message.author.mention, entered_want.capitalize()),embed=want_embed)

@Meowth.command(pass_context = True)
async def wild(ctx):
    """Report a wild Pokemon spawn location.
    
    Usage: !wild <species> <location>
    Meowth will insert the details (really just everything after the species name) into a
    Google maps link and post the link to the same channel the report was made in."""
    space1 = ctx.message.content.find(" ",6)
    if space1 == -1:
        await Meowth.send_message(ctx.message.channel, _("Meowth! Give more details when reporting! Usage: !wild <pokemon name> <location>"))
        return
    else:
        entered_wild = ctx.message.content[6:space1].lower()
        wild_details = ctx.message.content[space1:]
        wild_gmaps_link = create_gmaps_query(wild_details)
        if entered_wild not in pkmn_info['pokemon_list']:
            await Meowth.send_message(ctx.message.channel, spellcheck(entered_wild))
            return
        else:
            wild = discord.utils.get(ctx.message.server.roles, name = entered_wild)
            if wild is None:
                wild = await Meowth.create_role(server = ctx.message.server, name = entered_wild, hoist = False, mentionable = True)
                await asyncio.sleep(0.5)
            wild_number = pkmn_info['pokemon_list'].index(entered_wild) + 1
            wild_img_url = "http://floatzel.net/pokemon/black-white/sprites/images/{0}.png".format(str(wild_number))
            wild_embed = discord.Embed(title=_("Meowth! Click here for directions to the wild {0}!").format(entered_wild.capitalize()),url=wild_gmaps_link,description=_("This is just my best guess!"),colour=discord.Colour(0x2ecc71))
            wild_embed.set_thumbnail(url=wild_img_url)
            await Meowth.send_message(ctx.message.channel, content=_("Meowth! Wild {0} reported by {1}! Details: {2}").format(wild.mention, ctx.message.author.mention, wild_details),embed=wild_embed)

@Meowth.command(pass_context=True)
async def raid(ctx):
    """Report an ongoing raid.
    
    Usage: !raid <species> <location>
    Meowth will insert the details (really just everything after the species name) into a
    Google maps link and post the link to the same channel the report was made in.
    Meowth's message will also include the type weaknesses of the boss.
    
    Finally, Meowth will create a separate channel for the raid report, for the purposes of organizing the raid."""
    
    if 'raid_channels' in config and ctx.message.channel.name not in config['raid_channels']:
        abc = []
        for channel in config['raid_channels']:
            ch = discord.utils.get(ctx.message.server.channels, name = channel)
            if ch and ch.permissions_for(ctx.message.author).read_messages:
                abc.append(ch.mention)
        await Meowth.send_message(ctx.message.channel, """Meowth! Please confine raid reports to one of these channels:
    {0}""".format(", ".join(abc)))
        return
    
    space1 = ctx.message.content.find(" ",6)
    if space1 == -1:
        await Meowth.send_message(ctx.message.channel, _("Meowth! Give more details when reporting! Usage: !raid <pokemon name> <location>"))
        return
    
    entered_raid = ctx.message.content[6:space1].lower()
    raid_details = ctx.message.content[space1:]
    raid_gmaps_link = create_gmaps_query(raid_details)
    if entered_raid not in pkmn_info['pokemon_list']:
        await Meowth.send_message(ctx.message.channel, spellcheck(entered_raid))
        return
    if entered_raid not in pkmn_info['raid_list'] and entered_raid in pkmn_info['pokemon_list']:
        await Meowth.send_message(ctx.message.channel, "Meowth! The Pokemon {0} does not appear in raids!".format(entered_raid.capitalize()))
        return
    else:
        raid_channel_name = entered_raid + sanitize_channel_name(raid_details)
        raid_channel = await Meowth.create_channel(ctx.message.server, raid_channel_name, *ctx.message.channel.overwrites)
        raid = discord.utils.get(ctx.message.server.roles, name = entered_raid)
        if raid is None:
            raid = await Meowth.create_role(server = ctx.message.server, name = entered_raid, hoist = False, mentionable = True)
            await asyncio.sleep(0.5)
        raid_number = pkmn_info['pokemon_list'].index(entered_raid) + 1
        raid_img_url = "http://floatzel.net/pokemon/black-white/sprites/images/{0}.png".format(str(raid_number))
        raid_embed = discord.Embed(title="Meowth! Click here for directions to the raid!",url=raid_gmaps_link,description="Weaknesses: {0}".format(weakness_to_str(ctx.message.server, get_weaknesses(entered_raid))),colour=discord.Colour(0x2ecc71))
        raid_embed.set_thumbnail(url=raid_img_url)
        await Meowth.send_message(ctx.message.channel, content = "Meowth! {0} raid reported by {1}! Details: {2}. Coordinate in {3}".format(raid.mention, ctx.message.author.mention, raid_details, raid_channel.mention),embed=raid_embed)
        await asyncio.sleep(1) #Wait for the channel to be created.
            
        raidmsg = """Meowth! {0} raid reported by {1}! Details: {2}. Coordinate here!

Reply (not react) to this message with {3} to say you are on your way, or {4} if you are at the raid already!
If your plans change, reply with {5} if you are no longer on the way, or {6} if you left the raid.

To see a list of trainers on their way use !otw. To see a list of trainers at the raid use !waiting.
Be sure to set the time left on the raid using !timerset H:MM so others can check it with !timer.
Once you start a raid, use !starting to clear the waiting list.

This channel will be deleted in 2 hours.""".format(raid.mention, ctx.message.author.mention, raid_details, print_emoji_name(ctx.message.server, config['omw_id']), print_emoji_name(ctx.message.server, config['here_id']), print_emoji_name(ctx.message.server, config['unomw_id']), print_emoji_name(ctx.message.server, config['unhere_id']))
        raidmessage = await Meowth.send_message(raid_channel, content = raidmsg, embed=raid_embed)
        raidchannel_dict[raid_channel] = {
          'trainer_dict' : {},
          'exp' : "No expiration time set!",
          'raidmessage' : raidmessage
            }
        raidtime = re.search('[01]:[0-5][0-9]', raid_details)
        if raidtime:
            await Meowth.send_message(raid_channel, "!timerset {0}".format(raidtime.group(0)))

                
"""Deletes any raid channel that is created after two hours and removes corresponding entries in waiting, omw, and
raidexpmsg lists.""" 
@Meowth.event
async def on_channel_create(channel):
    await asyncio.sleep(7200)
    if channel in raidchannel_dict:
        del raidchannel_dict[channel]
        await Meowth.delete_channel(channel)
    
@Meowth.command(pass_context=True)
async def unwant(ctx):
    """A command for removing the a !want for a Pokemon.
    
    Usage: !unwant <species>
    You will no longer be notified of reports about this Pokemon."""
    
    """Behind the scenes, Meowth removes the user from
    the server role for the Pokemon species."""
    entered_unwant = ctx.message.content[8:].lower()
    role = discord.utils.get(ctx.message.server.roles, name=entered_unwant)
    if entered_unwant not in pkmn_info['pokemon_list']:
        await Meowth.send_message(ctx.message.channel, spellcheck(entered_unwant))
        return
    else:
        # Create role if it doesn't exist yet
        if role is None:
            role = await Meowth.create_role(server = ctx.message.server, name = entered_unwant, hoist = False, mentionable = True)
            await asyncio.sleep(0.5)
        
        # If user is not already wanting the Pokemon,
        # print a less noisy message
        if role not in ctx.message.author.roles:
            await Meowth.send_message(ctx.message.channel, content=_("Meowth! {0}, I already know you don't want {1}!").format(ctx.message.author.mention, entered_unwant.capitalize()))
        else:
            await Meowth.remove_roles(ctx.message.author, role)
            unwant_number = pkmn_info['pokemon_list'].index(entered_unwant) + 1
            unwant_img_url = "http://floatzel.net/pokemon/black-white/sprites/images/{0}.png".format(str(unwant_number))
            unwant_embed = discord.Embed(colour=discord.Colour(0x2ecc71))
            unwant_embed.set_thumbnail(url=unwant_img_url)
            await Meowth.send_message(ctx.message.channel, content=_("Meowth! Got it! {0} no longer wants {1}").format(ctx.message.author.mention, entered_unwant.capitalize()),embed=unwant_embed)

@Meowth.command(pass_context = True)
async def timerset(ctx):
    """Set the remaining duration on a raid.
    
    Usage: !timerset <HH:MM>
    Works only in raid channels, can be set or overridden by anyone.
    Meowth displays the end time in HH:MM local time."""
    
    # Meowth saves the timer message in the channel's 'exp' field.
    if ctx.message.channel in raidchannel_dict:
        ticks = time.time()
        try:
            h, m = ctx.message.content[10:].split(':')
            if int(h) >= 2 or int(m) >= 60:
                await Meowth.send_message(ctx.message.channel, _("Meowth... Raids currently last no more than two hours..."))
                return
            if int(h) < 0 or int(m) < 0:
                await Meowth.send_message(ctx.message.channel, _("Meowth... I couldn't understand your time format..."))
            s = int(h) * 3600 + int(m) * 60
        except:
            await Meowth.send_message(ctx.message.channel, _("Meowth...I couldn't understand your time format..."))
            return
        expire = ticks + s
        localexpire = time.localtime(expire)
        
        # Send message
        expmsg = _("Meowth! This raid will end at {0}!").format(strftime("%I:%M", localexpire))
        await Meowth.send_message(ctx.message.channel, expmsg)
        # Save message for later !timer inquiries
        raidchannel_dict[ctx.message.channel]['exp'] = expmsg
        
@Meowth.command(pass_context=True)
async def timer(ctx):
    """Have Meowth resend the expire time message for a raid.
    
    Usage: !timer
    The expiry time should have been previously set with !timerset."""
    if ctx.message.channel in raidchannel_dict:
        await Meowth.send_message(ctx.message.channel, raidchannel_dict[ctx.message.channel]['exp'])

"""Meowth watches for messages that start with the omw, here, unomw, unhere emoji. For omw and here, Meowth
counts the number of emoji and adds that user and the number to the omw and waiting lists. For unomw and unhere,
Meowth removes that user and their number from the list regardless of emoji count. The emoji here will have to be
changed to fit the emoji ids in your server."""
@Meowth.event
async def on_message(message):
    if message.channel in raidchannel_dict:
        trainer_dict = raidchannel_dict[message.channel]['trainer_dict']
        omw_emoji = parse_emoji(message.server, config['omw_id'])
        if message.content.startswith(omw_emoji):
            # TODO: handle case where a user sends :omw:
            # after they've already sent :here:
            await Meowth.send_message(message.channel, _("Meowth! {0} is on the way with {1} trainers!").format(message.author.mention,message.content.count(omw_emoji)))
            # Add trainer name to trainer list
            if message.author.mention not in trainer_dict:
                trainer_dict[message.author.mention] = {}
            trainer_dict[message.author.mention]['status'] = "omw"
            trainer_dict[message.author.mention]['count'] = message.content.count(omw_emoji)
            return
        # TODO: there's no relation between the :here: count and the :omw: count.
        # For example, if a user is :omw: with 4, they have to send 4x :here:
        # or else they only count as 1 person waiting
        here_emoji = parse_emoji(message.server, config['here_id'])
        if message.content.startswith(here_emoji):
            await Meowth.send_message(message.channel, _("Meowth! {0} is at the raid with {1} trainers!").format(message.author.mention, message.content.count(here_emoji)))
            # Add trainer name to trainer list
            if message.author.mention not in raidchannel_dict[message.channel]['trainer_dict']:
                trainer_dict[message.author.mention] = {}
            trainer_dict[message.author.mention]['status'] = "waiting"
            trainer_dict[message.author.mention]['count'] = message.content.count(here_emoji)
            return
        if message.content.startswith(parse_emoji(message.server, config['unhere_id'])):
            if message.author.mention in trainer_dict and trainer_dict[message.author.mention]['status'] == "waiting":
                await Meowth.send_message(message.channel, _("Meowth! {0} and the trainers with them have left the raid!").format(message.author.mention))
                del trainer_dict[message.author.mention]
            return
        if message.content.startswith(parse_emoji(message.server, config['unomw_id'])):
            if message.author.mention in trainer_dict and trainer_dict[message.author.mention]['status'] == "omw":
                await Meowth.send_message(message.channel, _("Meowth! {0} and the trainers with them are no longer on their way!").format(message.author.mention))
                del trainer_dict[message.author.mention]
            return
        if "/maps" in message.content:
            mapsindex = message.content.find("/maps")
            newlocindex = message.content.rfind("http", mapsindex)
            if newlocindex == -1:
                return
            newlocend = message.content.find(" ", newlocindex)
            newloc = message.content[newlocindex:newlocend]
            oldraidmsg = raidchannel_dict[message.channel]['raidmessage']
            oldembed = oldraidmsg.embeds[0]
            newembed = discord.Embed(title=oldembed['title'],url=newloc,description=oldembed['description'],colour=discord.Colour(0x2ecc71))
            newembed.set_thumbnail(url=oldembed['thumbnail']['url'])
            await Meowth.edit_message(oldraidmsg, new_content=oldraidmsg.content, embed=newembed)
            otw_list = []
            trainer_dict = raidchannel_dict[message.channel]['trainer_dict']
            for trainer in trainer_dict.keys():
                if trainer_dict[trainer]['status']=='omw':
                    otw_list.append(trainer)
            await Meowth.send_message(message.channel, content = "Meowth! Someone has suggested a different location for the raid than what I guessed! Trainers {0}: make sure you are headed to the right place!".format(", ".join(otw_list)), embed = newembed)
    await Meowth.process_commands(message)

@Meowth.command(pass_context = True)
async def emoji_help(ctx):
    """Print help about using the raid command emoji.
    
    Usage: !emoji_help"""
    
    helpmsg = """```Emoji help:
    {0}: indicate you are on the way to a raid.
        To tell Meowth you are in a group, copy the emoji once for each person in your group.
    {1}: indicate you are no longer on the way to a raid.
        This will remove you and your group from the "omw" list.
    {2}: indicate you have arrived at the raid.
        To specify you are in a group, copy the emoji once for each person in your group.
        This will remove you from the "omw" list.
    {3}: indicate you are leaving the raid location.
        This will remove you and your group from the "waiting" list.```""".format(config['omw_id'], config['unomw_id'], config['here_id'], config['unhere_id'])
    await Meowth.send_message(ctx.message.channel, helpmsg)

@Meowth.command(pass_context=True)
async def otw(ctx):
    """Lists the number and users who are on the way to a raid.
    
    Usage: !otw
    Works only in raid channels."""
    if ctx.message.channel in raidchannel_dict:
        ctx_omwcount = 0
        
        # Grab all trainers who are :omw: and sum
        # up their counts
        trainer_dict = raidchannel_dict[ctx.message.channel]['trainer_dict']
        for trainer in trainer_dict.values():
            if trainer['status'] == "omw":
                ctx_omwcount += trainer['count']
        
        # If at least 1 person is on the way,
        # add an extra message indicating who it is.
        otw_exstr = ""
        otw_list = []
        for trainer in trainer_dict.keys():
            if trainer_dict[trainer]['status']=='omw':
                otw_list.append(trainer)
        if ctx_omwcount > 0:
            otw_exstr = _(" including {0} and the people with them! Be considerate and wait for them if possible").format(", ".join(otw_list))
        await Meowth.send_message(ctx.message.channel, _("Meowth! {0} on the way{1}!").format(str(ctx_omwcount), otw_exstr))

@Meowth.command(pass_context=True)
async def waiting(ctx):
    """List the number and users who are waiting at a raid.
    
    Usage: !waiting
    Works only in raid channels."""
    if ctx.message.channel in raidchannel_dict:
        ctx_waitingcount = 0
        
        # Grab all trainers who are :here: and sum
        # up their counts
        trainer_dict = raidchannel_dict[ctx.message.channel]['trainer_dict']
        for trainer in trainer_dict.values():
            if trainer['status'] == "waiting":
                ctx_waitingcount += trainer['count']
        
        # If at least 1 person is waiting,
        # add an extra message indicating who it is.
        waiting_exstr = ""
        waiting_list = []
        for trainer in trainer_dict.keys():
            if trainer_dict[trainer]['status']=='waiting':
                waiting_list.append(trainer)
        if ctx_waitingcount > 0:
            waiting_exstr = _(" including {0} and the people with them! Be considerate and let them know if and when you'll be there").format(", ".join(waiting_list))
        await Meowth.send_message(ctx.message.channel, _("Meowth! {0} waiting at the raid{1}!").format(str(ctx_waitingcount), waiting_exstr))

@Meowth.command(pass_context=True)
async def starting(ctx):
    """Signal that a raid is starting.
    
    Usage: !starting
    Works only in raid channels. Sends a message and clears the waiting list. Users who are waiting
    for a second group must reannounce with the :here: emoji."""
    
    if ctx.message.channel in raidchannel_dict:
        ctx_startinglist = []
        
        trainer_dict = raidchannel_dict[ctx.message.channel]['trainer_dict']
        
        # Add all waiting trainers to the starting list
        for trainer in trainer_dict:
            if trainer_dict[trainer]['status'] == "waiting":
                ctx_startinglist.append(trainer)
        
        # Go back and delete the trainers from the waiting list
        for trainer in ctx_startinglist:
            del trainer_dict[trainer]
        

        starting_str = "Meowth! The group that was waiting is starting the raid! Trainers {0}, please respond with {1} if you are waiting for another group!".format(", ".join(ctx_startinglist), parse_emoji(ctx.message.server, config['here_id']))
        if len(ctx_startinglist) == 0:
            starting_str = _("Meowth! How can you start when there's no one waiting at this raid!?")
        await Meowth.send_message(ctx.message.channel, starting_str)
        


            
    

            



            
    


Meowth.run(config['bot_token'])
