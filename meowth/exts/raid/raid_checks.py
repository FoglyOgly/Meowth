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
    query.where(guild=ctx.guild.id)
    query.where(raid_table['channels'].contains_(str(ctx.channel.id)))
    data = await query.get()
    if data:
        report_channel_id = data[0].get('report_channel')
        raid_id = data[0].get('id')
        ctx.raid_id = raid_id
        ctx.report_channel_id = report_channel_id
        return True
    else:
        ctx.raid_id = None
        return False

def raid_channel():
    return commands.check(is_raid_channel)

async def is_train_enabled(ctx):
    if await is_raid_channel(ctx):
        report_channel = ctx.bot.get_channel(ctx.report_channel_id)
        if report_channel:
            ctx.channel = report_channel
            return await is_train_enabled(ctx)
        else:
            return False
    report_table = ctx.bot.dbi.table('report_channels')
    query = report_table.query('train')
    query.where(channelid=ctx.channel.id)
    train = await query.get_value()
    if not train:
        return False
    else:
        return True

def train_enabled():
    return commands.check(is_train_enabled)