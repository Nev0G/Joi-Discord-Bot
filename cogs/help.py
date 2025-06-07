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

    @commands.command(name="help", aliases=["aide", "h"])
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
            value="`j!casino` - Tous les jeux de casino\n"
                  "`j!games` - Jeux fun et mini-jeux",
            inline=True
        )
        
        embed.add_field(
            name="💰 Économie & Shop",
            value="`j!eco` - Système économique\n"
                  "`j!shop` - Boutique et achats",
            inline=True
        )
        
        embed.add_field(
            name="🤖 Gestion du Bot",
            value="`j!botcmds` - Personnaliser le bot\n"
                  "`j!presets` - Statuts pré-définis",
            inline=True
        )
        
        embed.add_field(
            name="🛠️ Modération & Utilitaires",
            value="`j!mod` - Commandes de modération\n"
                  "`j!utils` - Outils utilitaires",
            inline=True
        )
        
        embed.add_field(
            name="📊 Statistiques & Infos",
            value="`j!stats` - Vos statistiques\n"
                  "`j!info` - Infos sur le bot",
            inline=True
        )
        
        embed.add_field(
            name="🎪 Fun & Divertissement",
            value="`j!fun` - Commandes amusantes\n"
                  "`j!random` - Générateurs aléatoires",
            inline=True
        )
        
        embed.set_footer(
            text="💡 Astuce : Utilisez j!help <catégorie> pour plus de détails",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="casino")
    async def casino_help(self, ctx):
        """Aide pour les jeux de casino"""
        embed = discord.Embed(
            title="🎰 JackBot Casino - Guide Complet",
            description="**Le meilleur casino Discord !** 🎉\n"
                       "Tentez votre chance et gagnez gros !",
            color=0xff6b6b
        )
        
        # Jeux principaux
        embed.add_field(
            name="🎰 Machines à Sous",
            value="```css\n"
                  "j!slots <mise>        • Machine classique\n"
                  "j!megaslots <mise>    • Jackpot géant\n"
                  "j!fruitslots <mise>   • Thème fruité\n"
                  "```",
            inline=False
        )
        
        # Jeux de cartes
        embed.add_field(
            name="🃏 Jeux de Cartes",
            value="```css\n"
                  "j!blackjack <mise>    • 21 classique\n"
                  "j!poker <mise>        • Texas Hold'em\n"
                  "j!baccarat <mise>     • Jeu de banque\n"
                  "```",
            inline=False
        )
        
        # Jeux de hasard
        embed.add_field(
            name="🎲 Jeux de Hasard",
            value="```css\n"
                  "j!roulette <mise> <n> • Roulette européenne\n"
                  "j!coinflip <mise>     • Pile ou face\n"
                  "j!dice <mise> <n>     • Lancer de dés\n"
                  "j!crash <mise>        • Multiplicateur risqué\n"
                  "j!plinko <mise>       • Boules et obstacles\n"
                  "```",
            inline=False
        )
        
        # Jeux spéciaux
        embed.add_field(
            name="🎪 Jeux Spéciaux",
            value="```css\n"
                  "j!limbo <mise> <mult> • Limbo risqué\n"
                  "j!mines <mise> <nb>   • Démineur interactif\n"
                  "j!wheel <mise>        • Roue de la fortune\n"
                  "j!lottery             • Loterie communautaire\n"
                  "```",
            inline=False
        )
        
        # Bonus
        embed.add_field(
            name="🎁 Bonus & Récompenses",
            value="🍋 `j!daily` - **1000 pts** quotidiens\n"
                  "🍌 `j!weekly` - **5000 pts** hebdomadaires\n"
                  "🎰 `j!casinostats` - Vos statistiques\n"
                  "🏆 `j!leaderboard casino` - Top joueurs",
            inline=True
        )
        
        # Fonctionnalités spéciales
        embed.add_field(
            name="✨ Fonctionnalités Spéciales",
            value="🎬 **Animations fluides** pour chaque jeu\n"
                  "⚡ **Interactions temps réel** (boutons, réactions)\n"
                  "🎨 **Graphiques dynamiques** selon les gains\n"
                  "🔥 **Effets visuels** pour les gros gains",
            inline=True
        )
        
        # Conseils
        embed.add_field(
            name="💡 Conseils Pro",
            value="💰 Commencez avec des petites mises\n"
                  "📊 Consultez vos stats régulièrement\n"
                  "🎯 Fixez-vous des limites\n"
                  "🍀 La chance sourit aux audacieux !",
            inline=False
        )
        
        embed.set_footer(
            text="🎮 Jouez responsable • Amusez-vous bien !",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="eco", aliases=["economy", "economie"])
    async def economy_help(self, ctx):
        """Aide pour le système économique"""
        user_data = self.load_user_data()
        user_points = user_data.get(str(ctx.author.id), {}).get('points', 0)
        
        embed = discord.Embed(
            title="💰 Système Économique JackBot",
            description="Gérez vos points et votre fortune !",
            color=0x2ecc71
        )
        
        embed.add_field(
            name="💳 Gestion Points",
            value="`j!balance` / `j!bal` - Voir vos points\n"
                  "`j!pay <user> <montant>` - Transférer des points\n"
                  "`j!gift <user> <montant>` - Faire un cadeau",
            inline=False
        )
        
        embed.add_field(
            name="🎁 Récompenses Quotidiennes",
            value="`j!daily` - 1,000 pts par jour\n"
                  "`j!weekly` - 5,000 pts par semaine\n"
                  "`j!monthly` - 20,000 pts par mois\n"
                  "`j!streak` - Voir votre série",
            inline=False
        )
        
        embed.add_field(
            name="💼 Travail & Missions",
            value="`j!work` - Travailler pour des points\n"
                  "`j!mission` - Missions spéciales\n"
                  "`j!invest <montant>` - Investissements",
            inline=False
        )
        
        embed.add_field(
            name="🏆 Classements",
            value="`j!leaderboard` - Top des plus riches\n"
                  "`j!rank` - Votre classement\n"
                  "`j!compare <user>` - Comparer fortunes",
            inline=False
        )
        
        embed.add_field(
            name="💰 Vos Points Actuels",
            value=f"**{user_points:,} points**",
            inline=True
        )
        
        embed.add_field(
            name="📊 Moyens de Gagner",
            value="🎰 Jeux de casino\n💬 Messages (+0.1 pt)\n🎯 Missions quotidiennes\n💼 Travail régulier",
            inline=True
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="shop", aliases=["boutique", "store"])
    async def shop_help(self, ctx):
        """Aide pour la boutique"""
        embed = discord.Embed(
            title="🛒 Boutique JackBot",
            description="Dépensez vos points pour des récompenses !",
            color=0x9b59b6
        )
        
        embed.add_field(
            name="🛍️ Commandes de Base",
            value="`j!shop` - Voir tous les articles\n"
                  "`j!buy <item>` - Acheter un article\n"
                  "`j!inventory` - Votre inventaire",
            inline=False
        )
        
        embed.add_field(
            name="🏷️ Rôles Spéciaux",
            value="👑 **VIP** - 10,000 pts\n"
                  "💎 **Premium** - 25,000 pts\n"
                  "🔥 **Legend** - 50,000 pts\n"
                  "🎭 **Parrain Mafia** - 75,000 pts",
            inline=True
        )
        
        embed.add_field(
            name="🤖 Personnalisation Bot",
            value="🖼️ **Avatar Changer** - 5,000 pts\n"
                  "🏷️ **Name Changer** - 7,500 pts\n"
                  "🎮 **Custom Status** - 3,500 pts\n"
                  "⭐ **Premium Status** - 6,000 pts",
            inline=True
        )
        
        embed.add_field(
            name="🎪 Cosmétiques",
            value="🎨 Couleurs de profil personnalisées\n"
                  "🏆 Titres exclusifs\n"
                  "✨ Effets spéciaux\n"
                  "🎭 Emojis personnalisés",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="botcmds", aliases=["botcommands"])
    async def management_help(self, ctx):
        """Affiche les commandes de gestion du bot"""
        embed = discord.Embed(
            title="🤖 Commandes de Gestion du Bot",
            description="Personnalisez l'apparence du bot avec vos points !",
            color=0x3498db
        )
        
        embed.add_field(
            name="🖼️ Gestion Avatar",
            value="`j!avatar <URL>` - Changer l'avatar (5,000 pts)\n"
                  "`j!avatar` + image jointe - Avec fichier\n"
                  "`j!reset_avatar` - Remettre par défaut (1,000 pts)",
            inline=False
        )
        
        embed.add_field(
            name="🏷️ Gestion Nom", 
            value="`j!name <nouveau_nom>` - Changer le nom (7,500 pts)\n"
                  "⚠️ Limité par les restrictions Discord",
            inline=False
        )
        
        embed.add_field(
            name="🎮 Gestion Statut",
            value="`j!status <type> <texte>` - Changer le statut\n"
                  "• **Standard**: 3,500 pts (6h)\n"
                  "• **Premium**: 6,000 pts (12h)\n"
                  "`j!reset_status` - Reset statut (500 pts)\n"
                  "`j!presets` - Statuts pré-définis populaires",
            inline=False
        )
        
        embed.add_field(
            name="📊 Informations",
            value="`j!bot_status` - Voir toutes les modifications actives\n"
                  "Affiche avatar, nom et statut temporaires",
            inline=False
        )
        
        embed.add_field(
            name="🎮 Types de Statut",
            value="🎮 `playing` - Joue à...\n🎵 `listening` - Écoute...\n"
                  "📺 `watching` - Regarde...\n🔴 `streaming` - Streame...\n"
                  "🏆 `competing` - Participe à...",
            inline=True
        )
        
        embed.add_field(
            name="💡 Exemples",
            value="```\nj!status playing Minecraft\nj!status listening to Spotify\nj!status watching Netflix\n```",
            inline=True
        )
        
        embed.add_field(
            name="⏰ Durées",
            value="• Toutes les modifications sont **temporaires**\n"
                  "• Restoration automatique après expiration\n"
                  "• Surveillance continue en arrière-plan",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="presets", aliases=["status_presets"])
    async def status_presets(self, ctx):
        """Affiche des statuts pré-définis populaires"""
        embed = discord.Embed(
            title="🎮 Statuts Pré-définis Populaires",
            description="Copiez-collez ces commandes populaires :",
            color=0x3498db
        )
        
        embed.add_field(
            name="🎮 Gaming",
            value="`j!status playing Minecraft`\n"
                  "`j!status playing Among Us`\n"
                  "`j!status playing Fortnite`\n"
                  "`j!status competing in Ranked`",
            inline=True
        )
        
        embed.add_field(
            name="🎵 Musique",
            value="`j!status listening to Spotify`\n"
                  "`j!status listening to Lo-Fi Hip Hop`\n"
                  "`j!status listening to your requests`\n"
                  "`j!status listening to the radio`",
            inline=True
        )
        
        embed.add_field(
            name="📺 Divertissement",
            value="`j!status watching Netflix`\n"
                  "`j!status watching YouTube`\n"
                  "`j!status watching the server`\n"
                  "`j!status watching movies`",
            inline=True
        )
        
        embed.add_field(
            name="🤖 Bot",
            value="`j!status playing with commands`\n"
                  "`j!status watching over the server`\n"
                  "`j!status listening to your problems`\n"
                  "`j!status competing for your attention`",
            inline=True
        )
        
        embed.add_field(
            name="🔥 Populaires",
            value="`j!status playing Casino Games`\n"
                  "`j!status watching Discord`\n"
                  "`j!status listening to your bets`\n"
                  "`j!status streaming Just Chatting`",
            inline=True
        )
        
        embed.add_field(
            name="😂 Fun",
            value="`j!status playing hide and seek`\n"
                  "`j!status watching paint dry`\n"
                  "`j!status listening to silence`\n"
                  "`j!status competing with humans`",
            inline=True
        )
        
        embed.set_footer(
            text="💰 Prix: Standard (6h) = 3,500 pts • Premium (12h) = 6,000 pts"
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="mod", aliases=["moderation"])
    async def moderation_help(self, ctx):
        """Aide pour les commandes de modération"""
        embed = discord.Embed(
            title="🛠️ Commandes de Modération",
            description="Outils pour gérer votre serveur",
            color=0xe74c3c
        )
        
        embed.add_field(
            name="👮 Actions de Modération",
            value="`j!kick <user>` - Expulser un membre\n"
                  "`j!ban <user>` - Bannir un membre\n"
                  "`j!mute <user>` - Rendre muet\n"
                  "`j!warn <user>` - Avertir un membre",
            inline=False
        )
        
        embed.add_field(
            name="🧹 Nettoyage",
            value="`j!clear <nombre>` - Supprimer des messages\n"
                  "`j!purge <user>` - Nettoyer les messages d'un user\n"
                  "`j!clean` - Nettoyer les messages du bot",
            inline=False
        )
        
        embed.add_field(
            name="🔒 Gestion Salon",
            value="`j!lock` - Verrouiller le salon\n"
                  "`j!unlock` - Déverrouiller le salon\n"
                  "`j!slowmode <temps>` - Mode lent",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="utils", aliases=["utilitaires", "utilities"])
    async def utilities_help(self, ctx):
        """Aide pour les outils utilitaires"""
        embed = discord.Embed(
            title="🔧 Outils Utilitaires",
            description="Commandes pratiques pour tous",
            color=0x34495e
        )
        
        embed.add_field(
            name="👤 Informations Utilisateur",
            value="`j!userinfo <user>` - Infos sur un membre\n"
                  "`j!avatar <user>` - Avatar d'un user\n"
                  "`j!profile` - Votre profil complet",
            inline=False
        )
        
        embed.add_field(
            name="🖥️ Informations Serveur",
            value="`j!serverinfo` - Infos du serveur\n"
                  "`j!membercount` - Nombre de membres\n"
                  "`j!channels` - Liste des salons",
            inline=False
        )
        
        embed.add_field(
            name="⏰ Temps & Date",
            value="`j!time` - Heure actuelle\n"
                  "`j!uptime` - Temps de fonctionnement\n"
                  "`j!ping` - Latence du bot",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="fun", aliases=["amusant"])
    async def fun_help(self, ctx):
        """Aide pour les commandes amusantes"""
        embed = discord.Embed(
            title="🎪 Commandes Fun & Divertissement",
            description="Pour s'amuser et rigoler !",
            color=0xf39c12
        )
        
        embed.add_field(
            name="😂 Réactions",
            value="`j!hug <user>` - Faire un câlin\n"
                  "`j!kiss <user>` - Faire un bisou\n"
                  "`j!slap <user>` - Gifle amicale\n"
                  "`j!pat <user>` - Caresser la tête",
            inline=False
        )
        
        embed.add_field(
            name="🎲 Jeux Rapides",
            value="`j!8ball <question>` - Boule magique\n"
                  "`j!flip` - Pile ou face\n"
                  "`j!roll` - Lancer de dé\n"
                  "`j!choose <choix1> <choix2>` - Choisir",
            inline=False
        )
        
        embed.add_field(
            name="🤖 IA Fun",
            value="`j!joke` - Blague aléatoire\n"
                  "`j!quote` - Citation inspirante\n"
                  "`j!fact` - Fait aléatoire\n"
                  "`j!meme` - Meme du jour",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="stats", aliases=["statistiques"])
    async def stats_help(self, ctx):
        """Aide pour les statistiques"""
        embed = discord.Embed(
            title="📊 Statistiques & Données",
            description="Suivez vos performances !",
            color=0x1abc9c
        )
        
        embed.add_field(
            name="🎰 Stats Casino",
            value="`j!casinostats` - Vos stats de jeux\n"
                  "`j!gamestats <jeu>` - Stats d'un jeu spécifique\n"
                  "`j!winrate` - Taux de victoire",
            inline=False
        )
        
        embed.add_field(
            name="🏆 Classements", 
            value="`j!leaderboard` - Top général\n"
                  "`j!leaderboard casino` - Top casino\n"
                  "`j!rank` - Votre position",
            inline=False
        )
        
        embed.add_field(
            name="📈 Progression",
            value="`j!progress` - Votre évolution\n"
                  "`j!history` - Historique des gains\n"
                  "`j!achievements` - Vos succès",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="info", aliases=["botinfo", "about"])
    async def info(self, ctx):
        """Informations sur le bot"""
        embed = discord.Embed(
            title="🤖 JackBot - Informations",
            description="Le bot casino et divertissement ultime !",
            color=0x9b59b6
        )
        
        embed.add_field(
            name="📊 Statistiques",
            value=f"🏠 **Serveurs :** {len(self.bot.guilds)}\n"
                  f"👥 **Utilisateurs :** {len(set(self.bot.get_all_members()))}\n"
                  f"💬 **Commandes :** 50+",
            inline=True
        )
        
        embed.add_field(
            name="⚡ Performance",
            value=f"🏓 **Ping :** {round(self.bot.latency * 1000)}ms\n"
                  f"🐍 **Python :** {discord.__version__}\n"
                  f"🔥 **Uptime :** En ligne",
            inline=True
        )
        
        embed.add_field(
            name="🎮 Fonctionnalités",
            value="🎰 **20+ jeux** de casino\n"
                  "💰 **Économie** complète\n"
                  "🛒 **Boutique** interactive\n"
                  "🤖 **Personnalisation** du bot",
            inline=False
        )
        
        embed.add_field(
            name="🔗 Liens Utiles",
            value="[Support Server](https://discord.gg/ton-serveur)\n"
                  "[Code Source](https://github.com/ton-repo)\n"
                  "[Documentation](https://ton-docs.com)",
            inline=False
        )
        
        embed.set_footer(
            text="Développé avec ❤️ pour Discord",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="commands", aliases=["cmdlist"])
    async def all_commands(self, ctx):
        """Liste rapide de toutes les commandes"""
        embed = discord.Embed(
            title="📋 Liste Rapide des Commandes",
            description="Toutes les commandes disponibles",
            color=0x95a5a6
        )
        
        commands_list = [
            "**🎰 Casino:** slots, blackjack, roulette, poker, crash, limbo",
            "**💰 Économie:** balance, daily, weekly, pay, work, invest",
            "**🛒 Shop:** shop, buy, inventory",
            "**🤖 Bot:** avatar, name, status, bot_status",
            "**🛠️ Mod:** kick, ban, mute, clear, lock",
            "**🔧 Utils:** userinfo, serverinfo, ping, time",
            "**🎪 Fun:** 8ball, hug, joke, meme, flip",
            "**📊 Stats:** casinostats, leaderboard, rank, progress"
        ]
        
        embed.description = "\n".join(commands_list)
        embed.add_field(
            name="💡 Astuce",
            value="Utilisez `j!help <catégorie>` pour des infos détaillées !",
            inline=False
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))
