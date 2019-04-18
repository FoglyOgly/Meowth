from discord.ext import commands


# simple predicates

async def is_team_set(ctx):
    users_table = ctx.bot.dbi.table('users')
    query = users_table.query('team')
    query.where(id=ctx.author.id)
    team = await query.get_value()
    if team:
        return True
    return False

async def is_team_not_set(ctx):
    return not await is_team_set(ctx)

async def is_users_enabled(ctx):
    table = ctx.bot.dbi.table('report_channels')
    query = table.query('users')
    query.where(channelid=ctx.channel.id)
    return await query.get_value()


# decorator checks

def team_set():
    return commands.check(is_team_set)

def team_not_set():
    return commands.check(is_team_not_set)

def users_enabled():
    return commands.check(is_users_enabled)
