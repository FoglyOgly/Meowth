from .raid_cog import RaidCog, Raid

def setup(bot):
    bot.add_cog(RaidCog(bot))