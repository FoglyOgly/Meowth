from discord.ext import commands

async def check_forecast_enabled(ctx):
    table = ctx.bot.dbi.table('forecast_config')
    guild_id = ctx.guild.id
    query = table.query('enabled')
    try:
        query.where(guild_id=guild_id)
        return await query.get_value()
    except:
        return False
    
def forecast_enabled():
    return commands.check(check_forecast_enabled)

async def check_channel_has_location(ctx):
    report_table = ctx.bot.dbi.table('report_channels')
    channel_id = ctx.channel.id
    report_query = report_table.query('lat', 'lon', 'radius')
    try:
        report_query.where(channelid=channel_id)
        data = await report_query.get()
        if data:
            ctx.location = 'channel'
            return True
    except:
        pass
    return False

def channel_has_location():
    return commands.check(check_channel_has_location)
