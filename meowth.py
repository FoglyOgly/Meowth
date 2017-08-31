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

with open("serverdict", "rb") as fd:
    server_dict = pickle.load(fd)


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
        else:
            emoji_strong = "{0}".format(emoji_string.strip(':').capitalize())

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
def create_gmaps_query(details, channel):
    details_list = details.split()
    loc_list = server_dict[channel.server]['city_channels'][channel.name].split()
    return "https://www.google.com/maps/search/?api=1&query={0}+{1}".format('+'.join(details_list),'+'.join(loc_list))

# Given a User, check that it is Meowth's master
def check_master(user):
    return str(user) == config['master']

def check_server_owner(user, server):
    return str(user) == str(server.owner)

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

# Coroutine for deleting channels.
# Waits 5 minutes, then deletes the channel
async def delete_channel(channel):
    # If the channel exists, get ready to delete it.
    # Otherwise, just clean up the dict since someone
    # else deleted the actual channel at some point.
    if discord.utils.get(channel.server.channels, id=channel.id):
        await Meowth.send_message(channel, """This channel timer has expired! The channel has been deactivated and will be deleted in 5 minutes.
To reactivate the channel, use !timerset to set the timer again.""")
        await asyncio.sleep(300)
        # If the channel has already been deleted from the dict, someone
        # else got to it before us, so don't do anything.
        # Also, if the channel got reactivated, don't do anything either.
        if server_dict[channel.server]['raidchannel_dict'][channel] and not server_dict[channel.server]['raidchannel_dict'][channel]['active']:
            del server_dict[channel.server]['raidchannel_dict'][channel]
            # Check one last time to make sure the channel exists
            if discord.utils.get(channel.server.channels, id=channel.id):
                await Meowth.delete_channel(channel)
    else:
        del server_dict[channel.server]['raidchannel_dict'][channel]

# Periodic callback.
# Loop through all channels--if any are found
# to have the timer expired, mark them for deletion
async def channel_cleanup(loop = False):
    while True:
        deleted_channels = []

        for channel in Meowth.get_all_channels():
            if channel in server_dict[channel.server]['raidchannel_dict']:
                if server_dict[channel.server]['raidchannel_dict'][channel]['active'] and server_dict[channel.server]['raidchannel_dict'][channel]['exp'] <= time.time():
                    event_loop.create_task(delete_channel(channel))
                    server_dict[channel.server]['raidchannel_dict'][channel]['active'] = False

        # If this is not a looping cleanup, then
        # just break out and exit.
        if not loop:
            break
        for server in server_dict:
            deadchannel_list = []
            for channel in server_dict[server]['raidchannel_dict']:
                if channel not in server.channels:
                    deadchannel_list.append(channel)
            for channel in deadchannel_list:
                del server_dict[server]['raidchannel_dict'][channel]
        await asyncio.sleep(60)
async def autosave(loop = False):
    while True:
        event_loop.create_task(_save())
        await asyncio.sleep(60)


"""

======================

End helper functions

======================

"""


"""
Meowth tracks raiding commands through the raidchannel_dict.
Each channel contains the following fields:
'trainer_dict' : a dictionary of all trainers interested in the raid.
'exp'          : an instance of time.struct_time tracking when the raid ends.
'active'       : a Boolean indicating whether the raid is still active.

The trainer_dict contains "trainer" elements, which have the following fields:
'status' : a string indicating either "omw" or "waiting"
'count'  : the number of trainers in the party
"""




# Create a channel cleanup loop which runs every minute
event_loop = asyncio.get_event_loop()
event_loop.create_task(channel_cleanup(loop=True))
event_loop.create_task(autosave(loop=True))


team_msg = " or ".join(["'!team {0}'".format(team) for team in config['team_dict'].keys()])


@Meowth.event
async def on_ready():
    print(_("Meowth! That's right!")) #prints to the terminal or cmd prompt window upon successful connection to Discord
    await channel_cleanup()
    for server in Meowth.servers:
        server_dict[server] = server_dict.pop(server)



@Meowth.event
async def on_server_join(server):
    owner = server.owner
    server_dict[server] = {'want_channel_list': [], 'offset': 0, 'welcome': False, 'welcomechan': "", 'wantset': False, 'raidset': False, 'wildset': False, 'team': False, 'want': False, 'other': False, 'done': False, 'raidchannel_dict' : {}}
    await Meowth.send_message(owner, _("Meowth! I'm Meowth, a Discord helper bot for Pokemon Go communities, and someone has invited me to your server! Type !help to see a list of things I can do, and type !configure in any channel of your server to begin!"))

