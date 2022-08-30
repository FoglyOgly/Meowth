from typing import List
import discord
from discord import app_commands
from .research_cog import Task, ItemReward
from ..pkmn import Pokemon

class ResearchCommands(app_commands.Group):

    def __init__(self):
        super().__init__(name='research', description='Report Pokemon Go field research')

    async def on_error(self, interaction, command, error):
        raise error.original
    
    async def task_autocomplete(
        self, interaction: discord.Interaction, current: str, namespace: app_commands.Namespace
    ) -> List[app_commands.Choice[str]]:
        bot = interaction.client
        research_cog = bot.get_cog('ResearchCog')
        task_list = await research_cog.get_tasks(current)
        return [
            app_commands.Choice(name=x, value=x)
            for x in task_list
        ][:25]
    
    async def reward_autocomplete(
        self, interaction: discord.Interaction, current: str, namespace: app_commands.Namespace
    ) -> List[app_commands.Choice[str]]:
        bot = interaction.client
        task = Task(bot, namespace.task)
        possible_rewards = await task.possible_rewards()
        async def reward_desc(reward):
            if '/' in reward:
                reward = ItemReward(bot, reward)
                desc = await reward.description()
            elif reward == 'unknown_encounter':
                desc = "Unknown Encounter"
            else:
                pkmn = Pokemon(bot, reward)
                desc = await pkmn.name()
            return desc
        reward_descs = [await reward_desc(x) for x in possible_rewards]
        return [
            app_commands.Choice(name=x, value=x)
            for x in reward_descs if current.lower() in x.lower()
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
    
    @app_commands.command(name='task')
    @app_commands.describe(task='the field research task', reward='the Pokemon or item reward', location='the Pokestop where the research is')
    @app_commands.autocomplete(task=task_autocomplete, reward=reward_autocomplete, location=location_autocomplete)
    async def research_slash_command(self, interaction: discord.Interaction, task: str, reward: str, location: str):
        await interaction.response.send_message('Thanks for your report!', ephemeral=True)
        bot = interaction.client
        research_cog = bot.get_cog('ResearchCog')
        reward = reward.replace(' ', '')
        return await research_cog.research_slash_command(interaction, task, location, reward)
