from meowth import Cog, command

from . import teams_checks


class Teams(Cog):

    @command()
    @teams_checks.team_not_set()
    async def team(self, *, chosen_team):
        """Set your Pokemon Go team."""