@Meowth.command(pass_context=True, hidden=True)
async def configure(ctx):
    if check_server_owner(ctx.message.author, ctx.message.server):
        server = ctx.message.server
        owner = ctx.message.author
        server_dict[server]['done']=False
        await Meowth.send_message(owner, _("""__**Meowth Configuration**__\n\nMeowth! That's Right! Welcome to the configuration for Meowth the Pokemon Go Helper Bot! I will be guiding you through some setup steps to get me setup on your server.\n\n**Team Assignment Configuration**\n\nFirst, I have a feature that allows users to assign their Pokemon Go team using roles. If you have a bot that handles this already, or you don't want this feature, type N, otherwise type Y to enable the feature!"""))
        teamreply = await Meowth.wait_for_message(author = owner)
        if teamreply.content == "Y" or teamreply.content == "y":
            server_dict[server]['team']=True
            await Meowth.send_message(owner, "Meowth! Team assignments enabled! Please make sure that my role is moved to the top of your server role hierarchy, or at least above your team roles. Your team roles must be 'mystic', 'valor', and 'instinct' and *must* be lowercase.")
        elif teamreply.content == "N" or teamreply.content == "n":
            server_dict[server]['team']=False
        await Meowth.send_message(owner, _("**Welcome Message Configuration**\n\nNext, I have a feature where I welcome new members to the server with a short welcome message in a channel or with a direct message. If you have a bot that handles this already, or if you don't want this feature, type N, otherwise type Y to enable this feature!"))
        if server_dict[server]['team'] == True:
            await Meowth.send_message(owner, _("Sample message:```Meowth! Welcome to [SERVER], @[MEMBER]! Set your team by typing '!team mystic' or '!team valor' or '!team instinct' without quotations. If you have any questions just ask an admin.```"))
        else:
            await Meowth.send_message(owner, _("Sample message:```Meowth! Welcome to [SERVER], @[MEMBER]! If you have any questions just ask an admin.```"))
        welcomereply = await Meowth.wait_for_message(author = owner)
        if welcomereply.content == "Y" or welcomereply.content == "y":
            server_dict[server]['welcome'] = True
            await Meowth.send_message(owner, "Meowth! Welcome message enabled!\n\n**Welcome Message Channel Configuration**\n\nNow I need to know what channel you want me to post these welcome messages in. Reply with a channel name or 'DM' if you would rather I direct message the user.")
            welcomechannelreply = await Meowth.wait_for_message(author = owner)
            if welcomechannelreply.content == "DM" or welcomechannelreply == "dm":
                server_dict[server]['welcomechan'] = "dm"
            else:
                server_dict[server]['welcomechan'] = welcomechannelreply.content
        elif welcomereply.content == "N" or welcomereply.content == "n":
            server_dict[server]['welcome'] = False
        await Meowth.send_message(owner, _("**Main Function Configuration**\n\nMeowth! Alright. Next I just want to check that you want to enable *any* of my main functions. These include assigning roles for each Pokemon a user wants, wild spawn reports, creating channels for raids, and keeping track of users coming to each raid. If you don't want me to do *any* of that, type N, otherwise type Y to start enabling my main functions!"))
        otherreply = await Meowth.wait_for_message(author = owner)
        if otherreply.content == "Y" or otherreply.content == "y":
            server_dict[server]['other']=True
            await Meowth.send_message(owner, _("Meowth! Okay. Now make sure that I have either an admin role on your server, or at least a role with these permissions: 'read messages', 'send messages', 'embed links', 'manage roles', and 'manage channels'. Also, check if my role is at the top of your server role hierarchy."))
            await Meowth.send_message(owner, _("**City Channel Configuration**\n\nMeowth! Next, I need to know which channels will be used for raid and/or wild reports. If your server covers only one community, that's probably your server's default channel. If you cover multiple communities, you should probably have a channel for each community that only those with roles for that community can see. Otherwise your users could be spammed with notifications for raids that are not relevant to them!"))
            await Meowth.send_message(owner, _("Here's what I need: a list of channels in your server that will be used for raid and/or wild reports. Give them in this format: channelname, channelname, channelname"))
            await Meowth.send_message(owner, _("In other words, the name of each channel, each separated by a comma and a single space. If you do not require raid and wild reporting and are only requiring want/unwant, reply with 'N'; however, want/unwant is quite limited without raid or wild reporting."))
            citychannel_dict = {}
            citychannels = await Meowth.wait_for_message(author = owner)
            if citychannels.content == "N" or citychannels.content == "n":
                server_dict[server]['wildset']=False
                server_dict[server]['raidset']=False
            else:
                citychannel_list = citychannels.content.split(', ')
                server_channel_list = []
                for channel in server.channels:
                    server_channel_list.append(channel.name)
                if set(citychannel_list) <= set(server_channel_list):
                    await Meowth.send_message(server.owner, "Meowth! Great! Looks like all of these are names of channels in your server.")
                else:
                    await Meowth.send_message(server.owner, "Meowth! Something went wrong! Please type !configure to start over! Make sure the channels above are created already!")
                    return
                await Meowth.send_message(server.owner, """**City Location Configuration**\n\nMeowth! Alright, we need to set starting locations for each of the channels you just mentioned in the SAME ORDER you typed before. This is what I use to generate Google Maps links to give people directions to raids and spawns! Knowing what town everything is in is often good enough to narrow it down. One way to put it is, for each channel you just listed, I need a location specific enough that I'll know which First Baptist Church people mean. This is important, so please enter it in just this way. For each channel, give me a location using only letters, no punctuation. So something like 'kansas city mo' or 'hull uk' without the quotes and separate your locations with a comma and single space.""")
                cities = await Meowth.wait_for_message(author=server.owner)
                city_list = cities.content.split(', ')
                if len(city_list) == len(citychannel_list):
                    for i in range(len(citychannel_list)):
                        citychannel_dict[citychannel_list[i]]=city_list[i]
                else:
                    await Meowth.send_message(server.owner,"""Meowth! There weren't the same number of cities and channels! Please type !configure to start over!""")
                    return
                server_dict[server]['city_channels'] = citychannel_dict
                await Meowth.send_message(server.owner, "**Raid Command**\n\nMeowth! Alright. Do you want raid reports in these channels? Reply with 'Y' to enable !raid reports, or 'N' to disable !raid")
                raidconfigset = await Meowth.wait_for_message(author=server.owner)
                if raidconfigset.content == "Y" or raidconfigset.content == "y":
                    server_dict[server]['raidset']=True
                    await Meowth.send_message(owner, "**Timezone Configuration**\n\nMeowth! Ok, to finish the raid configuration I need to know what timezone you're in! This will help me coordinate raids for you. The current 24-hr time UTC is {0}. How many hours off from that are you? Please enter your answer as a number between -12 and 12.".format(strftime("%H:%M",time.gmtime())))
                    offsetmsg = await Meowth.wait_for_message(author = owner)
                    offset = float(offsetmsg.content)
                    if not -12 <= offset <= 14:
                        await Meowth.send_message(owner, _("Meowth! I couldn't convert your answer to a number! Type !configure in your server to start again."))
                        return
                    server_dict[server]['offset'] = offset
                elif raidconfigset.content == "N" or raidconfigset.content == "n":
                    server_dict[server]['raidset']=False
                await Meowth.send_message(server.owner, "**Wild Command**\n\nMeowth! Alright. Do you want wild reports in these channels? Reply with 'Y' to enable !wild reports, or 'N' to disable !wild")
                wildconfigset = await Meowth.wait_for_message(author=server.owner)
                if wildconfigset.content == "Y" or wildconfigset.content == "y":
                    server_dict[server]['wildset']=True
                elif wildconfigset.content == "N" or wildconfigset.content == "n":
                    server_dict[server]['wildset']=False
            await Meowth.send_message(server.owner, """Meowth! Ok. Time to do one last check that I have either an admin role on your server, or at least a role with these permissions: 'read messages', 'send messages', 'embed links', 'manage roles', and 'manage channels'. Also, check if my role is at the top of your server role hierarchy. You can restrict me to specific channels by editing channel-specific permissions if you like.\n\n**Want/Unwant Configuration**\n\nThe last thing you should know is that the !want and !unwant commands can produce a lot of clutter if they are allowed on your main channels. I suggest having a dedicated channel for want and unwant. Just type the name or names of the channel(s) you want me to allow. If you type something that isn't a name of an existing channel, I'll create one by that name. If you do not want to enable want/unwant, reply with 'N'. By the way: if you need to change any of these settings, just type !configure in your server and we can do this again.""")
            wantchs = await Meowth.wait_for_message(author=server.owner)
            if wantchs.content == "N" or wantchs.content == "n":
                server_dict[server]['wantset']=False
            else:
                server_dict[server]['wantset']=True
                want_list = wantchs.content.split(', ')
                try:
                    for want_channel_name in want_list:
                        want_channel = discord.utils.get(server.channels, name = want_channel_name)
                        if want_channel == None:
                            want_channel = await Meowth.create_channel(server, want_channel_name)
                        if want_channel not in server_dict[server]['want_channel_list']:
                            server_dict[server]['want_channel_list'].append(want_channel)
                    fd = open("serverdict", "wb")
                    pickle.dump(server_dict, fd)
                    fd.close()
                except:
                    await Meowth.send_message(owner, "Meowth! You didn't give me enough permissions! Type !configure to start over!")
            server_dict[server]['done']=True
        if otherreply.content == "N" or otherreply.content == "n":
            server_dict[server]['other']=False
            server_dict[server]['raidset']=False
            server_dict[server]['wildset']=False
            server_dict[server]['wantset']=False
            server_dict[server]['done']=True
            await Meowth.send_message(owner, _("Meowth! Okay. All of my main functions have been disabled."))
        await Meowth.send_message(owner, "**Emojis**\n\nMeowth! Alright! I'm ready to go! One more thing. I like to use custom emoji for certain things, especially for displaying type weaknesses for raid bosses! I'm going to send you a .rar file that contains all the emoji I need. There are 23 in all. All you have to do is download, extract, and upload the images to Discord as custom emoji. You can do this all at once, and you can just leave the emoji titles alone!")
        fd = open("emoji.rar", "rb")
        await Meowth.send_file(owner, fd)

