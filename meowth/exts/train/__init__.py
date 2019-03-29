from .train_cog import TrainCog, Train, TrainEmbed, RaidEmbed

def setup(bot):
    bot.add_cog(TrainCog(bot))