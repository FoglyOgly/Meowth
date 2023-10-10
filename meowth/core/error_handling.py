import traceback
import asyncio
import time

from inspect import signature, getfullargspec

import discord
from discord.ext import commands
from discord.ext.commands.view import StringView

from meowth import errors
from meowth.core.context import Context
from .cog_base import Cog

async def delete_error(message, error):
    try:
        await message.delete()
    except (discord.errors.Forbidden, discord.errors.HTTPException):
        pass
    try:
        await error.delete()
    except (discord.errors.Forbidden, discord.errors.HTTPException):
        pass

def missing_args(ctx):
    #prefix = ctx.prefix.replace(ctx.bot.user.mention, '@' + ctx.bot.user.name)
    #command = ctx.invoked_with
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
    if 'self' in sig:
        sig.remove('self')
        arg_num = len(ctx.args) - 2
    args_missing = sig[arg_num:]
    return args_missing

class ErrorHandler(Cog):

    @Cog.listener()
    async def on_command_error(self, ctx, error):
        channel = ctx.channel
        prefix = ctx.prefix.replace(ctx.bot.user.mention, '@' + ctx.bot.user.name)

        if isinstance(error, commands.MissingRequiredArgument):
            fields = {
                'Missing Arguments': "\n".join(missing_args(ctx))
            }
            await ctx.warning(title="Warning: Missing Required Arguments",
                details="Reply to this message with the missing arguments listed below!", fields=fields)
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            reply = await ctx.bot.wait_for('message', check=check)
            ctx.message.content += f' {reply.content}'
            ctx.view = StringView(ctx.message.content)
            ctx.view.get_word()
            try:
                await ctx.command.invoke(ctx)
            except errors.CommandError as exc:
                await ctx.command.dispatch_error(ctx, exc)
            else:
                ctx.bot.dispatch('command_completion', ctx)

        elif isinstance(error, commands.BadArgument):
            await ctx.bot.send_cmd_help(
                ctx, title=f'Bad Argument - {error}', msg_type='error')

        elif isinstance(error, errors.MissingSubcommand):
            await ctx.bot.send_cmd_help(
                ctx, title=f'Missing Subcommand - {error}', msg_type='error')

        elif isinstance(error, commands.DisabledCommand):
            await ctx.send("That command is disabled.")

        elif isinstance(error, commands.CommandInvokeError):
            error_table = ctx.bot.dbi.table('unhandled_errors')
            ctx.bot.logger.exception(
                f"Exception in command '{ctx.command.qualified_name}'",
                exc_info=error.original)
            message = (f"Error in command '{ctx.command.qualified_name}'. This error has been logged "
                       "and will be tracked. Contact support for more information.")
            exception_log = f"Exception in command '{ctx.command.qualified_name}'\n"
            exception_log += "".join(traceback.format_exception(
                type(error), error, error.__traceback__))
            ctx.bot._last_exception = exception_log
            d = {
                'command_name': ctx.command.name,
                'guild_id': ctx.guild.id,
                'channel_id': ctx.channel.id,
                'author_id': ctx.author.id,
                'created': time.time(),
                'full_traceback': exception_log
            }
            insert = error_table.insert
            insert.row(**d)
            await insert.commit()
            await ctx.send(message)

        elif isinstance(error, commands.MissingPermissions):
            await ctx.error("User Missing Required Permissions",
                fields={"Missing": "\n".join(error.missing_permissions)})

        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.error("Bot Missing Required Permissions",
                fields={"Missing": "\n".join(error.missing_permissions)})

        elif isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.CheckFailure):
            pass
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send("That command is not available in DMs.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"This command is on cooldown. Try again in {error.retry_after:.2f}s")

        elif isinstance(error, errors.LocationNotSet):
            msg = f"Location has not been set for this channel. Use **{prefix}setlocation** to fix."
            error = await ctx.error('Location not set', details=msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)

        elif isinstance(error, errors.TeamSetCheckFail):
            msg = f"Meowth! Team Management is not enabled on this server. **{prefix}{ctx.invoked_with}** is unable to be used."
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)

        elif isinstance(error, errors.WantSetCheckFail):
            msg = f"Meowth! Pokemon Notifications are not enabled on this server. **{prefix}{ctx.invoked_with}** is unable to be used."
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)

        elif isinstance(error, errors.WildSetCheckFail):
            msg = f"Meowth! Wild Reporting is not enabled on this server. **{prefix}{ctx.invoked_with}** is unable to be used."
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)

        elif isinstance(error, errors.ReportCheckFail):
            msg = f"Meowth! Reporting is not enabled for this channel. **{prefix}{ctx.invoked_with}** is unable to be used."
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)

        elif isinstance(error, errors.RaidSetCheckFail):
            msg = f"Meowth! Raid Management is not enabled on this server. **{prefix}{ctx.invoked_with}** is unable to be used."
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)

        elif isinstance(error, errors.EXRaidSetCheckFail):
            msg = f"Meowth! EX Raid Management is not enabled on this server. **{prefix}{ctx.invoked_with}** is unable to be used."
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)

        elif isinstance(error, errors.ResearchSetCheckFail):
            msg = f"Meowth! Research Reporting is not enabled on this server. **{prefix}{ctx.invoked_with}** is unable to be used."
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)

        elif isinstance(error, errors.MeetupSetCheckFail):
            msg = f"Meowth! Meetup Reporting is not enabled on this server. **{prefix}{ctx.invoked_with}** is unable to be used."
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)

        elif isinstance(error, errors.ArchiveSetCheckFail):
            msg = f"Meowth! Channel Archiving is not enabled on this server. **{prefix}{ctx.invoked_with}** is unable to be used."
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)

        elif isinstance(error, errors.InviteSetCheckFail):
            msg = f"Meowth! EX Raid Invite is not enabled on this server. **{prefix}{ctx.invoked_with}** is unable to be used."
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)

        elif isinstance(error, errors.CityChannelCheckFail):
            guild = ctx.guild
            msg = f"'Meowth! Please use **{prefix}{ctx.invoked_with}** in "
            city_channels = ctx.bot.guild_dict[guild.id]['configure_dict']['raid']['report_channels']
            if len(city_channels) > 10:
                msg += ('a Region report channel.')
            else:
                msg += ('one of the following region channels:')
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
            msg = f"Meowth! Please use **{prefix}{ctx.invoked_with}** in the following channel"
            want_channels = ctx.bot.guild_dict[guild.id]['configure_dict']['want']['report_channels']
            if len(want_channels) > 1:
                msg += ('s:\n')
            else:
                msg += (': ')
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
            msg = ('Meowth! Please use **{prefix}{cmd_name}** in a Raid channel. Use **{prefix}list** in any ').format(cmd_name=ctx.invoked_with, prefix=prefix)
            city_channels = ctx.bot.guild_dict[guild.id]['configure_dict']['raid']['report_channels']
            if len(city_channels) > 10:
                msg += ('Region report channel to see active raids.')
            else:
                msg += ('of the following Region channels to see active raids:')
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
            msg = ('Meowth! Please use **{prefix}{cmd_name}** in an Egg channel. Use **{prefix}list** in any ').format(cmd_name=ctx.invoked_with, prefix=prefix)
            city_channels = ctx.bot.guild_dict[guild.id]['configure_dict']['raid']['report_channels']
            if len(city_channels) > 10:
                msg += ('Region report channel to see active raids.')
            else:
                msg += ('of the following Region channels to see active raids:')
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
            msg = f"Meowth! **{prefix}{ctx.invoked_with}** can't be used in a Raid channel."
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)

        elif isinstance(error, errors.ActiveRaidChannelCheckFail):
            guild = ctx.guild
            msg = f"Meowth! Please use **{prefix}{ctx.invoked_with}** in an Active Raid channel. Use **{prefix}list** in any "
            city_channels = ctx.bot.guild_dict[guild.id]['configure_dict']['raid']['report_channels']
            try:
                egg_check = ctx.bot.guild_dict[guild.id]['raidchannel_dict'][ctx.channel.id].get('type',None)
                meetup = ctx.bot.guild_dict[guild.id]['raidchannel_dict'][ctx.channel.id].get('meetup',{})
            except:
                egg_check = ""
                meetup = False
            if len(city_channels) > 10:
                msg += ('Region report channel to see active channels.')
            else:
                msg += ('of the following Region channels to see active channels:')
                for c in city_channels:
                    channel = discord.utils.get(guild.channels, id=c)
                    if channel:
                        msg += '\n' + channel.mention
                    else:
                        msg += '\n#deleted-channel'
            if egg_check == "egg" and not meetup:
                msg += f"\nThis is an egg channel. The channel needs to be activated with **{prefix}raid <pokemon>** before I accept commands!"
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)

        elif isinstance(error, errors.ActiveChannelCheckFail):
            guild = ctx.guild
            msg = f"Meowth! Please use **{prefix}{ctx.invoked_with}** in an Active channel. Use **{prefix}list** in any "
            city_channels = ctx.bot.guild_dict[guild.id]['configure_dict']['raid']['report_channels']
            try:
                egg_check = ctx.bot.guild_dict[guild.id]['raidchannel_dict'][ctx.channel.id].get('type',None)
                meetup = ctx.bot.guild_dict[guild.id]['raidchannel_dict'][ctx.channel.id].get('meetup',{})
            except:
                egg_check = ""
                meetup = False
            if len(city_channels) > 10:
                msg += ('Region report channel to see active raids.')
            else:
                msg += ('of the following Region channels to see active raids:')
                for c in city_channels:
                    channel = discord.utils.get(guild.channels, id=c)
                    if channel:
                        msg += '\n' + channel.mention
                    else:
                        msg += '\n#deleted-channel'
            if egg_check == "egg" and not meetup:
                msg += f"\nThis is an egg channel. The channel needs to be activated with **{prefix}raid <pokemon>** before I accept commands!"
            error = await ctx.channel.send(msg)
            await asyncio.sleep(10)
            await delete_error(ctx.message, error)

        elif isinstance(error, errors.CityRaidChannelCheckFail):
            guild = ctx.guild
            msg = f"Meowth! Please use **{prefix}{ctx.invoked_with}** in either a Raid channel or "
            city_channels = ctx.bot.guild_dict[guild.id]['configure_dict']['raid']['report_channels']
            if len(city_channels) > 10:
                msg += ('a Region report channel.')
            else:
                msg += ('one of the following region channels:')
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
            msg = f"Meowth! Please use **{prefix}{ctx.invoked_with}** in either a Raid Egg channel or "
            city_channels = ctx.bot.guild_dict[guild.id]['configure_dict']['raid']['report_channels']
            if len(city_channels) > 10:
                msg += ('a Region report channel.')
            else:
                msg += ('one of the following region channels:')
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
            msg = f"Meowth! Please use **{prefix}{ctx.invoked_with}** in either a EX Raid channel or one of the following region channels:"
            city_channels = ctx.bot.guild_dict[guild.id]['configure_dict']['exraid']['report_channels']
            if len(city_channels) > 10:
                msg += ('a Region report channel.')
            else:
                msg += ('one of the following region channels:')
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
            msg = f"Meowth! Please use **{prefix}{ctx.invoked_with}** in a EX Raid channel. Use **{prefix}list** in any of the following region channels to see active raids:"
            city_channels = ctx.bot.guild_dict[guild.id]['configure_dict']['exraid']['report_channels']
            if len(city_channels) > 10:
                msg += ('a Region report channel.')
            else:
                msg += ('one of the following region channels:')
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
            msg = f"Meowth! Please use **{prefix}{ctx.invoked_with}** in "
            city_channels = ctx.bot.guild_dict[guild.id]['configure_dict']['research']['report_channels']
            if len(city_channels) > 10:
                msg += ('a Region report channel.')
            else:
                msg += ('one of the following region channels:')
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
            msg = f"Meowth! Please use **{prefix}{ctx.invoked_with}** in "
            city_channels = ctx.bot.guild_dict[guild.id]['configure_dict']['meetup']['report_channels']
            if len(city_channels) > 10:
                msg += ('a Region report channel.')
            else:
                msg += ('one of the following region channels:')
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
            msg = f"Meowth! Please use **{prefix}{ctx.invoked_with}** in "
            city_channels = ctx.bot.guild_dict[guild.id]['configure_dict']['wild']['report_channels']
            if len(city_channels) > 10:
                msg += ('a Region report channel.')
            else:
                msg += ('one of the following region channels:')
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
    bot.add_cog(ErrorHandler(bot))
