import re
from meowth import Cog, command
from meowth.utils import get_match

import discord

class Move:

    def __init__(
        self, bot, moveId: str, is_fast: bool
    ):
        self.bot = bot
        self.id = moveId
        self.is_fast = is_fast

    @classmethod
    async def convert(cls, ctx, argument):
        move_names_table = ctx.bot.dbi.table('move_names')
        query = move_names_table.query('name')
        query.where(language_id=ctx.language)
        move_name_list = await query.get_values()
        match = get_match(move_name_list, argument, score_cutoff=80)[0]
        if match:
            query.select('moveId')
            query.where(name=match)
            result = await query.get_value()
            query.select('fast')
            query.where(moveId=result)
            is_fast = await query.get_value()
            return cls(ctx.bot, result, is_fast)
        else:
            raise #move not found error


class Pokemon:

    def __init__(
        self, bot, pokemonId, gender=None, shiny=False,
        attiv=None, defiv=None, staiv=None, lvl=None,
        cp=None, quickMoveid=None, chargeMoveid=None
    ):
        self.bot = bot
        self.id = pokemonId
        self.gender = gender
        self.shiny = shiny
        self.attiv = attiv
        self.defiv = defiv
        self.staiv = staiv
        self.lvl = lvl
        self.cp = cp
        self.quickMoveid = quickMoveid
        self.chargeMoveid = chargeMoveid

    async def get_img_url(self):
        url = """https://github.com/FoglyOgly/Meowth
            /images/pkmn/""" #url different
        url += str(self.id)
        pkmn_table = self.bot.dbi.table('pokemon')
        query = pkmn_table.query()
        query.where(pokemonId=self.id)
        if self.gender == 'female':
            query.select('gender')
            result = await query.get_value()
            if result == 'DIMORPH':
                url += '_FEMALE'
        if self.shiny:
            query.select('shiny')
            result = await query.get_value()
            if result:
                url += '_SHINY'
        url += '.png'
        return url
    
    @classmethod
    async def convert(cls, ctx, argument):
        shiny = False
        cp = None
        lvl = None
        gender = None
        form = None
        attiv = None
        defiv = None
        staiv = None
        quickmoveid = None
        chargemoveid = None
        form_list = ['sunny', 'rainy', 'snowy', 'attack',
            'defense', 'speed', 'alola'
        ]         
        pkmn_names_table = ctx.bot.dbi.table('pokemon_names')
        query = pkmn_names_table.query()
        query.where(language_id=ctx.pkmn_language)
        query.select('name')
        name_list = await query.get_values()
        arg_words = argument.lower().split()
        move_names_table = ctx.bot.dbi.table('move_names')
        move_query = move_names_table.query('name')
        move_query.where(language_id=ctx.language)
        move_list = await move_query.get_values()
        cpre = r'cp[1-9][0-9]{1,3}'
        lvlre = r'lvl[1-9]([0-9]?)(\.5)?'
        attre = r'att((1[0-5])|([0-9]))'
        defre = r'def((1[0-5])|([0-9]))'
        stare = r'sta((1[0-5])|([0-9]))'
        movre = r'@\w+'
        for arg in arg_words:
            match = get_match(name_list, arg.title(), score_cutoff=80)[0]
            if match:
                query.select('pokemonID')
                query.where(name=match)
                matches = await query.get_values()
                pokemonID = matches[0]
                continue
            if arg == 'female': #check for other names?
                gender = 'female'
                continue
            if arg == 'shiny': #check for other names?
                shiny = True
                continue
            if any([form == arg for form in form_list]): 
                form = arg # probably not the best way to do this
                continue
            cp_match = re.fullmatch(cpre, arg)
            if cp_match:
                cparg = cp_match.group()
                cp = cparg[2:]
                continue
            lvl_match = re.fullmatch(lvlre, arg)
            if lvl_match:
                lvlarg = lvl_match.group()
                lvl = lvlarg[3:]
                continue
            att_match = re.fullmatch(attre, arg)
            if att_match:
                attarg = att_match.group()
                attiv = int(attarg[3:])
                continue
            def_match = re.fullmatch(defre, arg)
            if def_match:
                defarg = def_match.group()
                defiv = int(defarg[3:])
                continue
            sta_match = re.fullmatch(stare, arg)
            if sta_match:
                starg = sta_match.group()
                staiv = int(starg[3:])
                continue
            move_match = re.fullmatch(movre, arg)
            if move_match:
                movearg = move_match.group(0)
                match = get_match(move_list, movearg[1:], score_cutoff=80)[0]
                if match:
                    move_query.select('moveId')
                    move_query.where(name=match)
                    result = await move_query.get_value()
                    move = await Move.convert(ctx, result)
                    if move.is_fast:
                        quickmoveid = move.id
                    else:
                        chargemoveid = move.id
        if form:
            pokemonID += f'_{form.capitalize()}_FORM'
        pkmn_table = ctx.bot.dbi.table('pokemon')
        query = pkmn_table.query()
        query.where(pokemonId=pokemonID)
        if gender:
            query.select('gender')
            result = await query.get_value()
            if not result:
                gender = None
        if shiny:
            query.select('shiny')
            result = await query.get_value()
            if not result:
                shiny = False
        result = await query.get_value()
        if not result:
            raise
            # pokemon not found error
        return cls(ctx.bot, pokemonID, gender=gender,
            shiny=shiny, lvl=lvl, cp=cp, attiv=attiv,
            defiv=defiv, staiv=staiv, quickMoveid=quickmoveid,
            chargeMoveid=chargemoveid)
            
