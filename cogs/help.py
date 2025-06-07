import discord
from discord.ext import commands
import json

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load_user_data(self):
        try:
            with open('user_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    @commands.command(name="aide")
    async def help_command(self, ctx):
        """Commande d'aide principale"""
        embed = discord.Embed(
            title="🎰 JackBot - Menu d'Aide Principal",
            description="**Bienvenue sur JackBot !** 🎉\n"
                       "Votre bot de casino et divertissement Discord.\n\n"
                       "📋 **Utilisez les commandes ci-dessous pour plus d'infos :**",
            color=0xffd700
        )
        
        embed.add_field(
            name="🎰 Casino & Jeux",
            value="`j!casinohelp` - Tous les jeux de casino\n"
                  "`j!funhelp` - Jeux fun et mini-jeux",
            inline=True
        )
        
        embed.add_field(
            name="💰 Économie & Shop",
            value="`j!ecohelp` - Système économique\n"
                  "`j!shophelp` - Boutique et achats",
            inline=True
        )
        
        embed.add_field(
            name="🤖 Gestion du Bot",
            value="`j!bothelp` - Personnaliser le bot\n"
                  "`j!presetshelp` - Statuts pré-définis",
            inline=True
        )
        
        embed.add_field(
            name="🛠️ Modération & Utilitaires",
            value="`j!modhelp` - Commandes de modération\n"
                  "`j!utilshelp` - Outils utilitaires",
            inline=True
        )
        
        embed.add_field(
            name="📊 Statistiques & Classements",
            value="`j!statshelp` - Stats et leaderboards\n"
                  "`j!infohelp` - Infos serveur/utilisateur",
            inline=True
        )
        
        embed.add_field(
            name="🎪 Divers & Sondages",
            value="`j!pollhelp` - Système de sondages\n"
                  "`j!mischelp` - Commandes diverses",
            inline=True
        )
        
        # Quickstart
        embed.add_field(
            name="⚡ Démarrage Express",
            value="```\n"
                  "j!daily     → Bonus quotidien (1000 pts)\n"
                  "j!slot 100  → Premier jeu de casino\n"
                  "j!balance   → Voir vos points\n"
                  "j!shop      → Découvrir la boutique\n"
                  "```",
            inline=False
        )
        
        # Stats du bot
        embed.add_field(
            name="📈 Statistiques du Bot",
            value=f"🏆 Serveurs: {len(self.bot.guilds)}\n"
                  f"👥 Utilisateurs: {len(self.bot.users)}\n"
                  f"⚡ Latence: {round(self.bot.latency * 1000)}ms",
            inline=True
        )
        
        embed.add_field(
            name="🔗 Liens Utiles",
            value="[Support](https://discord.gg/votre-serveur) • "
                  "[Documentation](https://votre-site.com) • "
                  "[GitHub](https://github.com/votre-repo)",
            inline=True
        )
        
        embed.set_footer(
            text="💡 Conseil: Tapez la commande d'aide spécifique pour plus de détails !",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="casinohelp")
    async def casino_help(self, ctx):
        """Aide pour les jeux de casino"""
        embed = discord.Embed(
            title="🎰 Casino - Guide des Jeux",
            description="Tentez votre chance avec nos jeux de casino !",
            color=0xe74c3c
        )
        
        embed.add_field(
            name="🎰 Machines à Sous",
            value="`j!slot <mise>` - Machine à sous classique\n"
                  "`j!megaslot <mise>` - Jackpot géant\n"
                  "`j!fruitslot <mise>` - Fruits tropicaux",
            inline=False
        )
        
        embed.add_field(
            name="🃏 Jeux de Cartes",
            value="`j!blackjack <mise>` - 21 contre le dealer\n"
                  "`j!poker <mise>` - Poker à 5 cartes\n"
                  "`j!baccarat <mise>` - Jeu royal",
            inline=False
        )
        
        embed.add_field(
            name="🎲 Jeux de Hasard",
            value="`j!roulette <mise> <couleur/nombre>` - Roulette européenne\n"
                  "`j!diceroll <mise>` - Lancé de dés\n"
                  "`j!coinflip <mise> <pile/face>` - Pile ou face",
            inline=False
        )
        
        embed.add_field(
            name="📈 Trading & Finance",
            value="`j!crash <mise>` - Graphique qui crash\n"
                  "`j!limbo <mise> <multiplicateur>` - Risque extrême\n"
                  "`j!stocks` - Bourse en temps réel",
            inline=False
        )
        
        embed.add_field(
            name="💡 Conseils",
            value="• Commencez avec de petites mises\n"
                  "• Gérez votre bankroll intelligemment\n"
                  "• Les gains dépendent de votre mise\n"
                  "• Utilisez `j!casinostats` pour vos stats",
            inline=False
        )
        
        embed.add_field(
            name="🏆 Récompenses",
            value="**Jackpots:** Jusqu'à 1,000,000 points !\n"
                  "**Bonus quotidien:** 1,000 points avec j!daily\n"
                  "**Multiplicateurs:** Jusqu'à x50 sur certains jeux",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="ecohelp")
    async def economy_help(self, ctx):
        """Aide pour le système économique"""
        embed = discord.Embed(
            title="💰 Économie - Guide Complet",
            description="Gérez vos points et votre richesse !",
            color=0xf39c12
        )
        
        embed.add_field(
            name="💳 Gestion de Base",
            value="`j!balance` - Voir vos points\n"
                  "`j!pay <@user> <montant>` - Transférer des points\n"
                  "`j!profile` - Votre profil complet",
            inline=False
        )
        
        embed.add_field(
            name="💼 Gains Quotidiens",
            value="`j!daily` - Bonus quotidien (1,000 pts)\n"
                  "`j!weekly` - Bonus hebdomadaire (7,500 pts)\n"
                  "`j!work` - Travailler (50-500 pts)",
            inline=False
        )
        
        embed.add_field(
            name="📈 Investissements",
            value="`j!invest <montant>` - Investir en bourse\n"
                  "`j!portfolio` - Voir vos investissements\n"
                  "`j!market` - État du marché",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Objectifs & Achievements",
            value="`j!achievements` - Vos succès débloqués\n"
                  "`j!goals` - Objectifs à atteindre\n"
                  "`j!progress` - Votre progression",
            inline=False
        )
        
        embed.add_field(
            name="💡 Stratégies",
            value="• Récupérez vos bonus quotidiens\n"
                  "• Diversifiez vos sources de revenus\n"
                  "• Investissez une partie de vos gains\n"
                  "• Participez aux événements spéciaux",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="shophelp")
    async def shop_help(self, ctx):
        """Aide pour la boutique"""
        embed = discord.Embed(
            title="🛍️ Boutique - Guide d'Achat",
            description="Dépensez vos points dans notre boutique exclusive !",
            color=0x9b59b6
        )
        
        embed.add_field(
            name="🛒 Navigation",
            value="`j!shop` - Voir tous les items\n"
                  "`j!buy <item>` - Acheter un item\n"
                  "`j!inventory` - Votre inventaire",
            inline=False
        )
        
        embed.add_field(
            name="🎭 Items de Rôle",
            value="• **VIP Access** - Salons exclusifs\n"
                  "• **Color Master** - Couleur personnalisée\n"
                  "• **Shérif** - Pouvoirs de modération temporaires",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Items de Commande",
            value="• **Message Anonyme** - Envoyer un message secret\n"
                  "• **Changeur de Pseudo** - Modifier le pseudo de quelqu'un\n"
                  "• **Notification Troll** - Spam friendly",
            inline=False
        )
        
        embed.add_field(
            name="🤖 Personnalisation Bot",
            value="• **Custom Avatar** - Changer l'avatar du bot (6h)\n"
                  "• **Custom Name** - Changer le nom du bot (6h)\n" 
                  "• **Custom Status** - Statut personnalisé (6h/12h)",
            inline=False
        )
        
        embed.add_field(
            name="🎁 Items de Buff",
            value="• **Doubleur de Mise** - Double automatiquement\n"
                  "• **Bouclier Anti-Vol** - Protection 48h\n"
                  "• **Lucky Charm** - +25% de chance de gain",
            inline=False
        )
        
        embed.add_field(
            name="💰 Prix Indicatifs",
            value="**Commandes:** 750-3,000 pts\n"
                  "**Rôles:** 3,000-15,000 pts\n"
                  "**Bot:** 3,500-7,500 pts\n"
                  "**Buffs:** 1,800-5,000 pts",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="bothelp")
    async def management_help(self, ctx):
        """Aide pour la gestion du bot"""
        embed = discord.Embed(
            title="🤖 Gestion du Bot - Personnalisation",
            description="Personnalisez l'apparence et le comportement du bot !",
            color=0xe67e22
        )
        
        embed.add_field(
            name="🖼️ Avatar",
            value="`j!avatar <url>` - Changer l'avatar (5,000 pts)\n"
                  "Durée: 6 heures | Vous pouvez joindre une image",
            inline=False
        )
        
        embed.add_field(
            name="🏷️ Nom",
            value="`j!name <nouveau_nom>` - Changer le nom (7,500 pts)\n"
                  "Durée: 6 heures | Max 32 caractères",
            inline=False
        )
        
        embed.add_field(
            name="🎮 Statut",
            value="`j!status <type> <texte>` - Changer le statut\n"
                  "`j!reset_status` - Remettre par défaut (500 pts)\n"
                  "`j!presets` - Statuts populaires pré-faits",
            inline=False
        )
        
        embed.add_field(
            name="🎭 Types de Statut",
            value="**Standard (3,500 pts - 6h):**\n"
                  "• `playing` - Joue à...\n• `listening` - Écoute...\n• `watching` - Regarde...\n\n"
                  "**Premium (6,000 pts - 12h):**\n"
                  "• `streaming` - Streame...\n• `competing` - Participe à...",
            inline=False
        )
        
        embed.add_field(
            name="📊 Monitoring",
            value="`j!bot_status` - Voir toutes les modifications actives\n"
                  "• Qui a fait quoi\n• Temps restant\n• Valeurs actuelles vs originales",
            inline=False
        )
        
        embed.add_field(
            name="⚠️ Notes Importantes",
            value="• Toutes les modifications sont temporaires\n"
                  "• Restauration automatique après expiration\n" 
                  "• Cooldowns anti-spam intégrés\n"
                  "• Remboursement automatique en cas d'erreur",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="presetshelp")
    async def presets_help(self, ctx):
        """Aide pour les statuts pré-définis"""
        embed = discord.Embed(
            title="🎮 Statuts Pré-définis Populaires",
            description="Copiez-collez ces commandes directement !",
            color=0x9b59b6
        )

        embed.add_field(
            name="🎮 Gaming (Standard - 6h)",
            value="```\nj!status playing Minecraft\n"
                  "j!status playing Among Us\n"
                  "j!status playing Valorant\n"
                  "j!status playing Genshin Impact```",
            inline=False
        )
        
        embed.add_field(
            name="🎵 Musique (Standard - 6h)",
            value="```\nj!status listening to Spotify\n"
                  "j!status listening to Lofi Hip Hop\n"
                  "j!status listening to vos playlistes\n"
                  "j!status listening to la radio```",
            inline=False
        )
        
        embed.add_field(
            name="📺 Divertissement (Standard - 6h)", 
            value="```\nj!status watching Netflix\n"
                  "j!status watching YouTube\n"
                  "j!status watching les membres\n"
                  "j!status watching du contenu```",
            inline=False
        )
        
        embed.add_field(
            name="🟣 Streaming (Premium - 12h)",
            value="```\nj!status streaming Just Chatting\n"
                  "j!status streaming Gaming\n"
                  "j!status streaming Music\n"
                  "j!status streaming Art```",
            inline=False
        )
        
        embed.add_field(
            name="🏆 Compétition (Premium - 12h)",
            value="```\nj!status competing dans Ranked\n"
                  "j!status competing pour l'attention\n"
                  "j!status competing dans un tournoi\n"
                  "j!status competing contre les bugs```",
            inline=False
        )
        
        embed.add_field(
            name="😎 Fun & Créatif",
            value="```\nj!status playing avec mes circuits\n"
                  "j!status watching le chaos du serveur\n"
                  "j!status listening to vos conversations\n"
                  "j!status competing contre SkyNet```",
            inline=False
        )
        
        embed.add_field(
            name="💰 Coûts",
            value="**Standard:** 3,500 points (6 heures)\n"
                  "**Premium:** 6,000 points (12 heures)\n"
                  "**Reset:** 500 points",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="funhelp")
    async def fun_help(self, ctx):
        """Aide pour les jeux fun"""
        embed = discord.Embed(
            title="🎪 Jeux Fun - Divertissement",
            description="Amusez-vous avec ces mini-jeux !",
            color=0x1abc9c
        )
        
        embed.add_field(
            name="🎲 Jeux de Hasard",
            value="`j!8ball <question>` - Boule magique\n"
                  "`j!flip` - Pile ou face\n"
                  "`j!dice` - Lancer de dé\n"
                  "`j!rps <choix>` - Pierre-papier-ciseaux",
            inline=False
        )
        
        embed.add_field(
            name="😄 Interactions Sociales",
            value="`j!hug <@user>` - Faire un câlin\n"
                  "`j!highfive <@user>` - Tape m'en cinq\n"
                  "`j!pat <@user>` - Caresser la tête\n"
                  "`j!poke <@user>` - Piquer quelqu'un",
            inline=False
        )
        
        embed.add_field(
            name="😂 Humour",
            value="`j!joke` - Blague aléatoire\n"
                  "`j!meme` - Mème du jour\n"
                  "`j!fact` - Fait intéressant\n"
                  "`j!quote` - Citation inspirante",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Mini-Jeux",
            value="`j!trivia` - Questions culture générale\n"
                  "`j!riddle` - Énigmes à résoudre\n"
                  "`j!wordscramble` - Mots mélangés\n"
                  "`j!mathquiz` - Quiz de maths",
            inline=False
        )
        
        embed.add_field(
            name="🎁 Récompenses",
            value="Gagnez entre 5-50 points selon le jeu !\n"
                  "Bonus spéciaux pour les bonnes réponses consécutives.",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="pollhelp")
    async def poll_help(self, ctx):
        """Aide pour les sondages"""
        embed = discord.Embed(
            title="📊 Sondages - Guide Complet",
            description="Créez et gérez des sondages interactifs !",
            color=0x3498db
        )
        
        embed.add_field(
            name="📝 Création",
            value="`j!poll \"Titre\" \"Option 1\" \"Option 2\" ...` - Sondage complet\n"
                  "`j!quickpoll \"Question\"` - Sondage oui/non rapide\n"
                  "Maximum 10 options par sondage",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Gestion",
            value="`j!closepoll <ID>` - Fermer un sondage\n"
                  "`j!mypolls` - Vos sondages actifs\n"
                  "`j!pollresults <ID>` - Résultats détaillés",
            inline=False
        )
        
        embed.add_field(
            name="📊 Fonctionnalités",
            value="• Votes par réactions emoji\n"
                  "• Résultats en temps réel avec barres\n"
                  "• Système anti-vote multiple\n"
                  "• Historique des sondages",
            inline=False
        )
        
        embed.add_field(
            name="🎁 Récompenses",
            value="• Créer un sondage: **+10 points**\n"
                  "• Sondage rapide: **+5 points**\n"
                  "• Voter: **+1 point**",
            inline=False
        )
        
        embed.add_field(
            name="💡 Conseils",
            value="• Utilisez des guillemets pour les options avec espaces\n"
                  "• Les sondages restent actifs jusqu'à fermeture manuelle\n"
                  "• Seul le créateur peut fermer son sondage",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="modhelp")
    async def moderation_help(self, ctx):
        """Aide pour la modération"""
        if not ctx.author.guild_permissions.manage_messages:
            embed = discord.Embed(
                title="❌ Accès Refusé",
                description="Vous devez avoir les permissions de modération pour voir cette aide.",
                color=0xe74c3c
            )
            await ctx.send(embed=embed)
            return
            
        embed = discord.Embed(
            title="🛠️ Modération - Guide Complet",
            description="Outils de modération pour maintenir l'ordre !",
            color=0xe74c3c
        )
        
        embed.add_field(
            name="👤 Gestion Membres",
            value="`j!kick <@user> [raison]` - Expulser un membre\n"
                  "`j!ban <@user> [raison]` - Bannir un membre\n"
                  "`j!unban <user_id>` - Débannir un membre\n"
                  "`j!timeout <@user> <durée>` - Timeout temporaire",
            inline=False
        )
        
        embed.add_field(
            name="💬 Gestion Messages",
            value="`j!clear <nombre>` - Supprimer des messages\n"
                  "`j!purge <@user> <nombre>` - Supprimer messages d'un user\n"
                  "`j!slowmode <secondes>` - Mode lent du salon",
            inline=False
        )
        
        embed.add_field(
            name="🔒 Gestion Salon",
            value="`j!lock` - Verrouiller le salon\n"
                  "`j!unlock` - Déverrouiller le salon\n"
                  "`j!lockdown` - Verrouillage serveur d'urgence",
            inline=False
        )
        
        embed.add_field(
            name="⚠️ Avertissements",
            value="`j!warn <@user> <raison>` - Donner un avertissement\n"
                  "`j!warnings <@user>` - Voir les avertissements\n"
                  "`j!clearwarns <@user>` - Effacer les avertissements",
            inline=False
        )
        
        embed.add_field(
            name="📋 Permissions Requises",
            value="• Kick: `Expulser des membres`\n"
                  "• Ban: `Bannir des membres`\n"
                  "• Clear: `Gérer les messages`\n"
                  "• Lock: `Gérer les salons`",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="utilshelp")
    async def utils_help(self, ctx):
        """Aide pour les utilitaires"""
        embed = discord.Embed(
            title="🔧 Utilitaires - Outils Pratiques",
            description="Commandes utiles pour tous !",
            color=0x95a5a6
        )
        
        embed.add_field(
            name="ℹ️ Informations",
            value="`j!userinfo <@user>` - Infos sur un utilisateur\n"
                  "`j!serverinfo` - Infos sur le serveur\n"
                  "`j!botinfo` - Informations sur le bot\n"
                  "`j!ping` - Latence du bot",
            inline=False
        )
        
        embed.add_field(
            name="🕒 Temps & Date",
            value="`j!time` - Heure actuelle\n"
                  "`j!timezone <zone>` - Heure dans une timezone\n"
                  "`j!uptime` - Temps d'activité du bot",
            inline=False
        )
        
        embed.add_field(
            name="🔢 Calculs",
            value="`j!calc <expression>` - Calculatrice\n" 
                  "`j!convert <valeur> <de> <vers>` - Convertisseur\n"
                  "`j!random <min> <max>` - Nombre aléatoire",
            inline=False
        )
        
        embed.add_field(
            name="🔍 Recherche",
            value="`j!weather <ville>` - Météo\n"
                  "`j!translate <lang> <texte>` - Traducteur\n"
                  "`j!wiki <terme>` - Recherche Wikipedia",
            inline=False
        )
        
        embed.add_field(
            name="🛠️ Outils Serveur",
            value="`j!avatar <@user>` - Avatar d'un utilisateur\n"
                  "`j!membercount` - Nombre de membres\n"
                  "`j!roleinfo <@role>` - Infos sur un rôle",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="statshelp")
    async def stats_help(self, ctx):
        """Aide pour les statistiques"""
        embed = discord.Embed(
            title="📊 Statistiques - Classements & Analyses",
            description="Suivez vos performances et comparez-vous !",
            color=0xf39c12
        )
        
        embed.add_field(
            name="🏆 Classements",
            value="`j!leaderboard` - Top 10 des plus riches\n"
                  "`j!casinoleaderboard` - Top joueurs casino\n"
                  "`j!weeklytop` - Top de la semaine\n"
                  "`j!monthlytop` - Top du mois",
            inline=False
        )
        
        embed.add_field(
            name="📈 Stats Personnelles",
            value="`j!mystats` - Vos statistiques complètes\n"
                  "`j!casinostats` - Vos stats de casino\n"
                  "`j!rank` - Votre rang actuel\n"
                  "`j!progress` - Votre progression",
            inline=False
        )
        
        embed.add_field(
            name="🎰 Analyses Casino",
            value="`j!winrate` - Taux de victoire par jeu\n"
                  "`j!biggestwins` - Vos plus gros gains\n"
                  "`j!luckyfactor` - Votre facteur chance\n"
                  "`j!gamestats <jeu>` - Stats pour un jeu spécifique",
            inline=False
        )
        
        embed.add_field(
            name="📊 Stats Serveur",
            value="`j!serverstats` - Statistiques du serveur\n"
                  "`j!activity` - Activité des membres\n"
                  "`j!topgamers` - Joueurs les plus actifs",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Objectifs",
            value="`j!achievements` - Vos succès débloqués\n"
                  "`j!goals` - Objectifs à atteindre\n"
                  "`j!rewards` - Récompenses disponibles",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="infohelp")
    async def info_help(self, ctx):
        """Aide pour les informations"""
        embed = discord.Embed(
            title="ℹ️ Informations - Guide des Commandes",
            description="Toutes les informations dont vous avez besoin !",
            color=0x3498db
        )
        
        embed.add_field(
            name="👤 Utilisateurs",
            value="`j!whois <@user>` - Profil détaillé d'un membre\n"
                  "`j!joined <@user>` - Date d'arrivée sur le serveur\n"
                  "`j!created <@user>` - Date de création du compte",
            inline=False
        )
        
        embed.add_field(
            name="🏠 Serveur",
            value="`j!server` - Informations complètes du serveur\n"
                  "`j!channels` - Liste des salons\n"
                  "`j!roles` - Liste des rôles\n"
                  "`j!emojis` - Émojis personnalisés",
            inline=False
        )
        
        embed.add_field(
            name="🤖 Bot",
            value="`j!about` - À propos du bot\n"
                  "`j!version` - Version et changelog\n"
                  "`j!invite` - Lien d'invitation\n"
                  "`j!support` - Serveur de support",
            inline=False
        )
        embed.add_field(
            name="📊 Performances",
            value="`j!status` - État du bot en temps réel\n"
                  "`j!performance` - Métriques de performance\n"
                  "`j!guilds` - Serveurs où est présent le bot\n"
                  "`j!shardinfo` - Informations sur les shards",
            inline=False
        )
        
        embed.add_field(
            name="🔗 Permissions",
            value="`j!perms <@user>` - Permissions d'un utilisateur\n"
                  "`j!botperms` - Permissions du bot\n"
                  "`j!checkperms <action>` - Vérifier une permission",
            inline=False
        )
        
        embed.add_field(
            name="📅 Historique",
            value="`j!history` - Historique des commandes\n"
                  "`j!logs` - Logs d'activité récente\n"
                  "`j!events` - Événements du serveur",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="mischelp")
    async def misc_help(self, ctx):
        """Aide pour les commandes diverses"""
        embed = discord.Embed(
            title="🎪 Divers - Commandes Variées",
            description="Toutes les autres fonctionnalités utiles !",
            color=0xe91e63
        )
        
        embed.add_field(
            name="🎨 Personnalisation",
            value="`j!color <couleur>` - Changer votre couleur de rôle\n"
                  "`j!nickname <pseudo>` - Changer votre surnom\n"
                  "`j!bio <texte>` - Modifier votre bio personnelle",
            inline=False
        )
        
        embed.add_field(
            name="🔔 Notifications",
            value="`j!notify <message>` - Programmer une notification\n"
                  "`j!reminder <temps> <message>` - Rappel personnalisé\n"
                  "`j!subscribe <événement>` - S'abonner aux notifications",
            inline=False
        )
        
        embed.add_field(
            name="💝 Cadeaux & Social",
            value="`j!gift <@user> <points>` - Offrir des points\n"
                  "`j!birthday <date>` - Définir votre anniversaire\n"
                  "`j!marriage <@user>` - Demander en mariage (RP)",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Événements",
            value="`j!events` - Événements en cours\n"
                  "`j!participate <événement>` - Participer\n"
                  "`j!schedule` - Calendrier des événements",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Préférences",
            value="`j!settings` - Vos paramètres personnels\n"
                  "`j!privacy <niveau>` - Niveau de confidentialité\n"
                  "`j!language <langue>` - Changer la langue",
            inline=False
        )
        
        embed.add_field(
            name="📱 Intégrations",
            value="`j!connect <service>` - Connecter un service externe\n"
                  "`j!sync` - Synchroniser les données\n"
                  "`j!backup` - Sauvegarder vos données",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="commandlist")
    async def command_list(self, ctx):
        """Liste complète de toutes les commandes disponibles"""
        embed = discord.Embed(
            title="📋 Liste Complète des Commandes",
            description="Toutes les commandes disponibles organisées par catégorie",
            color=0x9b59b6
        )
        
        # Casino & Jeux
        embed.add_field(
            name="🎰 Casino",
            value="```\nslot, megaslot, fruitslot\nblackjack, poker, baccarat\nroulette, diceroll, coinflip\ncrash, limbo, stocks```",
            inline=True
        )
        
        # Économie
        embed.add_field(
            name="💰 Économie",
            value="```\nbalance, pay, profile\ndaily, weekly, work\ninvest, portfolio, market\nachievements, goals```",
            inline=True
        )
        
        # Boutique
        embed.add_field(
            name="🛍️ Boutique",
            value="```\nshop, buy, inventory\nuse, gift, trade\nwishlist, catalog```",
            inline=True
        )
        
        # Bot Management
        embed.add_field(
            name="🤖 Bot",
            value="```\navatar, name, status\nreset_status, presets\nbot_status```",
            inline=True
        )
        
        # Fun
        embed.add_field(
            name="🎪 Fun",
            value="```\n8ball, flip, dice, rps\nhug, highfive, pat, poke\njoke, meme, fact, quote\ntrivia, riddle, wordscramble```",
            inline=True
        )
        
        # Sondages
        embed.add_field(
            name="📊 Sondages",
            value="```\npoll, quickpoll\nclosepoll, mypolls\npollresults```",
            inline=True
        )
        
        # Modération (si autorisé)
        if ctx.author.guild_permissions.manage_messages:
            embed.add_field(
                name="🛠️ Modération",
                value="```\nkick, ban, unban, timeout\nclear, purge, slowmode\nlock, unlock, lockdown\nwarn, warnings, clearwarns```",
                inline=True
            )
        
        # Utilitaires
        embed.add_field(
            name="🔧 Utilitaires",
            value="```\nuserinfo, serverinfo, botinfo\ntime, timezone, calc\nweather, translate, wiki\navatar, membercount```",
            inline=True
        )
        
        # Statistiques
        embed.add_field(
            name="📊 Stats",
            value="```\nleaderboard, casinoleaderboard\nmystats, casinostats, rank\nwinrate, biggestwins\nserverstats, activity```",
            inline=True
        )
        
        embed.add_field(
            name="⚡ Total des Commandes",
            value=f"**{len([cmd for cmd in self.bot.commands])} commandes** disponibles\n"
                  f"Utilisez `j!aide` pour l'aide détaillée",
            inline=False
        )
        
        embed.set_footer(
            text="💡 Utilisez 'j!<catégorie>help' pour plus de détails sur chaque catégorie"
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="quickstart")
    async def quickstart_guide(self, ctx):
        """Guide de démarrage rapide"""
        user_data = self.load_user_data()
        user_id = str(ctx.author.id)
        
        # Vérifier si c'est un nouvel utilisateur
        is_new_user = user_id not in user_data
        
        embed = discord.Embed(
            title="⚡ Guide de Démarrage Rapide",
            description="Bienvenue sur JackBot ! Voici comment commencer :",
            color=0x00ff00 if is_new_user else 0xffd700
        )
        
        if is_new_user:
            embed.add_field(
                name="🎉 Nouveau Membre Détecté !",
                value="Vous recevez **500 points de bienvenue** ! 🎁",
                inline=False
            )
        
        embed.add_field(
            name="1️⃣ Premiers Pas",
            value="```\nj!daily     → Récupérez 1000 points quotidiens\n"
                  "j!balance   → Vérifiez vos points actuels\n"
                  "j!profile   → Consultez votre profil```",
            inline=False
        )
        
        embed.add_field(
            name="2️⃣ Premier Jeu",
            value="```\nj!slot 50   → Jouez aux machines à sous\n"
                  "j!coinflip 25 pile → Pariez sur pile ou face\n"
                  "j!8ball Vais-je gagner? → Consultez la boule```",
            inline=False
        )
        
        embed.add_field(
            name="3️⃣ Découverte",
            value="```\nj!shop      → Explorez la boutique\n"
                  "j!leaderboard → Voyez le classement\n"
                  "j!casinohelp → Guide des jeux complet```",
            inline=False
        )
        
        embed.add_field(
            name="4️⃣ Fonctionnalités Avancées",
            value="```\nj!poll \"Question?\" \"Oui\" \"Non\" → Créez un sondage\n"
                  "j!mystats   → Vos statistiques complètes\n"
                  "j!bothelp   → Personnalisez le bot```",
            inline=False
        )
        
        embed.add_field(
            name="💡 Conseils Pro",
            value="• **Récupérez votre bonus quotidien** avec `j!daily`\n"
                  "• **Commencez avec de petites mises** pour apprendre\n"
                  "• **Participez aux sondages** pour gagner des points bonus\n"
                  "• **Échangez avec la communauté** avec `j!pay @user <montant>`\n"
                  "• **Investissez intelligemment** avec `j!invest`",
            inline=False
        )
        
        embed.add_field(
            name="🆘 Besoin d'Aide ?",
            value="• `j!aide` - Menu principal\n"
                  "• `j!commandlist` - Toutes les commandes\n"
                  "• `j!support` - Serveur de support\n"
                  "• Mentionnez un modérateur pour assistance",
            inline=False
        )
        
        if is_new_user:
            embed.set_footer(
                text="🌟 Profitez de votre expérience sur JackBot ! Les 500 points bonus ont été ajoutés."
            )
            # Ajouter les points de bienvenue
            if user_id not in user_data:
                user_data[user_id] = {'points': 500, 'games_played': 0}
            else:
                user_data[user_id]['points'] = user_data[user_id].get('points', 0) + 500
            self.save_user_data(user_data)
        else:
            points = user_data.get(user_id, {}).get('points', 0)
            embed.set_footer(
                text=f"💰 Vous avez actuellement {points:,} points • Bonne chance !"
            )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))
