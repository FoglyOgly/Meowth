import re
from meowth import Cog, command
from meowth.utils import get_match

import discord

class Pokemon:

    def __init__(
        self, bot, pokemonId, gender=None, shiny=False,
        atkiv=None, defiv=None, staiv=None, lvl=None,
        cp=None, quickMoveid=None, chargeMoveid=None
    ):
        self.bot = bot
        self.id = pokemonId
        self.gender = gender
        self.shiny = shiny
        self.atkiv = atkiv
        self.defiv = defiv
        self.staiv = staiv
        self.lvl = lvl
        self.cp = cp
        self.quickMoveid = quickMoveid
        self.chargeMoveid = chargeMoveid

        async def get_img_url(self):
            url = """https://github.com/FoglyOgly/Meowth
                /images/pkmn/"""
            url += str(self.id)
            pkmn_table = self.bot.dbi.table('pokemon')
            query = pkmn_table.query()
            query.where(pokemonId==self.id)
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
            form_list = ['sunny', 'rainy', 'snowy', 'attack',
                'defense', 'speed', 'alola'
            ]         
            pkmn_names_table = ctx.bot.dbi.table('pokemon_names')
            query = pkmn_names_table.query()
            query.where(language_id==ctx.pkmn_language)
            query.select('name')
            name_list = await query.get_values()
            arg_words = argument.lower().split()
            cpre = r'cp[1-9][0-9]{1,3}'
            lvlre = r'lvl[1-9]([0-9]?)(\.5)?'
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
            if form:
                pokemonID += f'_{form.capitalize()}_FORM'
            pkmn_table = ctx.bot.dbi.table('pokemon')
            query = pkmn_table.query()
            query.where(pokemonId=pokemonID)
            result = await query.get_value()
            if not result:
                # pokemon not found error
            return cls(ctx.bot, pokemonID, gender=gender,
                shiny=shiny, lvl=lvl, cp=cp)
            
