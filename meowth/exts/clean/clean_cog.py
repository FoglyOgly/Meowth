from meowth import checks, command, group, Cog

class CleanCog(Cog):

    def __init__(self, bot):
        self.bot = bot
    
    async def is_clean_channel(self, channel_id):
        table = self.bot.dbi.table('report_channels')
        query = table.query('clean')
        query.where(channelid=channel_id)
        return await query.get_value()

    @Cog.listener()
    async def on_message(self, message):
        channel_id = message.channel.id
        if await self.is_clean_channel(channel_id):
            if message.author.id != self.bot.user.id:
                return await message.delete()