"""Welcome message to the server and some basic instructions."""

@Meowth.event
async def on_member_join(member):
    server = member.server
    if server_dict[server]['done'] == False or server_dict[server]['welcome'] == False:
        return
    # Build welcome message

    admin_message = _(" If you have any questions just ask an admin.")

    message = _("Meowth! Welcome to {0.name}, {1.mention}! ")
    if server_dict[server]['team'] == True:
        message += "Set your team by typing {0} without quotations.".format(team_msg)
    message += admin_message

    print(server_dict[server]['welcomechan'])
    if server_dict[server]['welcomechan'] == "dm":
        await Meowth.send_message(member, message.format(server, member))
    else:
        default = discord.utils.get(server.channels, name = server_dict[server]['welcomechan'])
        if not default:
            print(_("WARNING: no default channel configured. Unable to send welcome message."))
        await Meowth.send_message(default, message.format(server, member))


"""

Admin commands

"""



async def _save():
    fd = open("serverdict", "wb")
    pickle.dump(server_dict, fd)
    fd.close()


@Meowth.command(pass_context=True, hidden=True)
async def save(ctx):
    """Save persistent state to file.

    Usage: !save
    File path is relative to current directory."""
    member = ctx.message.author
    if check_master(member):
        space1 = ctx.message.content.find(" ")
        if space1 == -1:
            try:
                await _save()
            except Exception as err:
                print(_("Error occured while trying to save!"))
                print(err)
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
        await Meowth.send_message(ctx.message.channel, _("Meowth! The \"{0}\" role isn't configured on this server! Contact an admin!").format(entered_team))
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
    this species in their !wild or !raid command.
    This command only works in #meowth-chat."""

    """Behind the scenes, Meowth tracks user !wants by
    creating a server role for the Pokemon species, and
    assigning it to the user."""
    if server_dict[ctx.message.server]['wantset'] == True:
        if server_dict[ctx.message.server]['want_channel_list'] and ctx.message.channel not in server_dict[ctx.message.server]['want_channel_list']:
            await Meowth.send_message(ctx.message.channel, "Meowth! Please use one of the following channels for **!want** commands: {0}".format(", ".join(i.mention for i in server_dict[ctx.message.server]['want_channel_list'])))
            return
        else:
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
                    await Meowth.add_reaction(ctx.message, '✅')
                    #await Meowth.send_message(ctx.message.channel, content=_("Meowth! {0}, I already know you want {1}!").format(ctx.message.author.mention, entered_want.capitalize()))
                else:
                    await Meowth.add_roles(ctx.message.author, role)
                    want_number = pkmn_info['pokemon_list'].index(entered_want) + 1
                    await Meowth.add_reaction(ctx.message, '✅')
                    #want_img_url = "http://floatzel.net/pokemon/black-white/sprites/images/{0}.png".format(str(want_number)) #This part embeds the sprite
                    #want_embed = discord.Embed(colour=discord.Colour(0x2ecc71))
                    #want_embed.set_thumbnail(url=want_img_url)
                    #await Meowth.send_message(ctx.message.channel, content=_("Meowth! Got it! {0} wants {1}").format(ctx.message.author.mention, entered_want.capitalize()),embed=want_embed)
    else:
        await Meowth.send_message(message.channel, "Meowth! **!want** commands have been disabled.")

@Meowth.command(pass_context = True)
async def wild(ctx):
    """Report a wild Pokemon spawn location.

    Usage: !wild <species> <location>
    Meowth will insert the details (really just everything after the species name) into a
    Google maps link and post the link to the same channel the report was made in."""
    bot = ""
    await _wild(ctx.message, bot)

async def _wild(message, bot):
    if message.channel.name not in server_dict[message.server]['city_channels'].keys() and message.channel != message.server.default_channel:
        await Meowth.send_message(message.channel, _("Meowth! Please restrict wild reports to city channels or the default channel!"))
        return
    if server_dict[message.server]['wildset'] == True:
        if bot == "":
            space1 = message.content.find(" ",6)
            if space1 == -1:
                await Meowth.send_message(message.channel, _("Meowth! Give more details when reporting! Usage: **!wild <pokemon name> <location>**"))
                return
            else:
                entered_wild = message.content[6:space1].lower()
                wild_details = message.content[space1:]
                wild_gmaps_link = create_gmaps_query(wild_details, message.channel)
        else:
            space1 = bot.split(" ")
            entered_wild = space1[1].lower()
            wild_details = space1[2]
            wild_gmaps_link = "https://www.google.com/maps/dir/Current+Location/{0}".format(wild_details)

        if entered_wild not in pkmn_info['pokemon_list']:
            await Meowth.send_message(message.channel, spellcheck(entered_wild))
            return
        else:
            wild = discord.utils.get(message.server.roles, name = entered_wild)
            if wild is None:
                wild = await Meowth.create_role(server = message.server, name = entered_wild, hoist = False, mentionable = True)
                await asyncio.sleep(0.5)
            wild_number = pkmn_info['pokemon_list'].index(entered_wild) + 1
            wild_img_url = "http://floatzel.net/pokemon/black-white/sprites/images/{0}.png".format(str(wild_number))
            wild_embed = discord.Embed(title=_("Meowth! Click here for directions to the wild {0}!").format(entered_wild.capitalize()),url=wild_gmaps_link,description=_("This is just my best guess!"),colour=discord.Colour(0x2ecc71))
            wild_embed.set_thumbnail(url=wild_img_url)
            await Meowth.send_message(message.channel, content=_("Meowth! Wild {0} reported by {1}! Details: {2}").format(wild.mention, message.author.mention, wild_details),embed=wild_embed)
    else:
        await Meowth.send_message(message.channel, "Meowth! **!wild** commands have been disabled.")

