from .scoreboard_cog import ScoreCog

def setup(bot):
    bot.add_cog(ScoreCog(bot))