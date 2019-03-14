from .raid_cog import RaidCog

def setup(bot):
    bot.add_cog(RaidCog(bot))

def teardown(bot):
    print(0)
    bot.remove_cog('RaidCog')