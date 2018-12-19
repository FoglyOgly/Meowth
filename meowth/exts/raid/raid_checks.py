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

async def is_raid_channel(ctx):
    raid_table = ctx.bot.dbi.table('raids')
    query = raid_table.query('channels')
    query.where(guildid=ctx.guild.id)
    query.where(raid_table['channels'].contains_(str(ctx.channel.id)))
    data = await query.get()
    if data:
        return True
    else:
        return False

def raid_channel():
    return commands.check(is_raid_channel)