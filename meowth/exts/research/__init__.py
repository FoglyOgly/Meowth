from .research_cog import ResearchCog, Research

def setup(bot):
    bot.add_cog(ResearchCog(bot))