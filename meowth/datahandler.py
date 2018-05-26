import json
from functools import partial

from discord.ext import commands
import utils
import checks

class DataHandler:
    """Data Loading and Saving Test Cog."""

    def __init__(self, bot):
        self.bot = bot
        self.raid_info = None
        self.pkmn_info = None
        self.init_json(bot.raid_json_path, bot.pkmn_info_path)
        self.pkmn_match = partial(utils.get_match, self.pkmn_info['pokemon_list'])

    def __local_check(self, ctx):
        return checks.is_owner_check(ctx) or checks.is_dev_check(ctx)

    def init_json(self, raid_path, pkmn_path):
        with open(raid_path) as fd:
            self.raid_info = json.load(fd)
        with open(pkmn_path) as fd:
            self.pkmn_info = json.load(fd)

    def get_name(self, pkmn_number):
        pkmn_number = int(pkmn_number) - 1
        try:
            name = self.pkmn_info['pokemon_list'][pkmn_number]
        except IndexError:
            name = None
        return name

    def get_number(self, pkm_name):
        try:
            number = self.pkmn_info['pokemon_list'].index(pkm_name) + 1
        except ValueError:
            number = None
        return number

    @commands.group(invoke_without_command=True)
    async def raiddata(self, ctx, level=None):
        """Show all raid Pokemon, showing only the raid level if provided."""
        data = []
        title = None
        if level:
            title = f"Pokemon Data for Raid {level}"
            try:
                for pkmnno in self.raid_info['raid_eggs'][level]["pokemon"]:
                    data.append(f"#{pkmnno} - {self.get_name(pkmnno)}")
            except KeyError:
                return await ctx.send('Invalid raid level specified.')
        else:
            title = f"Pokemon Data for All Raids"
            data = []
            for pkmnlvl, vals in self.raid_info['raid_eggs'].items():
                if not vals["pokemon"]:
                    continue
                leveldata = []
                for pkmnno in vals["pokemon"]:
                    leveldata.append(f"#{pkmnno} - {self.get_name(pkmnno)}")
                leveldata = '\n'.join(leveldata)
                data.append(f"**Raid {pkmnlvl} Pokemon**\n{leveldata}\n")
        data_str = '\n'.join(data)
        await ctx.send(f"**{title}**\n{data_str}")

    @raiddata.command(name='remove', aliases=['rm', 'del', 'delete'])
    async def remove_rd(self, ctx, *raid_pokemon):
        """Removes all pokemon provided as arguments from the raid data.

        Note: If a multi-word pokemon name is used, wrap in quote marks:
        Example: !raiddata remove "Mr Mime" Jynx
        """
        results = []
        for pokemon in raid_pokemon:
            if not pokemon.isdigit():
                pokemon = self.pkmn_match(pokemon)[0]
                if not pokemon:
                    return await ctx.send('Invalid Pokemon Name')
                pokemon = self.get_number(pokemon)
            hit_key = []
            for k, v in self.raid_info['raid_eggs'].items():
                if pokemon in v['pokemon']:
                    hit_key.append(k)
                    self.raid_info['raid_eggs'][k]['pokemon'].remove(pokemon)
            hits = '\n'.join(hit_key)
            results.append(f"#{pokemon} {self.get_name(pokemon)} from {hits}")
        results_st = '\n'.join(results)
        await ctx.send(f"**Pokemon removed from raid data**\n{results_st}")

    @raiddata.command(name='add')
    async def add_rd(self, ctx, level, *raid_pokemon):
        """Adds all pokemon provided as arguments to the specified raid
        level in the raid data.
        
        Note: If a multi-word pokemon name is used, wrap in quote marks:
        Example: !raiddata add "Mr Mime" Jynx
        """
        results = []
        if level not in self.raid_info['raid_eggs'].keys():
            return await ctx.send("Invalid raid level specified.")
        for pokemon in raid_pokemon:
            if not pokemon.isdigit():
                pokemon = self.pkmn_match(pokemon)[0]
                if not pokemon:
                    return await ctx.send('Invalid Pokemon Name')
                pokemon = self.get_number(pokemon)
            self.raid_info['raid_eggs'][level]['pokemon'].append(pokemon)
            results.append(f"#{pokemon} {self.get_name(pokemon)}")
        results_st = '\n'.join(results)
        await ctx.send(f"**Pokemon added to Raid {level}**\n{results_st}")

    @raiddata.command(name='save', aliases=['commit'])
    async def save_rd(self, ctx):
        """Saves the current raid data state to the json file."""
        with open(ctx.bot.raid_json_path, 'w') as fd:
            json.dump(self.raid_info, fd, indent=4)
        await ctx.message.add_reaction('\u2705')

def setup(bot):
    bot.add_cog(DataHandler(bot))
