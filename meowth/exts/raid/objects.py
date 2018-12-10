from discord import Embed
from .raid_cog import Raid
from meowth.exts.pkmn import Move
from meowth.exts.weather import Weather
from meowth.exts.map import Gym
from meowth.utils import formatters
from datetime import datetime

class RaidEmbed(Embed):

    raid_icon = 'https://media.discordapp.net/attachments/423492585542385664/512682888236367872/imageedit_1_9330029197.png' #TODO
    footer_icon = 'https://media.discordapp.net/attachments/346766728132427777/512699022822080512/imageedit_10_6071805149.png'

    boss_index = 0
    weather_index = 1
    weak_index = 2
    resist_index = 3
    cp_index = 4
    moveset_index = 5
    status_index = 6
    team_index = 7
    ctrs_index = 8

    def set_boss(self, boss_dict):
        name = boss_dict['name']
        shiny_available = boss_dict['shiny_available']
        cp_str = boss_dict['cp_str']
        resists = boss_dict['resists']
        weaks = boss_dict['weaks']
        ctrs_str = boss_dict['ctrs_str']
        moveset_str = "Unknown | Unknown"

        self.set_field_at(boss_index, name="Boss", value=name)
        self.set_field_at(weak_index, name="Weaknesses", value=weaks)
        self.set_field_at(resist_index, name="Resistances", value=resists)
        self.set_field_at(cp_index, name="CP Range", value=cp_str)
        self.set_field_at(ctrs_index, name="<:pkbtlr:512707623812857871> Counters", value=ctrs_str)
        self.set_field_at(moveset_index, name="Moveset", value=moveset_str)
        return self
    
    def set_weather(self, weather_str, cp_str, ctrs_str):
        self.set_field_at(weather_index, name="Weather", value=weather_str)
        self.set_field_at(cp_index, name="CP Range", value=cp_str)
        self.set_field_at(ctrs_index, name='<:pkbtlr:512707623812857871> Counters', value=ctrs_str)
        return self
    
    def set_moveset(self, moveset_str):
        self.set_field_at(moveset_index, name="Moveset", value=moveset_str)
        return self
    
    @property
    def status_str(self):
        return self.fields[status_index].value
    
    @status_str.setter
    def status_str(self, status_str):
        self.set_field_at(status_index, name="Status List", value=status_str)
    
    @property
    def team_str(self):
        return self.fields[team_index].value
    
    @team_str.setter
    def team_str(self, team_str):
        self.set_field_at(team_index, name="Team List", value=team_str)



    @classmethod
    async def from_raid(raid: Raid):
        boss = raid.pkmn
        bot = raid.bot
        name = await boss.name()
        type_emoji = await boss.type_emoji()
        shiny_available = await boss._shiny_available()
        if shiny_available:
            name += ':sparkles:'
        quick_move = Move(bot, boss.quickMoveid) if boss.quickMoveid else None
        charge_move = Move(bot, boss.chargeMoveid) if boss.chargeMoveid else None
        if quick_move:
            quick_name = await quick_move.name()
            quick_emoji = await quick_move.emoji()
        else:
            quick_name = "Unknown"
            quick_emoji = ""
        if charge_move:
            charge_name = await charge_move.name()
            charge_emoji = await charge_move.emoji()
        else:
            charge_name = "Unknown"
            charge_emoji = ""
        moveset = f"{quick_name} {quick_emoji}| {charge_name} {charge_emoji}"
        weather = await raid.weather()
        weather = Weather(bot, weather)
        weather_name = await weather.name()
        weather_emoji = await weather.boosted_emoji_str()
        is_boosted = await boss.is_boosted(weather.value)
        cp_range = await raid.cp_range()
        cp_str = f"{cp_range[0]}-{cp_range[1]}"
        end = raid.end
        enddt = datetime.fromtimestamp(end)
        if is_boosted:
            cp_str += " (Boosted)"
        img_url = await boss.sprite_url()
        # color = await boss.color()
        gym = raid.gym
        if isinstance(gym, Gym):
            directions_url = await gym.url()
            directions_text = await gym._name()
            exraid = await gym._exraid()
        else:
            directions_url = gym.url
            directions_text = gym.name + "(Unknown Gym)"
            exraid = False
        if exraid:
            directions_text += " (EX Raid Gym)"
        resists = await boss.resistances_emoji()
        weaks = await boss.weaknesses_emoji()
        ctrs_list = await raid.generic_counters_data()
        status_dict = await raid.status_dict()
        status_str = f"{bot.config.emoji['maybe']}: {status_dict['maybe']} | "
        status_str += f"{bot.config.emoji['coming']}: {status_dict['coming']} | "
        status_str += f"{bot.config.emoji['here']}: {status_dict['here']}"
        team_dict = await raid.team_dict()
        team_str = f"{bot.config.team_emoji['mystic']}: {team_dict['mystic']} | "
        team_str += f"{bot.config.team_emoji['instinct']}: {team_dict['instinct']} | "
        team_str += f"{bot.config.team_emoji['valor']}: {team_dict['valor']} | "
        team_str += f"{bot.config.team_emoji['unknown']}: {team_dict['unknown']}"
        fields = {
            "Boss": f"{boss_name} {type_emoji}",
            "Weather": f"{weather_name} {weather_emoji}",
            "Weaknesses": weaks,
            "Resistances": resists,
            "CP Range": f"{cp_range[0]}-{cp_range[1]}",
            "Moveset": moveset,
            "Status List": status_str,
            "Team List": team_str
        }
        i = 1
        ctrs_str = []
        for ctr in ctrs_list:
            name = await ctr.name()
            fast = Move(bot, ctr.quickMoveid)
            fast_name = await fast.name()
            fast_emoji = await fast.emoji()
            charge = Move(bot, ctr.chargeMoveid)
            charge_name = await charge.name()
            charge_emoji = await charge.emoji()
            ctr_str = f"**{name}**: {fast_name} {fast_emoji} | {charge_name} {charge_emoji}"
            ctrs_str.append(ctr_str)
            i += 1
        ctrs_str.append(f'[Results courtesy of Pokebattler](https://www.pokebattler.com/raids/{boss.id})')
        fields['<:pkbtlr:512707623812857871> Counters'] = "\n".join(ctrs_str)
        embed = formatters.make_embed(icon=raid_icon, title=directions_text, # msg_colour=color,
            title_url=directions_url, thumbnail=img_url, fields=fields, footer="Ending",
            footer_icon=footer_icon)
        embed.timestamp = enddt
        return embed