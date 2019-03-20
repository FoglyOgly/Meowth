from meowth import Cog, command, bot, checks
from meowth.exts.map import Gym, ReportChannel
from meowth.exts.raid import Raid

class Train:

    instances = dict()
    by_channel = dict()

    def __init__(self, bot, guild_id, channel_id, report_channel_id):
        self.bot = bot
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.report_channel_id = report_channel_id
        self.current_raid = None
    
    @property
    def guild(self):
        return self.bot.get_guild(self.guild_id)
    
    @property
    def channel(self):
        return self.bot.get_channel(self.channel_id)
    
    @property
    def report_channel(self):
        rchan = self.bot.get_channel(self.report_channel_id)
        return ReportChannel(self.bot, rchan)
    
    async def possible_raids(self):
        return await self.report_channel.get_all_raids()
    
    async def distance_matrix(self):
        if not isinstance(self.current_raid.gym, Gym):
            return None
        origin = await self.current_raid.gym._coords()
        raid_ids = await self.possible_raids()
        raids = [Raid.instances.get(x) for x in raid_ids]
        dests = [x.gym._coords() for x in raids if isinstance(x.gym, Gym)]
        matrix = self.bot.gmaps.distance_matrix(origin, dests)
        print(matrix)
        return matrix
    
    async def route_url(self, next_raid):
        if isinstance(next_raid.gym, Gym):
            lat2, lon2 = await next_raid.gym._coords()
            dest_str = f"&destination={lat2},{lon2}"
        else:
            return next_raid.gym.url
        prefix = "https://www.google.com/maps/dir/?api=1"
        if isinstance(self.current_raid.gym, Gym):
            lat1, lon1 = await self.current_raid.gym._coords()
            origin_str = f"&origin={lat1},{lon1}"
            prefix += origin_str
        prefix += dest_str
        prefix += "&dir_action=navigate"

class TrainCog(Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @command()
    async def train(self, ctx):
        name = f'raid-train-{ctx.channel.name}'
        cat = ctx.channel.category
        ow = dict(ctx.channel.overwrites)
        train_channel = await ctx.guild.create_text_channel(name, category=cat, overwrites=ow)
        new_train = Train(self.bot, ctx.guild.id, train_channel.id, ctx.channel.id)
        possible_raid_ids = await new_train.possible_raids()
        print(possible_raid_ids)
        possible_raids = [Raid.instances.get(x) for x in possible_raid_ids]
        print(possible_raids)
        raid_display = [await x.summary_str() for x in possible_raids]
        react_list = formatters.mc_emoji(len(possible_raids))
        choice_dict = dict(zip(react_list, possible_raids))
        display_dict = dict(zip(react_list, raid_display))
        embed = formatters.mc_embed(display_dict)
        multi = await train_channel.send('Which raid would you like to start with?',
            embed=embed)
        payload = await formatters.ask(ctx.bot, [multi], user_list=[ctx.author.id],
            react_list=react_list)
        first_raid = choice_dict[str(payload.emoji)]
        await multi.delete()
        new_train.current_raid = first_raid
        await train_channel.send(repr(await new_train.possible_raids()))
        await train_channel.send(repr(await new_train.distance_matrix()))



