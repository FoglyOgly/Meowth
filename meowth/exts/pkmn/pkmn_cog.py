from meowth import Cog, command, bot
from meowth.utils import formatters, fuzzymatch
from meowth.exts.weather import Weather
from math import log, floor

import discord
from discord.ext.commands import CommandError

class PokemonNotFound(CommandError):
    'Exception raised, Pokemon not found'
    pass

class Pokemon():

    def __init__(
        self, bot, pokemonId, form=None, gender=None, shiny=False,
        attiv=None, defiv=None, staiv=None, lvl=None,
        cp=None, quickMoveid=None, chargeMoveid=None
    ):
        self.bot = bot
        self.id = pokemonId
        self.form = form
        self.gender = gender
        self.shiny = shiny
        self.attiv = attiv
        self.defiv = defiv
        self.staiv = staiv
        self.lvl = lvl
        self.cp = cp
        self.quickMoveid = quickMoveid
        self.chargeMoveid = chargeMoveid

    
    @property
    def _data(self):
        pokemon_ref = self.bot.dbi.table('pokemon').query()
        data = pokemon_ref.where(pokemonid=self.id)
        return data
    
    
    async def _num(self):
        data = self._data
        return await data.select('num').get_value()

    
    async def _gen(self):
        data = self._data
        return await data.select('gen').get_value()
    
    
    async def _type(self):
        data = self._data
        return await data.select('type').get_value()
    
    
    async def _type2(self):
        data = self._data
        return await data.select('type2').get_value()

    async def boost_weather(self):
        type1 = await self._type()
        type2 = await self._type2()
        types_table = self.bot.dbi.table('types')
        weather_query = types_table.query('weather')
        if not type2:
            weather_query.where(typeid=type1)
        else:
            weather_query.where((types_table['typeid']==type1, types_table['typeid']==type2))
        weather = await weather_query.get_values()
        return weather
    
    async def weather_str(self):
        weather = await self.boost_weather()
        weather_names = []
        for item in weather:
            name = await Weather(self.bot, item).name()
            weather_names.append(name)
        weather_str = ", ".join(weather_names)
        return weather_str

    async def is_boosted(self, weather):
        boost_weather = await self.boost_weather()
        return weather in boost_weather
    
    
    async def type_emoji(self):
        emoji_string = ''
        type1 = await self._type()
        type1_ref = self.bot.dbi.table('types').query().select('emoji').where(typeid=type1)
        type1_emoji = await type1_ref.get_value()
        type2 = await self._type2()
        type2_emoji = ''
        if type2:
            type2_ref = self.bot.dbi.table('types').query().select('emoji').where(typeid=type2)
            type2_emoji = await type2_ref.get_value()
        emoji_string += type1_emoji
        emoji_string += type2_emoji
        return emoji_string
    
    
    async def _form_type_id(self):
        data = self._data
        return await data.select('form_type_id').get_value()
    
    
    async def _gender_type(self):
        data = self._data
        return await data.select('gender_type').get_value()
    
    
    async def _mythical(self):
        data = self._data
        return await data.select('mythical').get_value()
    
    
    async def _legendary(self):
        data = self._data
        return await data.select('legendary').get_value()
    
    
    async def _wild_available(self):
        data = self._data
        return await data.select('wild_available').get_value()
    
    
    async def _shiny_available(self):
        data = self._data
        return await data.select('shiny_available').get_value()
    
    
    async def _baseStamina(self):
        data = self._data
        return await data.select('baseStamina').get_value()
    
    
    async def _baseAttack(self):
        data = self._data
        return await data.select('baseAttack').get_value()
    
    
    async def _baseDefense(self):
        data = self._data
        return await data.select('baseDefense').get_value()
    
    
    async def _HeightM(self):
        data = self._data
        return await data.select('HeightM').get_value()
    
    
    async def _WeightKg(self):
        data = self._data
        return await data.select('WeightKg').get_value()
    
    
    async def _HeightStdDev(self):
        data = self._data
        return await data.select('HeightStdDev').get_value()
    
    
    async def _WeightStdDev(self):
        data = self._data
        return await data.select('WeightStdDev').get_value()
    
    
    async def _familyId(self):
        data = self._data
        return await data.select('familyId').get_value()
    
    
    async def _stageID(self):
        data = self._data
        return await data.select('stageID').get_value()
    
    
    async def _evolves_from(self):
        data = self._data
        return await data.select('evolves_from').get_value()
    
    
    async def _evo_cost_candy(self):
        data = self._data
        return await data.select('evo_cost_candy').get_value()
    
    
    async def _evo_cost_item(self):
        data = self._data
        return await data.select('evo_cost_item').get_value()
    
    
    async def _evo_condition(self):
        data = self._data
        return await data.select('evo_condition').get_value()
    
    
    async def sprite_url(self):
        url = ("https://raw.githubusercontent.com/"
            "FoglyOgly/Meowth/discordpy-v1/images/pkmn/")
        url += self.id
        if self.form:
            url += str(self.form)
        if self.shiny:
            url += 'SHINY'
        if await self._gender_type() == 'DIMORPH' and self.gender:
            url += self.gender
        url += '.png?cache=1'
        return url
    
    async def color(self):
        url = await self.sprite_url()
        color = await formatters.url_color(url)
        return color

    @property
    def _dex_data(self):
        dex_ref = self.bot.dbi.table('pokedex').query().where(pokemonid=self.id)
        data = dex_ref.where(language_id=9)
        return data

    
    async def name(self):
        dex_data = self._dex_data
        name = await dex_data.select('name').get_value()
        name = name.strip()
        if self.form:
            name += " "
            form_names_table = self.bot.dbi.table('form_names')
            form_name_query = form_names_table.query('name')
            form_name_query.where(formid=self.form, language_id=9)
            form_name = await form_name_query.get_value()
            name += form_name
        return name
    
    
    async def description(self):
        dex_data = self._dex_data
        return await dex_data.select('description').get_value()
    
    
    async def category(self):
        dex_data = self._dex_data
        return await dex_data.select('category').get_value()
    
    
    async def type_dict(self):
        type_chart_ref = self.bot.dbi.table('type_chart').query()
        type1_ref = await type_chart_ref.where(defender_type_id=await self._type()).get()
        type1_dict = {}
        for typedoc in type1_ref:
            attacker_type = typedoc['attack_type_id']
            dmg = typedoc['dmg_multiplier']
            type1_dict[attacker_type] = dmg
        type2 = await self._type2()
        type2_dict = {}
        if type2:
            type_chart_ref = self.bot.dbi.table('type_chart').query()
            type2_ref = await type_chart_ref.where(defender_type_id=type2).get()
            for typedoc in type2_ref:
                attacker_type = typedoc['attack_type_id']
                dmg = typedoc['dmg_multiplier']
                type2_dict[attacker_type] = dmg
        type_dict = {}
        for type in type1_dict:
            type_dict[type] = type1_dict[type] * type2_dict.get(type, 1)
        return type_dict
    
    
    async def type_chart(self):
        type_dict = await self.type_dict()
        type_chart = {}
        for type in type_dict:
            type_chart[type] = round(log(float(type_dict[type]), 1.4))
        return type_chart
    
    
    async def weaknesses_emoji(self):
        type_chart = await self.type_chart()
        types_sorted = sorted(type_chart.items(), key=(lambda x: x[1]), reverse=True)
        emoji_string = ''
        for type_tuple in types_sorted:
            type_ref = self.bot.dbi.table('types').query()
            emoji = await type_ref.select('emoji').where(typeid=type_tuple[0]).get_value()
            if type_tuple[1] == 2:
                emoji += 'x2'
                emoji_string += emoji
            elif type_tuple[1] == 1:
                emoji_string += emoji
            else:
                break
        return emoji_string

    
    async def resistances_emoji(self):
        type_chart = await self.type_chart()
        types_sorted = sorted(type_chart.items(), key=(lambda x: x[1]))
        emoji_string = ''
        for type_tuple in types_sorted:
            type_ref = self.bot.dbi.table('types').query()
            emoji = await type_ref.select('emoji').where(typeid=type_tuple[0]).get_value()
            if type_tuple[1] == -2:
                emoji += 'x2'
                emoji_string += emoji
            elif type_tuple[1] == -1:
                emoji_string += emoji
            else:
                break
        return emoji_string
    
    
    async def moves(self):
        movesets_query = await self.bot.dbi.table('movesets').query().where(
            pokemonid=self.id).get()
        moves = []
        for movedoc in movesets_query:
            moves.append(movedoc['moveid'])
        return moves
    
    
    async def fast_moves(self):
        moves = await self.moves()
        fast_moves = []
        for x in moves:
            move = Move(self.bot, x)
            if await move._fast():
                fast_moves.append(move.id)
        return fast_moves

    
    async def charge_moves(self):
        moves = await self.moves()
        charge_moves = []
        for x in moves:
            move = Move(self.bot, x)
            if not await move._fast():
                charge_moves.append(move.id)
        return charge_moves
    
    
    async def dex_embed(self):
        num = await self._num()
        description = await self.description()
        category = await self.category()
        height = await self._HeightM()
        weight = await self._WeightKg()
        weaks = await self.weaknesses_emoji()
        resists = await self.resistances_emoji()
        pkmn_name = await self.name()
        type_emoji = await self.type_emoji()
        sprite_url = await self.sprite_url()
        color = await self.color()
        fast_moves = await self.fast_moves()
        fast_move_names = []
        for x in fast_moves:
            move = Move(self.bot, x)
            name = await move.name()
            emoji = await move.emoji()
            fast_move_names.append(name+' '+emoji)
        fast_moves_str = "\n".join(fast_move_names)
        charge_moves = await self.charge_moves()
        charge_move_names = []
        for x in charge_moves:
            move = Move(self.bot, x)
            name = await move.name()
            emoji = await move.emoji()
            charge_move_names.append(name+' '+emoji)
        charge_moves_str = "\n".join(charge_move_names)
        embed_desc = f"```{description}```"
        weather_str = await self.weather_str()
        # author_icon = type icon TODO
        fields = {
            "Height/Weight": f"{height} m/{weight} kg",
            "Boosted in:": weather_str,
            "Weaknesses": weaks,
            "Resistances": resists,
            "Fast Moves": fast_moves_str,
            "Charge Moves": charge_moves_str
        }
        embed = formatters.make_embed(
            # icon = author_icon,
            title=f"#{num} {pkmn_name} - {category}",
            content=embed_desc,
            msg_colour = color,
            thumbnail = sprite_url,
            fields = fields
        )
        return embed
    
    
    async def cpm(self):
        if not self.lvl:
            return None
        else:
            cpm_ref = self.bot.dbi.table('cpm_table').query().where(
                level=self.lvl)
            cpm = await cpm_ref.select('cpm').get_value()
            return cpm
    
    
    async def calculate_cp(self):
        if not all([self.lvl, self.attiv, self.defiv, self.staiv]):
            return None
        else:
            cpm = await self.cpm()
            att = (await self._baseAttack() + self.attiv)*cpm
            defense = (await self._baseDefense() + self.defiv)*cpm
            sta = (await self._baseStamina() + self.staiv)*cpm
            cp = floor((att*defense**0.5*sta**0.5)/10)
            return cp

    @classmethod    
    async def convert(cls, ctx, arg):
        pokemon = ctx.bot.dbi.table('pokemon')
        pokedex = ctx.bot.dbi.table('pokedex')
        form_names = ctx.bot.dbi.table('form_names')
        forms_table = ctx.bot.dbi.table('forms')
        movesets = ctx.bot.dbi.table('movesets')
        id_list = await pokemon.query('pokemonid').where(formid=0).get_values()
        name_list = await pokedex.query('name').get_values()
        form_list = await form_names.query('name').get_values()
        args = arg.lower().split()
        shiny = False
        form = None
        gender = None
        attiv = None
        defiv = None
        staiv = None
        lvl = None
        quickMoveid = None
        chargeMoveid = None
        cp = None
        alolan = False
        for arg in args:
            if arg.startswith('cp'):
                cp = int(arg[2:])
            elif arg.startswith('@'):
                arg = arg[1:]
                move = await Move.convert(ctx, arg)
                if move:
                    if await move._fast():
                        quickMoveid = move.id
                    else:
                        chargeMoveid = move.id
                else:
                    pass
            elif arg == 'shiny':
                shiny = True
            elif arg == 'male':
                gender = 'male'
            elif arg == 'female':
                gender = 'female'
            elif arg.startswith('$att'):
                attiv = int(arg[4:])
            elif arg.startswith('$def'):
                defiv = int(arg[4:])
            elif arg.startswith('$sta'):
                staiv = int(arg[4:])
            elif arg.startswith('$lvl'):
                lvl = int(arg[4:])
            else:
                form_name = fuzzymatch.get_match(form_list, arg)
                if form_name[0]:
                    forms = form_names.query('formid').where(name=form_name[0])
                    form = await forms.get_value()
                    id_list = await forms_table.query('pokemonid').where(formid=form).get_values()
                else:
                    names = fuzzymatch.get_matches(name_list, arg)
                    if names:
                        names = [x[0] for x in names]
                        ref = pokedex.query('pokemonid').where(
                            pokedex['name'].in_(names))
                        ids = await ref.get_values()
        possible_ids = set(ids) & set(id_list)
        if len(possible_ids) == 1:
            pokemonid = possible_ids.pop()
        elif len(possible_ids) == 0:
            raise PokemonNotFound
        else:
            multi = await ctx.send('Multiple possible Pokemon found! Please select from the following list.')
            # port utils.ask from v2
        return cls(ctx.bot, pokemonid, form=form, gender=gender, shiny=shiny,
            attiv=attiv, defiv=defiv, staiv=staiv, lvl=lvl, quickMoveid=quickMoveid,
            chargeMoveid=chargeMoveid, cp=cp)




