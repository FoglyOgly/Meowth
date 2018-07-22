import asyncio

import discord
from discord.ext import commands


from meowth import utils
from meowth import checks

class Tutorial:
    def __init__(self, bot):
        self.bot = bot

    async def wait_for_cmd(self, tutorial_channel, newbie, command_name):

        # build check relevant to command
        def check(c):
            if not c.channel == tutorial_channel:
                return False
            if not c.author == newbie:
                return False
            if c.command.name == command_name:
                return True
            return False

        # wait for the command to complete
        cmd_ctx = await self.bot.wait_for(
            'command_completion', check=check, timeout=300)

        return cmd_ctx

    def get_overwrites(self, guild, member):
        return {
            guild.default_role: discord.PermissionOverwrite(
                read_messages=False),
            member: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                manage_channels=True),
            guild.me: discord.PermissionOverwrite(
                read_messages=True)
            }

    async def want_tutorial(self, ctx, config):
        report_channels = config['want']['report_channels']
        report_channels.append(ctx.tutorial_channel.id)

        await ctx.tutorial_channel.send(
            f"Ce serveur utilise la commande **{ctx.prefix}want ** pour vous aider "
            "les membres reçoivent des notifications push sur les Pokemon qu'ils veulent! "
            "Je crée des rôles Discord pour chaque Pokemon que les gens veulent, "
            "et @mentioning ces rôles enverra une notification à "
            f"Quelqu'un qui **{ctx.prefix}veut**-drait ce Pokemon !\n"
            f"Essayez la commande {ctx.prefix}want!\n"
            f"Ex: `{ctx.prefix}want koygre`")

        try:
            await self.wait_for_cmd(ctx.tutorial_channel, ctx.author, 'want')

            # acknowledge and wait a second before continuing
            await ctx.tutorial_channel.send("Bon boulot !")
            await asyncio.sleep(1)

        # if no response for 5 minutes, close tutorial
        except asyncio.TimeoutError:
            await ctx.tutorial_channel.send(
                "Vous avez pris trop de temps pour compléter la commande "
                f"**{ctx.prefix}want** ! Cette chaîne sera supprimée dans dix secondes.")
            await asyncio.sleep(10)
            await ctx.tutorial_channel.delete()

            return False

        # clean up by removing tutorial from report channel config
        finally:
            report_channels.remove(ctx.tutorial_channel.id)

        return True

    async def wild_tutorial(self, ctx, config):
        report_channels = config['wild']['report_channels']
        report_channels[ctx.tutorial_channel.id] = 'test'

        await ctx.tutorial_channel.send(
            f"Ce serveur utilise la commande **{ctx.prefix}wild** pour "
            "signaler des spawns wild ! Quand vous l'utiliserez, j'enverrai un message "
            "résummant la signalisation et contenant un lien vers ma meilleur "
            "estimation de l'emplacement de réapparition. Si le Pokemon rapporté a un "
            "rôle associé sur le serveur, je vais @mentionner le rôle "
            "dans mon message! Votre signalement doit contenir le nom du "
            "Pokémon suivi de son emplacement. "
            "Essayez de signaler un spawn sauvage!\n"
            f"Ex: `{ctx.prefix}wild magicarpe \"quelque part\"`")

        try:
            await self.wait_for_cmd(ctx.tutorial_channel, ctx.author, 'wild')

            # acknowledge and wait a second before continuing
            await ctx.tutorial_channel.send("Bon boulot !")
            await asyncio.sleep(1)

        # if no response for 5 minutes, close tutorial
        except asyncio.TimeoutError:
            await ctx.tutorial_channel.send(
                f"Vous avez pris trop de temps pour compléter la commande "
                f"**{ctx.prefix}wild** ! Cette chaîne sera supprimée dans dix secondes.")
            await asyncio.sleep(10)
            await ctx.tutorial_channel.delete()
            return False

        # clean up by removing tutorial from report channel config
        finally:
            del report_channels[ctx.tutorial_channel.id]

        return True

    async def raid_tutorial(self, ctx, config):
        report_channels = config['raid']['report_channels']
        category_dict = config['raid']['category_dict']
        tutorial_channel = ctx.tutorial_channel
        prefix = ctx.prefix
        raid_channel = None

        # add tutorial channel to valid want report channels
        report_channels[tutorial_channel.id] = 'test'

        if config['raid']['categories'] == "region":
            category_dict[tutorial_channel.id] = tutorial_channel.category_id

        async def timeout_raid(cmd):
            await tutorial_channel.send(
                "Vous avez pris trop de temps pour compléter la commande "
                f"**{prefix}{cmd}** ! Cette chaîne sera supprimée dans dix secondes.")
            await asyncio.sleep(10)
            await tutorial_channel.delete()
            del report_channels[tutorial_channel.id]
            del category_dict[tutorial_channel.id]
            if raid_channel:
                await raid_channel.delete()
                ctx.bot.loop.create_task(self.bot.expire_channel(raid_channel))
            return

        await tutorial_channel.send(
            f"Ce serveur utilise la commande **{prefix}raid** pour "
            "signaler les raids! Quand vous l'utiliserez, j'enverrai un message "
            "résumant le signalement et je créerai un canal de texte pour "
            "coordination. \n"
            "Le rapport doit contenir, dans cet ordre: Le Pokémon (si un "
            "raid actif) ou niveau de raid (si un oeuf), et l'emplacement;\n"
            "le rapport peut éventuellement contenir le temps (voir "
            f"**{prefix}help weather** pour les options acceptées) et les "
            "minutes restantes jusqu'à l'éclosion ou l'expiration (à la fin du "
            "signalement) \n\n"
            "Essayez de signaler un raid!\n"
            f"Ex: `{prefix}raid magicarpe local church ensoleillé 42`\n"
            f"`{prefix}raid 3 local church ensoleillé 27`")

        try:
            while True:
                raid_ctx = await self.wait_for_cmd(
                    tutorial_channel, ctx.author, 'raid')

                # get the generated raid channel
                raid_channel = raid_ctx.raid_channel

                if raid_channel:
                    break

                # acknowledge failure and redo wait_for
                await tutorial_channel.send(
                    "Ça n'a pas l'air de fonctionner. Assurez-vous de n'avoir oublié "
                    "aucun parametres à votre commande raid "
                    "et réessayez.")

            # acknowledge and redirect to new raid channel
            await tutorial_channel.send(
                "Bon boulot! Retrouvons-nous dans la chaine que vous venez de "
                f"créer: {raid_channel.mention}")
            await asyncio.sleep(1)

        # if no response for 5 minutes, close tutorial
        except asyncio.TimeoutError:
            await timeout_raid('raid')
            return False

        # post raid help info prefix, avatar, user
        helpembed = await utils.get_raid_help(
            ctx.prefix, ctx.bot.user.avatar_url)

        await raid_channel.send(
            f"Ceci est une chaine d'exemple pour les Raid. Voici une liste "
            "de commandes que vous pouvez utiliser ici:", embed=helpembed)

        await raid_channel.send(
            f"Essayez de montrer votre intéret pour ce raid!\n\n"
            f"Ex: `{prefix}interested 5 m3 i1 v1` Veut dire 5 dresseurs: "
            "3 Mystic, 1 Instinct, 1 Valor")

        # wait for interested status update
        try:
            await self.wait_for_cmd(
                raid_channel, ctx.author, 'interested')

        # if no response for 5 minutes, close tutorial
        except asyncio.TimeoutError:
            await timeout_raid('interested')
            return False

        # acknowledge and continue with pauses between
        await asyncio.sleep(1)
        await raid_channel.send(
            f"Super ! Pour aller plus vite, vous pouvez aussi utiliser **{prefix}i** "
            f"c'est un alias pour la command **{prefix}interested**.")

        await asyncio.sleep(1)
        await raid_channel.send(
            "Maintenant, essayons d'informer les autres que vous arrivez!\n\n"
            f"Ex: `{prefix}coming`")

        # wait for coming status update
        try:
            await self.wait_for_cmd(
                raid_channel, ctx.author, 'coming')

        # if no response for 5 minutes, close tutorial
        except asyncio.TimeoutError:
            await timeout_raid('coming')
            return False

        # acknowledge and continue with pauses between
        await asyncio.sleep(1)
        await raid_channel.send(  
            "Parfait! Notez que si vous avez déjà spécifié votre participation "
            "dans une commande précédente, vous n'avez pas à nouveau pour "
            "le raid en cours à moins que vous l'ayez modifié. De même, "
            f"**{prefix}c** est un alias pour **{prefix}coming**.")

        await asyncio.sleep(1)
        await raid_channel.send(
            "Maintenant, essayez de faire savoir aux gens que vous êtes arrivé au "
            "raid!\n\n"
            f"Ex: `{prefix}here`")

        # wait for here status update
        try:
            await self.wait_for_cmd(
                raid_channel, ctx.author, 'here')

        # if no response for 5 minutes, close tutorial
        except asyncio.TimeoutError:
            await timeout_raid('here')
            return False

        # acknowledge and continue with pauses between
        await asyncio.sleep(1)
        await raid_channel.send(
            f"Good! Notez que  **{prefix}h** est un alias pour "
            f"**{prefix}here**")

        await asyncio.sleep(1)
        await raid_channel.send(
            "Maintenant voyons les réponses des autres joueurs pour ce "
            f"raid!\n\nEx: `{prefix}list`")

        # wait for list command completion
        try:
            await self.wait_for_cmd(
                raid_channel, ctx.author, 'list')

        # if no response for 5 minutes, close tutorial
        except asyncio.TimeoutError:
            await timeout_raid('list')
            return False

        # acknowledge and continue with pauses between
        await asyncio.sleep(1)
        await raid_channel.send(
            "Génial! Puisque plus personne n'est en chemin, essayons "
            f"la commande **{prefix}starting** pour faire entrer les gens "
            " de la liste 'here' dans le lobby!")

        # wait for starting command completion
        try:
            await self.wait_for_cmd(
                raid_channel, ctx.author, 'starting')

        # if no response for 5 minutes, close tutorial
        except asyncio.TimeoutError:
            await timeout_raid('starting')
            return False

        # acknowledge and continue with pauses between
        await asyncio.sleep(1)
        await raid_channel.send(
            f"Génial! Vous êtes maintenant listé comme étant 'dans le hall', où "
            "vous resterez pendant deux minutes jusqu'à ce que le raid commence. "
            "Pendantce temps, tout le monde peut demander un backout avec la "
            f"commande **{prefix}backout**. Si la personne qui demande est "
            "dans le hall, la sortie est automatique. Si c'est quelqu'un "
            "qui est arrivé au raid par la suite, la confirmation sera "
            "demandée à un membre du lobby. Lorsqu'un backout est confirmé, "
            "tous les membres seront renvoyés à la liste 'here'.")

        await asyncio.sleep(1)
        await raid_channel.send(
            "Quelques notes sur les canaux de raid. Meowth a "
            "établi un partenariat avec Pokebattler pour vous donner les meilleurs contres "
            "pour chaque boss de raid dans toutes les situations. Vous pouvez définir la "
            "météo dans le rapport de raid initial ou avec la "
            f"commande **{prefix}weather**. Vous pouvez sélectionner le moveset "
            "en utilisant les réactions dans le message des contres initiaux. Si "
            f"vous avez un compte Pokebattler, vous pouvez utiliser **{prefix}set "
            "pokebattler <id>** pour les lier! Après cela, la commande "
            f"**{prefix}counters**  vous enverra en DM les meilleurs contres "
            "venant de votre Pokebox.")

        await asyncio.sleep(1)
        await raid_channel.send(
            "Dernière chose: si vous avez besoin de mettre à jour l'heure d'expiration, utilisez "
            f"**{prefix}timerset <minutes left>**\n\n"
            "N'hésitez pas à jouer avec les commandes ici pendant un moment. "
            f"Lorsque vous avez terminé, tapez `{prefix}timerset 0` et le "
            "raid expirera vous permettant de passer à la suite du Tutorial.")

        # wait for timerset command completion
        try:
            await self.wait_for_cmd(
                raid_channel, ctx.author, 'timerset')

        # if no response for 5 minutes, close tutorial
        except asyncio.TimeoutError:
            await timeout_raid('timerset')
            return False

        # acknowledge and direct member back to tutorial channel
        await raid_channel.send(
            f"Great! Now return to {tutorial_channel.mention} to "
            "continue the tutorial. This channel will be deleted in "
            "ten seconds.")

        await tutorial_channel.send(
            f"Hey {ctx.author.mention}, once I'm done cleaning up the "
            "raid channel, the tutorial will continue here!")

        await asyncio.sleep(10)

        # remove tutorial raid channel
        await raid_channel.delete()
        raid_channel = None
        del report_channels[tutorial_channel.id]

        return True

    async def research_tutorial(self, ctx, config):
        report_channels = config['research']['report_channels']
        report_channels[ctx.tutorial_channel.id] = 'test'

        await ctx.tutorial_channel.send(
            f"This server utilizes the **{ctx.prefix}research** command to "
            "report field research tasks! There are two ways to use this "
            f"command: **{ctx.prefix}research** will start an interactive "
            "session where I will prompt you for the task, location, and "
            "reward of the research task. You can also use "
            f"**{ctx.prefix}research <pokestop>, <task>, <reward>** to "
            "submit the report all at once.\n\n"
            f"Try it out by typing `{ctx.prefix}research`")

        # wait for research command completion
        try:
            await self.wait_for_cmd(
                ctx.tutorial_channel, ctx.author, 'research')

            # acknowledge and wait a second before continuing
            await ctx.tutorial_channel.send("Great job!")
            await asyncio.sleep(1)

        # if no response for 5 minutes, close tutorial
        except asyncio.TimeoutError:
            await ctx.tutorial_channel.send(
                f"You took too long to use the **{ctx.prefix}research** "
                "command! This channel will be deleted in ten seconds.")
            await asyncio.sleep(10)
            await ctx.tutorial_channel.delete()
            return False

        # clean up by removing tutorial from report channel config
        finally:
            del report_channels[ctx.tutorial_channel.id]

        return True

    async def team_tutorial(self, ctx):
        await ctx.tutorial_channel.send(
            f"This server utilizes the **{ctx.prefix}team** command to "
            "allow members to select which Pokemon Go team they belong "
            f"to! Type `{ctx.prefix}team mystic` for example if you are in "
            "Team Mystic.")

        # wait for team command completion
        try:
            await self.wait_for_cmd(
                ctx.tutorial_channel, ctx.author, 'team')

            # acknowledge and wait a second before continuing
            await ctx.tutorial_channel.send("Great job!")
            await asyncio.sleep(1)

        # if no response for 5 minutes, close tutorial
        except asyncio.TimeoutError:
            await ctx.tutorial_channel.send(
                f"You took too long to use the **{ctx.prefix}team** command! "
                "This channel will be deleted in ten seconds.")
            await asyncio.sleep(10)
            await ctx.tutorial_channel.delete()
            return False

        return True

    @commands.group(invoke_without_command=True)
    async def tutorial(self, ctx):
        """Launches an interactive tutorial session for Meowth.

        Meowth will create a private channel and initiate a
        conversation that walks you through the various commands
        that are enabled on the current server."""

        newbie = ctx.author
        guild = ctx.guild
        prefix = ctx.prefix

        # get channel overwrites
        ows = self.get_overwrites(guild, newbie)

        # create tutorial channel
        name = utils.sanitize_channel_name(newbie.display_name+"-tutorial")
        ctx.tutorial_channel = await guild.create_text_channel(
            name, overwrites=ows)
        await ctx.message.delete()
        await ctx.send(
            ("Meowth! I've created a private tutorial channel for "
             f"you! Continue in {ctx.tutorial_channel.mention}"),
            delete_after=20.0)

        # get tutorial settings
        cfg = self.bot.guild_dict[guild.id]['configure_dict']
        enabled = [k for k, v in cfg.items() if v.get('enabled', False)]

        await ctx.tutorial_channel.send(
            f"Hi {ctx.author.mention}! I'm Meowth, a Discord helper bot for "
            "Pokemon Go communities! I created this channel to teach you all "
            "about the things I can do to help you on this server! You can "
            "abandon this tutorial at any time and I'll delete this channel "
            "after five minutes. Let's get started!")

        try:

            # start want tutorial
            if 'want' in enabled:
                completed = await self.want_tutorial(ctx, cfg)
                if not completed:
                    return

            # start wild tutorial
            if 'wild' in enabled:
                completed = await self.wild_tutorial(ctx, cfg)
                if not completed:
                    return

            # start raid
            if 'raid' in enabled:
                completed = await self.raid_tutorial(ctx, cfg)
                if not completed:
                    return

            # start exraid
            if 'exraid' in enabled:
                invitestr = ""

                if 'invite' in enabled:
                    invitestr = (
                        "The text channels that are created with this command "
                        f"are read-only until members use the **{prefix}invite** "
                        "command.")

                await ctx.tutorial_channel.send(
                    f"This server utilizes the **{prefix}exraid** command to "
                    "report EX raids! When you use it, I will send a message "
                    "summarizing the report and create a text channel for "
                    f"coordination. {invitestr}\n"
                    "The report must contain only the location of the EX raid.\n\n"
                    "Due to the longer-term nature of EX raid channels, we won't "
                    "try this command out right now.")

            # start research
            if 'research' in enabled:
                completed = await self.research_tutorial(ctx, cfg)
                if not completed:
                    return

            # start team
            if 'team' in enabled:
                completed = await self.team_tutorial(ctx)
                if not completed:
                    return

            # finish tutorial
            await ctx.tutorial_channel.send(
                f"This concludes the Meowth tutorial! "
                "This channel will be deleted in 30 seconds.")
            await asyncio.sleep(30)

        finally:
            await ctx.tutorial_channel.delete()

    @tutorial.command()
    @checks.feature_enabled('want')
    async def want(self, ctx):
        """Launches an tutorial session for the want feature.

        Meowth will create a private channel and initiate a
        conversation that walks you through the various commands
        that are enabled on the current server."""

        newbie = ctx.author
        guild = ctx.guild

        # get channel overwrites
        ows = self.get_overwrites(guild, newbie)

        # create tutorial channel
        name = utils.sanitize_channel_name(newbie.display_name+"-tutorial")
        ctx.tutorial_channel = await guild.create_text_channel(
            name, overwrites=ows)
        await ctx.message.delete()
        await ctx.send(
            ("Meowth! I've created a private tutorial channel for "
             f"you! Continue in {ctx.tutorial_channel.mention}"),
            delete_after=20.0)

        # get tutorial settings
        cfg = self.bot.guild_dict[guild.id]['configure_dict']

        await ctx.tutorial_channel.send(
            f"Hi {ctx.author.mention}! I'm Meowth, a Discord helper bot for "
            "Pokemon Go communities! I created this channel to teach you "
            "about the want command! You can abandon this tutorial at any time "
            "and I'll delete this channel after five minutes. "
            "Let's get started!")

        try:
            await self.want_tutorial(ctx, cfg)
            await ctx.tutorial_channel.send(
                f"This concludes the Meowth tutorial! "
                "This channel will be deleted in ten seconds.")
            await asyncio.sleep(10)
        finally:
            await ctx.tutorial_channel.delete()

    @tutorial.command()
    @checks.feature_enabled('wild')
    async def wild(self, ctx):
        """Launches an tutorial session for the wild feature.

        Meowth will create a private channel and initiate a
        conversation that walks you through wild command."""

        newbie = ctx.author
        guild = ctx.guild

        # get channel overwrites
        ows = self.get_overwrites(guild, newbie)

        # create tutorial channel
        name = utils.sanitize_channel_name(newbie.display_name+"-tutorial")
        ctx.tutorial_channel = await guild.create_text_channel(
            name, overwrites=ows)
        await ctx.message.delete()
        await ctx.send(
            ("Meowth! I've created a private tutorial channel for "
             f"you! Continue in {ctx.tutorial_channel.mention}"),
            delete_after=20.0)

        # get tutorial settings
        cfg = self.bot.guild_dict[guild.id]['configure_dict']

        await ctx.tutorial_channel.send(
            f"Hi {ctx.author.mention}! I'm Meowth, a Discord helper bot for "
            "Pokemon Go communities! I created this channel to teach you "
            "about the wild command! You can abandon this tutorial at any time "
            "and I'll delete this channel after five minutes. "
            "Let's get started!")

        try:
            await self.wild_tutorial(ctx, cfg)
            await ctx.tutorial_channel.send(
                f"This concludes the Meowth tutorial! "
                "This channel will be deleted in ten seconds.")
            await asyncio.sleep(10)
        finally:
            await ctx.tutorial_channel.delete()

    @tutorial.command()
    @checks.feature_enabled('raid')
    async def raid(self, ctx):
        """Launches an tutorial session for the raid feature.

        Meowth will create a private channel and initiate a
        conversation that walks you through the raid commands."""

        newbie = ctx.author
        guild = ctx.guild

        # get channel overwrites
        ows = self.get_overwrites(guild, newbie)

        # create tutorial channel
        name = utils.sanitize_channel_name(newbie.display_name+"-tutorial")
        ctx.tutorial_channel = await guild.create_text_channel(
            name, overwrites=ows)
        await ctx.message.delete()
        await ctx.send(
            ("Meowth! I've created a private tutorial channel for "
             f"you! Continue in {ctx.tutorial_channel.mention}"),
            delete_after=20.0)

        # get tutorial settings
        cfg = self.bot.guild_dict[guild.id]['configure_dict']

        await ctx.tutorial_channel.send(
            f"Hi {ctx.author.mention}! I'm Meowth, a Discord helper bot for "
            "Pokemon Go communities! I created this channel to teach you "
            "about the raid command! You can abandon this tutorial at any time "
            "and I'll delete this channel after five minutes. "
            "Let's get started!")

        try:
            await self.raid_tutorial(ctx, cfg)
            await ctx.tutorial_channel.send(
                f"This concludes the Meowth tutorial! "
                "This channel will be deleted in ten seconds.")
            await asyncio.sleep(10)
        finally:
            await ctx.tutorial_channel.delete()

    @tutorial.command()
    @checks.feature_enabled('research')
    async def research(self, ctx):
        """Launches an tutorial session for the research feature.

        Meowth will create a private channel and initiate a
        conversation that walks you through the research command."""

        newbie = ctx.author
        guild = ctx.guild

        # get channel overwrites
        ows = self.get_overwrites(guild, newbie)

        # create tutorial channel
        name = utils.sanitize_channel_name(newbie.display_name+"-tutorial")
        ctx.tutorial_channel = await guild.create_text_channel(
            name, overwrites=ows)
        await ctx.message.delete()
        await ctx.send(
            ("Meowth! I've created a private tutorial channel for "
             f"you! Continue in {ctx.tutorial_channel.mention}"),
            delete_after=20.0)

        # get tutorial settings
        cfg = self.bot.guild_dict[guild.id]['configure_dict']

        await ctx.tutorial_channel.send(
            f"Hi {ctx.author.mention}! I'm Meowth, a Discord helper bot for "
            "Pokemon Go communities! I created this channel to teach you "
            "about the research command! You can abandon this tutorial at "
            "any time and I'll delete this channel after five minutes. "
            "Let's get started!")

        try:
            await self.research_tutorial(ctx, cfg)
            await ctx.tutorial_channel.send(
                f"This concludes the Meowth tutorial! "
                "This channel will be deleted in ten seconds.")
            await asyncio.sleep(10)
        finally:
            await ctx.tutorial_channel.delete()

    @tutorial.command()
    @checks.feature_enabled('team')
    async def team(self, ctx):
        """Launches an tutorial session for the team feature.

        Meowth will create a private channel and initiate a
        conversation that walks you through the team command."""

        newbie = ctx.author
        guild = ctx.guild

        # get channel overwrites
        ows = self.get_overwrites(guild, newbie)

        # create tutorial channel
        name = utils.sanitize_channel_name(newbie.display_name+"-tutorial")
        ctx.tutorial_channel = await guild.create_text_channel(
            name, overwrites=ows)
        await ctx.message.delete()
        await ctx.send(
            ("Meowth! I've created a private tutorial channel for "
             f"you! Continue in {ctx.tutorial_channel.mention}"),
            delete_after=20.0)

        await ctx.tutorial_channel.send(
            f"Hi {ctx.author.mention}! I'm Meowth, a Discord helper bot for "
            "Pokemon Go communities! I created this channel to teach you "
            "about the team command! You can abandon this tutorial at any time "
            "and I'll delete this channel after five minutes. "
            "Let's get started!")

        try:
            await self.team_tutorial(ctx)
            await ctx.tutorial_channel.send(
                f"This concludes the Meowth tutorial! "
                "This channel will be deleted in ten seconds.")
            await asyncio.sleep(10)
        finally:
            await ctx.tutorial_channel.delete()

def setup(bot):
    bot.add_cog(Tutorial(bot))
