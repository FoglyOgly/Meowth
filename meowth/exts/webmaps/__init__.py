from .webmaps_cog import WebmapCog

def setup(bot):
    bot.add_cog(WebmapCog(bot))