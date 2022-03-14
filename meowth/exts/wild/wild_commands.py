from typing import List
import discord
from discord import app_commands

from ..pkmn import Pokemon

class WildCommands(app_commands.Group):

    def __init__(self):
        super().__init__(name='wild', description='Report Pokemon Go wild spawns')
    
    async def on_error(self, interaction, command, error):
        raise error.original

    async def pokemon_autocomplete(
        self, interaction: discord.Interaction, current: str, namespace: app_commands.Namespace
    ) -> List[app_commands.Choice[str]]:
        bot = interaction.client
        pkmn_cog = bot.get_cog('Pokedex')
        wild_list = await pkmn_cog.get_wilds()
        pkmn_list = [await x.name() for x in wild_list]
        return [
            app_commands.Choice(name=pkmn, value=pkmn)
            for pkmn in pkmn_list if current.lower() in pkmn.lower()
        ][:25]
    
    async def location_autocomplete(
        self, interaction: discord.Interaction, current: str, namespace: app_commands.Namespace
    ) -> List[app_commands.Choice[str]]:
        bot = interaction.client
        map_cog = bot.get_cog('Mapper')
        poi_list = await map_cog.list_all_pois(interaction.channel)
        return [
            app_commands.Choice(name=poi, value=poi)
            for poi in poi_list if current.lower() in poi.lower()
        ][:25]


    @app_commands.command(name='spawn')
    @app_commands.describe(pokemon='the wild pokemon', location='the spawn location', disguise='the pokemon Ditto is disguised as')
    @app_commands.autocomplete(pokemon=pokemon_autocomplete, location=location_autocomplete, disguise=pokemon_autocomplete)
    async def wild_slash_command(self, interaction: discord.Interaction, pokemon: str, location: str, disguise: str=None):
        await interaction.response.send_message('Thanks for your report!', ephemeral=True)
        bot = interaction.client
        wild_cog = bot.get_cog('WildCog')
        pokemon = pokemon.replace(' ', '')
        return await wild_cog.wild_slash_command(interaction, pokemon, location, disguise)
