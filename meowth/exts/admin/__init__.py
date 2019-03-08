from .admin_cog import AdminCog

def setup(bot):
    bot.add_cog(AdminCog(bot))