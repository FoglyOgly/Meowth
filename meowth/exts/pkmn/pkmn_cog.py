from meowth import Cog, command, bot, checks
from meowth.utils import formatters, fuzzymatch
from meowth.exts.weather import Weather
from math import log, floor
import aiohttp

import discord
from discord.ext.commands import CommandError
from .errors import *


class Pokemon():

    def __init__(
        self, bot, pokemonId, form=None, gender=None, shiny=False,
        attiv=None, defiv=None, staiv=None, lvl=None,
        cp=None, quickMoveid=None, chargeMoveid=None, chargeMove2id=None
    ):
        self.bot = bot
        self.id = pokemonId
        if 'ALOLA' in pokemonId:
            form = 1
        elif 'RAINY' in pokemonId:
            form = 2
        elif 'SNOWY' in pokemonId:
            form = 3
        elif 'SUNNY' in pokemonId:
            form = 4
        elif 'ATTACK' in pokemonId:
            form = 5
        elif 'DEFENSE' in pokemonId:
            form = 6
        elif 'SPEED' in pokemonId:
            form = 7
        elif 'ORIGIN' in pokemonId:
            form = 53
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
        self.chargeMove2id = chargeMove2id

    @property
    def to_dict(self):
        d = {
            'id': self.id,
            'form': self.form,
            'gender': self.gender,
            'shiny': self.shiny,
            'attiv': self.attiv,
            'defiv': self.defiv,
            'staiv': self.staiv,
            'lvl': self.lvl,
            'cp': self.cp,
            'quickMoveid': self.quickMoveid,
            'chargeMoveid': self.chargeMoveid,
            'chargeMove2id': self.chargeMove2id
        }
        return d
    
    def __repr__(self):
        return repr(self.to_dict)
    
    @classmethod
    def from_dict(cls, bot, data):
        pkmn_id = data['id']
        form = data['form']
        gender = data['gender']
        shiny = data['shiny']
        attiv = data['attiv']
        defiv = data['defiv']
        staiv = data['staiv']
        lvl = data['lvl']
        cp = data['cp']
        quickMoveid = data['quickMoveid']
        chargeMoveid = data['chargeMoveid']
        chargeMove2id = data['chargeMove2id']
        return cls(bot, pkmn_id, form=form, gender=gender,
            shiny=shiny, attiv=attiv, defiv=defiv, staiv=staiv,
            lvl=lvl, cp=cp, quickMoveid=quickMoveid, 
            chargeMoveid=chargeMoveid, chargeMove2id=chargeMove2id)
    
    async def moveset_str(self):
        fast = self.quickMoveid or None
        charge = self.chargeMoveid or None
        charge2 = self.chargeMove2id or None
        quick_move = Move(self.bot, fast) if fast else None
        charge_move = Move(self.bot, charge) if charge else None
        charge2_move = Move(self.bot, charge2) if charge2 else None
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
        moveset_str = f"{quick_name} {quick_emoji}| {charge_name} {charge_emoji}"
        if charge2_move:
            charge2_name = await charge2_move.name()
            charge2_emoji = await charge2_move.emoji()
            moveset_str += f'| {charge2_name} {charge2_emoji}'
        return moveset_str
    
    async def trade_display_str(self):
        name = await self.name()
        if self.shiny:
            shiny_str = "Shiny "
        else:
            shiny_str = ""
        if not any((self.quickMoveid, self.chargeMoveid, self.chargeMove2id)):
            moveset_str = ""
        else:
            moveset_str = " " + await self.moveset_str()
        if self.gender:
            if (await self._gender_type()) in ('MALE', 'FEMALE', 'NONE'):
                gender_str = ""
            else:
                gender_str = self.gender.title() + " "
        else:
            gender_str = ""
        if self.lvl:
            level_str = f"Level {self.lvl}"
        else:
            level_str = ""
        display_str = f"{shiny_str}{gender_str}{level_str}{name}{moveset_str}"
        return display_str
    
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
    
    def _raid_available(self):
        raid_lists = self.bot.raid_info.raid_lists
        for level in raid_lists:
            if self.id in raid_lists[level]:
                return True
        return False

    async def _trade_available(self):
        data = self._data
        return await data.select('trade_available').get_value()
    
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
            "FoglyOgly/Meowth/new-core/meowth/images/pkmn/")
        url += self.id
        if self.form:
            url += '_'
            url += str(self.form)
        if self.shiny:
            url += '_'
            url += 'SHINY'
        if await self._gender_type() == 'DIMORPH' and self.gender:
            url += '_'
            url += self.gender.upper()
        url += '.png?cache=2'
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
            type_chart[type] = round(log(float(type_dict[type]), 1.6))
        return type_chart
    
    
    async def weaknesses_emoji(self):
        type_chart = await self.type_chart()
        types_sorted = sorted(type_chart.items(), key=(lambda x: x[1]), reverse=True)
        emoji_string = '\u200b'
        i = 0
        for type_tuple in types_sorted:
            if i == 4:
                emoji_string += '\n'
            type_ref = self.bot.dbi.table('types').query()
            emoji = await type_ref.select('emoji').where(typeid=type_tuple[0]).get_value()
            if type_tuple[1] == 4:
                emoji += 'x4'
                emoji_string += emoji
            elif type_tuple[1] == 3:
                emoji += 'x3'
                emoji_string += emoji
            elif type_tuple[1] == 2:
                emoji += 'x2'
                emoji_string += emoji
            elif type_tuple[1] == 1:
                emoji_string += emoji
            else:
                break
            i += 1
        return emoji_string

    
    async def resistances_emoji(self):
        type_chart = await self.type_chart()
        types_sorted = sorted(type_chart.items(), key=(lambda x: x[1]))
        emoji_string = '\u200b'
        i = 0
        for type_tuple in types_sorted:
            if i == 4:
                emoji_string += '\n'
            type_ref = self.bot.dbi.table('types').query()
            emoji = await type_ref.select('emoji').where(typeid=type_tuple[0]).get_value()
            if type_tuple[1] == -4:
                emoji += 'x4'
                emoji_string += emoji
            elif type_tuple[1] == -3:
                emoji += 'x3'
                emoji_string += emoji
            elif type_tuple[1] == -2:
                emoji += 'x2'
                emoji_string += emoji
            elif type_tuple[1] == -1:
                emoji_string += emoji
            else:
                break
            i += 1
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
        if await self._shiny_available():
            pkmn_name += " :sparkles:"
        type_emoji = await self.type_emoji()
        sprite_url = await self.sprite_url()
        # color = await self.color()
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
        embed_desc = f"#{num} {pkmn_name} - {category}\n```{description}```"
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
            title="Pokedex Entry",
            content=embed_desc,
            # msg_colour = color,
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
            if cp < 10:
                cp = 10
            return cp

    async def min_cp(self, level=1):
        cpm_ref = self.bot.dbi.table('cpm_table').query('cpm').where(
            level=level)
        cpm = await cpm_ref.get_value()
        att = (await self._baseAttack())*cpm
        defense = (await self._baseDefense())*cpm
        sta = (await self._baseStamina())*cpm
        cp = floor((att*defense**0.5*sta**0.5)/10)
        if cp < 10:
            cp = 10
        return cp
    
    async def max_cp(self, level=40):
        cpm_ref = self.bot.dbi.table('cpm_table').query('cpm').where(
            level=level)
        cpm = await cpm_ref.get_value()
        att = (await self._baseAttack() + 15)*cpm
        defense = (await self._baseDefense() + 15)*cpm
        sta = (await self._baseStamina() + 15)*cpm
        cp = floor((att*defense**0.5*sta**0.5)/10)
        if cp < 10:
            cp = 10
        return cp
    
    async def validate(self, context, weather=None):
        if self.quickMoveid:
            quick_moves = await self.fast_moves()
            if self.quickMoveid not in quick_moves:
                self.quickMoveid = None
        if self.chargeMoveid:
            charge_moves = await self.charge_moves()
            if self.chargeMoveid not in charge_moves:
                self.chargeMoveid = None
        if self.chargeMove2id:
            if self.chargeMove2id not in charge_moves:
                self.chargeMove2id = None
            elif not self.chargeMoveid:
                self.chargeMoveid = self.chargeMove2id
                self.chargeMove2id = None
        if self.shiny:
            if not await self._shiny_available():
                self.shiny = False
        gender_type = await self._gender_type()
        if gender_type in ('NONE', 'MALE', 'FEMALE'):
            self.gender = gender_type
        if context == 'wild':
            if self.shiny:
                self.shiny = False
            if weather:
                if await self.is_boosted(weather=weather):
                    max_level = 35
                    min_level = 6
                else:
                    max_level = 30
                    min_level = 1
            else:
                max_level = 35
                min_level = 1
            if self.lvl:
                if self.lvl > max_level:
                    self.lvl = max_level
                elif self.lvl < min_level:
                    self.lvl = min_level
                else:
                    max_level = self.lvl
                    min_level = self.lvl
            if self.cp:
                min_cp = await self.min_cp(level=min_level)
                max_cp = await self.max_cp(level=max_level)
                if self.cp and self.cp > max_cp:
                    self.cp = max_cp
                elif self.cp and self.cp < min_cp:
                    self.cp = min_cp
            else:
                calc_cp = await self.calculate_cp()
                if calc_cp:
                    self.cp = calc_cp
            if self.chargeMove2id:
                self.chargeMove2id = None
        return self
    
    async def get_info_from_arg(self, bot, arg):
        if arg.startswith('cp'):
            cp = int(arg[2:])
            self.cp = cp
        elif arg.startswith('@'):
            arg = arg[1:]
            move = await Move.from_arg(bot, arg)
            if move:
                if await move._fast():
                    self.quickMoveid = move.id
                else:
                    if not self.chargeMoveid:
                        self.chargeMoveid = move.id
                    else:
                        self.chargeMove2id = move.id
            else:
                pass
        elif arg == 'shiny':
            self.shiny = True
        elif arg == 'male':
            self.gender = 'MALE'
        elif arg == 'female':
            self.gender = 'FEMALE'
        elif arg.startswith('$iv'):
            iv_arg = arg[3:]
            attiv, defiv, staiv = iv_arg.split('/', maxsplit=2)
            attiv = int(attiv)
            defiv = int(defiv)
            staiv = int(staiv)
            if attiv > 15:
                attiv = 15
            elif attiv < 0:
                attiv = 0
            self.attiv = attiv
            if defiv > 15:
                defiv = 15
            elif defiv < 0:
                defiv = 0
            self.defiv = defiv
            if staiv > 15:
                staiv = 15
            elif staiv < 0:
                staiv = 0
            self.staiv = staiv
        elif arg.startswith('$lvl'):
            lvl = float(arg[4:])
            double = lvl*2
            rounded = round(double)
            if rounded < 2:
                rounded = 2
            elif rounded > 80:
                rounded = 80
            valid_level = rounded/2
            self.lvl = valid_level

    @classmethod
    async def from_arg(cls, bot, command_name, chn, user_id, arg):
        pokemon = bot.dbi.table('pokemon')
        pokedex = bot.dbi.table('pokedex')
        form_names = bot.dbi.table('form_names')
        forms_table = bot.dbi.table('forms')
        movesets = bot.dbi.table('movesets')
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
        chargeMove2id = None
        cp = None
        for arg in args:
            if arg.startswith('cp'):
                cp = int(arg[2:])
            elif arg.startswith('@'):
                arg = arg[1:]
                move = await Move.from_arg(bot, arg)
                if move:
                    if await move._fast():
                        quickMoveid = move.id
                    else:
                        if not chargeMoveid:
                            chargeMoveid = move.id
                        else:
                            chargeMove2id = move.id
                else:
                    pass
            elif arg == 'shiny':
                shiny = True
            elif arg == 'male':
                gender = 'male'
            elif arg == 'female':
                gender = 'female'
            elif arg.startswith('$iv'):
                iv_arg = arg[3:]
                attiv, defiv, staiv = iv_arg.split('/', maxsplit=2)
                attiv = int(attiv)
                defiv = int(defiv)
                staiv = int(staiv)
                if attiv > 15:
                    attiv = 15
                elif attiv < 0:
                    attiv = 0
                if defiv > 15:
                    defiv = 15
                elif defiv < 0:
                    defiv = 0
                if staiv > 15:
                    staiv = 15
                elif staiv < 0:
                    staiv = 0
            elif arg.startswith('$lvl'):
                lvl = float(arg[4:])
                double = lvl*2
                rounded = round(double)
                if rounded < 2:
                    rounded = 2
                elif rounded > 80:
                    rounded = 80
                valid_level = rounded/2
                lvl = valid_level
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
                    else:
                        raise PokemonNotFound
        possible_ids = set(ids) & set(id_list)
        length = len(possible_ids)
        if length == 0:
            raise PokemonNotFound
        else:
            possible_mons = [(cls(bot, x)) for x in possible_ids]
            if command_name == 'raid':
                possible_mons = [x for x in possible_mons if x._raid_available()]
            elif command_name == 'wild':
                possible_mons = [x for x in possible_mons if await x._wild_available()]
            elif command_name == 'trade':
                possible_mons = [x for x in possible_mons if await x._trade_available()]
            if len(possible_mons) == 0:
                raise PokemonInvalidContext
            elif len(possible_mons) == 1:
                pkmn = possible_mons[0]
            else:
                possible_names = [(await mon.name()) for mon in possible_mons]
                react_list = formatters.mc_emoji(length)
                choice_dict = dict(zip(react_list, possible_mons))
                display_dict = dict(zip(react_list, possible_names))
                embed = formatters.mc_embed(display_dict)
                multi = await chn.send('Multiple possible Pokemon found! Please select from the following list.',
                    embed=embed)
                payload = await formatters.ask(bot, [multi], user_list=[user_id],
                    react_list=react_list)
                pkmn = choice_dict[str(payload.emoji)]
                await multi.delete()
        pkmn.form = form
        pkmn.gender = gender
        pkmn.shiny = shiny
        pkmn.attiv = attiv
        pkmn.defiv = defiv
        pkmn.staiv = staiv
        pkmn.lvl = lvl
        pkmn.quickMoveid = quickMoveid
        pkmn.chargeMoveid = chargeMoveid
        pkmn.chargeMove2id = chargeMove2id
        pkmn.cp = cp
        return pkmn

    @classmethod    
    async def convert(cls, ctx, arg):
        return await cls.from_arg(ctx.bot, ctx.command.name, ctx.channel, ctx.author.id, arg)




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
    async def from_arg(cls, bot, arg):
        names = bot.dbi.table('move_names')
        name_list = await names.query('name').get_values()
        match = fuzzymatch.get_match(name_list, arg)
        if match[0]:
            match_id = await names.query('moveid').where(name=match[0]).get_value()
            return cls(bot, match_id)
        else:
            raise MoveNotFound
    
    @classmethod
    async def convert(cls, ctx, arg):
        return await cls.from_arg(ctx.bot, arg)
            
            

