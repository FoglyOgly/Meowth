from discord.ext import commands

async def is_users_enabled(ctx):
    table = ctx.bot.dbi.table('report_channels')
    query = table.query('users')
    query.where(channelid=ctx.channel.id)
    return await query.get_value()


# decorator checks

def users_enabled():
    return commands.check(is_users_enabled)