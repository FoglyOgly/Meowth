from meowth import checks, command, group, Cog
from discord.ext import commands
from timezonefinder import TimezoneFinder

class AdminCog(Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @command()
    @commands.has_permissions(manage_guild=True)
    async def setlocation(self, ctx, city: str, lat: float, lon: float, radius: float):
        report_channel_table = self.bot.dbi.table('report_channels')
        channel_id = ctx.channel.id
        query = report_channel_table.query.where(channelid=channel_id)
        data = await query.get()
        if data:
            d = data[0]
        else:
            d = {}
        d['city'] = city
        d['lat'] = lat
        d['lon'] = lon
        d['radius'] = radius
        tf = TimezoneFinder()
        zone = tf.timezone_at(lng=lon, lat=lat)
        d['timezone'] = zone
        insert = report_channel_table.insert()
        insert.row(**d)
        await insert.commit()

    @command()
    @commands.has_permissions(manage_guild=True)
    async def enable(self, ctx, *features):
        channel_id = ctx.channel.id
        channel_table = self.bot.dbi.table('report_channels')
        query = channel_table.query.where(channelid=channel_id)
        data = await query.get()
        if data:
            rcrd = dict(data[0])
        else:
            rcrd = {'channelid': channel_id}
        possible_commands = ['raid', 'wild', 'research', 'user', 'raidparty', 'trade',
            'clean']
        features = [x for x in features if x in possible_commands]
        if not features:
            return await ctx.send("The list of valid command groups to enable is `raid, wild, research, user, raidparty, trade, clean`.")
        location_commands = ['raid', 'wild', 'research', 'raidparty']
        enabled_commands = []
        for x in features:
            if x in location_commands:
                if not rcrd.get('city'):
                    await ctx.send(f"You must set a location for this channel before enabling `{ctx.prefix}{x}`. Use `{ctx.prefix}setlocation`")
                    continue
            rcrd[x] = True
            enabled_commands.append(x)
        if 'raid' in enabled_commands:
            raid_levels = ['1', '2', '3', '4', '5', 'EX', 'EX Raid Gyms']
            for level in raid_levels:
                column = f'category_{level}'
                if level == 'EX Raid Gyms':
                    column = 'category_ex_gyms'
                    content = ('I can categorize raids of any level that are reported at '
                        'recognized EX Raid Gyms differently from other raids of the same level. '
                        'You can type `disable` if you do not want this, or type the name or ID of '
                        'the category you want those raid channels to appear in.')
                else:
                    content = (f'How do you want Level {level} Raids reported in this ' 
                        'channel to be displayed? You can type `message` if you want just '
                        'a message in this channel. If you want each raid to be given its own '
                        'channel for coordination, type the name or ID of the category you '
                        'want the channel to appear in, or type `none` for an uncategorized '
                        'channel. You can also type `disable` to disallow reports of Level '
                        f'{level} Raids in this channel.')
                await ctx.send(content)
                def check(m):
                    return m.author == ctx.message.author and m.channel == ctx.channel
                while True:
                    try:
                        resp = await self.bot.wait_for('message', check=check)
                    except:
                        break
                    if resp.content.lower() == 'message':
                        rcrd[column] = 'message'
                    elif resp.content.lower() == 'disable':
                        rcrd[column] = None
                    else:
                        category = await commands.CategoryChannelConverter.convert(ctx, resp.content)
                        if category:
                            rcrd[column] = str(category.id)
                            break
                        else:
                            await ctx.send('I could not interpret your response. Try again!')
                            continue
        insert = channel_table.insert
        insert.row(**rcrd)
        await insert.commit()
        return await ctx.send(f'The following commands have been enabled in this channel: `{", ".join(enabled_commands)}`')