@Meowth.command(pass_context=True)
async def raid(ctx):
    """Report an ongoing raid.

    Usage: !raid <species> <location>
    Meowth will insert the details (really just everything after the species name) into a
    Google maps link and post the link to the same channel the report was made in.
    Meowth's message will also include the type weaknesses of the boss.

    Finally, Meowth will create a separate channel for the raid report, for the purposes of organizing the raid."""
    bot = ""
    await _raid(ctx.message, bot)

async def _raid(message, bot):
    if message.channel.name not in server_dict[message.server]['city_channels'].keys() and message.channel != message.server.default_channel:
        await Meowth.send_message(message.channel, "Meowth! Please restrict raid reports to a city channel or the default channel!")
        return
    if server_dict[message.server]['raidset'] == True:
        if bot == "":
            space1 = message.content.find(" ",6)
            if space1 == -1:
                await Meowth.send_message(message.channel, _("Meowth! Give more details when reporting! Usage: **!raid <pokemon name> <location>**"))
                return
            entered_raid = message.content[6:space1].lower()
            raid_message = message.content[space1:]
            raidtime = re.search('[01]:[0-5][0-9]', message.content)
            if raidtime:
                raid_details = message.content[space1:raidtime.start()-1]
                raidexp = raidtime.group()
            else:
                raid_details = raid_message
            raid_gmaps_link = create_gmaps_query(raid_details, message.channel)
        else:
            space1 = bot.find(" ",6)
            entered_raid = bot.split(" ")[1].lower()
            raid_message = bot[space1:]
            raidtime = re.search('[01]:[0-5][0-9]', bot)
            raid_gmaps_link = "https://www.google.com/maps/dir/Current+Location/{0}".format(bot.split("|")[1])
            if raidtime:
                raid_details = bot[space1:raidtime.start()-1]
                raidexp = raidtime.group()
            else:
                raid_details = raid_message

        if entered_raid not in pkmn_info['pokemon_list']:
            await Meowth.send_message(message.channel, spellcheck(entered_raid))
            return
        if entered_raid not in pkmn_info['raid_list'] and entered_raid in pkmn_info['pokemon_list']:
            await Meowth.send_message(message.channel, "Meowth! The Pokemon {0} does not appear in raids!".format(entered_raid.capitalize()))
            return
        else:
            raid_channel_name = entered_raid + sanitize_channel_name(raid_details)
            raid_channel = await Meowth.create_channel(message.server, raid_channel_name, *message.channel.overwrites)
            raid = discord.utils.get(message.server.roles, name = entered_raid)
            if raid is None:
                raid = await Meowth.create_role(server = message.server, name = entered_raid, hoist = False, mentionable = True)
                await asyncio.sleep(0.5)
            raid_number = pkmn_info['pokemon_list'].index(entered_raid) + 1
            raid_img_url = "http://floatzel.net/pokemon/black-white/sprites/images/{0}.png".format(str(raid_number))
            raid_embed = discord.Embed(title="Meowth! Click here for directions to the raid!",url=raid_gmaps_link,description="Weaknesses: {0}".format(weakness_to_str(message.server, get_weaknesses(entered_raid))),colour=discord.Colour(0x2ecc71))
            raid_embed.set_thumbnail(url=raid_img_url)
            await Meowth.send_message(message.channel, content = "Meowth! {0} raid reported by {1}! Details:{2}. Coordinate in {3}".format(raid.mention, message.author.mention, raid_details, raid_channel.mention),embed=raid_embed)
            await asyncio.sleep(1) #Wait for the channel to be created.

            raidmsg = """Meowth! {0} raid reported by {1}! Details:{2}. Coordinate here!

Reply to this message with **!coming** (`!coming [number]` for trainers with you) to say you are on your way, and reply with **!here** once you arrive.
If you are at the raid already, reply with **!here** (`!here [number]` for trainers with you).
If you are interested in the raid and want to wait for a group, use **!maybe**.
If your plans change, reply with **!cancel** if you are no longer on the way or if you have left the raid.
You can set the time remaining with **!timerset H:MM** and access this with **!timer**.

You can see the list of trainers interested with **!interest**, trainers on their way with **!otw**, trainers at the raid with **!waiting**, or all lists with **!lists**.
Once you start a raid, use **!starting** to clear the waiting list to allow the next group to coordinate.

Sometimes I'm not great at directions, but I'll correct my directions if anybody sends me a maps link.

This channel will be deleted in 2 hours or five minutes after the timer expires.""".format(raid.mention, message.author.mention, raid_details)
            raidmessage = await Meowth.send_message(raid_channel, content = raidmsg, embed=raid_embed)

            server_dict[message.server]['raidchannel_dict'][raid_channel] = {
              'trainer_dict' : {},
              'exp' : time.time() + 2 * 60 * 60, # Two hours from now
              'manual_timer' : False, # No one has explicitly set the timer, Meowth is just assuming 2 hours
              'active' : True,
              'raidmessage' : raidmessage
            }
            if raidtime:
                await _timerset(raid_channel,raidexp)
            else:
                await Meowth.send_message(raid_channel, content = "Meowth! Hey {0}, if you can, set the time left on the raid using **!timerset H:MM** so others can check it with **!timer**.".format(message.author.mention))
            if bot:
                await Meowth.send_message(raid_channel, "This raid was reported by GymHuntrBot. If it is a duplicate of a raid already reported by a human, I can delete it with three **!duplicate** messages.")
    else:
        await Meowth.send_message(message.channel, "Meowth! **!raid** commands have been disabled.")

