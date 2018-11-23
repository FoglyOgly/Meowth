from meowth import Cog, command, bot, checks
from meowth.exts.pkmn import Pokemon
from meowth.utils import fuzzymatch

import discord

class Want():

    def __init__(self, bot, want, guild):
        self.bot = bot
        self.want = want
        self.guildid = guild
    
    @property
    def guild(self):
        return self.bot.get_guild(self.guildid)
    
    @property
    def _data(self):
        want_table = self.bot.dbi.table('wants')
        query = want_table.query()
        query.where(guild=self.guildid, want=self.want)
        return query
    
    @property
    def _insert(self):
        want_table = self.bot.dbi.table('wants')
        insert = want_table.insert()
        insert.row(guild=self.guildid, want=self.want)
    
    async def _users(self):
        _data = self._data
        _data.select('users')
        users = await _data.get_value()
        return users
    
    async def notify_users(self, content, embed):
        msgs = []
        users = await self._users()
        guild = self.guild
        members = [guild.get_member(x) for x in users]
        for member in members:
            msg = await member.send(content, embed=embed)
            msgs.append(msg.id)
        return msgs

    async def is_role(self):
        users = await self._users()
        if len(users) > 10:
            return True
        else:
            return False
        
    async def role(self):
        is_role = await self.is_role()
        if not is_role:
            return None
        else:
            _data = self._data
            _data.select('role')
            roleid = await _data.get_value()
            if roleid:
                role = self.guild.get_role(roleid)
            else:
                guild = self.guild
                users = await self._users()
                members = [guild.get_member(x) for x in users]
                raid_tiers = ['1', '2', '3', '4', '5', 'EX']
                if self.want.startswith('FAMILY'):
                    pokemon_table = self.bot.dbi.table('pokemon')
                    pokemon_query = pokemon_table.query('pokemonid')
                    pokemon_query.where(familyid=self.want, stageid=1)
                    pokemonid = await pokemon_query.get_value()
                    pokedex = self.bot.dbi.table('pokedex')
                    name_query = pokedex.query('name')
                    name_query.where(pokemonid=pokemonid, language_id=9)
                    name = await name_query.get_value()
                    role = await guild.create_role(name=name, mentionable=True)
                elif self.want in raid_tiers:
                    name = "Tier " + self.want
                    role = await guild.create_role(name=name, mentionable=True)
                elif self.want.startswith('POKEMON_TYPE'):
                    types_table = self.bot.dbi.table('type_names')
                    name_query = types_table.query('name')
                    name_query.where(typeid=self.want, language_id=9)
                    name = await name_query.get_value()
                    role = await guild.create_role(name=name, mentionable=True)
                else:
                    items_table = self.bot.dbi.table('item_names')
                    name_query = items_table.query('name')
                    name_query.where(itemid=self.want, language_id=9)
                    name = await name_query.get_value()
                    role = await guild.create_role(name=name, mentionable=True)
                insert = self._update
                insert.row(role=role.id)
                await insert.commit(do_update=True)
                for user in users:
                    await user.add_roles(role)
            return role

class WantCog(Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @command()
    async def want(self, ctx, *wants):
        for want in wants:
            pkmn = await Pokemon.convert(ctx, want)

