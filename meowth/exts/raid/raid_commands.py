from typing import List, Literal

import discord
from discord import app_commands

from ..pkmn import Pokemon

class RaidCommands(app_commands.Group):

    def __init__(self):
        super().__init__(name='raid', description='Report Pokemon Go raids')
    
    async def on_error(self, interaction, command, error):
        raise error.original

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
        ][:25]

    async def gym_autocomplete(
        self, interaction: discord.Interaction, current: str, namespace: app_commands.Namespace
    ) -> List[app_commands.Choice[str]]:
        bot = interaction.client
        map_cog = bot.get_cog('Mapper')
        gym_list = await map_cog.list_all_gyms(interaction.channel)
        return [
            app_commands.Choice(name=gym, value=gym)
            for gym in gym_list if current.lower() in gym.lower()
        ][:25]

    @app_commands.command(name='hatched')
    @app_commands.describe(boss='the raid boss', gym='the raid gym', minutes_remaining='whole number of minutes remaining')
    @app_commands.autocomplete(boss=boss_autocomplete, gym=gym_autocomplete)
    async def raid_slash_command(self, interaction: discord.Interaction, boss: str, gym: str, minutes_remaining: app_commands.Range[int, 1, 45]=45):
        await interaction.response.send_message('Thanks for your report!', ephemeral=True)
        bot = interaction.client
        raid_cog = bot.get_cog('RaidCog')
        boss = boss.replace(' ', '')
        return await raid_cog.raid_slash_command(interaction, boss, gym, minutes_remaining)
    
    @app_commands.command(name='egg')
    @app_commands.describe(level='the raid level', gym='the raid gym', minutes_to_hatch='whole number of minutes to hatch')
    @app_commands.autocomplete(gym=gym_autocomplete)
    async def egg_slash_command(self, interaction: discord.Interaction, level: Literal['1', '3', '5', '7'], gym: str, minutes_to_hatch: app_commands.Range[int, 1, 60]=60):
        await interaction.response.send_message('Thanks for your report!', ephemeral=True)
        bot = interaction.client
        raid_cog = bot.get_cog('RaidCog')
        return await raid_cog.egg_slash_command(interaction, level, gym, minutes_to_hatch)
    
    