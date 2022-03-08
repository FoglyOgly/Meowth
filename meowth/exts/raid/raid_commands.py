import discord
from discord import app_commands

class RaidCommands(app_commands.Group):

    @app_commands.command(name='raid')
    @app_commands.guilds(discord.Object(id=344960572649111552))
    async def raid_slash_command(self, interaction: discord.Interaction, boss: str, gym: str, minutes_remaining: app_commands.Range[int, 1, 45]=45):
        bot = interaction.client
        raid_cog = bot.get_cog('RaidCog')
        return await raid_cog.raid_slash_command(interaction, boss, gym, minutes_remaining)