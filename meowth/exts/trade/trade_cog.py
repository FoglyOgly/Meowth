from meowth import Cog, command, bot, checks
from meowth.utils.converters import ChannelMessage
from meowth.exts.pkmn import Pokemon, Move
from meowth.exts.pkmn.errors import PokemonInvalidContext, PokemonNotFound
from meowth.exts.want import Want
from meowth.exts.users import MeowthUser
from meowth.utils import formatters, snowflake

from discord.ext import commands

import asyncio
import shlex
from functools import partial

from . import trade_checks

class Trade():

    instances = dict()
    by_listing = dict()
    by_offer = dict()

    def __new__(cls, trade_id, *args, **kwargs):
        if trade_id in cls.instances:
            return cls.instances[trade_id]
        instance = super().__new__(cls)
        cls.instances[trade_id] = instance
        return instance

    def __init__(self, trade_id, bot, guild_id, lister_id, listing_id, offered_pkmn, wanted_pkmn):
        self.id = trade_id
        self.bot = bot
        self.guild_id = guild_id
        self.lister_id = lister_id
        self.listing_id = listing_id
        self.offered_pkmn = offered_pkmn
        self.wanted_pkmn = wanted_pkmn
        self.offer_list = []
    
    icon_url = 'https://github.com/FoglyOgly/Meowth/blob/new-core/meowth/images/misc/trade_icon_small.png?raw=true'

    @classmethod
    def from_data(cls, bot, data):
        guild_id = data['guild_id']
        lister_id = data['lister_id']
        listing_id = data['listing_id']
        offered_pokemon = [Pokemon.from_dict(bot, eval(x)) for x in data['offers']]
        wanted_pokemon = []
        for want in data['wants']:
            want = eval(want)
            if want in ['obo', 'any']:
                continue
            want = Pokemon.from_dict(bot, want)
            wanted_pokemon.append(want)
        if 'any' in data['wants']:
            wanted_pokemon.append('any')
        if 'obo' in data['wants']:
            wanted_pokemon.append('obo')
        offer_list = []
        if data['offer_list']:
            offer_list_data = [eval(x) for x in data['offer_list']]
            for x in offer_list_data:
                listed = Pokemon.from_dict(bot, x['listed'])
                if isinstance(x['offered'], dict):
                    offered = Pokemon.from_dict(bot, x['offered'])
                else:
                    offered = x['offered']
                trader_id = x['trader']
                msg = x['msg']
                d = {
                    'trader': trader_id,
                    'listed': listed,
                    'offered': offered,
                    'msg': msg
                }
                offer_list.append(d)
        trade_id = data['id']
        new_trade = cls(trade_id, bot, guild_id, lister_id, listing_id, offered_pokemon, wanted_pokemon)
        new_trade.offer_list = offer_list
        cls.by_listing[listing_id] = new_trade
        for offer in offer_list:
            cls.by_offer[offer['msg']] = new_trade
        return new_trade




    @property
    def lister_name(self):
        g = self.bot.get_guild(self.guild_id)
        m = g.get_member(self.lister_id)
        if not m:
            m = g.fetch_member(self.lister_id)
        return m.display_name
    
    @property
    def lister(self):
        g = self.bot.get_guild(self.guild_id)
        m = g.get_member(self.lister_id)
        if not m:
            m = g.fetch_member(self.lister_id)
        return m
    
    @property
    def lister_avy(self):
        u = self.bot.get_user(self.lister_id)
        return u.avatar_url
    
    @property
    def react_list(self):
        reacts = formatters.mc_emoji(len(self.wanted_pkmn))
        reacts.append('\u23f9')
        return reacts
    
    @property
    def offer_msgs(self):
        return [x['msg'] for x in self.offer_list]

    @property
    def guild(self):
        return self.bot.get_guild(self.guild_id)

    async def listing_chnmsg(self):
        chn, msg = await ChannelMessage.from_id_string(self.bot, self.listing_id)
        return chn, msg
    
    @staticmethod
    async def make_offer_embed(trader, listed_pokemon, offer):
        if isinstance(listed_pokemon, Pokemon):
            listed_str = await listed_pokemon.trade_display_str()
        elif listed_pokemon == 'any':
            listed_str = "Any Pokemon"
        if isinstance(offer, Pokemon):
            offer_str = await offer.trade_display_str()
            offer_url = await offer.sprite_url()
        elif offer == 'any':
            offer_str = "Any Pokemon"
            offer_url = None
        return formatters.make_embed(
            title="Pokemon Trade Offer",
            icon=Trade.icon_url,
            fields={
                "You Offered": listed_str,
                "They Offer": offer_str
                },
            inline=True,
            footer=trader.display_name,
            footer_icon=trader.avatar_url_as(format='png', size=256),
            thumbnail=offer_url
        )
    
    async def make_offer(self, trader, listed_pokemon, offered_pokemon):
        offer_dict = {
            'trader': trader.id,
            'listed': listed_pokemon,
            'offered': offered_pokemon,
        }
        embed = await self.make_offer_embed(trader, listed_pokemon, offered_pokemon)
        embed.color = self.guild.me.color
        offermsg = await self.lister.send(
            f"{trader.display_name} has made an offer on your trade! Use the reactions to accept or reject the offer.",
            embed=embed
        )
        react_list = ['✅', '❎']
        for react in react_list:
            await offermsg.add_reaction(react)
        offer_dict['msg'] = f'{offermsg.channel.id}/{offermsg.id}'
        Trade.by_offer[f'{offermsg.channel.id}/{offermsg.id}'] = self
        self.offer_list.append(offer_dict)
        offer_list_data = [repr(x) for x in self.offer_list]
        trade_table = self.bot.dbi.table('trades')
        update = trade_table.update.where(id=self.id)
        update.values(offer_list=offer_list_data)
        await update.commit()
    
    async def accept_offer(self, trader, listed, offer):
        content = f'{self.lister_name} has accepted your trade offer! Please DM them to coordinate the trade.'
        embed = await self.make_offer_embed(self.lister, offer, listed)
        embed.color = self.guild.me.color
        await trader.send(content, embed=embed)
        trade_table = self.bot.dbi.table('trades')
        query = trade_table.query.where(id=self.id)
        chn, msg = await self.listing_chnmsg()
        if msg:
            await msg.edit(content=f'{self.lister_name} has accepted an offer!')
            await msg.clear_reactions()
        await query.delete()
        score_table = self.bot.dbi.table('scoreboard')
        query = score_table.query
        query.where(guild_id=self.guild_id)
        query.where(user_id=self.lister_id)
        old_data = await query.get()
        if not old_data:
            d = {
                'guild_id': self.guild_id,
                'user_id': self.lister_id,
                'raid': 0,
                'wild': 0,
                'trade': 0,
                'research': 0,
                'service': 0
            }
        else:
            d = dict(old_data[0])
        d['trade'] += 1
        insert = score_table.insert
        insert.row(**d)
        query = score_table.query
        query.where(guild_id=self.guild_id)
        query.where(user_id=trader.id)
        old_data = await query.get()
        if not old_data:
            d = {
                'guild_id': self.guild_id,
                'user_id': trader.id,
                'raid': 0,
                'wild': 0,
                'trade': 0,
                'research': 0,
                'service': 0
            }
        else:
            d = dict(old_data[0])
        d['trade'] += 1
        insert.row(**d)
        await insert.commit(do_update=True)

    async def reject_offer(self, trader, listed, offer, msg):
        c, m = await ChannelMessage.from_id_string(self.bot, msg)
        try:
            await m.delete()
        except:
            pass
        content = f'{self.lister_name} has rejected your trade offer.'
        embed = await self.make_offer_embed(self.lister, offer, listed)
        embed.color = self.guild.me.color
        await trader.send(content, embed=embed)
        offer_dict = {
            'trader': trader.id,
            'listed': listed,
            'offered': offer,
            'msg': msg
        }
        for offer in self.offer_list:
            if offer_dict == offer:
                self.offer_list.remove(offer)
                offer_list_data = [repr(x) for x in self.offer_list]
                trade_table = self.bot.dbi.table('trades')
                update = trade_table.update.where(id=self.id)
                update.values(offer_list=offer_list_data)
                return await update.commit()         

    async def cancel_trade(self):
        trade_table = self.bot.dbi.table('trades')
        query = trade_table.query.where(id=self.id)
        chn, msg = await self.listing_chnmsg()
        try:
            await msg.delete()
        except:
            pass
        return await query.delete()

    async def process_reactions(self, payload):
        idstring = f'{payload.channel_id}/{payload.message_id}'
        chn, msg = await ChannelMessage.from_id_string(self.bot, idstring)
        user = self.bot.get_user(payload.user_id)
        if payload.emoji.is_custom_emoji():
            emoji = payload.emoji.id
        else:
            emoji = str(payload.emoji)
        try:
            await msg.remove_reaction(emoji, user)
        except:
            pass
        if idstring == self.listing_id:
            if emoji == '\u23f9' and payload.user_id == self.lister_id:
                return await self.cancel_trade()
            if emoji not in self.react_list or payload.user_id == self.lister_id:
                return
            i = self.react_list.index(emoji)
            offer = self.wanted_pkmn[i]
            trader = payload.member
            if len(self.offered_pkmn) > 1:
                content = f"{trader.display_name}, which of the following Pokemon do you want to trade for?"
                mc_emoji = formatters.mc_emoji(len(self.offered_pkmn))
                choice_dict = dict(zip(mc_emoji, self.offered_pkmn))
                display_list = [await x.trade_display_str() for x in self.offered_pkmn]
                display_dict = dict(zip(mc_emoji, display_list))
                embed = formatters.mc_embed(display_dict)
                channel = self.bot.get_channel(payload.channel_id)
                choicemsg = await channel.send(content, embed=embed)
                response = await formatters.ask(self.bot, [choicemsg], user_list=[trader.id],
                    react_list=mc_emoji)
                pkmn = choice_dict[str(response.emoji)]
                try:
                    await choicemsg.delete()
                except:
                    pass
            else:
                pkmn = self.offered_pkmn[0]
            if offer == 'obo':
                content = f'{trader.display_name} - what Pokemon would you like to offer?'
                askmsg = await chn.send(content)
                def check(m):
                    return m.channel == chn and m.author == trader
                offermsg = await self.bot.wait_for('message', check=check)
                offer = await Pokemon.from_arg(self.bot, 'trade', chn, trader.id, offermsg.content)
                if not await offer._trade_available():
                    return await chn.send(f'{await offer.name()} cannot be traded!')
                await askmsg.delete()
                try:
                    await offermsg.delete()
                except:
                    pass
            return await self.make_offer(trader, pkmn, offer)
        if idstring in self.offer_msgs:
            if emoji == '\u2705':
                for offer in self.offer_list:
                    if offer['msg'] == idstring:
                        g = self.bot.get_guild(self.guild_id)
                        trader = g.get_member(offer['trader'])
                        if not trader:
                            trader = g.fetch_member(offer['trader'])
                        listed = offer['listed']
                        offered = offer['offered']
                        return await self.accept_offer(trader, listed, offered)
            elif emoji == '❎':
                await msg.delete()
                for offer in self.offer_list:
                    if offer['msg'] == idstring:
                        g = self.bot.get_guild(self.guild_id)
                        trader = g.get_member(offer['trader'])
                        if not trader:
                            trader = g.fetch_member(offer['trader'])
                        listed = offer['listed']
                        offered = offer['offered']
                        msg = offer['msg']
                        return await self.reject_offer(trader, listed, offered, msg)
    
    async def get_wants(self):
        wants = []
        for pkmn in self.offered_pkmn:
            family = await pkmn._familyId()
            wants.append(family)
        wants = [Want(self.bot, x, self.guild_id) for x in wants]
        want_dict = {x: await x.mention() for x in wants}
        return want_dict
            
        