@Meowth.command(pass_context=True)
async def unwant(ctx):
    """A command for removing the a !want for a Pokemon.

    Usage: !unwant <species>
    You will no longer be notified of reports about this Pokemon."""

    """Behind the scenes, Meowth removes the user from
    the server role for the Pokemon species."""
    if server_dict[ctx.message.server]['wantset'] == True:
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
                await Meowth.add_reaction(ctx.message, '✅')
                #await Meowth.send_message(ctx.message.channel, content=_("Meowth! {0}, I already know you don't want {1}!").format(ctx.message.author.mention, entered_unwant.capitalize()))
            else:
                await Meowth.remove_roles(ctx.message.author, role)
                unwant_number = pkmn_info['pokemon_list'].index(entered_unwant) + 1
                await Meowth.add_reaction(ctx.message, '✅')
                #unwant_img_url = "http://floatzel.net/pokemon/black-white/sprites/images/{0}.png".format(str(unwant_number))
                #unwant_embed = discord.Embed(colour=discord.Colour(0x2ecc71))
                #unwant_embed.set_thumbnail(url=unwant_img_url)
                #await Meowth.send_message(ctx.message.channel, content=_("Meowth! Got it! {0} no longer wants {1}").format(ctx.message.author.mention, entered_unwant.capitalize()),embed=unwant_embed)
    else:
        await Meowth.send_message(message.channel, "Meowth! **!unwant** commands have been disabled.")

# Print raid timer
async def print_raid_timer(channel):
    localexpiresecs = server_dict[channel.server]['raidchannel_dict'][channel]['exp'] + 3600 * server_dict[channel.server]['offset']
    localexpire = time.gmtime(localexpiresecs)
    if not server_dict[channel.server]['raidchannel_dict'][channel]['active']:
        await Meowth.send_message(channel, "Meowth! This raid's timer has already expired as of {0}!".format(strftime("%I:%M", localexpire)))
    else:
        if server_dict[channel.server]['raidchannel_dict'][channel]['manual_timer']:
            await Meowth.send_message(channel, "Meowth! This raid will end at {0}!".format(strftime("%I:%M", localexpire)))
        else:
            await Meowth.send_message(channel, "Meowth! No one told me when the raid ends, so I'm assuming it will end at {0}!".format(strftime("%I:%M", localexpire)))


async def _timerset(channel, exptime):


    # Meowth saves the timer message in the channel's 'exp' field.
    if channel in server_dict[channel.server]['raidchannel_dict']:
        ticks = time.time()
        try:
            h, m = exptime.split(':')
            s = int(h) * 3600 + int(m) * 60
            if s >= 7200:
                await Meowth.send_message(channel, _("Meowth...that's too long. Raids currently last no more than two hours..."))
                return
            if int(h) < 0 or int(m) < 0:
                await Meowth.send_message(channel, _("Meowth...I can't do that! No negative numbers, please!"))
                return
        except:
            await Meowth.send_message(channel, _("Meowth...I couldn't understand your time format..."))
            return
        expire = ticks + s


        # Update timestamp
        server_dict[channel.server]['raidchannel_dict'][channel]['exp'] = expire
        # Reactivate channel
        if not server_dict[channel.server]['raidchannel_dict'][channel]['active']:
            await Meowth.send_message(channel, "The channel has been reactivated.")
        server_dict[channel.server]['raidchannel_dict'][channel]['active'] = True
        # Mark that timer has been manually set
        server_dict[channel.server]['raidchannel_dict'][channel]['manual_timer'] = True
        # Send message
        await print_raid_timer(channel)
        # Trigger channel cleanup
        await channel_cleanup()

@Meowth.command(pass_context=True)
async def timerset(ctx):
    """Set the remaining duration on a raid.

    Usage: !timerset <HH:MM>
    Works only in raid channels, can be set or overridden by anyone.
    Meowth displays the end time in HH:MM local time."""
    exptime = re.search('[01]:[0-5][0-9]', ctx.message.content)
    if exptime:
        await _timerset(ctx.message.channel, exptime.group(0))
    else:
        await Meowth.send_message(ctx.message.channel, _("Meowth... I couldn't understand your time format. Try again like this: **!timerset H:MM**"))

@Meowth.command(pass_context=True)
async def timer(ctx):
    """Have Meowth resend the expire time message for a raid.

    Usage: !timer
    The expiry time should have been previously set with !timerset."""
    await _timer(ctx)

async def _timer(ctx):
    if ctx.message.channel in server_dict[ctx.message.server]['raidchannel_dict']:
        await print_raid_timer(ctx.message.channel)


"""
Behind-the-scenes functions for raid management.
Triggerable through commands or through emoji
"""
async def _maybe(message, count):
    if message.channel in server_dict[message.server]['raidchannel_dict'] and server_dict[message.server]['raidchannel_dict'][message.channel]['active']:
        trainer_dict = server_dict[message.server]['raidchannel_dict'][message.channel]['trainer_dict']
        if count == 1:
            await Meowth.send_message(message.channel, _("Meowth! {0} is interested!").format(message.author.mention))
        else:
            await Meowth.send_message(message.channel, _("Meowth! {0} is interested with a total of {1} trainers!").format(message.author.mention, count))
        # Add trainer name to trainer list
        if message.author.mention not in server_dict[message.server]['raidchannel_dict'][message.channel]['trainer_dict']:
            trainer_dict[message.author.mention] = {}
        trainer_dict[message.author.mention]['status'] = "maybe"
        trainer_dict[message.author.mention]['count'] = count
        server_dict[message.server]['raidchannel_dict'][message.channel]['trainer_dict'] = trainer_dict

async def _coming(message, count):
    if message.channel in server_dict[message.server]['raidchannel_dict'] and server_dict[message.server]['raidchannel_dict'][message.channel]['active']:
        trainer_dict = server_dict[message.server]['raidchannel_dict'][message.channel]['trainer_dict']

        # TODO: handle case where a user sends !coming
        # after they've already sent !here
        if count == 1:
            await Meowth.send_message(message.channel, _("Meowth! {0} is on the way!").format(message.author.mention))
        else:
            await Meowth.send_message(message.channel, _("Meowth! {0} is on the way with a total of {1} trainers!").format(message.author.mention, count))
        # Add trainer name to trainer list
        if message.author.mention not in trainer_dict:
            trainer_dict[message.author.mention] = {}
        trainer_dict[message.author.mention]['status'] = "omw"
        trainer_dict[message.author.mention]['count'] = count
        server_dict[message.server]['raidchannel_dict'][message.channel]['trainer_dict'] = trainer_dict