class Pokedex(Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, PokemonNotFound):
            await ctx.error('Pokemon not found!')
        elif isinstance(error, MoveNotFound):
            await ctx.error('Move not found!')
        elif isinstance(error, PokemonInvalidContext):
            await ctx.error('Pokemon invalid in current context.')
        elif isinstance(error, MoveInvalid):
            await ctx.error('Move not learned by Pokemon.')

    @command()
    async def pokedex(self, ctx, *, pokemon: Pokemon):
        return await ctx.send(embed=await pokemon.dex_embed())
    
    @command()
    @checks.is_co_owner()
    async def movesupdate(self, ctx):
        async with aiohttp.ClientSession() as sess:
            async with sess.get('https://fight.pokebattler.com/pokemon') as resp:
                data = await resp.json()

        pokemon_dicts = data['pokemon']
        move_list = []
        for pokemon in pokemon_dicts:
            pokemonId = pokemon['pokemonId']
            for moveset in pokemon['movesets']:
                quickmove = moveset['quickMove']
                chargemove = moveset['cinematicMove']
                if moveset.get('legacyDate'):
                    legacy = True
                else:
                    legacy = False
                for move in move_list:
                    if move['pokemonid'] == pokemonId and move['moveid'] == quickmove:
                        break
                else:
                    move_list.append({'pokemonid': pokemonId, 'moveid': quickmove, 'legacy': legacy})
                for move in move_list:
                    if move['pokemonid'] == pokemonId and move['moveid'] == chargemove:
                        break
                else:
                    move_list.append({'pokemonid': pokemonId, 'moveid': chargemove, 'legacy': legacy})
        movesets_table = ctx.bot.dbi.table('movesets')
        insert = movesets_table.insert()
        insert.rows(move_list)
        await movesets_table.query().delete()
        await insert.commit()
        return await ctx.send('Movesets table updated')
        
