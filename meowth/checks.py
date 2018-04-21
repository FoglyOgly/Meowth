
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

#configuration
def check_wantset(ctx):
    if ctx.guild is None:
        return False
    guild = ctx.guild
    return ctx.bot.guild_dict[guild.id]['configure_dict']['want'].get('enabled',False)

def check_wantchannel(ctx):
    if ctx.guild is None:
        return False
    channel = ctx.channel
    guild = ctx.guild
    want_channels = ctx.bot.guild_dict[guild.id]['configure_dict']['want'].get('report_channels',[])
    return channel.id in want_channels

def check_citychannel(ctx):
    if ctx.guild is None:
        return False
    channel = ctx.channel
    guild = ctx.guild
    channel_list = [x for x in ctx.bot.guild_dict[guild.id]['configure_dict']['raid'].get('report_channels',{}).keys()]
    channel_list.extend([x for x in ctx.bot.guild_dict[guild.id]['configure_dict']['exraid'].get('report_channels',{}).keys()])
    channel_list.extend([x for x in ctx.bot.guild_dict[guild.id]['configure_dict']['wild'].get('report_channels',{}).keys()])
    channel_list.extend([x for x in ctx.bot.guild_dict[guild.id]['configure_dict']['research'].get('report_channels',{}).keys()])
    return channel.id in channel_list

def check_raidset(ctx):
    if ctx.guild is None:
        return False
    guild = ctx.guild
    return ctx.bot.guild_dict[guild.id]['configure_dict']['raid'].get('enabled',False)

def check_raidreport(ctx):
    if ctx.guild is None:
        return False
    channel = ctx.channel
    guild = ctx.guild
    channel_list = [x for x in ctx.bot.guild_dict[guild.id]['configure_dict']['raid'].get('report_channels',{}).keys()]
    return channel.id in channel_list

def check_raidchannel(ctx):
    if ctx.guild is None:
        return False
    channel = ctx.channel
    guild = ctx.guild
    raid_channels = ctx.bot.guild_dict[guild.id]['raidchannel_dict'].keys()
    return channel.id in raid_channels

def check_eggchannel(ctx):
    if ctx.guild is None:
        return False
    channel = ctx.channel
    guild = ctx.guild
    type = ctx.bot.guild_dict[guild.id].get('raidchannel_dict',{}).get(channel.id,{}).get('type',None)
    return type == 'egg'

def check_raidactive(ctx):
    if ctx.guild is None:
        return False
    channel = ctx.channel
    guild = ctx.guild
    return ctx.bot.guild_dict[guild.id].get('raidchannel_dict',{}).get(channel.id,{}).get('active',False)



def check_exraidset(ctx):
    if ctx.guild is None:
        return False
    guild = ctx.guild
    return ctx.bot.guild_dict[guild.id]['configure_dict']['exraid'].get('enabled',False)

def check_exraidreport(ctx):
    if ctx.guild is None:
        return False
    channel = ctx.channel
    guild = ctx.guild
    channel_list = [x for x in ctx.bot.guild_dict[guild.id]['configure_dict']['exraid'].get('report_channels',{}).keys()]
    return channel.id in channel_list

def check_inviteset(ctx):
    if ctx.guild is None:
        return False
    guild = ctx.guild
    return ctx.bot.guild_dict[guild.id]['configure_dict']['invite'].get('enabled',False)

def check_exraidchannel(ctx):
    if ctx.guild is None:
        return False
    channel = ctx.channel
    guild = ctx.guild
    level = ctx.bot.guild_dict[guild.id].get('raidchannel_dict',{}).get(channel.id,{}).get('egglevel',False)
    type =  ctx.bot.guild_dict[guild.id].get('raidchannel_dict',{}).get(channel.id,{}).get('type',False)
    return (level == 'EX') or (type == 'exraid')

def check_wildset(ctx):
    if ctx.guild is None:
        return False
    guild = ctx.guild
    return ctx.bot.guild_dict[guild.id]['configure_dict']['wild'].get('enabled',False)

