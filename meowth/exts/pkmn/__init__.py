"""This cog contains features relating to Pokemon."""

from .pkmn_cog import Pokedex, Pokemon, Move, RaidBoss

def setup(bot):
    bot.add_cog(Pokedex(bot))
