from discord.ext import commands
from meowth import errors

async def is_users_enabled(ctx):
    table = ctx.bot.dbi.table('report_channels')
    query = table.query('users')
    query.where(channelid=ctx.channel.id)
    users = await query.get_value()
    if not users:
        raise errors.UsersSetCheckFail
    else:
        return True


# decorator checks

def users_enabled():
    return commands.check(is_users_enabled)