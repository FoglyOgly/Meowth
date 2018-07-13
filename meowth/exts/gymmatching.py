import asyncio
import os
import json

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

import discord
from discord.ext import commands

from unidecode import unidecode

class GymMatching:
    def __init__(self, bot):
        self.bot = bot
        self.gym_data = self.init_json()
        self.gym_data = self.prepare_gyms_data()
        self.num_to_emoji = {0: '0\u20e3', 1: '1\u20e3', 2: '2\u20e3', 3: '3\u20e3', 4: '4\u20e3', 5: '5\u20e3',
                             6: '6\u20e3', 7: '7\u20e3', 8: '8\u20e3', 9: '9\u20e3'}
        self.emoji_to_num = {v: k for k, v in self.num_to_emoji.items()}

    def init_json(self):
        with open(os.path.join('data', 'gym_data.json')) as fd:
            return json.load(fd)

    def prepare_gyms_data(self):
        updated_gyms_data = {}
        for guild, gyms in self.gym_data.items():
            updated_gyms_data[guild] = {}
            for gym, data in gyms.items():
                new_name = unidecode(gym)
                updated_gyms_data[guild][new_name.lower()] = data
                updated_gyms_data[guild][new_name.lower()]['name'] = gym
        return updated_gyms_data

    def get_gyms(self, guild_id):
        return self.gym_data.get(str(guild_id))

    def gym_match(self, gym_name, gyms):
        return self._get_n_match(list(gyms.keys()), gym_name, 1)

    def _get_n_match(self, gyms: list, gym: str, max_count: int = 9):
        """Uses fuzzywuzzy to see if gym is close to entries in gyms

        Returns a list of tuples of (MATCH, SCORE)
        """
        result = process.extract(gym, gyms, scorer=fuzz.token_set_ratio, limit=max_count)
        return [] if not result else result

    def _create_embed_gyms(self, ctx, gym, add_emoji: bool = False, verbose: bool = True, score_limit: int = 70,
                           count_limit: int = 10):
        if count_limit > 10:
            count_limit = 10
        gyms = self.get_gyms(ctx.guild.id)
        if not gyms:
            return None
        normalized_gym_name = unidecode(gym).lower()
        result = self._get_n_match(list(gyms.keys()), normalized_gym_name, count_limit)
        if len(result) == 0:
            return None
        embed = discord.Embed(colour=ctx.guild.me.colour,
                              description=f"Dla podanej nazwy **\"{gym}\"** znaleziono następujące gymy")
        printed = []
        gyms_to_print = []
        for match, score in result:
            if score < score_limit:
                continue
            if len(printed) > count_limit-1:
                continue
            gym_info = gyms[match]
            name = gym_info['name']
            coords = gym_info['coordinates']
            coords_link = "https://www.google.com/maps/search/?api=1&query={0}".format('+'.join(coords.split()))
            coords_str = f"Współrzędne: [{coords}]({coords_link})"
            notes = gym_info.get('notes', None)
            notes_str = "" if notes is None else f"\nDodatkowe informacje: {notes}"
            districts = gym_info.get('districts', [])
            districts_str = '' if districts is None else "\nDzielnice: **{}**".format(", ".join(districts))
            is_ex = gym_info.get('is_ex', None)
            can_be_ex = gym_info.get('can_be_ex', None)
            ex_status = ''
            if is_ex == "Yes":
                ex_status = 'ex-raidowy'
            else:
                if can_be_ex == "Yes":
                    ex_status = 'potencjalnie ex-rajdowy'
                else:
                    if is_ex is not None and can_be_ex is not None:
                        ex_status = 'zwykły'
                    else:
                        ex_status = 'nieznany'
            ex_status_str = f"\nTyp gymu: **{ex_status}**"
            emoji = "" if add_emoji is False else self.num_to_emoji[len(printed)] + " "
            if verbose:
                value = f"{coords_str}{districts_str}{ex_status_str}{notes_str}"
                embed.add_field(name=f"{emoji}{name}", value=value, inline=False)
            else:
                gyms_to_print.append(f"{emoji}{name}")
            printed.append((name, districts))
        if not verbose:
            embed.add_field(name="Wybierz jeden z gymów używając emoji poniżej:", value="\n".join(gyms_to_print))
        return embed, printed

    @commands.command(aliases=['findgym', 'znajdźgym', 'znajdzgym', 'szukajgym', 'szukajgyma', 'szukajgymu'])
    async def find_gym(self, ctx, *, gym):
        guild = ctx.guild
        gyms = self.get_gyms(guild.id)
        if not gyms:
            await ctx.send('Gym matching nie został poprawnie skonfigurowany {}.'.format(guild.id))
            return
        embed, printed = self._create_embed_gyms(ctx, gym)
        if embed is not None and len(printed) > 0:
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"Nie znaleziono żadnego gymu pasującego do \"{gym}\".")

    async def pick_gym_prompt(self, ctx, gym):
        embed, printed = self._create_embed_gyms(ctx, gym, add_emoji=True, verbose=False)
        if embed is None or len(printed) == 0:
            return None, None
        if len(printed) == 1:
            return printed[0]
        try:
            q_msg = await ctx.send(embed=embed)
            reaction, user = await self._ask(ctx, q_msg, [ctx.message.author.id],
                                             [self.num_to_emoji[key] for key in range(len(printed))])
        except TypeError:
            await q_msg.delete()
            return None, None
        await q_msg.delete()
        if not reaction:
            return "__TIMEOUT__", None
        if reaction.emoji not in self.emoji_to_num:
            return None, None
        return printed[self.emoji_to_num[reaction.emoji]]

    async def _ask(self, ctx, message, user_list: list, react_list: list):
        def check(reaction, user):
            return (user.id in user_list) and (reaction.message.id == message.id) and (reaction.emoji in react_list)

        for r in react_list:
            await asyncio.sleep(0.1)
            await message.add_reaction(r)
        try:
            reaction, user = await ctx.bot.wait_for('reaction_add', check=check, timeout=10)
            return reaction, user
        except asyncio.TimeoutError:
            await message.clear_reactions()
            return None, None


def setup(bot):
    bot.add_cog(GymMatching(bot))
