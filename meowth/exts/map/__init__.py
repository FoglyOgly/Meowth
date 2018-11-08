from .map_cog import Mapper, S2_L10

def setup(bot):
    bot.add_cog(Mapper(bot))