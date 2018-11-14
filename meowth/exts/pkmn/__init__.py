"""This cog contains features relating to Pokemon."""

from .pkmn_cog import Pokedex, Pokemon, Move

def setup(bot):
    bot.add_cog(Pokedex(bot))
