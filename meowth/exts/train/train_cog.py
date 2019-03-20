from meowth import Cog, command, bot, checks
from meowth.exts.map import Gym, ReportChannel
from meowth.exts.raid import Raid
from meowth.utils import formatters

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
        idlist = await self.report_channel.get_all_raids()
        return [Raid.instances.get(x) for x in idlist]
    
    async def distance_matrix(self):
        if not isinstance(self.current_raid.gym, Gym):
            return None
        origin = await self.current_raid.gym._coords()
        raids = await self.possible_raids()
        dests = [await x.gym._coords() for x in raids if isinstance(x.gym, Gym)]
        matrix = self.bot.gmaps.distance_matrix(origin, dests)
        print(matrix)
        return matrix
    
    async def display_choices(self):
        raids = await self.possible_raids()
        dest_dict = {}
        eggs_list = []
        hatched_list = []
        active_list = []
        if self.current_raid:
            raids.remove(self.current_raid)
            if isinstance(self.current_raid.gym, Gym):
                origin = await self.current_raid.gym._coords()
                known_dest_ids = [x.id for x in raids if isinstance(x.gym, Gym)]
                dests = [await x.gym._coords() for x in known_dest_ids]
                matrix = self.bot.gmaps.distance_matrix(origin, dests)
                row = matrix['rows'][0]['elements']
                times = [row[i]['duration']['text'] for i in range(len(row))]
                dest_dict = dict(zip(known_dest_ids, times))
        urls = {x.id: await self.route_url(x) for x in raids}
        react_list = formatters.mc_emoji(len(raids))
        for i in range(len(raids)):
            x = raids[i]
            e = react_list[i]
            summary = f'{e} {await x.summary_str()}'
            if x.id in dest_dict:
                travel = f'Travel Time: {dest_dict[x.id]}'
            else:
                travel = "Travel Time: Unknown"
            directions = f'[{travel}]({urls[x.id]})'
            summary += f"\n{directions}"
            if x.status == 'egg':
                eggs_list.append(summary)
            elif x.status == 'hatched':
                hatched_list.append(summary)
            elif x.status == 'active':
                active_list.append(summary)
        fields = {}
        if active_list:
            fields['Active'] = "\n\n".join(active_list) + "\n\u200b"
        if hatched_list:
            fields['Hatched'] = "\n\n".join(hatched_list) + "\n\u200b"
        if eggs_list:
            fields['Eggs'] = "\n\n".join(eggs_list)
        embed = formatters.make_embed(title="Raid Choices", fields=fields)
        content = "Select a raid from the list below."
        multi = await self.channel.send(content, embed=embed)
        payload = await formatters.ask(self.bot, [multi],
            react_list=react_list)
        choice_dict = dict(zip(react_list, raids))
        next_raid = choice_dict[str(payload.emoji)]
        self.current_raid = next_raid
        

    
    async def route_url(self, next_raid):
        if isinstance(next_raid.gym, Gym):
            lat2, lon2 = await next_raid.gym._coords()
            dest_str = f"&destination={lat2},{lon2}"
        else:
            return next_raid.gym.url
        prefix = "https://www.google.com/maps/dir/?api=1"
        if self.current_raid:
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
        await new_train.display_choices()
        await new_train.display_choices()



