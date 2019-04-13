from discord.ext import commands
from .errors import *

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

async def is_raid_enabled(ctx):
    report_table = ctx.bot.dbi.table('report_channels')
    query = report_table.query('raid')
    query.where(channelid=ctx.channel.id)
    raid = await query.get_value()
    if not raid:
        raise RaidDisabled
    else:
        return True

async def raid_category(ctx, level):
    report_table = ctx.bot.dbi.table('report_channels')
    query = report_table.query(f'category_{level}')
    query.where(channelid=ctx.channel.id)
    cat = await query.get_value()
    if cat.isdigit():
        me = ctx.guild.me
        channel = ctx.channel
        perms = channel.permissions_for(me)
        if not perms.manage_channels:
            raise commands.BotMissingPermissions(['Manage Channels'])
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
        raise NotRaidChannel

def raid_channel():
    return commands.check(is_raid_channel)

async def is_train_enabled(ctx):
    if await is_raid_channel(ctx):
        report_channel = ctx.bot.get_channel(ctx.report_channel_id)
        if report_channel:
            ctx.channel = report_channel
            return await is_train_enabled(ctx)
        else:
            raise TrainDisabled
    report_table = ctx.bot.dbi.table('report_channels')
    query = report_table.query('train')
    query.where(channelid=ctx.channel.id)
    train = await query.get_value()
    if not train:
        raise TrainDisabled
    else:
        return True

def train_enabled():
    return commands.check(is_train_enabled)

async def is_train_channel(ctx):
    train_table = ctx.bot.dbi.table('trains')
    query = train_table.query('id')
    query.where(channel_id=ctx.channel.id)
    train_id = await query.get_value()
    if not train_id:
        raise NotTrainChannel
    else:
        return True

def train_channel():
    return commands.check(is_train_channel)

