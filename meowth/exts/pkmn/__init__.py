"""This cog contains features relating to Pokemon."""

from .pkmn_cog import Pokedex

def setup(bot):
    bot.add_cog(Pokedex(bot))
