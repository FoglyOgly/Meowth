from .map_cog import Mapper, S2_L10, Gym, ReportChannel, PartialPOI

def setup(bot):
    bot.add_cog(Mapper(bot))