from .train_cog import TrainCog

def setup(bot):
    bot.add_cog(TrainCog(bot))