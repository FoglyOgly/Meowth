from discord.ext import commands
import discord.utils

def is_owner_check(ctx):
    author = str(ctx.message.author)
    owner = ctx.bot.config['master']
    return author == owner

def is_owner():
    return commands.check(is_owner_check)

def check_permissions(ctx, perms):
    #if is_owner_check(ctx):
    #    return True
    if not perms:
        return False

    ch = ctx.message.channel
    author = ctx.message.author
    resolved = ch.permissions_for(author)
    return all(getattr(resolved, name, None) == value for name, value in perms.items())

def role_or_permissions(ctx, check, **perms):
    if check_permissions(ctx, perms):
        return True

    ch = ctx.message.channel
    author = ctx.message.author
    if ch.is_private:
        return False # can't have roles in PMs

    role = discord.utils.find(check, author.roles)
    return role is not None

def serverowner_or_permissions(**perms):
    def predicate(ctx):
        owner = ctx.message.server.owner
        if ctx.message.author.id == owner.id:
            return True

        return check_permissions(ctx,perms)
    return commands.check(predicate)

def serverowner():
    return serverowner_or_permissions()

def check_wantchannel(ctx):
    if ctx.message.server is None:
            return False
    channel = ctx.message.channel
    server = ctx.message.server
    try:
        want_channels = ctx.bot.server_dict[server]['want_channel_list']
    except KeyError:
        return False
    if channel in want_channels:
        return True

def check_citychannel(ctx):
    if ctx.message.server is None:
            return False
    channel = ctx.message.channel.name
    server = ctx.message.server
    try:
        city_channels = ctx.bot.server_dict[server]['city_channels'].keys()
    except KeyError:
        return False
    if channel in city_channels:
        return True

def check_raidchannel(ctx):
    if ctx.message.server is None:
        return False
    channel = ctx.message.channel
    server = ctx.message.server
    try:
        raid_channels = ctx.bot.server_dict[server]['raidchannel_dict'].keys()
    except KeyError:
        return False
    if channel in raid_channels:
        return True

def check_eggchannel(ctx):
    if ctx.message.server is None:
        return False
    channel = ctx.message.channel
    server = ctx.message.server
    try:
        type = ctx.bot.server_dict[server]['raidchannel_dict'][channel]['type']
    except KeyError:
        return False
    if type == 'egg':
        return True

def check_raidactive(ctx):
    if ctx.message.server is None:
        return False
    channel = ctx.message.channel
    server = ctx.message.server
    try:
        return ctx.bot.server_dict[server]['raidchannel_dict'][channel]['active']
    except KeyError:
        return False

def check_raidset(ctx):
    if ctx.message.server is None:
        return False
    server = ctx.message.server
    try:
        return ctx.bot.server_dict[server]['raidset']
    except KeyError:
        return False

def check_wildset(ctx):
    if ctx.message.server is None:
        return False
    server = ctx.message.server
    try:
        return ctx.bot.server_dict[server]['wildset']
    except KeyError:
        return False

def check_wantset(ctx):
    if ctx.message.server is None:
        return False
    server = ctx.message.server
    try:
        return ctx.bot.server_dict[server]['wantset']
    except KeyError:
        return False

def check_teamset(ctx):
    if ctx.message.server is None:
        return False
    server = ctx.message.server
    try:
        return ctx.bot.server_dict[server]['team']
    except KeyError:
        return False


def teamset():
    def predicate(ctx):
        return check_teamset(ctx)
    return commands.check(predicate)

def wantset():
    def predicate(ctx):
        return check_wantset(ctx)
    return commands.check(predicate)

def wildset():
    def predicate(ctx):
        return check_wildset(ctx)
    return commands.check(predicate)

def raidset():
    def predicate(ctx):
        return check_raidset(ctx)
    return commands.check(predicate)

def citychannel():
    def predicate(ctx):
        return check_citychannel(ctx)
    return commands.check(predicate)

def wantchannel():
    def predicate(ctx):
        if check_wantset(ctx):
            return check_wantchannel(ctx)
    return commands.check(predicate)

def raidchannel():
    def predicate(ctx):
        return check_raidchannel(ctx)
    return commands.check(predicate)

def notraidchannel():
    def predicate(ctx):
        return not check_raidchannel(ctx)
    return commands.check(predicate)

def activeraidchannel():
    def predicate(ctx):
        if check_raidchannel(ctx):
            return check_raidactive(ctx)
    return commands.check(predicate)

def cityraidchannel():
    def predicate(ctx):
        if check_raidchannel(ctx) == True:
            return True
        elif check_citychannel(ctx) == True:
            return True
    return commands.check(predicate)

def cityeggchannel():
    def predicate(ctx):
        if check_raidchannel(ctx) == True:
            if check_eggchannel(ctx) == True:
                return True
        elif check_citychannel(ctx) == True:
            return True
    return commands.check(predicate)
