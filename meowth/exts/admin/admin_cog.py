from meowth import checks, command, group, Cog
from discord.ext import commands
import discord
from timezonefinder import TimezoneFinder

class AdminCog(Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_guild_channel_update(self, before, after):
        coms = await self.enabled_commands(after)
        if not coms:
            return
        req_perms = self.required_perms(coms)
        reqs_met = self.check_channel_perms(after, req_perms)
        if not reqs_met:
            return await after.send('My permissions in this channel have been restricted! I may not be able to process all enabled commands in this channel.')


    async def enabled_commands(self, channel):
        table = self.bot.dbi.table('report_channels')
        query = table.query.where(channelid=channel.id)
        data = await query.get()
        if not data:
            return None
        data = dict(data[0])
        coms = [x for x in data if data[x] is True]
        if not coms:
            return None
        return coms

    def required_perms(self, coms):
        permissions = discord.Permissions()
        permissions.add_reactions = True
        permissions.manage_messages = True
        permissions.external_emojis = True
        permissions.embed_links = True
        if 'users' in coms:
            permissions.manage_roles = True
        if 'train' in coms:
            permissions.manage_channels = True
        return permissions

    def check_channel_perms(self, channel, required_perms):
        me = channel.guild.me
        perms = channel.permissions_for(me)
        for x in required_perms:
            print(x)
        print(bin(required_perms.value))
        for x in perms:
            print(x)
        print(bin(perms.value))
        if perms >= required_perms:
            return True
        return False


    @command()
    @commands.has_permissions(manage_guild=True)
    async def setlocation(self, ctx, city: str, lat: float, lon: float, radius: float):
        """Set the reporting location for the channel.

        **Arguments**
        *city:* The name of the city. Include the state or country for better results.
        *lat:* The latitude of the central point of the area.
        *lon:* The longitude of the central point of the area.
        *radius:* The radius in kilometers of the area.
        """
        report_channel_table = self.bot.dbi.table('report_channels')
        channel_id = ctx.channel.id
        query = report_channel_table.query.where(channelid=channel_id)
        data = await query.get()
        if data:
            d = dict(data[0])
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
        await insert.commit(do_update=True)
        return await ctx.send(f"Location set. Timezone is `{zone}`")

    @command()
    @commands.has_permissions(manage_guild=True)
    async def enable(self, ctx, *features):
        """Enable features in the current channel.

        **Arguments**
        *features:* list of features to enable. Can include any of
        `['raid', 'wild', 'research', 'users', 'train', 'trade', 'clean']`

        Raid, wild, research, and train require a defined location. Use `!setlocation`
        before enabling these.
        """
        channel_id = ctx.channel.id
        channel_table = self.bot.dbi.table('report_channels')
        query = channel_table.query.where(channelid=channel_id)
        data = await query.get()
        if data:
            rcrd = dict(data[0])
        else:
            rcrd = {'channelid': channel_id}
        possible_commands = ['raid', 'wild', 'research', 'users', 'train', 'trade',
            'clean']
        features = [x for x in features if x in possible_commands]
        if not features:
            return await ctx.send("The list of valid command groups to enable is `raid, train, wild, research, user, trade, clean`.")
        location_commands = ['raid', 'wild', 'research', 'train']
        enabled_commands = []
        required_perms = {}
        me = ctx.guild.me
        perms = ctx.channel.permissions_for(me)
        for x in features:
            if x in ['raid', 'wild', 'trade', 'train', 'research', 'users']:
                required_perms['Add Reactions'] = perms.add_reactions
                required_perms['Manage Messages'] = perms.manage_messages
                required_perms['Use External Emojis'] = perms.external_emojis
            if x == 'users':
                required_perms['Manage Roles'] = perms.manage_roles
            if x in location_commands:
                if not rcrd.get('city'):
                    await ctx.send(f"You must set a location for this channel before enabling `{ctx.prefix}{x}`. Use `{ctx.prefix}setlocation`")
                    continue
            rcrd[x] = True
            enabled_commands.append(x)
        if 'raid' in enabled_commands:
            raid_levels = ['1', '2', '3', '4', '5', 'EX', 'EX Raid Gyms']
            for level in raid_levels:
                column = f'category_{level.lower()}'
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
                        break
                    elif resp.content.lower() == 'disable':
                        rcrd[column] = None
                        break
                    else:
                        converter = commands.CategoryChannelConverter()
                        category = await converter.convert(ctx, resp.content)
                        if category:
                            rcrd[column] = str(category.id)
                            required_perms['Manage Channels'] = perms.manage_channels
                            break
                        else:
                            await ctx.send('I could not interpret your response. Try again!')
                            continue
        if not all(required_perms.values()):
            missing_perms = [x for x in required_perms if not required_perms[x]]
            while True:
                content = "I am missing the following required permissions in this channel. Please respond with `done` when you have granted me those permissions or `cancel` to cancel.\n\n"
                content += "\n".join(missing_perms)
                await ctx.send(content)
                def check(m):
                    return m.author == ctx.message.author and m.channel == ctx.channel
                resp = await self.bot.wait_for('message', check=check)
                if resp.content.lower() == 'cancel':
                    return await ctx.send("Configuration canceled.")
                elif resp.content.lower() == 'done':
                    channel = resp.channel
                    new_perms = channel.permissions_for(me)
                    req_perms = {x: None for x in required_perms}
                    for x in req_perms:
                        if x == 'Manage Channels':
                            req_perms[x] = new_perms.manage_channels
                        elif x == 'Manage Roles':
                            req_perms[x] = new_perms.manage_roles
                        elif x == 'Manage Messages':
                            req_perms[x] = new_perms.manage_messages
                        elif x == 'Use External Emojis':
                            req_perms[x] = new_perms.external_emojis
                        elif x == 'Add Reactions':
                            req_perms[x] = new_perms.add_reactions
                    if not all(req_perms.values()):
                        missing_perms = [x for x in req_perms if not req_perms[x]]
                        continue
                    else:
                        await ctx.send('Thanks for fixing those!')
                        break
        insert = channel_table.insert
        insert.row(**rcrd)
        await insert.commit(do_update=True)
        return await ctx.send(f'The following commands have been enabled in this channel: `{", ".join(enabled_commands)}`')

    @command()
    @commands.has_permissions(manage_guild=True)
    async def disable(self, ctx, *features):
        """Disable features in the current channel.

        **Arguments**
        *features:* list of features to disable. Can include any of
        `['raid', 'wild', 'research', 'users', 'train', 'trade', 'clean']`
        """
        channel_id = ctx.channel.id
        channel_table = self.bot.dbi.table('report_channels')
        query = channel_table.query.where(channelid=channel_id)
        data = await query.get()
        if data:
            rcrd = dict(data[0])
        else:
            rcrd = {'channelid': channel_id}
        possible_commands = ['raid', 'wild', 'research', 'users', 'train', 'trade',
            'clean']
        features = [x for x in features if x in possible_commands]
        if not features:
            return await ctx.send("The list of valid command groups to disable is `raid, wild, research, user, train, trade, clean`.")
        disabled_commands = []
        for x in features:
            rcrd[x] = False
            disabled_commands.append(x)
        insert = channel_table.insert
        insert.row(**rcrd)
        await insert.commit(do_update=True)
        return await ctx.send(f'The following commands have been disabled in this channel: `{", ".join(disabled_commands)}`')
        
