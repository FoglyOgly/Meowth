from .raid_cog import RaidCog, Raid, Meetup

def setup(bot):
    bot.add_cog(RaidCog(bot))