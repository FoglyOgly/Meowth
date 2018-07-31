"""This cog contains features relating to Pokemon Go teams."""

from .teams_cog import Teams

def setup(bot):
    bot.add_cog(Teams(bot))