class TradeCog(Cog):

    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.pickup_tradedata())
    
    async def pickup_tradedata(self):
        table = self.bot.dbi.table('trades')
        query = table.query
        data = await query.get()
        for rcrd in data:
            Trade.from_data(self.bot, rcrd)

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return
        idstring = f'{payload.channel_id}/{payload.message_id}'
        trade = Trade.by_listing.get(idstring)
        if not trade:
            trade = Trade.by_offer.get(idstring)
        if trade:
            await trade.process_reactions(payload)
    
    @command(aliases=['t'])
    @trade_checks.trade_enabled()
    async def trade(self, ctx, offers: commands.Greedy[Pokemon]):
        """Offer one or more Pokemon for trade.

        **Arguments**
        *offers:* List of Pokemon you are offering. Wrap multi-word
        arguments in quotes.

        **Example:** `!trade "shiny magikarp" "female combee"`
        """
        if len(offers) == 0:
            return await ctx.send(f'Did not receive any valid offers! Remember to wrap multi-word Pokemon arguments in quotes.')
        valid_offers = [await offer.validate('trade') for offer in offers if await offer._trade_available()]
        invalid_offers = [x for x in offers if x not in valid_offers]
        if len(valid_offers) == 0:
            raise PokemonInvalidContext(invalid_offers)
        elif len(invalid_offers) > 0:
            invalid_names = [await x.name() for x in invalid_offers]
            fields={"Invalid Pokemon": "\n".join(invalid_names)}
            await ctx.warning('The following Pokemon cannot be traded!',
                fields=fields)
        listmsg = await ctx.send(f"{ctx.author.display_name} - what Pokemon are you willing to accept in exchange? Use 'any' if you will accept anything and 'OBO' if you want to allow other offers. \n**NOTE: Remember to wrap multi-word Pokemon arguments in quotes.**")
        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author
        wantmsg = await ctx.bot.wait_for('message', check=check)
        wantmsg = wantmsg.content.lower()
        wantargs = wantmsg.split(',')
        wantargs = list(map(str.strip, wantargs))
        pkmn_convert = partial(Pokemon.convert, ctx)
        if len(wantargs) == 1:
            # No commas have been used.
            try:
                # Check if a single pokemon was specified, e.g. shiny pidgey.
                [await pkmn_convert(arg) for arg in wantargs]
            except PokemonNotFound:
                # Use new syntax instead; account for smart quotes.
                wantmsg = wantmsg.replace('“', '"')
                wantmsg = wantmsg.replace('”', '"')
                wantargs = shlex.split(wantmsg)
        if 'any' in wantargs:
            wantargs.remove('any')
            accept_any = True
        else:
            accept_any = False
        if 'obo' in wantargs:
            wantargs.remove('obo')
            accept_other = True
        else:
            accept_other = False
        wants = [await pkmn_convert(arg) for arg in wantargs]
        wants = [await Pokemon.validate(want, 'trade') for want in wants]
        if len(wants) == 1:
            if not await wants[0]._trade_available():
                return await ctx.send(f'{await wants[0].name()} cannot be traded!')
        else:
            wants = [want for want in wants if await want._trade_available()]
        if accept_any:
            wants.append('any')
        if accept_other:
            wants.append('obo')
        try:
            await listmsg.delete()
            await wantmsg.delete()
        except:
            pass
        trade_id = next(snowflake.create())
        new_trade = Trade(trade_id, self.bot, ctx.guild.id, ctx.author.id, None, valid_offers, wants)
        embed = await TradeEmbed.from_trade(new_trade)
        wants = await new_trade.get_wants()
        mentions = [wants.get(x) for x in wants if wants.get(x)]
        mention_str = "\u200b".join(mentions)
        listmsg = await ctx.send(mention_str, embed=embed.embed)
        listing_id = f'{ctx.channel.id}/{listmsg.id}'
        new_trade.listing_id = listing_id
        Trade.by_listing[listing_id] = new_trade
        want_emoji = new_trade.react_list
        for emoji in want_emoji:
            await listmsg.add_reaction(emoji)
        offer_data = [repr(x) for x in valid_offers]
        want_data = [repr(x) for x in wants]
        data = {
            'id': trade_id,
            'guild_id': ctx.guild.id,
            'lister_id': ctx.author.id,
            'listing_id': listing_id,
            'offers': offer_data,
            'wants': want_data,
        }
        trade_table = ctx.bot.dbi.table('trades')
        insert = trade_table.insert.row(**data)
        rcrd = await insert.commit()



    
