from meowth import Cog, command

from . import teams_checks

class Team:

    def __init__(self, bot, guild_id, team_id):
        self.bot = bot
        self.guild = guild_id
        self.id = team_id
        

class Teams(Cog):

    @command()
    @teams_checks.team_not_set()
    async def team(self, *, ctx, chosen_team):
        """Set your Pokemon Go team."""


