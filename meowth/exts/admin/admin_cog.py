from meowth import checks, command, group, Cog
from meowth.utils.formatters import ask
from discord.ext import commands
import discord
from timezonefinder import TimezoneFinder
import re

def do_template(message, author, guild):
    not_found = []

    def template_replace(match):
        if match.group(3):
            if match.group(3) == 'user':
                return '{user}'
            elif match.group(3) == 'server':
                return guild.name
            else:
                return match.group(0)
        match_type = match.group(1)
        full_match = match.group(0)
        match = match.group(2)
        print(match)
        print(full_match)
        print(match_type)
        if match_type == '<':
            mention_match = re.search('(#|@!?|&)([0-9]+)', match)
            match_type = mention_match.group(1)[0]
            match = mention_match.group(2)
            print(match_type)
            print(match)
        if match_type == '@':
            member = guild.get_member_named(match)
            if match.isdigit() and (not member):
                member = guild.get_member(match)
            if (not member):
                not_found.append(full_match)
            return member.mention if member else full_match
        elif match_type == '#':
            channel = discord.utils.get(guild.text_channels, name=match)
            if match.isdigit() and (not channel):
                channel = guild.get_channel(match)
            if (not channel):
                not_found.append(full_match)
            return channel.mention if channel else full_match
        elif match_type == '&':
            role = discord.utils.get(guild.roles, name=match)
            if match.isdigit() and (not role):
                role = discord.utils.get(guild.roles, id=int(match))
            if (not role):
                not_found.append(full_match)
            return role.mention if role else full_match
    template_pattern = '(?i){(@|#|&|<)([^{}]+)}|{(user|server)}|<*:([a-zA-Z0-9]+):[0-9]*>*'
    msg = re.sub(template_pattern, template_replace, message)
    return (msg, not_found)

class AdminCog(Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_guild_channel_update(self, before, after):
        coms = await self.enabled_commands(after)
        if not coms:
            return
        req_perms = self.required_perms(coms)
        missing_perms = self.check_channel_perms(after, req_perms)
        if missing_perms:
            content = 'I have lost the following required permissions in this channel!\n\n'
            content += "\n".join(missing_perms)
            return await after.send(content)
    
    @Cog.listener()
    async def on_member_join(self, member):
        print(0)
        guild = member.guild
        welcome_channel, message = await self.welcome_channel(guild)
        if not welcome_channel:
            return
        if welcome_channel == 'dm':
            send_to = member
        else:
            print(2)
            send_to = welcome_channel
        await send_to.send(message.format(server=guild.name, user=member.mention))
        print(3)

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
        if perms >= required_perms:
            return None
        missing_perms = []
        for x in required_perms:
            if x[1] and x not in perms:
                missing_perms.append(x[0])
        missing_perms = [x.replace('_', ' ').replace('guild', 'server').title() for x in missing_perms]
        return missing_perms
    
    async def welcome_channel(self, guild):
        table = self.bot.dbi.table('welcome')
        query = table.query
        query.where(guild_id=guild.id)
        data = await query.get()
        if data:
            data = data[0]
            channelid = data['channelid']
            message = data['message']
        else:
            return None, None
        if channelid.isdigit():
            return self.bot.get_channel(int(channelid)), message
        elif channelid == 'dm':
            return 'dm', message
        else:
            return None, None

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
            'clean', 'welcome']
        features = [x for x in features if x in possible_commands]
        if not features:
            return await ctx.send("The list of valid command groups to enable is `raid, train, wild, research, user, trade, clean, welcome`.")
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
            if x != 'welcome':
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
        if 'welcome' in enabled_commands:
            old_welcome_channel, message = await self.welcome_channel(ctx.guild)
            new_welcome_channel = None
            if old_welcome_channel:
                if old_welcome_channel == 'dm':
                    name = 'Direct Message'
                else:
                    name = old_welcome_channel.mention
                content = f"This server's current welcome channel is {name}. "
                content += "Do you want to disable that channel and enable another?"
                oldmsg = await ctx.send(content)
                payload = await ask(ctx.bot, [oldmsg], user_list=[ctx.author.id])
                if not payload:
                    await oldmsg.edit(content='Timed out!')
                elif str(payload.emoji) == '❎':
                    if old_welcome_channel == 'dm':
                        new_welcome_channel = 'dm'
                    else:
                        new_welcome_channel = str(old_welcome_channel.id)
                elif str(payload.emoji) == '✅':
                    pass
            if not new_welcome_channel:
                await ctx.send('What channel do you want to use? You can type the name or ID of a text channel, or type `dm` if you want the welcome message sent to DMs.')
                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel
                while True:
                    reply = await ctx.bot.wait_for('message', check=check)
                    if reply.content.lower() == 'dm':
                        new_welcome_channel = 'dm'
                        break
                    else:
                        converter = commands.TextChannelConverter()
                        channel = await converter.convert(ctx, reply.content)
                        if channel:
                            new_welcome_channel = str(channel.id)
                            break
                        else:
                            await ctx.send("I couldn't understand your reply. Try again.")
                            continue
            if not message:
                message = "Welcome to {server}, {user}!"
            content = f"Current welcome message: {message}\n"
            content += "Do you want to change the welcome message?"
            oldmsg = await ctx.send(content)
            payload = await ask(ctx.bot, [oldmsg], user_list=[ctx.author.id])
            if not payload:
                await oldmsg.edit(content='Timed out!')
            elif str(payload.emoji) == '❎':
                newmessage = message
            elif str(payload.emoji) == '✅':
                content = ("Type your welcome message below. Key: \n**{@member}** - Replace member with user name or ID\n"
                    "**{#channel}** - Replace channel with channel name or ID\n"
                    "**{&role}** - Replace role name or ID (shows as @deleted-role DM preview)\n"
                    "**{user}** - Will mention the new user\n"
                    "**{server}** - Will print your server's name\n"
                    )
                await ctx.send(content)
                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel
                while True:
                    reply = await ctx.bot.wait_for('message', check=check)
                    if len(reply.content) > 500:
                        await ctx.send("Please shorten your message to fewer than 500 characters.")
                        continue
                    message, errors = do_template(reply.content, ctx.author, ctx.guild)
                    if errors:
                        content = "The following could not be found:\n"
                        content += "\n".join(errors)
                        content += "\nPlease try again."
                        await ctx.send(content)
                        continue
                    q = await ctx.send(f"Here's what you sent:\n\n{message}\n\nDoes that look right?")
                    payload = await ask(ctx.bot, [q], user_list=[ctx.author.id], timeout=None)
                    if str(payload.emoji) == '❎':
                        await ctx.send('Try again.')
                        continue
                    elif str(payload.emoji) == '✅':
                        newmessage = message
                        break
            d = {
                'guild_id': ctx.guild.id,
                'channelid': new_welcome_channel,
                'message': newmessage
            }
            table = ctx.bot.dbi.table('welcome')
            insert = table.insert.row(**d)
            await insert.commit()
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
        `['raid', 'wild', 'research', 'users', 'train', 'trade', 'clean', 'welcome']`
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
        if 'welcome' in features:
            table = ctx.bot.dbi.table('welcome')
            query = table.query
            query.where(guild_id=ctx.guild.id)
            await query.delete()
            features.remove('welcome')
            disabled_commands.append('welcome')
        for x in features:
            rcrd[x] = False
            disabled_commands.append(x)
        insert = channel_table.insert
        insert.row(**rcrd)
        await insert.commit(do_update=True)
        return await ctx.send(f'The following commands have been disabled in this channel: `{", ".join(disabled_commands)}`')
        
