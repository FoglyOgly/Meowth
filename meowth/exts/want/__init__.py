from .want_cog import WantCog, Want

def setup(bot):
    bot.add_cog(WantCog(bot))