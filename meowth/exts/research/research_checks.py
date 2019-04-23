from discord.ext import commands
from .errors import *

async def is_research_enabled(ctx):
    table = ctx.bot.dbi.table('report_channels')
    query = table.query('research')
    query.where(channelid=ctx.channel.id)
    res = await query.get_value()
    if res:
        return True
    else:
        raise ResearchDisabled

def research_enabled():
    return commands.check(is_research_enabled)