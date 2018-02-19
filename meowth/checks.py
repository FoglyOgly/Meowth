
from discord.ext import commands
import discord.utils
import errors

def is_owner_check(ctx):
    author = ctx.author.id
    owner = ctx.bot.config['master']
    return author == owner

def is_owner():
    return commands.check(is_owner_check)

def check_permissions(ctx, perms):
    if (not perms):
        return False
    ch = ctx.channel
    author = ctx.author
    resolved = ch.permissions_for(author)
    return all((getattr(resolved, name, None) == value for (name, value) in perms.items()))

def role_or_permissions(ctx, check, **perms):
    if check_permissions(ctx, perms):
        return True
    ch = ctx.channel
    author = ctx.author
    if ch.is_private:
        return False
    role = discord.utils.find(check, author.roles)
    return role is not None

def serverowner_or_permissions(**perms):

    def predicate(ctx):
        owner = ctx.guild.owner
        if ctx.author.id == owner.id:
            return True
        return check_permissions(ctx, perms)
    return commands.check(predicate)

def serverowner():
    return guildowner_or_permissions()

def check_wantchannel(ctx):
    if ctx.guild is None:
        return False
    channel = ctx.channel
    guild = ctx.guild
    try:
        want_channels = ctx.bot.guild_dict[guild.id]['want_channel_list']
    except KeyError:
        return False
    if channel.id in want_channels:
        return True

def check_citychannel(ctx):
    if ctx.guild is None:
        return False
    channel = ctx.channel.id
    guild = ctx.guild
    try:
        city_channels = ctx.bot.guild_dict[guild.id]['city_channels'].keys()
    except KeyError:
        return False
    if channel in city_channels:
        return True

def check_raidchannel(ctx):
    if ctx.guild is None:
        return False
    channel = ctx.channel
    guild = ctx.guild
    try:
        raid_channels = ctx.bot.guild_dict[guild.id]['raidchannel_dict'].keys()
    except KeyError:
        return False
    if channel.id in raid_channels:
        return True

def check_eggchannel(ctx):
    if ctx.guild is None:
        return False
    channel = ctx.channel
    guild = ctx.guild
    try:
        type = ctx.bot.guild_dict[guild.id]['raidchannel_dict'][channel.id]['type']
    except KeyError:
        return False
    if type == 'egg':
        return True

def check_exraidchannel(ctx):
    if ctx.guild is None:
        return False
    channel = ctx.channel
    guild = ctx.guild
    try:
        level = ctx.bot.guild_dict[guild.id]['raidchannel_dict'][channel.id]['egglevel']
        type = ctx.bot.guild_dict[guild.id]['raidchannel_dict'][channel.id]['type']
    except KeyError:
        return False
    if (level == 'EX') or (type == 'exraid'):
        return True

def check_raidactive(ctx):
    if ctx.guild is None:
        return False
    channel = ctx.channel
    guild = ctx.guild
    try:
        return ctx.bot.guild_dict[guild.id]['raidchannel_dict'][channel.id]['active']
    except KeyError:
        return False

def check_raidset(ctx):
    if ctx.guild is None:
        return False
    guild = ctx.guild
    try:
        return ctx.bot.guild_dict[guild.id]['raidset']
    except KeyError:
        return False

def check_wildset(ctx):
    if ctx.guild is None:
        return False
    guild = ctx.guild
    try:
        return ctx.bot.guild_dict[guild.id]['wildset']
    except KeyError:
        return False

def check_wantset(ctx):
    if ctx.guild is None:
        return False
    guild = ctx.guild
    try:
        return ctx.bot.guild_dict[guild.id]['wantset']
    except KeyError:
        return False

def check_teamset(ctx):
    if ctx.guild is None:
        return False
    guild = ctx.guild
    try:
        return ctx.bot.guild_dict[guild.id]['team']
    except KeyError:
        return False

def teamset():

    def predicate(ctx):
        if check_teamset(ctx):
            return True
        raise errors.TeamSetCheckFail()
    return commands.check(predicate)

def wantset():

    def predicate(ctx):
        if check_wantset(ctx):
            return True
        raise errors.WantSetCheckFail()
    return commands.check(predicate)

def wildset():

    def predicate(ctx):
        if check_wildset(ctx):
            return True
        raise errors.WildSetCheckFail()
    return commands.check(predicate)

def raidset():

    def predicate(ctx):
        if check_raidset(ctx):
            return True
        raise errors.RaidSetCheckFail()
    return commands.check(predicate)

def citychannel():

    def predicate(ctx):
        if check_citychannel(ctx):
            return True
        raise errors.CityChannelCheckFail()
    return commands.check(predicate)

def wantchannel():

    def predicate(ctx):
        if check_wantset(ctx):
            if check_wantchannel(ctx):
                return True
        raise errors.WantChannelCheckFail()
    return commands.check(predicate)

def raidchannel():

    def predicate(ctx):
        if check_raidchannel(ctx):
            return True
        raise errors.RaidChannelCheckFail()
    return commands.check(predicate)

def exraidchannel():

    def predicate(ctx):
        if check_exraidchannel(ctx):
            return True
        raise errors.ExRaidChannelCheckFail()
    return commands.check(predicate)

def nonraidchannel():

    def predicate(ctx):
        if (not check_raidchannel(ctx)):
            return True
        raise errors.NonRaidChannelCheckFail()
    return commands.check(predicate)

def activeraidchannel():

    def predicate(ctx):
        if check_raidchannel(ctx):
            if check_raidactive(ctx):
                return True
        raise errors.ActiveRaidChannelCheckFail()
    return commands.check(predicate)

def cityraidchannel():

    def predicate(ctx):
        if check_raidchannel(ctx) == True:
            return True
        elif check_citychannel(ctx) == True:
            return True
        raise errors.CityRaidChannelCheckFail()
    return commands.check(predicate)

def cityeggchannel():

    def predicate(ctx):
        if check_raidchannel(ctx) == True:
            if check_eggchannel(ctx) == True:
                return True
        elif check_citychannel(ctx) == True:
            return True
        raise errors.RegionEggChannelCheckFail()
    return commands.check(predicate)

def cityexraidchannel():

    def predicate(ctx):
        if check_raidchannel(ctx) == True:
            if check_exraidchannel(ctx) == True:
                return True
        elif check_citychannel(ctx) == True:
            return True
        raise errors.RegionExRaidChannelCheckFail()
    return commands.check(predicate)
