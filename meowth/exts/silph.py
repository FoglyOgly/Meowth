import datetime
import dateparser
import aiohttp

import discord
from discord.ext import commands
from meowth import utils

class SilphBadge:

    __slots__ = ('count', '_awarded', 'slug', 'name', 'description', 'image_url')

    def __init__(self, data):
        self.count = data.get('count')
        badge_info = data.get('Badge', {})
        self.slug = badge_info.get('slug')
        self.name = badge_info.get('name')
        self.description = badge_info.get('description')
        self.image_url = badge_info.get('image_url')
        self._awarded = data.get('awarded')

    def __str__(self):
        return self.name

    def __repr__(self):
        type_name = type(self).__name__
        name = self.name
        created = self.awarded()
        return f"<{type_name} name='{name}' awarded='{created}'>"

    def awarded(self, utc_offset=None):
        if not self._awarded:
            return None
        date = dateparser.parse(self._awarded, settings={'TIMEZONE': 'UTC'})
        if utc_offset:
            date = date + datetime.timedelta(hours=utc_offset)
        return date.date().isoformat()

class SilphCheckin:

    __slots__ = ('name', 'description', 'image_url', '_is_global', '_start',
                 '_end', '_created')

    def __init__(self, data):
        self.name = data.get('name')
        self.description = data.get('description')
        self.image_url = data.get('image')
        self._is_global = data.get('is_global')
        event_checkin_data = data.get('EventCheckin', {})
        self._created = event_checkin_data.get('created')

    def __str__(self):
        return self.name

    def __repr__(self):
        type_name = type(self).__name__
        name = self.name
        created = self.created()
        return f"<{type_name} name='{name}' created='{created}'>"

    @property
    def is_global(self):
        if not self._is_global:
            return None
        return utils.convert_to_bool(self._is_global)

    def created(self, utc_offset=None):
        if not self._created:
            return None
        date = dateparser.parse(self._created, settings={'TIMEZONE': 'UTC'})
        if utc_offset:
            date = date + datetime.timedelta(hours=utc_offset)
        return date.date().isoformat()

