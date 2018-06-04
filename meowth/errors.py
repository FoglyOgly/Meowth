
import discord
from discord.ext import commands
from discord.ext.commands.errors import CommandError
from inspect import signature, getfullargspec
import asyncio

class TeamSetCheckFail(CommandError):
    'Exception raised checks.teamset fails'
    pass

class WantSetCheckFail(CommandError):
    'Exception raised checks.wantset fails'
    pass

class WildSetCheckFail(CommandError):
    'Exception raised checks.wildset fails'
    pass

class ReportCheckFail(CommandError):
    'Exception raised checks.allowreport fails'
    pass

class RaidSetCheckFail(CommandError):
    'Exception raised checks.raidset fails'
    pass

class EXRaidSetCheckFail(CommandError):
    'Exception raised checks.exraidset fails'
    pass

class ResearchSetCheckFail(CommandError):
    'Exception raised checks.researchset fails'
    pass

class MeetupSetCheckFail(CommandError):
    'Exception raised checks.meetupset fails'
    pass

class ArchiveSetCheckFail(CommandError):
    'Exception raised checks.archiveset fails'
    pass

class InviteSetCheckFail(CommandError):
    'Exception raised checks.inviteset fails'
    pass

class CityChannelCheckFail(CommandError):
    'Exception raised checks.citychannel fails'
    pass

class WantChannelCheckFail(CommandError):
    'Exception raised checks.wantchannel fails'
    pass

class RaidChannelCheckFail(CommandError):
    'Exception raised checks.raidchannel fails'
    pass

class EggChannelCheckFail(CommandError):
    'Exception raised checks.eggchannel fails'
    pass

class NonRaidChannelCheckFail(CommandError):
    'Exception raised checks.nonraidchannel fails'
    pass

class ActiveRaidChannelCheckFail(CommandError):
    'Exception raised checks.activeraidchannel fails'
    pass

class ActiveChannelCheckFail(CommandError):
    'Exception raised checks.activechannel fails'
    pass

class CityRaidChannelCheckFail(CommandError):
    'Exception raised checks.cityraidchannel fails'
    pass

class RegionEggChannelCheckFail(CommandError):
    'Exception raised checks.cityeggchannel fails'
    pass

class RegionExRaidChannelCheckFail(CommandError):
    'Exception raised checks.allowexraidreport fails'
    pass

class ExRaidChannelCheckFail(CommandError):
    'Exception raised checks.cityeggchannel fails'
    pass

class ResearchReportChannelCheckFail(CommandError):
    'Exception raised checks.researchreport fails'
    pass

class MeetupReportChannelCheckFail(CommandError):
    'Exception raised checks.researchreport fails'
    pass

class WildReportChannelCheckFail(CommandError):
    'Exception raised checks.researchreport fails'
    pass

async def delete_error(message, error):
    try:
        await message.delete()
    except (discord.errors.Forbidden, discord.errors.HTTPException):
        pass
    try:
        await error.delete()
    except (discord.errors.Forbidden, discord.errors.HTTPException):
        pass

def missing_arg_msg(ctx):
    prefix = ctx.prefix.replace(ctx.bot.user.mention, '@' + ctx.bot.user.name)
    command = ctx.invoked_with
    callback = ctx.command.callback
    sig = list(signature(callback).parameters.keys())
    (args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations) = getfullargspec(callback)
    rq_args = []
    nr_args = []
    if defaults:
        rqargs = args[:(- len(defaults))]
    else:
        rqargs = args
    if varargs:
        if varargs != 'args':
            rqargs.append(varargs)
    arg_num = len(ctx.args) - 1
    sig.remove('ctx')
    args_missing = sig[arg_num:]
    msg = _("Meowth! I'm missing some details! Usage: {prefix}{command}").format(prefix=prefix, command=command)
    for a in sig:
        if kwonlydefaults:
            if a in kwonlydefaults.keys():
                msg += ' [{0}]'.format(a)
                continue
        if a in args_missing:
            msg += ' **<{0}>**'.format(a)
        else:
            msg += ' <{0}>'.format(a)
    return msg

