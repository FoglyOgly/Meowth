"""This cog contains features relating to Pokemon."""

from .pkmn_cog import Pokemon

def setup(bot):
    bot.add_cog(Pokemon(bot))
