from .raid_cog import RaidCog

def setup(bot):
    bot.add_cog(RaidCog(bot))