class SilphCard:

    __slots__ = ('id', 'home_region', 'team', 'title', 'playstyle', 'level',
                 'avatar_url', 'silph_name', 'game_name', 'url',
                 'data_url', '_badges', '_top_6_pokemon', '_nest_migrations',
                 '_pokedex_count', '_xp', '_raid_average', '_goal', '_joined',
                 '_modified', '_connected_accounts', '_checkins', '_handshakes')

    def __init__(self, silph_username, data):
        data = data.get('data', data)
        self.silph_name = silph_username
        self.game_name = data.get('in_game_username')
        self.url = f'https://sil.ph/{silph_username}.json'
        self.data_url = f'https://sil.ph/{silph_username}'
        self.id = data.get('card_id')
        self.home_region = data.get('home_region')
        self.team = data.get('team')
        self.title = data.get('title')
        self.playstyle = data.get('playstyle')
        self.level = data.get('trainer_level')
        self.avatar_url = data.get('avatar')
        self._badges = data.get('badges')
        self._top_6_pokemon = data.get('top_6_pokemon')
        self._nest_migrations = data.get('nest_migrations')
        self._pokedex_count = data.get('pokedex_count')
        self._xp = data.get('xp')
        self._raid_average = data.get('raid_average')
        self._handshakes = data.get('handshakes')
        self._goal = data.get('goal')
        self._joined = data.get('joined')
        self._modified = data.get('modified')
        self._connected_accounts = data.get('socials')
        self._checkins = data.get('checkins')

    def __str__(self):
        return f"{self.id} - {self.silph_name}"

    def __repr__(self):
        type_name = type(self).__name__
        name = self.silph_name
        ign = self.game_name
        return f"<{type_name} id='{self.id}' silph_name='{name}' ign='{ign}'>"

    def get_connected_account(self, vendor):
        con_acc = self._connected_accounts
        search = (acc for acc in con_acc if acc.get('vendor') == vendor)
        return next(search, None)

    @property
    def badges(self):
        if not self._badges:
            return None
        return tuple(SilphBadge(b) for b in self._badges)

    @property
    def badge_count(self):
        if not self._badges:
            return 0
        return len(self._badges)

    @property
    def checkins(self):
        if not self._badges:
            return None
        return tuple(SilphCheckin(c) for c in self._checkins)

    @property
    def checkin_count(self):
        if not self._badges:
            return 0
        return len(self._checkins)

    @property
    def top_pkmn(self):
        if not self._top_6_pokemon:
            return None
        return tuple(self._top_6_pokemon)

    @property
    def migrations(self):
        return int(self._nest_migrations) if self._nest_migrations else 0

    @property
    def pd_count(self):
        return int(self._pokedex_count) if self._pokedex_count else 0

    @property
    def xp(self):
        return int(self._xp) if self._xp else 0

    @property
    def raid_avg(self):
        return int(self._raid_average) if self._raid_average else 0

    @property
    def handshakes(self):
        return int(self._handshakes) if self._handshakes else 0

    @property
    def goal(self):
        return self._goal.lower() if self._goal else None

    @property
    def discord_name(self):
        data = self.get_connected_account('Discord')
        return data.get('username') if data else None

    def joined(self, utc_offset=None):
        if not self._joined:
            return None
        date = dateparser.parse(self._joined, settings={'TIMEZONE': 'UTC'})
        if utc_offset:
            date = date + datetime.timedelta(hours=utc_offset)
        return date.date().isoformat()

    def modified(self, utc_offset=None):
        if not self._modified:
            return None
        date = dateparser.parse(self._modified, settings={'TIMEZONE': 'UTC'})
        if utc_offset:
            date = date + datetime.timedelta(hours=utc_offset)
        return date.date().isoformat()

    def embed(self, utc_offset=None):

        colour = discord.Colour(0xe8c13c)
        hyperlink_icon = "https://i.imgur.com/fn9E5nb.png"
        silph_icon = "https://assets.thesilphroad.com/img/snoo_sr_icon.png"

        if not self.discord_name:
            connected_str = "\u2754 **Discord Not Provided**"
        else:
            connected_str = (
                f"\u2611 **Connected to Discord:** {self.discord_name}")

        embed = discord.Embed(
            title='Playstyle', colour=colour, description=(
                f"{self.playstyle}, working on {self.goal}.\n"
                f"Active around {self.home_region}.\n\n"
                f"{connected_str}"))

        embed.set_thumbnail(url=self.avatar_url)

        embed.set_author(
            name=(
                f"{self.title} {self.game_name} - "
                f"Level {self.level} {self.team}"),
            url=self.url,
            icon_url=hyperlink_icon)

        embed.add_field(
            name="__Silph Stats__",
            value=(
                f"**Joined:** {self.joined(utc_offset)}\n"
                f"**Badges:** {self.badge_count}\n"
                f"**Check-ins:** {self.checkin_count}\n"
                f"**Handshakes:** {self.handshakes}\n"
                f"**Migrations:** {self.migrations}"),
            inline=True)

        embed.add_field(
            name="__Game Stats__",
            value=(
                f"**Name:** {self.game_name}\n"
                f"**Team:** {self.team}\n"
                f"**Level:** {self.level}\n"
                f"**Pokedex:** {self.pd_count}\n"
                f"**Raids:** {self.raid_avg}/week"),
            inline=True)

        embed.set_footer(
            text=(
                f"Silph Road Travelers Card - ID{self.id} - "
                f"Updated {self.modified(utc_offset)}"),
            icon_url=silph_icon)

        return embed

    @classmethod
    async def get_trainer_card(cls, silph_user):
        url = f'https://sil.ph/{silph_user}.json'
        async with aiohttp.ClientSession() as sess:
            async with sess.get(url) as resp:
                data = await resp.json()
        if data.get('error', None):
            return None
        return cls(silph_user, data)

class SilphTrainer:
    def __init__(self, silph_user):
        self.name = silph_user
        self.card = None

    async def load_card_data(self):
        self.card = await SilphCard.get_trainer_card(self.name)
        return self.card

    @classmethod
    async def load_trainer_data(cls, silph_user):
        instance = cls(silph_user)
        await instance.load_card_data()
        return instance

class Silph:
    """Silph intergrations."""
    def __init__(self, bot):
        self.bot = bot

    def get_silph_profile_lazy(self, silph_user):
        return SilphTrainer(silph_user)

    async def get_silph_profile(self, silph_user):
        return await SilphTrainer.load_trainer_data(silph_user)

    async def get_silph_card(self, silph_user):
        return await SilphCard.get_trainer_card(silph_user)

    @commands.command()
    async def silphcard(self, ctx, silph_user: str = None):
        """Displays a user's Silph Road Trainer Card."""
        guild_data = ctx.bot.guild_dict[ctx.guild.id]
        if not silph_user:
            silph_user = guild_data['trainers'].setdefault(ctx.author.id, {}).get('silphid', None)
            if not silph_user:
                return await ctx.error(f"You haven't setup a silphcard!")
        else:
            if ctx.message.mentions:
                mentioned = ctx.message.mentions[0]
                silph_user = guild_data['trainers'].setdefault(
                    mentioned.id, {}).get('silphid', None)
                if not silph_user:
                    return await ctx.error(
                        f"{mentioned.display_name} hasn't setup a silphcard!")
        async with ctx.typing():
            card = await SilphCard.get_trainer_card(silph_user)
        try:
            offset = guild_data['configure_dict']['settings']['offset']
        except KeyError:
            offset = None
        if card:
            await ctx.send(embed=card.embed(offset))
        else:
            await ctx.error(f'Silph Card for {silph_user} not found.')

def setup(bot):
    bot.add_cog(Silph(bot))
