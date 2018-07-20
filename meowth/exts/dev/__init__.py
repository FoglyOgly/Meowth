"""This cog contains primarily developer-focused features.

There is a local check that limits all commands to be used by co-owners
of the bot and above.
"""

from .dev_cog import Dev

def setup(bot):
    bot.add_cog(Dev(bot))
