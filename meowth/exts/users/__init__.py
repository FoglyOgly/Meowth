"""This cog contains features relating to Pokemon Go user management."""

from .users_cog import Users, MeowthUser, Team
from . import users_checks

def setup(bot):
    bot.add_cog(Users(bot))
