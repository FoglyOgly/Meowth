from meowth import Cog, command
from meowth.utils import get_match

import discord

from . import teams_checks

class Team:

    def __init__(self, bot, guild_id, team_id):
        self.bot = bot
        self.guild = guild_id
        self.id = team_id
        
    async def role(self):
        settings_table = self.bot.dbi.table('TeamSettings')
        query = settings_table.query()
        if self.id == 1:
            query.select('blue_role_id')
        elif self.id == 2:
            query.select('red_role_id')
        elif self.id == 3:
            query.select('yellow_role_id')
        query.where(guild_id=self.guild)
        result = await query.get_value()
        guild = self.bot.get_guild(self.guild)
        role = discord.utils.get(guild.roles, id=result)
        return role
    
    async def emoji(self):
        team_table = self.bot.dbi.table('teams')
        query = team_table.query('emoji')
        query.where(team_id=self.id)
        result = await query.get_value()
        return result

    @classmethod
    async def convert(cls, ctx, argument):
        argument = argument.lower()

        team_names_table = ctx.bot.dbi.table('team_names')
        team_names_query = team_names_table.query.select(
            'team_name')
        team_names = await team_names_query.get_values()
        match = get_match(team_names, argument, score_cutoff=80)[0]
        if match:
            query = team_names_table.query('team_id')
            query.where(team_name=match)
            team_id = await query.get_value()
        else:
            return await ctx.send("Team not found!")
        
        return cls(ctx.bot, ctx.guild.id, team_id)

        

class Teams(Cog):

    @command()
    @teams_checks.team_not_set()
    async def team(self, ctx, *, chosen_team: Team):
        """Set your Pokemon Go team."""

        role = await chosen_team.role()
        try:
            await ctx.author.add_roles(role)
            await ctx.send("Adding role succeeded")
        except discord.Forbidden:
            await ctx.send("Missing permissions")
        except discord.HTTPException:
            await ctx.send("Adding roles failed")


