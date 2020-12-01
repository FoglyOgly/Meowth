from discord.ext import commands

async def check_bot_permissions(ctx):
    me = ctx.guild.me
    channel = ctx.channel
    perms = channel.permissions_for(me)
    required_perms = {
        "Add Reactions": perms.add_reactions,
        "Manage Messages": perms.manage_messages,
        "Use External Emojis": perms.external_emojis
    }
    if all(required_perms.values()):
        return True
    else:
        missing_perms = [x for x in required_perms if not required_perms[x]]
        raise commands.BotMissingPermissions(missing_perms)

def bot_has_permissions():
    return commands.check(check_bot_permissions)

async def is_rocket_enabled(ctx):
    report_table = ctx.bot.dbi.table('report_channels')
    query = report_table.query('rocket')
    query.where(channelid=ctx.channel.id)
    wild = await query.get_value()
    if not wild:
        return False
    else:
        return True
    
def rocket_enabled():
    return commands.check(is_rocket_enabled)