from discord.ext import commands

async def is_raid_enabled(ctx):
    report_table = ctx.bot.dbi.table('report_channels')
    query = report_table.query('raid')
    query.where(channelid=ctx.channel.id)
    raid = await query.get_value()
    if not raid:
        return False
    else:
        return True

async def raid_category(ctx, level):
    report_table = ctx.bot.dbi.table('report_channels')
    query = report_table.query(f'category_{level}')
    query.where(channelid=ctx.channel.id)
    cat = await query.get_value()
    return cat

def raid_enabled():
    return commands.check(is_raid_enabled)