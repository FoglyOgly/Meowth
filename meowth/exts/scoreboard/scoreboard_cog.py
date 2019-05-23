from meowth import Cog, command, bot, checks
from typing import Optional

import discord
from discord import commands

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
        if user_ids:
            update.where(score_table['user_id'].in_(user_ids))
        for column in to_update:
            update.values(column=0)
        await update.commit()
        await ctx.success('Scoreboard reset', fields=fields)
