from discord.ext import commands


async def is_want_enabled(ctx):
    report_table = ctx.bot.dbi.table('report_channels')
    query = report_table.query('user')
    query.where(channelid=ctx.channel.id)
    want = await query.get_value()
    return want

def want_enabled():
    return commands.check(is_want_enabled)