def custom_error_handling(bot, logger):

    @bot.event
    async def on_command_error(ctx, error):
        channel = ctx.channel
        prefix = ctx.prefix.replace(ctx.bot.user.mention, '@' + ctx.bot.user.name)
        if isinstance(error, commands.MissingRequiredArgument):
            error = await ctx.channel.send(missing_arg_msg(ctx))
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)
        elif isinstance(error, commands.BadArgument):
            formatter = commands.formatter.HelpFormatter()
            page = await formatter.format_help_for(ctx, ctx.command)
            error = await ctx.channel.send(page[0])
            await asyncio.sleep(20)
            await delete_error(ctx.message, error)
        elif isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.CheckFailure):
            pass
        elif isinstance(error, TeamSetCheckFail):
            msg = _('Meowth! Team Management is not enabled on this server. **{prefix}{cmd_name}** is unable to be used.').format(cmd_name=ctx.invoked_with, prefix=prefix)
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)
        elif isinstance(error, WantSetCheckFail):
            msg = _('Meowth! Pokemon Notifications are not enabled on this server. **{prefix}{cmd_name}** is unable to be used.').format(cmd_name=ctx.invoked_with, prefix=prefix)
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)
        elif isinstance(error, WildSetCheckFail):
            msg = _('Meowth! Wild Reporting is not enabled on this server. **{prefix}{cmd_name}** is unable to be used.').format(cmd_name=ctx.invoked_with, prefix=prefix)
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)
        elif isinstance(error, ReportCheckFail):
            msg = _('Meowth! Reporting is not enabled for this channel. **{prefix}{cmd_name}** is unable to be used.').format(cmd_name=ctx.invoked_with, prefix=prefix)
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)
        elif isinstance(error, RaidSetCheckFail):
            msg = _('Meowth! Raid Management is not enabled on this server. **{prefix}{cmd_name}** is unable to be used.').format(cmd_name=ctx.invoked_with, prefix=prefix)
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)
        elif isinstance(error, EXRaidSetCheckFail):
            msg = _('Meowth! EX Raid Management is not enabled on this server. **{prefix}{cmd_name}** is unable to be used.').format(cmd_name=ctx.invoked_with, prefix=prefix)
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)
        elif isinstance(error, ResearchSetCheckFail):
            msg = _('Meowth! Research Reporting is not enabled on this server. **{prefix}{cmd_name}** is unable to be used.').format(cmd_name=ctx.invoked_with, prefix=prefix)
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)
        elif isinstance(error, MeetupSetCheckFail):
            msg = _('Meowth! Meetup Reporting is not enabled on this server. **{prefix}{cmd_name}** is unable to be used.').format(cmd_name=ctx.invoked_with, prefix=prefix)
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)
        elif isinstance(error, ArchiveSetCheckFail):
            msg = _('Meowth! Channel Archiving is not enabled on this server. **{prefix}{cmd_name}** is unable to be used.').format(cmd_name=ctx.invoked_with, prefix=prefix)
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)
        elif isinstance(error, InviteSetCheckFail):
            msg = _('Meowth! EX Raid Invite is not enabled on this server. **{prefix}{cmd_name}** is unable to be used.').format(cmd_name=ctx.invoked_with, prefix=prefix)
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)
        elif isinstance(error, CityChannelCheckFail):
            guild = ctx.guild
            msg = _('Meowth! Please use **{prefix}{cmd_name}** in ').format(cmd_name=ctx.invoked_with, prefix=prefix)
            city_channels = bot.guild_dict[guild.id]['configure_dict']['raid']['report_channels']
            if len(city_channels) > 10:
                msg += _('a Region report channel.')
            else:
                msg += _('one of the following region channels:')
                for c in city_channels:
                    channel = discord.utils.get(guild.channels, id=c)
                    if channel:
                        msg += '\n' + channel.mention
                    else:
                        msg += '\n#deleted-channel'
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)
        elif isinstance(error, WantChannelCheckFail):
            guild = ctx.guild
            msg = _('Meowth! Please use **{prefix}{cmd_name}** in the following channel').format(cmd_name=ctx.invoked_with, prefix=prefix)
            want_channels = bot.guild_dict[guild.id]['configure_dict']['want']['report_channels']
            if len(want_channels) > 1:
                msg += _('s:\n')
            else:
                msg += _(': ')
            counter = 0
            for c in want_channels:
                channel = discord.utils.get(guild.channels, id=c)
                if counter > 0:
                    msg += '\n'
                if channel:
                    msg += channel.mention
                else:
                    msg += '\n#deleted-channel'
                counter += 1
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)
        elif isinstance(error, RaidChannelCheckFail):
            guild = ctx.guild
            msg = _('Meowth! Please use **{prefix}{cmd_name}** in a Raid channel. Use **{prefix}list** in any ').format(cmd_name=ctx.invoked_with, prefix=prefix)
            city_channels = bot.guild_dict[guild.id]['configure_dict']['raid']['report_channels']
            if len(city_channels) > 10:
                msg += _('Region report channel to see active raids.')
            else:
                msg += _('of the following Region channels to see active raids:')
                for c in city_channels:
                    channel = discord.utils.get(guild.channels, id=c)
                    if channel:
                        msg += '\n' + channel.mention
                    else:
                        msg += '\n#deleted-channel'
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)
        elif isinstance(error, EggChannelCheckFail):
            guild = ctx.guild
            msg = _('Meowth! Please use **{prefix}{cmd_name}** in an Egg channel. Use **{prefix}list** in any ').format(cmd_name=ctx.invoked_with, prefix=prefix)
            city_channels = bot.guild_dict[guild.id]['configure_dict']['raid']['report_channels']
            if len(city_channels) > 10:
                msg += _('Region report channel to see active raids.')
            else:
                msg += _('of the following Region channels to see active raids:')
                for c in city_channels:
                    channel = discord.utils.get(guild.channels, id=c)
                    if channel:
                        msg += '\n' + channel.mention
                    else:
                        msg += '\n#deleted-channel'
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)
        elif isinstance(error, NonRaidChannelCheckFail):
            msg = _("Meowth! **{prefix}{cmd_name}** can't be used in a Raid channel.").format(cmd_name=ctx.invoked_with, prefix=prefix)
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)
        elif isinstance(error, ActiveRaidChannelCheckFail):
            guild = ctx.guild
            msg = _('Meowth! Please use **{prefix}{cmd_name}** in an Active Raid channel. Use **{prefix}list** in any ').format(cmd_name=ctx.invoked_with, prefix=prefix)
            city_channels = bot.guild_dict[guild.id]['configure_dict']['raid']['report_channels']
            try:
                egg_check = bot.guild_dict[guild.id]['raidchannel_dict'][ctx.channel.id].get('type',None)
                meetup = bot.guild_dict[guild.id]['raidchannel_dict'][ctx.channel.id].get('meetup',{})
            except:
                egg_check = ""
                meetup = False
            if len(city_channels) > 10:
                msg += _('Region report channel to see active channels.')
            else:
                msg += _('of the following Region channels to see active channels:')
                for c in city_channels:
                    channel = discord.utils.get(guild.channels, id=c)
                    if channel:
                        msg += '\n' + channel.mention
                    else:
                        msg += '\n#deleted-channel'
            if egg_check == "egg" and not meetup:
                msg += _('\nThis is an egg channel. The channel needs to be activated with **{prefix}raid <pokemon>** before I accept commands!').format(prefix=prefix)
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)
        elif isinstance(error, ActiveChannelCheckFail):
            guild = ctx.guild
            msg = _('Meowth! Please use **{prefix}{cmd_name}** in an Active channel. Use **{prefix}list** in any ').format(cmd_name=ctx.invoked_with, prefix=prefix)
            city_channels = bot.guild_dict[guild.id]['configure_dict']['raid']['report_channels']
            try:
                egg_check = bot.guild_dict[guild.id]['raidchannel_dict'][ctx.channel.id].get('type',None)
                meetup = bot.guild_dict[guild.id]['raidchannel_dict'][ctx.channel.id].get('meetup',{})
            except:
                egg_check = ""
                meetup = False
            if len(city_channels) > 10:
                msg += _('Region report channel to see active raids.')
            else:
                msg += _('of the following Region channels to see active raids:')
                for c in city_channels:
                    channel = discord.utils.get(guild.channels, id=c)
                    if channel:
                        msg += '\n' + channel.mention
                    else:
                        msg += '\n#deleted-channel'
            if egg_check == "egg" and not meetup:
                msg += _('\nThis is an egg channel. The channel needs to be activated with **{prefix}raid <pokemon>** before I accept commands!').format(prefix=prefix)
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)
        elif isinstance(error, CityRaidChannelCheckFail):
            guild = ctx.guild
            msg = _('Meowth! Please use **{prefix}{cmd_name}** in either a Raid channel or ').format(cmd_name=ctx.invoked_with, prefix=prefix)
            city_channels = bot.guild_dict[guild.id]['configure_dict']['raid']['report_channels']
            if len(city_channels) > 10:
                msg += _('a Region report channel.')
            else:
                msg += _('one of the following region channels:')
                for c in city_channels:
                    channel = discord.utils.get(guild.channels, id=c)
                    if channel:
                        msg += '\n' + channel.mention
                    else:
                        msg += '\n#deleted-channel'
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)
        elif isinstance(error, RegionEggChannelCheckFail):
            guild = ctx.guild
            msg = _('Meowth! Please use **{prefix}{cmd_name}** in either a Raid Egg channel or ').format(cmd_name=ctx.invoked_with, prefix=prefix)
            city_channels = bot.guild_dict[guild.id]['configure_dict']['raid']['report_channels']
            if len(city_channels) > 10:
                msg += _('a Region report channel.')
            else:
                msg += _('one of the following region channels:')
                for c in city_channels:
                    channel = discord.utils.get(guild.channels, id=c)
                    if channel:
                        msg += '\n' + channel.mention
                    else:
                        msg += '\n#deleted-channel'
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)
        elif isinstance(error, RegionExRaidChannelCheckFail):
            guild = ctx.guild
            msg = _('Meowth! Please use **{prefix}{cmd_name}** in either a EX Raid channel or ').format(cmd_name=ctx.invoked_with, prefix=prefix)
            city_channels = bot.guild_dict[guild.id]['configure_dict']['exraid']['report_channels']
            if len(city_channels) > 10:
                msg += _('a Region report channel.')
            else:
                msg += _('one of the following region channels:')
                for c in city_channels:
                    channel = discord.utils.get(guild.channels, id=c)
                    if channel:
                        msg += '\n' + channel.mention
                    else:
                        msg += '\n#deleted-channel'
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)
        elif isinstance(error, ExRaidChannelCheckFail):
            guild = ctx.guild
            msg = _('Meowth! Please use **{prefix}{cmd_name}** in a EX Raid channel. Use **{prefix}list** in ').format(cmd_name=ctx.invoked_with, prefix=prefix)
            city_channels = bot.guild_dict[guild.id]['configure_dict']['exraid']['report_channels']
            if len(city_channels) > 10:
                msg += _('a Region report channel.')
            else:
                msg += _('one of the following region channels:')
                for c in city_channels:
                    channel = discord.utils.get(guild.channels, id=c)
                    if channel:
                        msg += '\n' + channel.mention
                    else:
                        msg += '\n#deleted-channel'
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)
        elif isinstance(error, ResearchReportChannelCheckFail):
            guild = ctx.guild
            msg = _('Meowth! Please use **{prefix}{cmd_name}** in ').format(cmd_name=ctx.invoked_with, prefix=prefix)
            city_channels = bot.guild_dict[guild.id]['configure_dict']['research']['report_channels']
            if len(city_channels) > 10:
                msg += _('a Region report channel.')
            else:
                msg += _('one of the following region channels:')
                for c in city_channels:
                    channel = discord.utils.get(guild.channels, id=c)
                    if channel:
                        msg += '\n' + channel.mention
                    else:
                        msg += '\n#deleted-channel'
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)
        elif isinstance(error, MeetupReportChannelCheckFail):
            guild = ctx.guild
            msg = _('Meowth! Please use **{prefix}{cmd_name}** in ').format(cmd_name=ctx.invoked_with, prefix=prefix)
            city_channels = bot.guild_dict[guild.id]['configure_dict']['meetup']['report_channels']
            if len(city_channels) > 10:
                msg += _('a Region report channel.')
            else:
                msg += _('one of the following region channels:')
                for c in city_channels:
                    channel = discord.utils.get(guild.channels, id=c)
                    if channel:
                        msg += '\n' + channel.mention
                    else:
                        msg += '\n#deleted-channel'
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)
        elif isinstance(error,WildReportChannelCheckFail):
            guild = ctx.guild
            msg = _('Meowth! Please use **{prefix}{cmd_name}** in ').format(cmd_name=ctx.invoked_with, prefix=prefix)
            city_channels = bot.guild_dict[guild.id]['configure_dict']['wild']['report_channels']
            if len(city_channels) > 10:
                msg += _('a Region report channel.')
            else:
                msg += _('one of the following region channels:')
                for c in city_channels:
                    channel = discord.utils.get(guild.channels, id=c)
                    if channel:
                        msg += '\n' + channel.mention
                    else:
                        msg += '\n#deleted-channel'
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)
        else:
            logger.exception(type(error).__name__, exc_info=error)