async def _here(message, count):
    if message.channel in server_dict[message.server]['raidchannel_dict'] and server_dict[message.server]['raidchannel_dict'][message.channel]['active']:
        trainer_dict = server_dict[message.server]['raidchannel_dict'][message.channel]['trainer_dict']
        if count == 1:
            await Meowth.send_message(message.channel, _("Meowth! {0} is at the raid!").format(message.author.mention))
        else:
            await Meowth.send_message(message.channel, _("Meowth! {0} is at the raid with a total of {1} trainers!").format(message.author.mention, count))
        # Add trainer name to trainer list
        if message.author.mention not in trainer_dict:
            trainer_dict[message.author.mention] = {}
        trainer_dict[message.author.mention]['status'] = "waiting"
        trainer_dict[message.author.mention]['count'] = count
        server_dict[message.server]['raidchannel_dict'][message.channel]['trainer_dict'] = trainer_dict

async def _cancel(message):
    if message.channel in server_dict[message.server]['raidchannel_dict'] and server_dict[message.server]['raidchannel_dict'][message.channel]['active']:
        trainer_dict = server_dict[message.server]['raidchannel_dict'][message.channel]['trainer_dict']
        if message.author.mention in trainer_dict and trainer_dict[message.author.mention]['status'] == "maybe":
            if trainer_dict[message.author.mention]['count'] == 1:
                await Meowth.send_message(message.channel, _("Meowth! {0} is no longer interested!").format(message.author.mention))
            else:
                await Meowth.send_message(message.channel, _("Meowth! {0} and their total of {1} trainers are no longer interested!").format(message.author.mention, trainer_dict[message.author.mention]['count']))
        if message.author.mention in trainer_dict and trainer_dict[message.author.mention]['status'] == "waiting":
            if trainer_dict[message.author.mention]['count'] == 1:
                await Meowth.send_message(message.channel, _("Meowth! {0} has left the raid!").format(message.author.mention))
            else:
                await Meowth.send_message(message.channel, _("Meowth! {0} and their total of {1} trainers have left the raid!").format(message.author.mention, trainer_dict[message.author.mention]['count']))
        if message.author.mention in trainer_dict and trainer_dict[message.author.mention]['status'] == "omw":
            if trainer_dict[message.author.mention]['count'] == 1:
                await Meowth.send_message(message.channel, _("Meowth! {0} is no longer on their way!").format(message.author.mention))
            else:
                await Meowth.send_message(message.channel, _("Meowth! {0} and their total of {1} trainers are no longer on their way!").format(message.author.mention, trainer_dict[message.author.mention]['count']))
        del trainer_dict[message.author.mention]
        server_dict[message.server]['raidchannel_dict'][message.channel]['trainer_dict'] = trainer_dict

"""Meowth watches for messages that start with the omw, here, unomw, unhere emoji. For omw and here, Meowth
counts the number of emoji and adds that user and the number to the omw and waiting lists. For unomw and unhere,
Meowth removes that user and their number from the list regardless of emoji count. The emoji here will have to be
changed to fit the emoji ids in your server."""
@Meowth.event
async def on_message(message):
    if str(message.author) == "GymHuntrBot#7279":
        if message.embeds:
            ghgps = message.embeds[0]['url'].split("#")[1]
            ghdesc = message.embeds[0]['description'].splitlines()
            ghgym = ghdesc[0][2:-3]
            ghpokeid = ghdesc[1]
            ghtime = ghdesc[3].split(" ")
            ghhour = ghtime[2]
            ghminute = ghtime[4].zfill(2)
            bot = "!raid {0} {1} {2}:{3} |{4}".format(ghpokeid, ghgym, ghhour, ghminute, ghgps)
            await Meowth.delete_message(message)
            await _raid(message, bot)
            return
        return
    if str(message.author) == "HuntrBot#1845":
        if message.embeds:
            hlocation = message.embeds[0]['url'].split("#")[1]
            hpokeid = message.embeds[0]['title'].split(" ")[2]
            bot = "!wild {0} {1}".format(hpokeid, hlocation)
            await Meowth.delete_message(message)
            await _wild(message, bot)
            return
        return
    if message.server is not None:
        raid_status = server_dict[message.server]['raidchannel_dict'].get(message.channel,None)
        if raid_status is not None:
            if server_dict[message.server]['raidchannel_dict'][message.channel]['active']:
                trainer_dict = server_dict[message.server]['raidchannel_dict'][message.channel]['trainer_dict']
                omw_emoji = parse_emoji(message.server, config['omw_id'])
                if message.content.startswith(omw_emoji):
                    await _coming(message, message.content.count(omw_emoji))
                    return
                # TODO: there's no relation between the :here: count and the :omw: count.
                # For example, if a user is :omw: with 4, they have to send 4x :here:
                # or else they only count as 1 person waiting
                here_emoji = parse_emoji(message.server, config['here_id'])
                if message.content.startswith(here_emoji):
                    await _here(message, message.content.count(here_emoji))
                    return
                if "/maps" in message.content:
                    mapsindex = message.content.find("/maps")
                    newlocindex = message.content.rfind("http", 0, mapsindex)
                    if newlocindex == -1:
                        return
                    newlocend = message.content.find(" ", newlocindex)
                    if newlocend == -1:
                        newloc = message.content[newlocindex:]
                    else:
                        newloc = message.content[newlocindex:newlocend+1]
                    oldraidmsg = server_dict[message.server]['raidchannel_dict'][message.channel]['raidmessage']
                    oldembed = oldraidmsg.embeds[0]
                    newembed = discord.Embed(title=oldembed['title'],url=newloc,description=oldembed['description'],colour=discord.Colour(0x2ecc71))
                    newembed.set_thumbnail(url=oldembed['thumbnail']['url'])
                    await Meowth.edit_message(oldraidmsg, new_content=oldraidmsg.content, embed=newembed)
                    otw_list = []
                    trainer_dict = server_dict[message.server]['raidchannel_dict'][message.channel]['trainer_dict']
                    for trainer in trainer_dict.keys():
                        if trainer_dict[trainer]['status']=='omw':
                            otw_list.append(trainer)
                    await Meowth.send_message(message.channel, content = "Meowth! Someone has suggested a different location for the raid than what I guessed! Trainers {0}: make sure you are headed to the right place!".format(", ".join(otw_list)), embed = newembed)
                    return
    await Meowth.process_commands(message)

