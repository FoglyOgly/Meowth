from .tutorial_cog import Tutorial

def setup(bot):
    bot.add_cog(Tutorial(bot))