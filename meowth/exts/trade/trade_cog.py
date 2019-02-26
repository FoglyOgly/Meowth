from meowth import Cog, command, bot, checks
from meowth.utils.converters import ChannelMessage
from meowth.exts.pkmn import Pokemon, Move
from meowth.exts.want import Want
from meowth.exts.users import MeowthUser
from meowth.utils import formatters

from discord.ext import commands

from functools import partial

class Trade():

    def __init__(self, bot, guild_id, lister_id, listing_id, offered_pkmn, wanted_pkmn, offer_list = []):
        self.bot = bot
        self.guild_id = guild_id
        self.lister_id = lister_id
        self.listing_id = listing_id
        self.offered_pkmn = offered_pkmn
        self.wanted_pkmn = wanted_pkmn
        self.offer_list = offer_list
    
    @property
    def lister_name(self):
        g = self.bot.get_guild(self.guild_id)
        m = g.get_member(self.lister_id)
        return m.display_name
    
    @property
    def lister_avy(self):
        u = self.bot.get_user(self.lister_id)
        return u.avatar_url

    async def listing_chnmsg(self):
        chn, msg = await ChannelMessage.from_id_string(self.bot, self.listing_id)
        return chn, msg

    async def on_raw_reaction_add(self, payload):
        idstring = f'{payload.channel_id}/{payload.message_id}'
        if idstring != self.listing_id:
            return
        


class TradeCog(Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @command(aliases=['t'])
    async def trade(self, ctx, offers: commands.Greedy[Pokemon]):
        listmsg = await ctx.send(f"{ctx.author.display_name} - what Pokemon are you willing to accept in exchange? Use 'any' if you will accept anything and 'OBO' if you want to allow other offers. Use commas to separate Pokemon.")
        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author
        wantmsg = await ctx.bot.wait_for('message', check=check)
        wantargs = wantmsg.content.lower().split(',')
        wantargs = map(str.split, wantargs)
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
        pkmn_convert = partial(Pokemon.convert, ctx)
        wantpkmns = map(pkmn_convert, wantargs)
        wants = [await mon for mon in wantpkmns]
        if accept_any:
            wants.append('any')
        if accept_other:
            wants.append('obo')
        new_trade = Trade(self.bot, ctx.guild.id, ctx.author.id, listmsg.id, offers, wants)
        embed = await TradeEmbed.from_trade(new_trade)
        await listmsg.edit(content="", embed=embed)



    
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
                want_str = f'{want_emoji[i]}: Offer Another Pokemon'
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
            thumbnail = await offer_list[0].sprite_url()
        else:
            thumbnail = None
        embed = formatters.make_embed(title=title, footer=footer, footer_icon=footer_url,
            fields=fields, thumbnail=thumbnail)
        return cls(embed)

        

