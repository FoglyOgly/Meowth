from discord.ext import commands

async def is_trade_enabled(ctx):
    report_table = ctx.bot.dbi.table('report_channels')
    query = report_table.query('trade')
    query.where(channelid=ctx.channel.id)
    trade = await query.get_value()
    if not trade:
        return False
    else:
        return True
    
def trade_enabled():
    return commands.check(is_trade_enabled)