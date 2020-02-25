from discord.ext import commands

from meowth import checks

class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='embed')
    @checks.serverowner_or_permissions(manage_message=True)
    async def _embed(self, ctx, title, content=None, colour=None,
                     icon_url=None, image_url=None, thumbnail_url=None,
                     plain_msg=''):
        """Build and post an embed in the current channel.

        Note: Always use quotes to contain multiple words within one argument.
        """
        await ctx.embed(title=title, description=content, colour=colour,
                        icon=icon_url, image=image_url,
                        thumbnail=thumbnail_url, plain_msg=plain_msg)

def setup(bot):
    bot.add_cog(Utilities(bot))
