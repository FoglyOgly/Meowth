import asyncio
import re
import functools

import discord
from discord.ext import commands

from meowth import utils
from meowth import checks
from meowth import pkmn_match

from meowth.exts import pokemon


class Trade:

    __slots__ = [
        'bot', '_data', 'lister_id', 'listing_id', 'report_channel_id',
        'guild_id', 'wanted_pokemon', 'offered_pokemon', 'offers']

    def __init__(self, bot, lister_id, message_id, channel_id, guild_id,
                 wanted_pokemon, offered_pokemon):
        self.bot = bot
        trade_dict = bot.guild_dict[guild_id].setdefault('trade_dict', {})
        trade_channel_data = trade_dict.setdefault(channel_id, {})
        trade_channel_data[message_id] = {
            'lister_id'         : lister_id,
            'report_channel_id' : channel_id,
            'guild_id'          : guild_id,
            'wanted_pokemon'    : wanted_pokemon,
            'offered_pokemon'   : offered_pokemon,
            'offers'            : {}
        }
        self._data = trade_channel_data[message_id]
        self.lister_id = self._data['lister_id']
        self.listing_id = message_id
        self.report_channel_id = self._data['report_channel_id']
        self.guild_id = self._data['guild_id']
        self.wanted_pokemon = self._data['wanted_pokemon']
        self.offered_pokemon = self._data['offered_pokemon']
        self.offers = self._data['offers']

    async def on_raw_reaction_add(self, payload):

        # ignore if not relevant to this trade object
        if payload.message_id != self.listing_id:
            return



        emoji_check = [
            '\u20e3' in payload.emoji.name, # keycap 1-9
            '\u23f9' == payload.emoji.name # stop button
        ]

        if not any(emoji_check):
            return

        if payload.user_id != self.lister_id and '\u20e3' in payload.emoji.name:
            i = int(payload.emoji.name[0])
            offer = self.wanted_pokemon[i-1]
            await self.make_offer(payload.user_id, offer)

        elif payload.user_id == self.lister_id and payload.emoji.name == '\u23f9':
            await self.cancel_trade()


    @property
    def guild(self):
        return self.bot.get_guild(self.guild_id)

    @property
    def listing_channel(self):
        return self.guild.get_channel(self.report_channel_id)

    @property
    def lister(self):
        return self.guild.get_member(self.lister_id)

    @property
    def embed(self):
        return self.make_trade_embed(
            self.lister, self.wanted_pokemon, self.offered_pokemon)

    @staticmethod
    def make_trade_embed(lister, wanted_pokemon, offered_pokemon):
        """Returns a formatted embed message with trade details."""
        icon_url = (
            "https://raw.githubusercontent.com/FoglyOgly/Meowth/"
            "trade-beta/images/misc/trade_icon_small.png"
        )

        wants = [
            f'{i+1}\u20e3: {pkmn}' for i, pkmn in enumerate(wanted_pokemon)
        ]

        return utils.make_embed(
            title="Pokemon Trade - {}".format(lister.display_name),
            msg_colour=0x63b2f7,
            icon=icon_url,
            fields={
                "Wants":'\n'.join(wants),
                "Offers": str(offered_pokemon)
                },
            inline=True,
            footer=lister.display_name,
            footer_icon=lister.avatar_url_as(format='png', size=256),
            thumbnail = offered_pokemon.img_url
        )

    @staticmethod
    def make_offer_embed(trader, listed_pokemon, offer):
        icon_url = (
            "https://raw.githubusercontent.com/FoglyOgly/Meowth/"
            "trade-beta/images/misc/trade_icon_small.png"
        )

        return utils.make_embed(
            title = "Pokemon Trade Offer - {}".format(trader.display_name),
            msg_colour = 0x63b2f7,
            icon = icon_url,
            fields = {
                "You Offered": str(listed_pokemon),
                "They Offer": str(offer)
                },
            inline=True,
            footer = trader.display_name,
            footer_icon = trader.avatar_url_as(format='png', size=256),
            thumbnail = offer.img_url
        )

    @classmethod
    async def create_trade(cls, ctx, wanted_pokemon, offered_pokemon):
        """Creates a trade object and sends trade details in channel"""

        trade_embed = cls.make_trade_embed(
            ctx.author, wanted_pokemon, offered_pokemon)

        offer_str = "Meowth! {lister} offers a {pkmn} up for trade!".format(
            lister=ctx.author.display_name,
            pkmn=offered_pokemon
        )

        instructions = "React to this message to make an offer!"
        cancel_inst = "{lister} may cancel the trade with :stop_button:".format(
            lister = ctx.author.display_name
        )

        trade_msg = await ctx.send(f"{offer_str}\n\n{instructions}\n\n{cancel_inst}", embed=trade_embed)
        for i in range(len(wanted_pokemon)):
            await trade_msg.add_reaction(f'{i+1}\u20e3')
            await asyncio.sleep(0.25)
        await trade_msg.add_reaction('\u23f9')

        trade = cls(
            ctx.bot, ctx.author.id, trade_msg.id, ctx.channel.id, ctx.guild.id,
            wanted_pokemon, offered_pokemon)

        ctx.bot.add_listener(trade.on_raw_reaction_add)

        return trade

    @classmethod
    def from_data(cls, bot, message_id, data):
        trade = cls(
            bot, data['lister_id'], message_id, data['report_channel_id'],
            data['guild_id'], data['wanted_pokemon'], data['offered_pokemon']
        )

        bot.add_listener(trade.on_raw_reaction_add)

        return trade

    async def get_listmsg(self):
        return await self.listing_channel.get_message(self.listing_id)

    async def make_offer(self, trader_id, pkmn):
        self.offers[trader_id] = pkmn
        trader = self.guild.get_member(trader_id)
        offer_embed = self.make_offer_embed(
            trader, self.offered_pokemon, pkmn
        )
        offermsg = await self.lister.send(
            """Meowth! {} offers to trade their {} for your {}!
        React with :white_check_mark: to accept the offer or :negative_squared_cross_mark: to reject it!""".format(
                trader.display_name, pkmn, self.offered_pokemon),
            embed = offer_embed)
        reaction, user = await utils.ask(self.bot, offermsg, timeout=None)
        if reaction.emoji == '\u2705':
            await self.accept_offer(trader_id)
        elif reaction.emoji == '\u274e':
            await self.reject_offer(trader_id)
            await offermsg.delete()


    async def accept_offer(self, offer_id):
        offer = self.offers[offer_id]
        trader = self.guild.get_member(offer_id)
        lister = self.lister
        listingmsg = await self.get_listmsg()
        acceptedmsg = """Meowth! {} has agreed to trade their {} for {}'s {}\n\n
            Please DM them to coordinate the trade!
            React with :ballot_box_with_check: when the trade has been completed!
            To reject or cancel this offer, react with :stop_button:""".format(
                self.lister.mention, self.offered_pokemon, trader.mention, offer)
        special_check = [self.offered_pokemon.shiny, self.offered_pokemon.legendary,
            offer.shiny, offer.legendary]
        if any(special_check):
            acceptedmsg += ('\n\nThis is a Special Trade! These can only be completed'
                ' once per day and can cost up to 1 million stardust! '
                'Significant discounts can be earned by leveling up your friendship '
                'before the trade is made!')
        tradermsg = await trader.send(acceptedmsg)
        listermsg = await lister.send(acceptedmsg)
        await tradermsg.add_reaction('\u2611')
        await tradermsg.add_reaction('\u23f9')
        await listermsg.add_reaction('\u2611')
        await listermsg.add_reaction('\u23f9')

        for offerid in self.offers.keys():
            if offerid != offer_id:
                reject = self.guild.get_member(offerid)
                await reject.send("Meowth... {} accepted a competing offer for their {}. ".format(
                    self.lister.display_name, self.offered_pokemon))
                del self.offers[offerid]

        await listingmsg.edit(content='Meowth! {} has accepted an offer!'.format(self.lister.display_name), embed=self.embed)
        await listingmsg.clear_reactions()

        trader_confirms = False
        lister_confirms = False

        def check(r, u):
            user_check = [u == trader, u == lister]
            msg_check = [r.message.id == tradermsg.id, r.message.id == listermsg.id]
            emoji_check = [r.emoji == '\u2611', r.emoji == '\u23f9']
            if not any(msg_check) or not any(user_check) or not any(emoji_check):
                return False
            else:
                return True

        while True:
            reaction, user = await self.bot.wait_for('reaction_add', check=check)
            if user.id == trader.id:
                if reaction.emoji == '\u2611':
                    trader_confirms = True
                elif reaction.emoji == '\u23f9':
                    return await self.withdraw_offer(trader.id)
            elif user.id == lister.id:
                if reaction.emoji == '\u2611':
                    lister_confirms = True
                elif reaction.emoji == '\u23f9':
                    return await self.reject_offer(trader.id)
            if trader_confirms and lister_confirms:
                return await self.confirm_trade()
            else:
                continue
        # update the listing message if it still exists
        # dm others who offered saying the trade was completed
        # dm the member with the successful offer with details for trade
        # maybe ask the lister to provide a friend code optionally before dm

    async def withdraw_offer(self, offer_id):
        listingmsg = await self.get_listmsg()
        trader = self.guild.get_member(offer_id)
        await self.lister.send('Meowth... {} withdrew their trade offer of {}.'.format(
            trader.display_name, self.offers[offer_id]
        ))

        offer_str = "Meowth! {lister} offers a {pkmn} up for trade!".format(
            lister=self.lister.display_name,
            pkmn=self.offered_pokemon
        )

        instructions = "React to this message to make an offer!"
        cancel_inst = "{lister} may cancel the trade with :stop_button:".format(
            lister = self.lister.display_name
        )

        await listingmsg.edit(content=f"{offer_str}\n\n{instructions}\n\n{cancel_inst}", embed=self.embed)
        for i in range(len(self.wanted_pokemon)):
            await listingmsg.add_reaction(f'{i+1}\u20e3')
            await asyncio.sleep(0.25)
        await listingmsg.add_reaction('\u23f9')
        del self.offers[offer_id]


    async def reject_offer(self, offer_id):
        trader = self.guild.get_member(offer_id)
        await trader.send('Meowth... {} rejected your offer for their {}.'.format(
            self.lister.display_name, self.offered_pokemon))
        del self.offers[offer_id]

    async def cancel_trade(self):
        listingmsg = await self.get_listmsg()
        await listingmsg.delete()
        for offerid in self.offers:
            reject = self.guild.get_member(offerid)
            await reject.send('Meowth... {} canceled their trade offer of {}'.format(
                self.lister.display_name, self.offered_pokemon))
        self.close_trade()
        # update the listing message if it still exists
        # dm those who offered saying the trade was cancelled

    async def confirm_trade(self):
        listingmsg = await self.get_listmsg()
        await listingmsg.edit(content='Meowth! This trade has been completed!', embed=None)
        self.close_trade()

    def close_trade(self):
        self.bot.remove_listener(self.on_raw_reaction_add)
        try:
            guild_trades = self.bot.guild_dict[self.guild_id]
            del guild_trades[self.report_channel_id][self.listing_id]
        except KeyError:
            pass

class Trading:
    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self):
        for guild_id in self.bot.guild_dict:
            trade_dict = bot.guild_dict[guild_id].setdefault('trade_dict', {})
            for channel_id in trade_dict:
                trade_channel_data = trade_dict[channel_id]
                for message_id in trade_channel_data:
                    trade = Trade.from_data(self.bot,
                        message_id, trade_channel_data[message_id])


    @commands.command()
    async def trade(self, ctx, *, offer: pokemon.Pokemon):
        """Create a trade listing."""

        want_ask = await ctx.send(
            f"{ctx.author.mention}, what Pokemon are you willing to accept "
            f"in exchange for {str(offer)}?")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        want_reply = await ctx.bot.wait_for('message', check=check)

        wants = want_reply.content.lower().split(',')

        await want_ask.delete()
        await want_reply.delete()

        pkmn_convert = functools.partial(pokemon.Pokemon.convert, ctx)

        wants = map(str.strip, wants)
        wants = [await pkmn_convert(want) for want in wants]

        await Trade.create_trade(ctx, wants, offer)


def setup(bot):
    bot.add_cog(Trading(bot))
