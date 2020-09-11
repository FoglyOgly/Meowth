from meowth import checks, command, group, Cog
from meowth.utils.formatters import ask
from meowth.exts.users import Team
from discord.ext import commands
import discord
from timezonefinder import TimezoneFinder
import re
import pickle
from typing import Union

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
        if match_type == '<':
            mention_match = re.search('(#|@!?|&)([0-9]+)', match)
            match_type = mention_match.group(1)[0]
            match = mention_match.group(2)
        if match_type == '@':
            member = guild.get_member_named(match)
            if match.isdigit() and (not member):
                member = guild.get_member(int(match))
            if (not member):
                not_found.append(full_match)
            return member.mention if member else full_match
        elif match_type == '#':
            channel = discord.utils.get(guild.text_channels, name=match)
            if match.isdigit() and (not channel):
                channel = guild.get_channel(int(match))
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
            try:
                await after.send(content)
                return
            except:
                guild = before.guild
                actions = [discord.AuditLogAction.overwrite_update,
                    discord.AuditLogAction.overwrite_create,
                    discord.AuditLogAction.overwrite_delete]
                async for entry in guild.audit_logs():
                    if entry.action not in actions:
                        continue
                    if entry.target.id == before.id:
                        user = entry.user
                        content = f'I have lost the following required permissions in {after.name}!\n\n'
                        content += "\n".join(missing_perms)
                        try:
                            await user.send(content)
                            return
                        except:
                            owner = guild.owner
                            try:
                                await owner.send(content)
                                return
                            except:
                                pass
    
    @Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        welcome_channel, message = await self.welcome_channel(guild)
        if not welcome_channel:
            return
        if welcome_channel == 'dm':
            send_to = member
        else:
            send_to = welcome_channel
        await send_to.send(message.format(server=guild.name, user=member.mention))

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
    
    async def archive_cat_phrases(self, guild):
        table = self.bot.dbi.table('archive')
        query = table.query
        query.where(guild_id=guild.id)
        data = await query.get()
        if data:
            data = data[0]
        else:
            return None, None
        catid = data['category']
        cat = self.bot.get_channel(catid)
        phrase_list = data.get('phrase_list', [])
        return cat, phrase_list
    
    @command()
    @commands.has_permissions(manage_guild=True)
    async def teamrole(self, ctx, team: Team, role: discord.Role):
        """Assign a role to a Pokemon Go team in your server."""

        user_data = []
        table = ctx.bot.dbi.table('users')
        for member in role.members:
            user_id = member.id
            query = table.query.where(id=user_id)
            data = await query.get()
            if not data:
                d = {
                    'id': user_id,
                    'team': team.id
                }
            else:
                d = dict(data[0])
                d['team'] = team.id
            user_data.append(d)
        if user_data:
            insert = table.insert.rows(user_data)
            await insert.commit(do_update=True)
        table = ctx.bot.dbi.table('team_roles')
        query = table.query.where(guild_id=ctx.guild.id)
        data = await query.get()
        if not data:
            d = {
                'guild_id': ctx.guild.id
            }
        else:
            d = dict(data[0])
        if team.id == 1:
            d['blue_role_id'] = role.id
        elif team.id == 2:
            d['yellow_role_id'] = role.id
        elif team.id == 3:
            d['red_role_id'] = role.id
        insert = table.insert
        insert.row(**d)
        await insert.commit(do_update=True)
        await ctx.success('Team Configuration Successful', details=f'{await team.emoji()} assigned to {role.name}')

    @command()
    @checks.is_admin()
    async def addcustomroles(self, ctx, roles: commands.Greedy[discord.Role]):
        if not roles:
            return await ctx.error('No roles found')
        table = ctx.bot.dbi.table('custom_roles')
        role_names = [x.name for x in roles]
        insert = table.insert
        rows = []
        for role in roles:
            d = {
                'guild_id': ctx.guild.id,
                'role_id': role.id
            }
            rows.append(d)
        insert.rows(rows)
        await insert.commit(do_update=True)
        await ctx.success('Custom roles added', details="\n".join(role_names))
    
    @command()
    @checks.is_admin()
    async def removecustomroles(self, ctx, roles: commands.Greedy[discord.Role]):
        if not roles:
            return await ctx.error('No roles found')
        role_ids = [x.id for x in roles]
        role_names = [x.name for x in roles]
        table = ctx.bot.dbi.table('custom_roles')
        query = table.query
        query.where(guild_id=ctx.guild.id)
        query.where(table['role_id'].in_(role_ids))
        await query.delete()
        await ctx.success('Custom roles removed', details="\n".join(role_names))

    @command()
    @commands.has_permissions(manage_guild=True)
    async def setlocation(self, ctx, city: str, lat: float, lon: float, radius: float):
        """Set the reporting location for the channel.

        **Arguments**
        *city:* The name of the city. Include the state or country for better results.
        *lat:* The latitude of the central point of the area.
        *lon:* The longitude of the central point of the area.
        *radius:* The radius in kilometers of the area.

        Example: `!setlocation "Joplin MO" 37.084086 -94.513494 20`
        """
        report_channel_table = self.bot.dbi.table('report_channels')
        channel_id = ctx.channel.id
        query = report_channel_table.query.where(channelid=channel_id)
        data = await query.get()
        if data:
            d = dict(data[0])
        else:
            d = {'channelid': channel_id}
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
        `['raid', 'wild', 'research', 'users', 'train', 'trade', 'clean', 'archive', 'welcome', 'meetup', 'forecast', 'rocket']`

        Raid, wild, research, train and meetup require a defined location. Use `!setlocation`
        before enabling these.
        """
        guild_id = ctx.guild.id
        settings = ctx.bot.dbi.table('guild_settings')
        insert = settings.insert
        insert.row(guild_id=guild_id, version=ctx.bot.version)
        await insert.commit(do_update=True)
        try:
            await ctx.guild.me.edit(nick='Meowth 3.0')
        except:
            pass
        channel_id = ctx.channel.id
        channel_table = self.bot.dbi.table('report_channels')
        query = channel_table.query.where(channelid=channel_id)
        data = await query.get()
        if data:
            rcrd = dict(data[0])
        else:
            rcrd = {'channelid': channel_id, 'guild_id': ctx.guild.id}
        possible_commands = ['raid', 'wild', 'research', 'users', 'train', 'trade',
            'clean', 'archive', 'welcome', 'meetup', 'forecast', 'rocket']
        features = [x for x in features if x in possible_commands]
        if not features:
            return await ctx.send("The list of valid command groups to enable is `raid, train, wild, users, trade, clean, welcome, archive, meetup, research, rocket`.")
        location_commands = ['raid', 'wild', 'research', 'train', 'meetup', 'forecast', 'rocket']
        enabled_commands = []
        required_perms = {}
        me = ctx.guild.me
        perms = ctx.channel.permissions_for(me)
        for x in features:
            if x in ['raid', 'wild', 'trade', 'train', 'users', 'meetup', 'research', 'rocket']:
                required_perms['Add Reactions'] = perms.add_reactions
                required_perms['Manage Messages'] = perms.manage_messages
                required_perms['Use External Emojis'] = perms.external_emojis
            if x == 'users':
                required_perms['Manage Roles'] = perms.manage_roles
            if x in location_commands:
                if not rcrd.get('city'):
                    await ctx.send(f"You must set a location for this channel before enabling `{ctx.prefix}{x}`. Use `{ctx.prefix}setlocation`")
                    continue
            if x != 'welcome' and x!= 'archive':
                rcrd[x] = True
            enabled_commands.append(x)
        if 'meetup' in enabled_commands:
            column = 'category_meetup'
            content = ('How do you want Meetup channels created from this channel '
                'to be categorized? You can type the name or ID of the category you want '
                'the channel to appear in.')
            await ctx.send(content)
            def check(m):
                return m.author == ctx.message.author and m.channel == ctx.channel
            while True:
                try:
                    resp = await self.bot.wait_for('message', check=check)
                except:
                    break
                converter = commands.CategoryChannelConverter()
                category = await converter.convert(ctx, resp.content)
                if category:
                    rcrd[column] = category.id
                    required_perms['Manage Channels'] = perms.manage_channels
                    break
                else:
                    await ctx.send('I could not interpret your response. Try again!')
                    continue
        if 'raid' in enabled_commands:
            raid_levels = ['1', '3', '5', '7', 'EX', 'EX Raid Gyms']
            for level in raid_levels:
                column = f'category_{level.lower()}'
                if level == 'EX Raid Gyms':
                    column = 'category_ex_gyms'
                    content = ('I can categorize raids of any level that are reported at '
                        'recognized EX Raid Gyms differently from other raids of the same level. '
                        'You can type `disable` if you do not want this, or type the name or ID of '
                        'the category you want those raid channels to appear in.')
                else:
                    if level == '7':
                        level_str = 'Mega'
                    elif level == 'EX':
                        level_str = "EX"
                    else:
                        level_str = f"Level {level}"
                    content = (f'How do you want {level_str} Raids reported in this ' 
                        'channel to be displayed? You can type `message` if you want just '
                        'a message in this channel. If you want each raid to be given its own '
                        'channel for coordination, type the name or ID of the category you '
                        'want the channel to appear in, or type `none` for an uncategorized '
                        'channel. You can also type `disable` to disallow reports of '
                        f'{level_str} Raids in this channel.')
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
                    elif resp.content.lower() == 'none':
                        rcrd[column] = 'none'
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
            await insert.commit(do_update=True)
        if 'archive' in enabled_commands:
            category, phrase_list = await self.archive_cat_phrases(ctx.guild)
            new_category = None
            new_phrase_list = []
            if category:
                content = f"This server's current archive category is {category.name}. "
                content += "Do you want to disable that category and enable another?"
                oldmsg = await ctx.send(content)
                payload = await ask(ctx.bot, [oldmsg], user_list=[ctx.author.id])
                if not payload:
                    await oldmsg.edit(content='Timed out!')
                elif str(payload.emoji) == '❎':
                    new_category = category.id
                elif str(payload.emoji) == '✅':
                    pass
            if not new_category:
                await ctx.send('What category do you want to use? You can type the name or ID of a category.')
                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel
                while True:
                    reply = await ctx.bot.wait_for('message', check=check)
                    converter = commands.CategoryChannelConverter()
                    channel = await converter.convert(ctx, reply.content)
                    if channel:
                        new_category = channel.id
                        break
                    else:
                        await ctx.send("I couldn't understand your reply. Try again.")
                        continue
            content = f"Current phrase list: {phrase_list}\n"
            content += "Do you want to change the phrase list?"
            oldmsg = await ctx.send(content)
            payload = await ask(ctx.bot, [oldmsg], user_list=[ctx.author.id])
            if not payload:
                await oldmsg.edit(content='Timed out!')
            elif str(payload.emoji) == '❎':
                new_phrase_list = phrase_list
            elif str(payload.emoji) == '✅':
                content = "Type your phrase list below. I will automatically archive any temporary channel in which your phrases are said. Separate each phrase with a comma."
                await ctx.send(content)
                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel
                while True:
                    reply = await ctx.bot.wait_for('message', check=check)
                    phrases = reply.content.split(',')
                    phrases = [x.strip() for x in phrases]
                    q = await ctx.send(f"Here's what you sent:\n\n`{phrases}`\n\nDoes that look right?")
                    payload = await ask(ctx.bot, [q], user_list=[ctx.author.id], timeout=None)
                    if str(payload.emoji) == '❎':
                        await ctx.send('Try again.')
                        continue
                    elif str(payload.emoji) == '✅':
                        new_phrase_list = phrases
                        break
            d = {
                'guild_id': ctx.guild.id,
                'category': new_category,
                'phrase_list': new_phrase_list
            }
            table = ctx.bot.dbi.table('archive')
            insert = table.insert.row(**d)
            await insert.commit(do_update=True)
        if 'forecast' in enabled_commands:
            g = ctx.bot.get_guild(344960572649111552)
            gm = g.get_member(ctx.author.id)
            r = g.get_role(616734835104546826)
            if not r in gm.roles:
                content = 'Unfortunately, because of the cost of using the AccuWeather API, you must be a Meowth Patreon Super Nerd to enable in-game weather forecasts. Visit www.patreon.com/meowthbot to become a Patron!'
                await ctx.send(content)
            else:
                d = {
                    'guild_id': ctx.guild.id,
                    'patron_id': ctx.author.id,
                    'enabled': True
                }
                table = ctx.bot.dbi.table('forecast_config')
                insert = table.insert.row(**d)
                await insert.commit(do_update=True)
                content = f'Forecasts have been enabled in this server! Please note that it may take up to eight hours for this to take effect. You can use `{ctx.prefix}forecast` in any reporting channel to check the forecast, and you can use `{ctx.prefix}weather` in raid channels at known Gyms to improve the forecast.'
                await ctx.send(content)
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
        `['raid', 'wild', 'research', 'users', 'train', 'trade', 'clean', 'welcome', 'meetup', 'forecast', 'rocket']`
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
            'clean', 'welcome', 'meetup', 'forecast', 'rocket']
        features = [x for x in features if x in possible_commands]
        if not features:
            return await ctx.send("The list of valid command groups to disable is `raid, wild, research, users, train, trade, clean, welcome, meetup`.")
        disabled_commands = []
        if 'forecast' in features:
            d = {
                'guild_id': ctx.guild.id,
                'patron_id': ctx.author.id,
                'enabled': False
            }
            table = ctx.bot.dbi.table('forecast_config')
            insert = table.insert.row(**d)
            await insert.commit(do_update=True)
            content = f'Forecasts have been disabled in this server. Please note that this does not delete your Patreon pledge. Visit Patreon if you wish to delete or alter your pledge.'
            await ctx.send(content)
            features.remove('forecast')
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

    @command()
    @commands.has_permissions(manage_guild=True)
    async def importconfig(self, ctx):
        """Imports existing settings from Meowth 2.0, if they exist.

        Usable only by server admins."""
        guild_id = ctx.guild.id
        settings = ctx.bot.dbi.table('guild_settings')
        insert = settings.insert
        insert.row(guild_id=guild_id, version=ctx.bot.version)
        await insert.commit(do_update=True)
        try:
            await ctx.guild.me.edit(nick='Meowth 3.0')
        except:
            pass
        old_shard_id = (guild_id >> 22) % 2
        path = f'/home/foglyogly1/MeowthProject/MeowthProject/Shard{old_shard_id}/data/serverdict'
        with open(path, 'rb') as fd:
            old_gd = pickle.load(fd)
        old_config = old_gd.get(ctx.guild.id, {}).get('configure_dict', {})
        if not old_config:
            return await ctx.error('No old configuration found!')
        old_prefix = old_config.get('settings', {}).get('prefix')
        if old_prefix:
            table = ctx.bot.dbi.table('prefixes')
            insert = table.insert
            d = {
                'guild_id': guild_id,
                'prefix': old_prefix
            }
            insert.row(**d)
            await insert.commit(do_update=True)
        welcome_dict = old_config.get('welcome', {})
        if welcome_dict.get('enabled'):
            welcome_chan = welcome_dict.get('welcomechan')
            if isinstance(welcome_chan, int):
                welcome_chan = str(welcome_chan)
            welcomemsg = welcome_dict.get('welcomemsg')
            d = {
                'guild_id': guild_id,
                'channelid': welcome_chan,
                'message': welcomemsg
            }
            table = ctx.bot.dbi.table('welcome')
            insert = table.insert
            insert.row(**d)
            await insert.commit(do_update=True)
        archive_dict = old_config.get('archive', {})
        if archive_dict.get('enabled'):
            archive_cat = archive_dict.get('category')
            if archive_cat == 'same':
                archive_cat = None
            archive_list = archive_dict.get('list')
            d = {
                'guild_id': guild_id,
                'category': archive_cat,
                'phrase_list': archive_list
            }
            table = ctx.bot.dbi.table('archive')
            insert = table.insert
            insert.row(**d)
            await insert.commit(do_update=True)
        report_channels = {}
        want_dict = old_config.get('want', {})
        if want_dict.get('enabled'):
            chans = want_dict.get('report_channels', [])
            for chan in chans:
                channel_exists = ctx.bot.get_channel(chan)
                if not channel_exists:
                    continue
                d = {
                    'guild_id': guild_id,
                    'channelid': chan,
                    'users': True
                }
                report_channels[chan] = d
        raid_dict = old_config.get('raid', {})
        if raid_dict.get('enabled'):
            chans = raid_dict.get('report_channels', {})
            catsort = raid_dict.get('categories')
            cat_dict = raid_dict.get('category_dict')
            for chan in chans:
                channel_exists = ctx.bot.get_channel(chan)
                if not channel_exists:
                    continue
                if chan in report_channels:
                    d = report_channels[chan]
                    d['raid'] = True
                else:
                    d = {
                        'guild_id': guild_id,
                        'channelid': chan,
                        'raid': True
                    }
                city = chans[chan]
                d['city'] = city
                if catsort == 'region':
                    cat = str(cat_dict.get(chan))
                    d['category_1'] = cat
                    d['category_2'] = cat
                    d['category_3'] = cat
                    d['category_4'] = cat
                    d['category_5'] = cat
                elif catsort == 'level':
                    cat_1 = str(cat_dict.get('1'))
                    cat_2 = str(cat_dict.get('2'))
                    cat_3 = str(cat_dict.get('3'))
                    cat_4 = str(cat_dict.get('4'))
                    cat_5 = str(cat_dict.get('5'))
                    d['category_1'] = cat_1
                    d['category_2'] = cat_2
                    d['category_3'] = cat_3
                    d['category_4'] = cat_4
                    d['category_5'] = cat_5
                elif catsort == 'same':
                    cat = str(channel_exists.category.id)
                    d['category_1'] = cat
                    d['category_2'] = cat
                    d['category_3'] = cat
                    d['category_4'] = cat
                    d['category_5'] = cat
                else:
                    d['category_1'] = 'none'
                    d['category_2'] = 'none'
                    d['category_3'] = 'none'
                    d['category_4'] = 'none'
                    d['category_5'] = 'none'
                report_channels[chan] = d
        exraid_dict = old_config.get('exraid', {})
        if exraid_dict.get('enabled'):
            chans = exraid_dict.get('report_channels', {})
            catsort = exraid_dict.get('categories')
            cat_dict = exraid_dict.get('category_dict')
            for chan in chans:
                channel_exists = ctx.bot.get_channel(chan)
                if not channel_exists:
                    continue
                if chan in report_channels:
                    d = report_channels[chan]
                    d['raid'] = True
                else:
                    d = {
                        'guild_id': guild_id,
                        'channelid': chan,
                        'raid': True
                    }
                city = chans[chan]
                d['city'] = city
                if catsort == 'region':
                    cat = str(cat_dict.get(chan))
                    d['category_ex'] = cat
                elif catsort == 'same':
                    cat = str(channel_exists.category.id)
                    d['category_ex'] = cat
                else:
                    d['category_ex'] = 'none'
                report_channels[chan] = d
        wild_dict = old_config.get('wild', {})
        if wild_dict.get('enabled'):
            chans = wild_dict.get('report_channels', {})
            for chan in chans:
                channel_exists = ctx.bot.get_channel(chan)
                if not channel_exists:
                    continue
                if chan in report_channels:
                    d = report_channels[chan]
                    d['wild'] = True
                else:
                    d = {
                        'guild_id': guild_id,
                        'channelid': chan,
                        'wild': True
                    }
                city = chans[chan]
                d['city'] = city
                report_channels[chan] = d
        trade_dict = old_config.get('trade', {})
        if trade_dict.get('enabled'):
            chans = trade_dict.get('report_channels', [])
            for chan in chans:
                channel_exists = ctx.bot.get_channel(chan)
                if not channel_exists:
                    continue
                if chan in report_channels:
                    d = report_channels[chan]
                    d['trade'] = True
                else:
                    d = {
                        'guild_id': guild_id,
                        'channelid': chan,
                        'trade': True
                    }
                report_channels[chan] = d
        research_dict = old_config.get('research', {})
        if research_dict.get('enabled'):
            chans = research_dict.get('report_channels', {})
            for chan in chans:
                channel_exists = ctx.bot.get_channel(chan)
                if not channel_exists:
                    continue
                if chan in report_channels:
                    d = report_channels[chan]
                    d['research'] = True
                else:
                    d = {
                        'guild_id': guild_id,
                        'channelid': chan,
                        'research': True
                    }
                city = chans[chan]
                d['city'] = city
                report_channels[chan] = d
        meetup_dict = old_config.get('meetup', {})
        if meetup_dict.get('enabled'):
            chans = meetup_dict.get('report_channels', {})
            catsort = meetup_dict.get('categories')
            cat_dict = meetup_dict.get('category_dict')
            for chan in chans:
                channel_exists = ctx.bot.get_channel(chan)
                if not channel_exists:
                    continue
                if chan in report_channels:
                    d = report_channels[chan]
                    d['meetup'] = True
                else:
                    d = {
                        'guild_id': guild_id,
                        'channelid': chan,
                        'meetup': True
                    }
                city = chans[chan]
                d['city'] = city
                if catsort == 'region':
                    cat = cat_dict.get(chan)
                    d['category_meetup'] = cat
                elif catsort == 'same':
                    cat = channel_exists.category.id
                    d['category_meetup'] = cat
                else:
                    d['category_meetup'] = None
                report_channels[chan] = d
        data = report_channels.values()
        location_channel_ids = []
        for x in data:
            if x.get('city'):
                location_channel_ids.append(x['channelid'])
        location_channels = [ctx.bot.get_channel(x) for x in location_channel_ids]
        location_channel_names = [x.mention for x in location_channels]
        table = ctx.bot.dbi.table('report_channels')
        insert = table.insert
        insert.rows(data)
        await insert.commit(do_update=True)
        old_prefix = old_prefix or '!'
        await ctx.send(f'Import successful, but you will need to use **{old_prefix}setlocation** in the following channels: {", ".join(location_channel_names)}')

    @command()
    @checks.is_admin()
    async def cleanroles(self, ctx):
        """Deletes all roles with no members in current server.

        Usable only by server admins."""
        guild = ctx.guild
        roles = guild.roles
        empty_roles = [x for x in roles if len(x.members) == 0]
        deleted_roles = 0
        for role in empty_roles:
            try:
                await role.delete()
                deleted_roles += 1
            except:
                pass
        await ctx.send(f'Deleted {deleted_roles} empty roles')
    
    @command()
    @checks.is_admin()
    async def configure(self, ctx):
        """Gives information about how to configure Meowth 3.0."""
        guild_id = ctx.guild.id
        settings = ctx.bot.dbi.table('guild_settings')
        insert = settings.insert
        insert.row(guild_id=guild_id, version=ctx.bot.version)
        await insert.commit(do_update=True)
        try:
            await ctx.guild.me.edit(nick='Meowth 3.0')
        except:
            pass
        await ctx.send('In order to set up or change your configuration for Meowth 3.0, '
            f'you will need to use the **{ctx.prefix}enable**, **{ctx.prefix}disable**, '
            f'and **{ctx.prefix}setlocation** commands. First, in any channel you want to use '
            f'for reporting raids, wilds, or research, use the {ctx.prefix}setlocation '
            'command. Then you can use enable in each of those channels.\n\n'
            f'Most of the non-reporting commands (for example, the {ctx.prefix}team command) '
            f'are enabled with `{ctx.prefix}enable users`. See `{ctx.prefix}help setlocation` '
            f'and `{ctx.prefix}help enable` for more information. \n\n**NOTE:** If you have an existing '
            f'Meowth 2.0 configuration, please use `{ctx.prefix}importconfig` to attempt to '
            'import your settings before attempting to configure Meowth 3.0. If this is not done, '
            'you may find that both Meowth versions attempt to respond to your commands.')
    
