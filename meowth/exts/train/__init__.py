from .train_cog import TrainCog, Train, TrainEmbed

def setup(bot):
    bot.add_cog(TrainCog(bot))