from .clean_cog import CleanCog

def setup(bot):
    bot.add_cog(CleanCog(bot))