from meowth import Cog, command, bot, checks
from meowth.exts.pkmn import Pokemon
from meowth.utils import fuzzymatch

import discord
from discord.ext import commands

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
        return insert
    
    @property
    def _update(self):
        want_table = self.bot.dbi.table('wants')
        update = want_table.update
        update.where(guild=self.guildid, want=self.want)
        return update
    
    async def _users(self):
        _data = self._data
        _data.select('users')
        users = await _data.get_value()
        if not users:
            users = []
        return users
    
    async def add_user(self, user_id):
        users = await self._users()
        if not users:
            insert = self._insert
            await insert.commit()
            users = []
        if user_id not in users:
            users.append(user_id)
            update = self._update
            update.values(users=users)
            await update.commit()
            role = await self.role()
            if role:
                member = self.guild.get_member(user_id)
                if role not in member.roles:
                    await member.add_roles(role)
            return 'success'
        else:
            return 'already done'
    
    async def remove_user(self, user_id):
        users = await self._users()
        if not users:
            return 'already done'
        if user_id not in users:
            return 'already done'
        users.remove(user_id)
        update = self._update
        update.values(users=users)
        await update.commit()
        role = await self.role()
        if role:
            member = self.guild.get_member(user_id)
            if role in member.roles:
                await member.remove_roles(role)
        return 'success'
    
    async def notify_users(self, content, embed, author=None):
        msgs = []
        users = await self._users()
        guild = self.guild
        members = [guild.get_member(x) for x in users]
        for member in members:
            # if member == author:
            #     continue
            msg = await member.send(content, embed=embed)
            msgs.append(f"{msg.channel.id}/{msg.id}")
        return msgs

    async def is_role(self):
        users = await self._users()
        if not users:
            return False
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
                # elif self.want.startswith('POKEMON_TYPE'):
                #     types_table = self.bot.dbi.table('type_names')
                #     name_query = types_table.query('name')
                #     name_query.where(typeid=self.want, language_id=9)
                #     name = await name_query.get_value()
                #     role = await guild.create_role(name=name, mentionable=True)
                else:
                    items_table = self.bot.dbi.table('item_names')
                    name_query = items_table.query('name')
                    name_query.where(itemid=self.want, language_id=9)
                    name = await name_query.get_value()
                    role = await guild.create_role(name=name, mentionable=True)
                insert = self._update
                insert.row(role=role.id)
                await insert.commit(do_update=True)
                for member in members:
                    await member.add_roles(role)
            return role
    
    @classmethod
    async def convert(cls, ctx, arg):
        arg = arg.lower()
        tiers = ['1', '2', '3', '4', '5', 'ex', 'exgym']
        if arg in tiers:
            return cls(ctx.bot, arg, ctx.guild.id)
        try:
            pkmn = await Pokemon.convert(ctx, arg)
        except:
            pkmn = False
        if pkmn:
            family = await pkmn._familyId()
            return cls(ctx.bot, family, ctx.guild.id)

class WantCog(Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @command()
    async def want(self, ctx, wants: commands.Greedy[Want]):
        added_wants = []
        for want in wants:
            status = await want.add_user(ctx.author.id)
            if status == 'already done':
                continue
            added_wants.append(want.want)
        await ctx.success(title="Wants Added", details="\n".join(added_wants))
    
    @command()
    async def unwant(self, ctx, wants: commands.Greedy[Want]):
        removed_wants = []
        for want in wants:
            status = await want.remove_user(ctx.author.id)
            if status == 'already done':
                continue
            removed_wants.append(want.want)
        await ctx.success(title="Wants Removed", details="\n".join(removed_wants))
    
    @command()
    async def listwants(self, ctx):
        user_id = ctx.author.id
        table = ctx.bot.dbi.table('wants')
        query = table.query('want')
        query.where(guild=ctx.guild.id)
        query.where(table['users'].contains_(user_id))
        want_list = await query.get_values()
        await ctx.send(f'Current want list for {ctx.author.display_name}:\n\n'
            f"{'\n'.join(want_list)}")

