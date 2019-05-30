from .research_cog import ResearchCog, Research, Item

def setup(bot):
    bot.add_cog(ResearchCog(bot))