"""This cog contains support for i18n."""

from .i18n_cog import I18n

def setup(bot):
    bot.add_cog(I18n(bot))