class TradeEmbed():
    
    def __init__(self, embed):
        self.embed = embed
    
    want_index = 0
    offer_index = 1

    @classmethod
    async def from_trade(cls, trade):
        want_list = []
        want_emoji = formatters.mc_emoji(len(trade.wanted_pkmn))
        for i in range(len(trade.wanted_pkmn)):
            if isinstance(trade.wanted_pkmn[i], Pokemon):
                want_str = f'{want_emoji[i]}: {await trade.wanted_pkmn[i].trade_display_str()}'
            elif trade.wanted_pkmn[i] == 'any':
                want_str = f'{want_emoji[i]}: Any Pokemon'
            elif trade.wanted_pkmn[i] == 'obo':
                want_str = f'{want_emoji[i]}: Other Pokemon'
            want_list.append(want_str)
        offer_list = []
        for i in range(len(trade.offered_pkmn)):
            offer_str = await trade.offered_pkmn[i].trade_display_str()
            offer_list.append(offer_str)
        title = "Pokemon Trade"
        footer = trade.lister_name
        footer_url = trade.lister_avy
        fields = {'Wants': "\n".join(want_list), 'Offers': "\n".join(offer_list)}
        if len(offer_list) == 1:
            thumbnail = await trade.offered_pkmn[0].sprite_url()
        else:
            thumbnail = None
        color = trade.guild.me.color
        embed = formatters.make_embed(title=title, footer=footer, footer_icon=footer_url,
            icon=Trade.icon_url, fields=fields, thumbnail=thumbnail, msg_colour=color)
        return cls(embed)

        