class Move:

    def __init__(
        self, bot, moveId: str
    ):
        self.bot = bot
        self.id = moveId


    @property
    def _data(self):
        data = self.bot.dbi.table('moves').query().where(moveid=self.id)
        return data
    
    
    async def _fast(self):
        data = self._data
        is_fast = await data.select('fast').get_value()
        return is_fast
    
    
    async def _type(self):
        data = self._data
        move_type = await data.select('type').get_value()
        return move_type
    
    
    async def _power(self):
        data = self._data
        power = await data.select('power').get_value()
        return power
    
    
    async def _criticalChance(self):
        data = self._data
        critChance = await data.select('criticalChance').get_value()
        return critChance
    
    
    async def _staminaLossScalar(self):
        data = self._data
        stamloss = await data.select('staminaLossScalar').get_value()
        return stamloss
    
    
    async def _durationMs(self):
        data = self._data
        duration = await data.select('durationMs').get_value()
        return duration
    
    
    async def _damageWindowStartMs(self):
        data = self._data
        start = await data.select('damageWindowStartMs').get_value()
        return start
    
    
    async def _damageWindowEndMs(self):
        data = self._data
        end = await data.select('damageWindowEndMs').get_value()
        return end
    
    
    async def _energyDelta(self):
        data = self._data
        energy = await data.select('energyDelta').get_value()
        return energy
    
    
    async def dps(self):
        power = await self._power()
        duration = await self._durationMs()
        return (power*1000/duration)
    
    
    async def eps(self):
        if not await self._fast():
            return None
        else:
            energy = await self._energyDelta()
            duration = await self._durationMs()
            return (energy*1000/duration)
        
    
    async def dpe(self):
        if await self._fast():
            return None
        else:
            energy = await self._energyDelta()
            power = await self._power()
            return (power/energy)
    
    
    async def emoji(self):
        _type = await self._type()
        type_ref = self.bot.dbi.table('types').query().where(typeid=_type)
        emoji = await type_ref.select('emoji').get_value()
        return emoji
    
    
    async def name(self):
        names_ref = self.bot.dbi.table('move_names').query().where(moveid=self.id).where(
            language_id=9)
        name = await names_ref.select('name').get_value()
        return name
    
    @classmethod
    async def convert(cls, ctx, arg):
        names = ctx.bot.dbi.table('move_names')
        name_list = await names.query('name').get_values()
        match = fuzzymatch.get_match(name_list, arg)
        if match[0]:
            match_id = await moves.query('moveid').where(name=match[0]).get_first()
            return cls(bot, match_id)
            
            

class Pokedex(Cog):

    def __init__(self, bot):
        self.bot = bot
    
    async def on_command_error(self, ctx, error):
        if isinstance(error, PokemonNotFound):
            await ctx.send('Pokemon not ')

    @command()
    async def pokedex(self, ctx, *, pokemon: Pokemon):
        return await ctx.send(embed=await pokemon.dex_embed())
