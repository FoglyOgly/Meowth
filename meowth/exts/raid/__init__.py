from .raid_cog import RaidCog, Raid

def setup(bot):
    _list = bot.get_command('list')
    bot.add_cog(RaidCog(bot))