@Meowth.command(pass_context=True)
async def maybe(ctx):
    """Indicate you are interested in the raid.

    Usage: !maybe [message]
    Works only in raid channels. If message is omitted, assumes you are a group of 1.
    Otherwise, this command expects at least one word in your message to be a number,
    and will assume you are a group with that many people."""
    if ctx.message.channel in server_dict[ctx.message.server]['raidchannel_dict'] and server_dict[ctx.message.server]['raidchannel_dict'][ctx.message.channel]['active']:
        trainer_dict = server_dict[ctx.message.server]['raidchannel_dict'][ctx.message.channel]['trainer_dict']
        count = 1
        space1 = ctx.message.content.find(" ")
        if space1 != -1:
            # Search for a number in the message
            # by trying to convert each word to integer
            count = None
            duplicate = False
            for word in ctx.message.content[7:].split():
                try:
                    newcount = int(word)
                    if not count:
                        count = newcount
                    else:
                        duplicate = True
                except ValueError:
                    pass
            # If count wasn't set, we didn't find a number
            if not count:
                await Meowth.send_message(ctx.message.channel, _("Meowth! Exactly *how many* are interested? There wasn't a number anywhere in your message. Or, just say `!maybe` if you're by yourself."))
                return
            # Don't allow duplicates
            if duplicate:
                await Meowth.send_message(ctx.message.channel, _("Meowth...I got confused because there were several numbers in your message. I don't know which one is the right one."))
                return
        await _maybe(ctx.message, count)


@Meowth.command(pass_context=True)
async def coming(ctx):
    """Indicate you are on the way to a raid.

    Usage: !coming [message]
    Works only in raid channels. If message is omitted, checks for previous !maybe
    command and takes the count from that. If it finds none, assumes you are a group
    of 1.
    Otherwise, this command expects at least one word in your message to be a number,
    and will assume you are a group with that many people."""
    if ctx.message.channel in server_dict[ctx.message.server]['raidchannel_dict'] and server_dict[ctx.message.server]['raidchannel_dict'][ctx.message.channel]['active']:
        trainer_dict = server_dict[ctx.message.server]['raidchannel_dict'][ctx.message.channel]['trainer_dict']
        count = 1
        space1 = ctx.message.content.find(" ")
        if space1 == -1:
            # If there was a previous !maybe command, take the count from that
            if ctx.message.author.mention in trainer_dict:
                count = trainer_dict[ctx.message.author.mention]['count']
            else:
                count = 1
        if space1 != -1:
            # Search for a number in the message
            # by trying to convert each word to integer
            count = None
            duplicate = False
            for word in ctx.message.content[8:].split():
                try:
                    newcount = int(word)
                    if not count:
                        count = newcount
                    else:
                        duplicate = True
                except ValueError:
                    pass
            # If count wasn't set, we didn't find a number
            if not count:
                await Meowth.send_message(ctx.message.channel, _("Meowth! Exactly *how many* are coming? There wasn't a number anywhere in your message. Or, just say **!coming** if you're by yourself."))
                return
            # Don't allow duplicates
            if duplicate:
                await Meowth.send_message(ctx.message.channel, _("Meowth...I got confused because there were several numbers in your message. I don't know which one is the right one."))
                return

        await _coming(ctx.message, count)

@Meowth.command(pass_context=True)
async def here(ctx):
    """Indicate you have arrived at the raid.

    Usage: !here [message]
    Works only in raid channels. If message is omitted, and
    you have previously issued !coming, then preserves the count
    from that command. Otherwise, assumes you are a group of 1.
    Otherwise, this command expects at least one word in your message to be a number,
    and will assume you are a group with that many people."""
    if ctx.message.channel in server_dict[ctx.message.server]['raidchannel_dict'] and server_dict[ctx.message.server]['raidchannel_dict'][ctx.message.channel]['active']:
        trainer_dict = server_dict[ctx.message.server]['raidchannel_dict'][ctx.message.channel]['trainer_dict']

        # If no message, default count is 1
        count = 1
        space1 = ctx.message.content.find(" ")
        if space1 == -1:
            # If there was a previous !coming command, take the count from that
            if ctx.message.author.mention in trainer_dict:
                count = trainer_dict[ctx.message.author.mention]['count']
            else:
                count = 1
        else:
            # Search for a number in the message
            # by trying to convert each word to integer
            count = None
            duplicate = False
            for word in ctx.message.content[6:].split():
                try:
                    newcount = int(word)
                    if not count:
                        count = newcount
                    else:
                        duplicate = True
                except ValueError:
                    pass
            # If count wasn't set, we didn't find a number
            if not count:
                await Meowth.send_message(ctx.message.channel, _("Meowth! Exactly *how many* are here? There wasn't a number anywhere in your message. Or, just say **!here** if you're by yourself."))
                return
            # Don't allow duplicates
            if duplicate:
                await Meowth.send_message(ctx.message.channel, _("Meowth...I got confused because there were several numbers in your message. I don't know which one is the right one."))
                return
        await _here(ctx.message, count)

@Meowth.command(pass_context=True)
async def cancel(ctx):
    """Indicate you are no longer interested in a raid.

    Usage: !cancel
    Works only in raid channels. Removes you and your party
    from the list of trainers who are "otw" or "here"."""
    await _cancel(ctx.message)

@Meowth.command(pass_context = True)
async def emoji_help(ctx):
    """Print help about using the raid command emoji.

    Usage: !emoji_help"""

    helpmsg = """**Emoji help**:
    {0}: indicate you are on the way to a raid.
        To tell Meowth you are in a group, copy the emoji once for each person in your group.

    {1}: indicate you have arrived at the raid.
        To specify you are in a group, copy the emoji once for each person in your group.
        This will remove you from the "omw" list.""".format(print_emoji_name(ctx.message.server, config['omw_id']), print_emoji_name(ctx.message.server, config['here_id']))

    await Meowth.send_message(ctx.message.channel, helpmsg)

@Meowth.command(pass_context=True)
async def interest(ctx):
    """Lists the number and users who are interested in the raid.

    Usage: !interest
    Works only in raid channels."""
    await _interest(ctx)

