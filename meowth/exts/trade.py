import asyncio
import re
import discord
from discord.ext import commands


from meowth import utils
from meowth import checks
from meowth import pkmn_match



class Trade:

    __slots__ = ['author', 'author_wants', 'author_offers', 'author_accepts', 'author_confirms', 'friendship_level',
    'trader', 'trader_offers', 'trader_accepts', 'trader_confirms', 'canceled']

    def __init__(self,data):
        self.author = data.get('author')
        self.author_wants = data.get('author_wants')
        self.author_offers = data.get('author_offers')
        self.author_accepts = data.get('author_accepts', False)
        self.author_confirms = data.get('author_confirms', False)
        self.friendship_level = data.get('friendship_level', 0)
        self.trader = data.get('trader')
        self.trader_offers = data.get('trader_offers')
        self.trader_accepts = data.get('trader_accepts', False)
        self.trader_confirms = data.get('trader_confirms', False)
        self.canceled = data.get('canceled', False)


    def embed(self, bot):

        colour = discord.Colour(0x63b2f7)

        def get_pkmn_url(name: str, shiny: bool):
            number = utils.get_number(bot, name)
            shiny_str = ""
            if shiny:
                shiny_str = "s"
            url = 'https://raw.githubusercontent.com/FoglyOgly/Meowth/discordpy-v1/images/pkmn/{0}_{1}.png?cache=1'.format(str(number).zfill(3),shiny_str)
            return url

        embed = discord.Embed(colour=colour)
        embed.set_author(name=f"{self.author.display_name}", icon_url=self.author.avatar_url)
        if self.trader:
            embed.set_footer(text=f"{self.trader.display_name}", icon_url=self.trader.avatar_url)
        if self.trader_offers:
            embed.set_image(url=get_pkmn_url(self.trader_offers))
        if 'shiny' in self.author_offers.lower():
            shiny = True
            self.author_offers = self.author_offers.replace('shiny', '').strip()
        else:
            shiny = False
        embed.set_thumbnail(url=get_pkmn_url(self.author_offers, shiny))
        if self.author_wants:
            want_str = ""
            i = 1
            for want in self.author_wants:
                emoji = f'{i}\u20e3'
                want_str = want_str +  emoji + f': {want}\n'
                i += 1
            embed.add_field(name=f'{self.author.display_name} wants:', value=want_str)

        return embed


    async def message(self, ctx):
        # role = discord.utils.get(ctx.guild.roles, name=self.author_offers)
        return await ctx.send(f"Meowth! {self.author.mention} wants to trade!\n\nOffers: {self.author_offers}\n\nReact to this message to make an offer!",embed=self.embed(ctx.bot))


class Trading:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def trade(self, ctx, *, offer):
        # rgx = '[^a-zA-Z0-9]'
        # pkmn_match = next((p for p in ctx.bot.pkmn_info['pokemon_list'] if re.sub(rgx, '', p) == re.sub(rgx, '', offer)), None)
        # if not pkmn_match:
        #     return await ctx.send(f"Meowth! {offer} is not a Pokemon!")
        trade = {'author': ctx.author, 'author_offers': offer}
        trade = Trade(trade)
        trademsg = await trade.message(ctx)
        detailsmsg = await ctx.send(f"{ctx.author.mention}, what Pokemon are you willing to accept in exchange for {offer.title()}?")
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        want_reply = await ctx.bot.wait_for('message', check=check)
        await detailsmsg.delete()
        await want_reply.delete()
        want_split = want_reply.content.lower().split(',')
        trade.author_wants = want_split
        await trademsg.edit(embed=trade.embed(ctx.bot))
        for i in range(len(want_split)):
            i += 1
            await trademsg.add_reaction(f'{i}\u20e3')
            await asyncio.sleep(0.25)


def setup(bot):
    bot.add_cog(Trading(bot))
