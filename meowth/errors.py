import discord
from discord.ext import commands
from discord.ext.commands.errors import CommandError

class TeamSetCheckFail(CommandError):
    """Exception raised checks.teamset fails"""
    pass

class WantSetCheckFail(CommandError):
    """Exception raised checks.wantset fails"""
    pass

class WildSetCheckFail(CommandError):
    """Exception raised checks.wildset fails"""
    pass

class RaidSetCheckFail(CommandError):
    """Exception raised checks.raidset fails"""
    pass

class CityChannelCheckFail(CommandError):
    """Exception raised checks.citychannel fails"""
    pass

class WantChannelCheckFail(CommandError):
    """Exception raised checks.wantchannel fails"""
    pass

class RaidChannelCheckFail(CommandError):
    """Exception raised checks.raidchannel fails"""
    pass

class NonRaidChannelCheckFail(CommandError):
    """Exception raised checks.nonraidchannel fails"""
    pass

class ActiveRaidChannelCheckFail(CommandError):
    """Exception raised checks.activeraidchannel fails"""
    pass

class CityRaidChannelCheckFail(CommandError):
    """Exception raised checks.cityraidchannel fails"""
    pass

class RegionEggChannelCheckFail(CommandError):
    """Exception raised checks.cityeggchannel fails"""
    pass

class RegionExRaidChannelCheckFail(CommandError):
    """Exception raised checks.cityeggchannel fails"""
    pass

class ExRaidChannelCheckFail(CommandError):
    """Exception raised checks.cityeggchannel fails"""
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



        elif isinstance(error, TeamSetCheckFail):
            msg = "Meowth! Team Management is not enabled on this server. **!{cmd_name}** is unable to be used.".format(cmd_name=ctx.command.name)
            await bot.send_message(ctx.message.channel,msg)
            pass

        elif isinstance(error, WantSetCheckFail):
            msg = "Meowth! Pokemon Management is not enabled on this server. **!{cmd_name}** is unable to be used.".format(cmd_name=ctx.command.name)
            await bot.send_message(ctx.message.channel,msg)
            pass

        elif isinstance(error, WildSetCheckFail):
            msg = "Meowth! Wild Reporting is not enabled on this server. **!{cmd_name}** is unable to be used.".format(cmd_name=ctx.command.name)
            await bot.send_message(ctx.message.channel,msg)
            pass

        elif isinstance(error, RaidSetCheckFail):
            msg = "Meowth! Raid Management is not enabled on this server. **!{cmd_name}** is unable to be used.".format(cmd_name=ctx.command.name)
            await bot.send_message(ctx.message.channel,msg)
            pass

        elif isinstance(error, CityChannelCheckFail):
            server = ctx.message.server
            msg = "Meowth! Please use **!{cmd_name}** in one of the following region channels:".format(cmd_name=ctx.command.name)
            city_channels = bot.server_dict[server]['city_channels']
            for c in city_channels:
                channel = discord.utils.get(server.channels,name=c)
                msg += "\n" + channel.mention
            await bot.send_message(ctx.message.channel,msg)
            pass

        elif isinstance(error, WantChannelCheckFail):
            server = ctx.message.server
            msg = "Meowth! Please use **!{cmd_name}** in the following channel".format(cmd_name=ctx.command.name)
            want_channels = bot.server_dict[server]['want_channel_list']

            if len(want_channels) > 1:
                msg += "s:\n"
            else:
                msg += ": "
            counter = 0
            for c in want_channels:
                channel = discord.utils.get(server.channels,id=c.id)
                if counter > 0:
                    msg += "\n"
                msg += channel.mention
                counter += 1
            await bot.send_message(ctx.message.channel,msg)
            pass

        elif isinstance(error, RaidChannelCheckFail):
            server = ctx.message.server
            msg = "Meowth! Please use **!{cmd_name}** in a Raid channel. Use **!list** in any of the following region channels to see active raids:".format(cmd_name=ctx.command.name)
            city_channels = bot.server_dict[server]['city_channels']
            for c in city_channels:
                channel = discord.utils.get(server.channels,name=c)
                msg += "\n" + channel.mention
            await bot.send_message(ctx.message.channel,msg)
            pass

        elif isinstance(error, NonRaidChannelCheckFail):
            msg = "Meowth! **!{cmd_name}** can't be used in a Raid channel.".format(cmd_name=ctx.command.name)
            await bot.send_message(ctx.message.channel,msg)
            pass

        elif isinstance(error, ActiveRaidChannelCheckFail):
            server = ctx.message.server
            msg = "Meowth! Please use **!{cmd_name}** in an Active Raid channel. Use **!list** in any of the following region channels to see active raids:".format(cmd_name=ctx.command.name)
            city_channels = bot.server_dict[server]['city_channels']
            for c in city_channels:
                channel = discord.utils.get(server.channels,name=c)
                msg += "\n" + channel.mention
            await bot.send_message(ctx.message.channel,msg)
            pass

        elif isinstance(error, CityRaidChannelCheckFail):
            server = ctx.message.server
            msg = "Meowth! Please use **!{cmd_name}** in either a Raid channel or one of the following region channels:".format(cmd_name=ctx.command.name)
            city_channels = bot.server_dict[server]['city_channels']
            for c in city_channels:
                channel = discord.utils.get(server.channels,name=c)
                msg += "\n" + channel.mention
            await bot.send_message(ctx.message.channel,msg)
            pass

        elif isinstance(error, RegionEggChannelCheckFail):
            server = ctx.message.server
            msg = "Meowth! Please use **!{cmd_name}** in either a Raid Egg channel or one of the following region channels:".format(cmd_name=ctx.command.name)
            city_channels = bot.server_dict[server]['city_channels']
            for c in city_channels:
                channel = discord.utils.get(server.channels,name=c)
                msg += "\n" + channel.mention
            await bot.send_message(ctx.message.channel,msg)
            pass

        elif isinstance(error, RegionExRaidChannelCheckFail):
            server = ctx.message.server
            msg = "Meowth! Please use **!{cmd_name}** in either a EX Raid channel or one of the following region channels:".format(cmd_name=ctx.command.name)
            city_channels = bot.server_dict[server]['city_channels']
            for c in city_channels:
                channel = discord.utils.get(server.channels,name=c)
                msg += "\n" + channel.mention
            await bot.send_message(ctx.message.channel,msg)
            pass

        elif isinstance(error, ExRaidChannelCheckFail):
            server = ctx.message.server
            msg = "Meowth! Please use **!{cmd_name}** in a EX Raid channel. Use **!list** in any of the following region channels to see active raids:".format(cmd_name=ctx.command.name)
            city_channels = bot.server_dict[server]['city_channels']
            for c in city_channels:
                channel = discord.utils.get(server.channels,name=c)
                msg += "\n" + channel.mention
            await bot.send_message(ctx.message.channel,msg)
            pass

        else:
            logger.exception(type(error).__name__, exc_info=error)
