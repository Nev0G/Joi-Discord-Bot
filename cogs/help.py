import discord
from discord.ext import commands

class CustomHelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')  # Supprime la commande help par défaut

    @commands.command(name="help", aliases=["h", "aide"])
    async def custom_help(self, ctx, category: str = None):
        """Système d'aide personnalisé"""
        if category is None:
            # Affichage du menu principal
            embed = discord.Embed(
                title="🔮 Centre d'Aide - Menu Principal",
                description="Voici toutes les catégories disponibles :",
                color=0x7289DA
            )
            
            embed.add_field(
                name="🎰 Casino",
                value="`j!help casino` - Tous les jeux du casino",
                inline=False
            )
            embed.add_field(
                name="📊 Stocks",
                value="`j!help stocks` - Système de trading",
                inline=False
            )
            embed.add_field(
                name="🛒 Shop",
                value="`j!help shop` - Boutique et achats",
                inline=False
            )
            embed.add_field(
                name="⚙️ Utilitaires",
                value="`j!help utils` - Commandes utiles",
                inline=False
            )
            embed.add_field(
                name="🎉 Fun",
                value="`j!help fun` - Commandes amusantes",
                inline=False
            )
            
            embed.set_footer(
                text="Utilisez j!help <catégorie> pour plus de détails",
                icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
            )
            
            await ctx.send(embed=embed)
            return
        
        category = category.lower()
        
        if category in ["casino", "c"]:
            await self.casino_help(ctx)
        elif category in ["stocks", "s", "stock"]:
            await self.stocks_help(ctx)
        elif category in ["shop", "boutique"]:
            await self.shop_help(ctx)
        elif category in ["utils", "utilitaires", "u"]:
            await self.utils_help(ctx)
        elif category in ["fun", "f"]:
            await self.fun_help(ctx)
        else:
            await ctx.send("❌ Catégorie inconnue ! Utilisez `j!help` pour voir toutes les catégories.")

    async def casino_help(self, ctx):
        """Aide détaillée du casino"""
        embed = discord.Embed(
            title="🎰 Casino - Guide Complet",
            description="Bienvenue dans le casino le plus complet de Discord !",
            color=0xFFD700
        )
        
        # Informations générales
        embed.add_field(
            name="💰 Informations Générales",
            value="• Mise minimum: **10 points**\n• Solde de départ: **1,000 points**\n• Bonus quotidien/hebdomadaire disponible",
            inline=False
        )
        
        # Jeux de base
        embed.add_field(
            name="🎲 Jeux de Base",
            value=(
                "`j!slot <mise>` - Machine à sous 🎰\n"
                "`j!coinflip <mise> <pile/face>` - Pile ou face 🪙\n"
                "`j!dice <mise> <1-6>` - Jeu de dés 🎲"
            ),
            inline=False
        )
        
        # Jeux de cartes
        embed.add_field(
            name="🃏 Jeux de Cartes",
            value=(
                "`j!blackjack <mise>` - Blackjack classique\n"
                "• `hit` pour tirer une carte\n"
                "• `stand` pour rester"
            ),
            inline=False
        )
        
        # Jeux de roulette et roue
        embed.add_field(
            name="🎡 Roulette & Roue",
            value=(
                "`j!roulette <mise> <choix>` - Roulette européenne\n"
                "• Choix: rouge/noir, pair/impair, 1-36\n"
                "`j!wheel <mise>` - Roue de la fortune"
            ),
            inline=False
        )
        
        # Jeux avancés
        embed.add_field(
            name="🚀 Jeux Avancés",
            value=(
                "`j!crash <mise>` - Jeu crash avec multiplicateur\n"
                "`j!limbo <mise> <target>` - Target multiplicateur\n"
                "`j!mines <mise> <nb_mines>` - Démineur interactif"
            ),
            inline=False
        )
        
        # Bonus et classement
        embed.add_field(
            name="🎁 Bonus & Classement",
            value=(
                "`j!daily` - Bonus quotidien (500-1000 pts)\n"
                "`j!weekly` - Bonus hebdomadaire (2000-5000 pts)\n"
                "`j!leaderboard` - Top des joueurs"
            ),
            inline=False
        )
        
        # Commandes utiles
        embed.add_field(
            name="📊 Gestion",
            value=(
                "`j!points` ou `j!balance` - Voir son solde\n"
                "`j!casinohelp` - Aide rapide casino"
            ),
            inline=False
        )
        
        embed.set_footer(text="🎰 Jouez de manière responsable !")
        await ctx.send(embed=embed)

    async def stocks_help(self, ctx):
        """Aide du système de stocks"""
        embed = discord.Embed(
            title="📊 Stocks - Guide de Trading",
            description="Système de trading d'actions en temps réel",
            color=0x00FF7F
        )
        
        embed.add_field(
            name="📈 Commandes de Base",
            value=(
                "`j!stocks` - Voir toutes les actions disponibles\n"
                "`j!stock <symbol>` - Info détaillée d'une action\n"
                "`j!portfolio` - Voir votre portefeuille"
            ),
            inline=False
        )
        
        embed.add_field(
            name="💳 Trading",
            value=(
                "`j!buy <symbol> <quantité>` - Acheter des actions\n"
                "`j!sell <symbol> <quantité>` - Vendre des actions\n"
                "`j!sellall <symbol>` - Tout vendre d'une action"
            ),
            inline=False
        )
        
        embed.add_field(
            name="📊 Analyse",
            value=(
                "`j!gainloss` - Gains/pertes totaux\n"
                "`j!marketcap` - Capitalisation du marché\n"
                "`j!trending` - Actions les plus actives"
            ),
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ Informations",
            value="• Prix mis à jour toutes les heures\n• Données de Yahoo Finance\n• Commissions incluses",
            inline=False
        )
        
        await ctx.send(embed=embed)

    async def shop_help(self, ctx):
        """Aide de la boutique"""
        embed = discord.Embed(
            title="🛒 Boutique - Guide d'Achat",
            description="Dépensez vos points dans notre boutique exclusive !",
            color=0xFF1493
        )
        
        embed.add_field(
            name="🛍️ Commandes Boutique",
            value=(
                "`j!shop` - Voir tous les articles\n"
                "`j!buy <item>` - Acheter un article\n"
                "`j!inventory` - Voir vos achats"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🎯 Types d'Articles",
            value=(
                "**🎭 Rôles Exclusifs** - Statut VIP sur le serveur\n"
                "**⚡ Commandes Spéciales** - Pouvoirs uniques\n"
                "**💪 Buffs Temporaires** - Bonus de points\n"
                "**🎪 Fonctions Fun** - Messages anonymes, spam..."
            ),
            inline=False
        )
        
        embed.add_field(
            name="💎 Articles Populaires",
            value=(
                "• **BombDM** (300 pts) - Message DM via bot\n"
                "• **Casino Addict** (10k pts) - Rôle VIP\n"
                "• **Multiplicateur x2** (2k pts) - Double gains 24h\n"
                "• **Voleur de Points** (1.5k pts) - Vol aléatoire"
            ),
            inline=False
        )
        
        await ctx.send(embed=embed)

    async def utils_help(self, ctx):
        """Aide des utilitaires"""
        embed = discord.Embed(
            title="⚙️ Utilitaires - Outils Pratiques",
            description="Commandes utiles pour le serveur",
            color=0x36393F
        )
        
        embed.add_field(
            name="👤 Informations Utilisateur",
            value=(
                "`j!userinfo [@user]` - Info sur un utilisateur\n"
                "`j!avatar [@user]` - Avatar d'un utilisateur\n"
                "`j!profile` - Votre profil complet"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🖥️ Informations Serveur",
            value=(
                "`j!serverinfo` - Info du serveur\n"
                "`j!membercount` - Nombre de membres\n"
                "`j!channels` - Liste des salons"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🔧 Outils",
            value=(
                "`j!ping` - Latence du bot\n"
                "`j!uptime` - Temps de fonctionnement\n"
                "`j!stats` - Statistiques générales"
            ),
            inline=False
        )
        
        await ctx.send(embed=embed)

    async def fun_help(self, ctx):
        """Aide des commandes fun"""
        embed = discord.Embed(
            title="🎉 Fun - Commandes Amusantes",
            description="Commandes pour s'amuser sur le serveur",
            color=0xff69b4
        )
        
        embed.add_field(
            name="🎲 Jeux Simples",
            value=(
                "`j!8ball <question>` - Boule magique\n"
                "`j!choose <choix1> <choix2>` - Choix aléatoire\n"
                "`j!roll <max>` - Dé personnalisé"
            ),
            inline=False
        )
        
        embed.add_field(
            name="😊 Interactions",
            value=(
                "`j!hug [@user]` - Faire un câlin\n"
                "`j!pat [@user]` - Caresser\n"
                "`j!highfive [@user]` - Top là !"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🔮 Générateurs",
            value=(
                "`j!joke` - Blague aléatoire\n"
                "`j!fact` - Fait intéressant\n"
                "`j!quote` - Citation inspirante"
            ),
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="commands", aliases=["cmds"])
    async def all_commands(self, ctx):
        """Liste rapide de toutes les commandes"""
        embed = discord.Embed(
            title="📋 Liste Rapide des Commandes",
            description="Toutes les commandes disponibles par catégorie",
            color=0x7289DA
        )
        
        # Casino (le plus important)
        casino_cmds = (
            "`slot`, `blackjack`, `roulette`, `coinflip`, `dice`, "
            "`crash`, `limbo`, `mines`, `wheel`, `daily`, `weekly`, "
            "`points`, `leaderboard`"
        )
        embed.add_field(name="🎰 Casino", value=casino_cmds, inline=False)
        
        # Autres catégories
        embed.add_field(
            name="📊 Stocks", 
            value="`stocks`, `buy`, `sell`, `portfolio`, `gainloss`", 
            inline=False
        )
        embed.add_field(
            name="🛒 Shop", 
            value="`shop`, `buy`, `inventory`", 
            inline=False
        )
        embed.add_field(
            name="⚙️ Utils", 
            value="`userinfo`, `serverinfo`, `ping`, `avatar`", 
            inline=False
        )
        embed.add_field(
            name="🎉 Fun", 
            value="`8ball`, `choose`, `joke`, `hug`, `pat`", 
            inline=False
        )
        
        embed.set_footer(text="Utilisez j!help <catégorie> pour plus de détails")
        await ctx.send(embed=embed)

    @commands.command(name="quickhelp", aliases=["qh"])
    async def quick_help(self, ctx):
        """Aide ultra-rapide pour commencer"""
        embed = discord.Embed(
            title="⚡ Aide Rapide - Pour Commencer",
            color=0x00FF00
        )
        
        embed.add_field(
            name="🎰 Commencer au Casino",
            value=(
                "1. `j!points` - Voir votre solde (1000 pts de base)\n"
                "2. `j!daily` - Récupérer bonus quotidien\n"
                "3. `j!slot 50` - Jouer aux machines à sous\n"
                "4. `j!casinohelp` - Voir tous les jeux"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🏆 Top Jeux Recommandés",
            value=(
                "• `j!blackjack 100` - Jeu de stratégie\n"
                "• `j!crash 50` - Tension maximale\n"
                "• `j!wheel 75` - Roue de la fortune\n"
                "• `j!mines 100 3` - Démineur palpitant"
            ),
            inline=False
        )
        
        embed.set_footer(text="Tapez j!help pour l'aide complète !")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CustomHelpCommand(bot))
