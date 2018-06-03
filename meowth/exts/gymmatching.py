import os
import json

from discord.ext import commands

from meowth import utils

class GymMatching:
    def __init__(self, bot):
        self.bot = bot
        self.gym_data = self.init_json()

    def init_json(self):
        with open(os.path.join('data', 'gym_data.json')) as fd:
            return json.load(fd)

    def get_gyms(self, guild_id):
        return self.gym_data.get(str(guild_id))

    def gym_match(self, gym_name, gyms):
        return utils.get_match(list(gyms.keys()), gym_name)

    @commands.command(hidden=True)
    async def gym_match_test(self, ctx, gym_name):
        gyms = self.get_gyms(ctx.guild.id)
        if not gyms:
            await ctx.send('Gym matching has not been set up for this server.')
            return
        match, score = self.gym_match(gym_name, gyms)
        if match:
            gym_info = gyms[match]
            coords = gym_info['coordinates']
            notes = gym_info.get('notes', 'No notes for this gym.')
            gym_info_str = (f"**Coordinates:** {coords}\n"
                            f"**Notes:** {notes}")
            await ctx.send(f"Successful match with `{match}` "
                           f"with a score of `{score}`\n{gym_info_str}")
        else:
            await ctx.send("No match found.")

def setup(bot):
    bot.add_cog(GymMatching(bot))
