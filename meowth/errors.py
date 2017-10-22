import discord
from discord.ext import commands
from discord.ext.commands.errors import CommandError

class NonRegionEggChannel(CommandError):
    """Exception raised when a command requiring a Regional Channel
    is attempted outside of one"""
    pass

def custom_error_handling(bot,logger):
    @bot.event
    async def on_command_error(error, ctx):
        channel = ctx.message.channel

        if isinstance(error, commands.MissingRequiredArgument):
            pages = bot.formatter.format_help_for(ctx,ctx.command)
            for page in pages:
                await bot.send_message(ctx.message.channel, page)

        elif isinstance(error, commands.BadArgument):
            pages = bot.formatter.format_help_for(ctx,ctx.command)
            for page in pages:
                await bot.send_message(ctx.message.channel, page)

        elif isinstance(error, commands.CommandNotFound):
            pass

        elif isinstance(error, commands.CheckFailure):
            pass

        elif isinstance(error, NonRegionEggChannel):
            server = ctx.message.server
            msg = "Meowth! Please use **!{cmd_name}** in either a Raid Egg channel or one of the following region channels:".format(cmd_name=ctx.command.name)
            city_channels = bot.server_dict[server]['city_channels']
            for c in city_channels:
                channel = discord.utils.get(server.channels,name=c)
                msg += "\n" + channel.mention
            await bot.send_message(ctx.message.channel,msg)
            pass

        else:
            logger.exception(type(error).__name__, exc_info=error)