def check_wildreport(ctx):
    if ctx.guild is None:
        return False
    channel = ctx.channel
    guild = ctx.guild
    channel_list = [x for x in ctx.bot.guild_dict[guild.id]['configure_dict']['wild'].get('report_channels',{}).keys()]
    return channel.id in channel_list

def check_teamset(ctx):
    if ctx.guild is None:
        return False
    guild = ctx.guild
    return ctx.bot.guild_dict[guild.id]['configure_dict']['team'].get('enabled',False)

def check_welcomeset(ctx):
    if ctx.guild is None:
        return False
    guild = ctx.guild
    return ctx.bot.guild_dict[guild.id]['configure_dict']['welcome'].get('enabled',False)

def check_archiveset(ctx):
    if ctx.guild is None:
        return False
    guild = ctx.guild
    return ctx.bot.guild_dict[guild.id]['configure_dict']['archive'].get('enabled',False)

def check_researchset(ctx):
    if ctx.guild is None:
        return False
    guild = ctx.guild
    return ctx.bot.guild_dict[guild.id]['configure_dict']['research'].get('enabled',False)

def check_researchreport(ctx):
    if ctx.guild is None:
        return False
    channel = ctx.channel
    guild = ctx.guild
    channel_list = [x for x in ctx.bot.guild_dict[guild.id]['configure_dict']['research'].get('report_channels',{}).keys()]
    return channel.id in channel_list

#Decorators
def allowraidreport():
    def predicate(ctx):
        if check_raidset(ctx):
            if check_raidreport(ctx) or (check_eggchannel(ctx) and check_raidchannel(ctx)):
                return True
            else:
                raise errors.RegionEggChannelCheckFail()
        else:
            raise errors.RaidSetCheckFail()
    return commands.check(predicate)

def allowexraidreport():
    def predicate(ctx):
        if check_exraidset(ctx):
            if check_exraidreport(ctx) or check_exraidchannel(ctx):
                return True
            else:
                raise errors.RegionExRaidChannelCheckFail()
        else:
            raise errors.EXRaidSetCheckFail()
    return commands.check(predicate)

def allowwildreport():
    def predicate(ctx):
        if check_wildset(ctx):
            if check_wildreport(ctx):
                return True
            else:
                raise errors.WildReportChannelCheckFail()
        else:
            raise errors.WildSetCheckFail()
    return commands.check(predicate)

def allowresearchreport():
    def predicate(ctx):
        if check_researchset(ctx):
            if check_researchreport(ctx):
                return True
            else:
                raise errors.ResearchReportChannelCheckFail()
        else:
            raise errors.ResearchSetCheckFail()
    return commands.check(predicate)

def allowinvite():
    def predicate(ctx):
        if check_inviteset(ctx):
            if check_citychannel(ctx):
                return True
            else:
                raise errors.CityChannelCheckFail()
        else:
            raise errors.InviteSetCheckFail()
    return commands.check(predicate)

def allowteam():
    def predicate(ctx):
        if check_teamset(ctx):
            if not check_raidchannel(ctx):
                return True
            else:
                raise errors.NonRaidChannelCheckFail()
        else:
            raise errors.TeamSetCheckFail()
    return commands.check(predicate)

def allowwant():
    def predicate(ctx):
        if check_wantset(ctx):
            if check_wantchannel(ctx):
                print(1)
                return True
            else:
                print(2)
                raise errors.WantChannelCheckFail()
        raise errors.WantSetCheckFail()
    return commands.check(predicate)

def allowarchive():
    def predicate(ctx):
        if check_archiveset(ctx):
            if check_raidchannel(ctx):
                return True
        raise errors.ArchiveSetCheckFail()
    return commands.check(predicate)

def citychannel():
    def predicate(ctx):
        if check_citychannel(ctx):
            return True
        raise errors.CityChannelCheckFail()
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
