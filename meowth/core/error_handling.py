import traceback
import asyncio

from inspect import signature, getfullargspec

import discord
from discord.ext import commands

from meowth import errors

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
    args, varargs, __, defaults, __, kwonlydefaults, __ = getfullargspec(callback)
    if defaults:
        rq_args = args[:(- len(defaults))]
    else:
        rq_args = args
    if varargs:
        if varargs != 'args':
            rq_args.append(varargs)
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

class ErrorHandler:

    async def on_command_error(self, ctx, error):
        channel = ctx.channel
        prefix = ctx.prefix.replace(ctx.bot.user.mention, '@' + ctx.bot.user.name)

        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.bot.send_cmd_help(
                ctx, title='Missing Arguments', msg_type='error')

        elif isinstance(error, commands.BadArgument):
            await ctx.bot.send_cmd_help(
                ctx, title=f'Bad Argument - {error}', msg_type='error')

        elif isinstance(error, errors.MissingSubcommand):
            await ctx.bot.send_cmd_help(
                ctx, title=f'Missing Subcommand - {error}', msg_type='error')

        elif isinstance(error, commands.DisabledCommand):
            await ctx.send("That command is disabled.")

        elif isinstance(error, commands.CommandInvokeError):
            ctx.bot.logger.exception(
                "Exception in command '{}'".format(ctx.command.qualified_name),
                exc_info=error.original)
            message = ("Error in command '{}'. Check your console or "
                       "logs for details."
                       "".format(ctx.command.qualified_name))
            exception_log = ("Exception in command '{}'\n"
                             "".format(ctx.command.qualified_name))
            exception_log += "".join(traceback.format_exception(
                type(error), error, error.__traceback__))
            ctx.bot._last_exception = exception_log
            await ctx.send(message)

        elif isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.CheckFailure):
            pass
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send("That command is not available in DMs.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send("This command is on cooldown. "
                           "Try again in {:.2f}s"
                           "".format(error.retry_after))

        elif isinstance(error, errors.TeamSetCheckFail):
            msg = _('Meowth! Team Management is not enabled on this server. **{prefix}{cmd_name}** is unable to be used.').format(cmd_name=ctx.invoked_with, prefix=prefix)
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)

        elif isinstance(error, errors.WantSetCheckFail):
            msg = _('Meowth! Pokemon Notifications are not enabled on this server. **{prefix}{cmd_name}** is unable to be used.').format(cmd_name=ctx.invoked_with, prefix=prefix)
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)

        elif isinstance(error, errors.WildSetCheckFail):
            msg = _('Meowth! Wild Reporting is not enabled on this server. **{prefix}{cmd_name}** is unable to be used.').format(cmd_name=ctx.invoked_with, prefix=prefix)
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)

        elif isinstance(error, errors.ReportCheckFail):
            msg = _('Meowth! Reporting is not enabled for this channel. **{prefix}{cmd_name}** is unable to be used.').format(cmd_name=ctx.invoked_with, prefix=prefix)
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)

        elif isinstance(error, errors.RaidSetCheckFail):
            msg = _('Meowth! Raid Management is not enabled on this server. **{prefix}{cmd_name}** is unable to be used.').format(cmd_name=ctx.invoked_with, prefix=prefix)
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)

        elif isinstance(error, errors.EXRaidSetCheckFail):
            msg = _('Meowth! EX Raid Management is not enabled on this server. **{prefix}{cmd_name}** is unable to be used.').format(cmd_name=ctx.invoked_with, prefix=prefix)
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)

        elif isinstance(error, errors.ResearchSetCheckFail):
            msg = _('Meowth! Research Reporting is not enabled on this server. **{prefix}{cmd_name}** is unable to be used.').format(cmd_name=ctx.invoked_with, prefix=prefix)
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)

        elif isinstance(error, errors.MeetupSetCheckFail):
            msg = _('Meowth! Meetup Reporting is not enabled on this server. **{prefix}{cmd_name}** is unable to be used.').format(cmd_name=ctx.invoked_with, prefix=prefix)
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)

        elif isinstance(error, errors.ArchiveSetCheckFail):
            msg = _('Meowth! Channel Archiving is not enabled on this server. **{prefix}{cmd_name}** is unable to be used.').format(cmd_name=ctx.invoked_with, prefix=prefix)
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)

        elif isinstance(error, errors.InviteSetCheckFail):
            msg = _('Meowth! EX Raid Invite is not enabled on this server. **{prefix}{cmd_name}** is unable to be used.').format(cmd_name=ctx.invoked_with, prefix=prefix)
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)

        elif isinstance(error, errors.CityChannelCheckFail):
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

        elif isinstance(error, errors.WantChannelCheckFail):
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

        elif isinstance(error, errors.RaidChannelCheckFail):
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

        elif isinstance(error, errors.EggChannelCheckFail):
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
        elif isinstance(error, errors.NonRaidChannelCheckFail):
            msg = _("Meowth! **{prefix}{cmd_name}** can't be used in a Raid channel.").format(cmd_name=ctx.invoked_with, prefix=prefix)
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)

        elif isinstance(error, errors.ActiveRaidChannelCheckFail):
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

        elif isinstance(error, errors.ActiveChannelCheckFail):
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

        elif isinstance(error, errors.CityRaidChannelCheckFail):
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

        elif isinstance(error, errors.RegionEggChannelCheckFail):
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

        elif isinstance(error, errors.RegionExRaidChannelCheckFail):
            guild = ctx.guild
            msg = _('Meowth! Please use **{prefix}{cmd_name}** in either a EX Raid channel or one of the following region channels:').format(cmd_name=ctx.invoked_with, prefix=prefix)
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

        elif isinstance(error, errors.ExRaidChannelCheckFail):
            guild = ctx.guild
            msg = _('Meowth! Please use **{prefix}{cmd_name}** in a EX Raid channel. Use **{prefix}list** in any of the following region channels to see active raids:').format(cmd_name=ctx.invoked_with, prefix=prefix)
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

        elif isinstance(error, errors.ResearchReportChannelCheckFail):
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

        elif isinstance(error, errors.MeetupReportChannelCheckFail):
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

        elif isinstance(error, errors.WildReportChannelCheckFail):
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
            ctx.bot.logger.exception(type(error).__name__, exc_info=error)

def setup(bot):
    bot.add_cog(ErrorHandler())
