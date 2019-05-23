from meowth import Cog, command, bot, checks

import discord
from discord.ext import commands
from typing import Optional

class ScoreCog(Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @command()
    @checks.is_admin()
    async def reset_board(self, ctx, users: commands.Greedy[discord.Member], *categories):
        possible_categories = ['raid', 'wild', 'trade', 'research', 'service']
        fields = {}
        if categories:
            to_update = [x for x in categories if x in possible_categories]
        else:
            to_update = possible_categories
        fields['Categories'] = "\n".join(to_update)
        if users:
            user_ids = [x.id for x in users]
            user_names = [x.display_name for x in users]
            fields['Users'] = "\n".join(user_names)
        else:
            user_ids = []
            fields['Users'] = "All"
        score_table = self.bot.dbi.table('scoreboard')
        update = score_table.update
        update.where(guild_id=ctx.guild.id)
        if user_ids:
            update.where(score_table['user_id'].in_(user_ids))
        d = {x: 0 for x in to_update}
        update.values(**d)
        await update.commit()
        await ctx.success('Scoreboard reset', fields=fields)
    
    @command()
    @checks.is_admin()
    async def adjust(self, ctx, user: discord.Member, category, amount: int):
        possible_categories = ['raid', 'wild', 'trade', 'research', 'service']
        if category not in possible_categories:
            return await ctx.error('No valid category found')
        score_table = ctx.bot.dbi.table('scoreboard')
        query = score_table.query
        query.where(guild_id=ctx.guild.id)
        query.where(user_id=user.id)
        old_data = await query.get()
        if not old_data:
            d = {
                'guild_id': ctx.guild.id,
                'user_id': user.id,
                'raid': 0,
                'wild': 0,
                'trade': 0,
                'research': 0,
                'service': 0
            }
        else:
            d = dict(old_data[0])
        old_score = d.get(category, 0)
        new_score = old_score + amount
        d[category] = new_score
        insert = score_table.insert
        insert.row(**d)
        await insert.commit(do_update=True)
        fields = {
            'User': user.display_name,
            'Category': category,
            'New Score': str(new_score)
        }
        return await ctx.success('Scoreboard adjusted', fields=fields)
    
    @command()
    async def scorecard(self, ctx, user: Optional[discord.Member]):
        if not user:
            user = ctx.author
        score_table = ctx.bot.dbi.table('scoreboard')
        query = score_table.query
        query.where(guild_id=ctx.guild.id)
        query.where(user_id=user.id)
        data = await query.get()
        if not data:
            fields = {
                'Raid': '0',
                'Wild': '0',
                'Trade': '0',
                'Research': '0',
                'Service': '0'
            }
        else:
            d = dict(data[0])
            fields = {
                'Raid': str(d['raid']),
                'Wild': str(d['wild']),
                'Trade': str(d['trade']),
                'Research': str(d['research']),
                'Service': str(d['service'])
            }
        return await ctx.info(f'Scorecard for {user.display_name}', fields=fields, thumbnail=user.avatar_url)
        
    @command()
    async def leaderboard(self, ctx, category):
        possible_categories = ['raid', 'wild', 'trade', 'research', 'service']
        if category not in possible_categories:
            return await ctx.error('No valid category found')
        score_table = ctx.bot.dbi.table('scoreboard')
        query = score_table.query('user_id', category)
        query.where(guild_id=ctx.guild.id)
        query.order_by(score_table[category], asc=False)
        query.limit(10)
        data = await query.get()
        l = []
        for i in range(len(data)):
            row = data[i]
            name = ctx.guild.get_member(row['user_id']).display_name
            score = row[category]
            l.append(f'**{i}**: {name} ({score})')
        return await ctx.info(f'Leaderboard for {category.title()}', details="\n".join(l))
