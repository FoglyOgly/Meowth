from discord.ext import commands

async def check_is_owner(ctx):
    return await ctx.bot.is_owner(ctx.author)

async def check_is_co_owner(ctx):
    if await check_is_owner(ctx):
        return True
    if ctx.author.id in ctx.bot.co_owners:
        return True
    return False

async def check_is_guildowner(ctx):
    if await check_is_co_owner(ctx):
        return True
    if ctx.author.id == ctx.guild.owner.id:
        return True
    return False

async def check_is_admin(ctx):
    if await check_is_guildowner(ctx):
        return True
    if ctx.author.guild_permissions.manage_server:
        return True
    return False

async def check_is_mod(ctx):
    if await check_is_admin(ctx):
        return True
    if ctx.author.permissions_in(ctx.channel).manage_messages:
        return True
    return False

def is_owner():
    return commands.check(check_is_owner)

def is_co_owner():
    return commands.check(check_is_co_owner)

def is_guildowner():
    return commands.check(check_is_guildowner)

def is_admin():
    return commands.check(check_is_admin)

def is_mod():
    return commands.check(check_is_mod)

def is_prefix(prefixes: list):
    def check(ctx):
        prefix = ctx.prefix
        return prefix in prefixes
    return commands.check(check)

async def check_cog_enabled(ctx, default=True):
    enabled = await ctx.cog_enabled()
    return enabled if enabled is not None else default

def cog_enabled():
    return commands.check(check_cog_enabled)
