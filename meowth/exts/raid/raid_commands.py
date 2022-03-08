from typing import List

import discord
from discord import app_commands

from ..pkmn import Pokemon

class RaidCommands(app_commands.Group):

    def __init__(self):
        super().__init__(name='raid', description='Report Pokemon Go raids')

    async def boss_autocomplete(
        self, interaction: discord.Interaction, current: str, namespace: app_commands.Namespace
    ) -> List[app_commands.Choice[str]]:
        bot = interaction.client
        raid_cog = bot.get_cog('RaidCog')
        raid_lists = await raid_cog.get_raid_lists()
        boss_list = [x for y in raid_lists.values() for x in list(y.keys())]
        pkmn_list = [await Pokemon(bot, x).name() for x in boss_list]
        return [
            app_commands.Choice(name=boss, value=boss)
            for boss in pkmn_list if current.lower() in boss.lower()
        ]

    @app_commands.command(name='hatched')
    @app_commands.guilds(discord.Object(id=344960572649111552))
    @app_commands.describe(boss='the raid boss', gym='the raid gym', minutes_remaining='whole number of minutes remaining')
    @app_commands.autocomplete(boss=boss_autocomplete)
    async def raid_slash_command(self, interaction: discord.Interaction, boss: str, gym: str, minutes_remaining: app_commands.Range[int, 1, 45]=45):
        await interaction.response.send_message('Thanks for your report!', ephemeral=True)
        bot = interaction.client
        raid_cog = bot.get_cog('RaidCog')
        return await raid_cog.raid_slash_command(interaction, boss, gym, minutes_remaining)
    
    