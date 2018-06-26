import asyncio
import re
import discord
from discord.ext import commands


from meowth import utils
from meowth import checks
from meowth import pkmn_match

from meowth.exts import pokemon



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


    def embed(self):

        colour = discord.Colour(0x63b2f7)
        offer_url = self.author_offers.img_url
        embed = discord.Embed(colour=colour)
        embed.set_author(name=f"Pokemon Trade", icon_url='https://raw.githubusercontent.com/FoglyOgly/Meowth/discordpy-v1/images/misc/trade_icon_small.png')
        if self.author_confirms and self.trader_confirms:
            embed = discord.Embed(colour=colour, description='This trade has been completed!')
            return embed
        if self.trader:
            embed.set_footer(text=f"{self.trader.display_name}", icon_url=self.trader.avatar_url)
        embed.set_thumbnail(url=offer_url)
        if self.author_accepts and self.trader_accepts:
            embed.add_field(name=f'{self.author.display_name} offered:', value=f'{str(self.author_offers)}')
            embed.add_field(name=f'{self.trader.display_name} offered:', value=f'{str(self.trader_offers)}')
            return embed
        if self.author_wants:
            want_str = ""
            i = 1
            for pkmn in self.author_wants:
                emoji = f'{i}\u20e3'
                want_str = want_str +  emoji + f': {str(pkmn)}\n'
                i += 1
            embed.add_field(name=f'{self.author.display_name} wants:', value=want_str)
        if self.trader_offers:
            embed.add_field(name=f'{self.trader.display_name} offers:', value=str(self.trader_offers))


        return embed


    async def message(self, ctx):
        role = self.author_offers.role(ctx.guild)
        if role:
            rolestr = role.mention + "- "
        else:
            rolestr = ""
        return await ctx.send(f"{rolestr}Meowth! {self.author.mention} offers a {str(self.author_offers)} for trade!\n\nReact to this message to make an offer!",embed=self.embed())

    async def clear_offer(self, message):
        await message.clear_reactions
        msg = f"Meowth! {self.author.mention} offers a {str(self.author_offers)} for trade! React to this message to make an offer!"
        self.trader = None
        self.trader_offers = None
        self.trader_accepts = False
        self.trader_confirms = False
        self.author_accepts = False
        self.author_confirms = False
        await message.edit(content=msg, embed=self.embed())

    async def accept_offer(self, message):
        await message.clear_reactions()
        msg = f"Meowth! {self.author.mention} and {self.trader.mention} have agreed to a trade!\n\n"
        f"{self.author.display_name} will trade their {str(self.author_offers)} for {self.trader.display_name}'s {str(self.trader_offers)}!\n\n"
        f"Please coordinate this trade via Direct Message and react to this message with :ballot_box_with_check: when the trade is complete!"
        await message.edit(content=msg, embed=self.embed())
        await message.add_reaction('\u2611')

    async def confirm_trade(self, message):
        await message.clear_reactions()
        msg = f"Meowth! {self.author.display_name} traded their {str(self.author_offers)} for {self.trader.display_name}'s {str(self.trader_offers)}!"
        await message.edit(content=msg, embed=self.embed())




class Trading:
    def __init__(self, bot):
        self.bot = bot

    async def on_raw_reaction_add(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        try:
            message = await channel.get_message(payload.message_id)
        except (discord.errors.NotFound, AttributeError):
            return
        guild = message.guild
        try:
            user = guild.get_member(payload.user_id)
        except AttributeError:
            return
        trade_dict = self.bot.guild_dict[guild.id].setdefault('trade_dict', {})
        if user == guild.me:
            return
        if message.id in trade_dict:
            trade = trade_dict[message.id]['trade']
            if trade.author_accepts and trade.trader_accepts:
                if str(payload.emoji) == '\u2611':
                    if user == trade.author:
                        trade.author_confirms = True
                    if user == trade.trader:
                        trade.trader_confirms = True
                    if trade.author_confirms and trade.trader_confirms:
                        await trade.confirm_trade(message)
                        del trade_dict[message.id]
            if trade.trader_offers:
                if str(payload.emoji) == '\u2705':
                    if user == trade.trader:
                        trade.trader_accepts = True
                    if user == trade.author:
                        trade.author_accepts = True
                    if trade.trader_accepts and trade.author_accepts:
                        await trade.accept_offer(message)
                if str(payload.emoji) == '\u274e' and (user == trade.trader or user == trade.author):
                    await trade.clear_offer(message)
                    for emoji in trade_dict[message.id]['emoji']:
                        await message.add_reaction(emoji)
                        await asyncio.sleep(0.25)



            if trade.author_wants and str(payload.emoji) in trade_dict[message.id]['emoji']:
                i = trade_dict[message.id]['emoji'].index(str(payload.emoji))
                trade.trader = user
                trade.trader_offers = trade.author_wants[i]
                await message.edit(content=f"Meowth! {trade.author.mention} offers a {str(trade.author_offers)} for trade and {trade.trader.mention} offers a {str(trade.trader_offers)} in exchange!"
                "\n\nTo confirm this trade, both members must react with :white_check_mark:! Either member can cancel with :negative_squared_cross_mark:", embed=trade.embed())
                await message.clear_reactions()
                await message.add_reaction('\u2705')
                await message.add_reaction('\u274e')
            trade_dict[message.id]['trade'] = trade




    @commands.command()
    async def trade(self, ctx, *, offer):
        trade_dict = ctx.bot.guild_dict[ctx.guild.id].setdefault('trade_dict', {})
        pkmn = await pokemon.Pokemon.convert(ctx, offer)
        # rgx = '[^a-zA-Z0-9]'
        # pkmn_match = next((p for p in ctx.bot.pkmn_info['pokemon_list'] if re.sub(rgx, '', p) == re.sub(rgx, '', offer)), None)
        # if not pkmn_match:
        #     return await ctx.send(f"Meowth! {offer} is not a Pokemon!")
        trade = {'author': ctx.author, 'author_offers': pkmn}
        trade = Trade(trade)
        trademsg = await trade.message(ctx)
        detailsmsg = await ctx.send(f"{ctx.author.mention}, what Pokemon are you willing to accept in exchange for {str(pkmn)}?")
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        want_reply = await ctx.bot.wait_for('message', check=check)
        await detailsmsg.delete()
        await want_reply.delete()
        want_split = want_reply.content.lower().split(',')
        want_pkmn_list = []
        for want in want_split:
            pkmn = await pokemon.Pokemon.convert(ctx, want)
            want_pkmn_list.append(pkmn)
        trade.author_wants = want_pkmn_list
        await trademsg.edit(embed=trade.embed())
        emoji_list = []
        for i in range(len(want_split)):
            i += 1
            emoji = f'{i}\u20e3'
            await trademsg.add_reaction(emoji)
            emoji_list.append(emoji)
            await asyncio.sleep(0.25)
        trade_dict[trademsg.id] = {'trade': trade, 'emoji': emoji_list}




def setup(bot):
    bot.add_cog(Trading(bot))
