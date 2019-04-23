"""This cog contains features relating to Pokemon Go teams."""

from .users_cog import Users, MeowthUser
from . import users_checks

def setup(bot):
    bot.add_cog(Users(bot))