async def _interest(ctx):

    if ctx.message.channel in server_dict[ctx.message.server]['raidchannel_dict'] and server_dict[ctx.message.server]['raidchannel_dict'][ctx.message.channel]['active']:
        ctx_maybecount = 0

        # Grab all trainers who are maybe and sum
        # up their counts
        trainer_dict = server_dict[ctx.message.server]['raidchannel_dict'][ctx.message.channel]['trainer_dict']
        for trainer in trainer_dict.values():
            if trainer['status'] == "maybe":
                ctx_maybecount += trainer['count']

        # If at least 1 person is interested,
        # add an extra message indicating who it is.
        maybe_exstr = ""
        maybe_list = []
        for trainer in trainer_dict.keys():
            if trainer_dict[trainer]['status']=='maybe':
                maybe_list.append(trainer)
        if ctx_maybecount > 0:
            maybe_exstr = _(" including {0} and the people with them! Let them know if there is a group forming").format(", ".join(maybe_list))
        await Meowth.send_message(ctx.message.channel, _("Meowth! {0} interested{1}!").format(str(ctx_maybecount), maybe_exstr))


@Meowth.command(pass_context=True)
async def otw(ctx):
    """Lists the number and users who are on the way to a raid.

    Usage: !otw
    Works only in raid channels."""
    await _otw(ctx)

async def _otw(ctx):

    if ctx.message.channel in server_dict[ctx.message.server]['raidchannel_dict'] and server_dict[ctx.message.server]['raidchannel_dict'][ctx.message.channel]['active']:
        ctx_omwcount = 0

        # Grab all trainers who are :omw: and sum
        # up their counts
        trainer_dict = server_dict[ctx.message.server]['raidchannel_dict'][ctx.message.channel]['trainer_dict']
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
    await _waiting(ctx)

async def _waiting(ctx):

    if ctx.message.channel in server_dict[ctx.message.server]['raidchannel_dict'] and server_dict[ctx.message.server]['raidchannel_dict'][ctx.message.channel]['active']:
        ctx_waitingcount = 0

        # Grab all trainers who are :here: and sum
        # up their counts
        trainer_dict = server_dict[ctx.message.server]['raidchannel_dict'][ctx.message.channel]['trainer_dict']
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
async def lists(ctx):
    """Print all lists concerning a raid at once.

    Usage: !lists
    Works only in raid channels. Calls the interest, otw, and waiting lists. Also prints
    the raid timer."""
    await _interest(ctx)
    await _otw(ctx)
    await _waiting(ctx)
    await _timer(ctx)

@Meowth.command(pass_context=True)
async def starting(ctx):
    """Signal that a raid is starting.

    Usage: !starting
    Works only in raid channels. Sends a message and clears the waiting list. Users who are waiting
    for a second group must reannounce with the :here: emoji."""

    if ctx.message.channel in server_dict[ctx.message.server]['raidchannel_dict'] and server_dict[ctx.message.server]['raidchannel_dict'][ctx.message.channel]['active']:
        ctx_startinglist = []

        trainer_dict = server_dict[ctx.message.server]['raidchannel_dict'][ctx.message.channel]['trainer_dict']

        # Add all waiting trainers to the starting list
        for trainer in trainer_dict:
            if trainer_dict[trainer]['status'] == "waiting":
                ctx_startinglist.append(trainer)

        # Go back and delete the trainers from the waiting list
        for trainer in ctx_startinglist:
            del trainer_dict[trainer]
        server_dict[ctx.message.server]['raidchannel_dict'][ctx.message.channel]['trainer_dict'] = trainer_dict


        starting_str = "Meowth! The group that was waiting is starting the raid! Trainers {0}, please respond with {1} or **!here** if you are waiting for another group!".format(", ".join(ctx_startinglist), parse_emoji(ctx.message.server, config['here_id']))
        if len(ctx_startinglist) == 0:
            starting_str = _("Meowth! How can you start when there's no one waiting at this raid!?")
        await Meowth.send_message(ctx.message.channel, starting_str)

@Meowth.command(pass_context=True)
async def omw(ctx):
    if ctx.message.channel in server_dict[ctx.message.server]['raidchannel_dict'] and server_dict[ctx.message.server]['raidchannel_dict'][ctx.message.channel]['active']:
        await Meowth.send_message(ctx.message.channel, content = "Meowth! Hey {0}, I don't know if you meant **!coming** to say that you are coming or **!otw** to see the other trainers on their way".format(ctx.message.author.mention))

@Meowth.command(pass_context=True)
async def interested(ctx):
    if ctx.message.channel in server_dict[ctx.message.server]['raidchannel_dict'] and server_dict[ctx.message.server]['raidchannel_dict'][ctx.message.channel]['active']:
        await Meowth.send_message(ctx.message.channel, content = "Meowth! Hey {0}, I don't know if you meant **!maybe** to say that you are interested or **!interest** to see the other trainers interest".format(ctx.message.author.mention))

@Meowth.command(pass_context=True, hidden=True)
async def duplicate(ctx):
    if ctx.message.channel in server_dict[ctx.message.server]['raidchannel_dict'] and server_dict[ctx.message.server]['raidchannel_dict'][ctx.message.channel]['active']:
        ctx_dupecount = 0
        trainer_dict = server_dict[ctx.message.server]['raidchannel_dict'][ctx.message.channel]['trainer_dict']
        if ctx.message.author.mention not in server_dict[ctx.message.server]['raidchannel_dict']:
            trainer_dict[ctx.message.author.mention] = {}
            trainer_dict[ctx.message.author.mention]['dupe'] = "dupe"
        for trainer in trainer_dict.values():
            if trainer['dupe'] == "dupe":
                ctx_dupecount += 1
        if ctx_dupecount == 3:
            await Meowth.send_message(ctx.message.channel, "This channel has been reported as a duplicate and has been deactivated. Check the channel list for the other raid channel to coordinate in! If this was an error you can reset the raid with **!timerset**")
            server_dict[ctx.message.server]['raidchannel_dict'][ctx.message.channel]['active'] = False
            if discord.utils.get(ctx.message.channel.server.channels, id=ctx.message.channel.id):
                await asyncio.sleep(300)
                if server_dict[ctx.message.channel.server]['raidchannel_dict'][ctx.message.channel] and not server_dict[ctx.message.channel.server]['raidchannel_dict'][ctx.message.channel]['active']:
                    del server_dict[ctx.message.channel.server]['raidchannel_dict'][ctx.message.channel]
                    if discord.utils.get(ctx.message.channel.server.channels, id=ctx.message.channel.id):
                        await Meowth.delete_channel(ctx.message.channel)
                        return
            else:
                del server_dict[ctx.message.channel.server]['raidchannel_dict'][ctx.message.channel]
    server_dict[ctx.message.server]['raidchannel_dict'][ctx.message.channel]['trainer_dict'] = trainer_dict









Meowth.run(config['bot_token'])
