from discord.ext import commands

async def is_wild_enabled(ctx):
    report_table = ctx.bot.dbi.table('report_channels')
    query = report_table.query('wild')
    query.where(channelid=ctx.channel.id)
    wild = await query.get_value()
    if not wild:
        return False
    else:
        return True
    
def wild_enabled():
    return commands.check(is_wild_enabled)