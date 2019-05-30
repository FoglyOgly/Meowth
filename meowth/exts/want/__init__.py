from .want_cog import WantCog, Want, Item, PartialItem

def setup(bot):
    bot.add_cog(WantCog(bot))