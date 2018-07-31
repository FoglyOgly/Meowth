from discord.ext import commands


# simple predicates

async def is_team_set(ctx):
    if ctx.team:
        return True
    return False

async def is_team_not_set(ctx):
    return not await is_team_set(ctx)


# decorator checks

def team_set():
    return commands.check(is_team_set)

def team_not_set():
    return commands.check(is_team_not_set)
