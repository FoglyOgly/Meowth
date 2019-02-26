from .trade_cog import TradeCog

def setup(bot):
    bot.add_cog(TradeCog(bot))