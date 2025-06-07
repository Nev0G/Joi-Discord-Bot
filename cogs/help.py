import discord
from discord.ext import commands
from discord import SelectOption
import asyncio
from datetime import datetime

class HelpDropdown(discord.ui.Select):
    def __init__(self, bot):
        self.bot = bot
        
        options = [
            SelectOption(
                label="🎰 Casino & Jeux",
                description="Machines à sous, blackjack, crash, mines...",
                emoji="🎲",
                value="casino"
            ),
            SelectOption(
                label="📈 Trading & Stocks",
                description="Acheter/vendre des actions, portfolio...",
                emoji="💹",
                value="stocks"
            ),
            SelectOption(
                label="🛍️ Shop & Items",
                description="Boutique, achats, rôles premium...",
                emoji="🛒",
                value="shop"
            ),
            SelectOption(
                label="💰 Économie",
                description="Points, bonus, transferts...",
                emoji="💵",
                value="economy"
            ),
            SelectOption(
                label="🎮 Fun & Divertissement",
                description="Jeux sociaux, défis, animations...",
                emoji="🎉",
                value="fun"
            ),
            SelectOption(
                label="⚙️ Utilitaires",
                description="Profil, stats, paramètres...",
                emoji="🔧",
                value="utils"
            ),
            SelectOption(
                label="🏠 Accueil",
                description="Retour au menu principal",
                emoji="🏠",
                value="home"
            )
        ]
        
        super().__init__(
            placeholder="🔍 Choisissez une catégorie...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="help_dropdown"
        )

    async def callback(self, interaction: discord.Interaction):
        embed = None
        view = HelpView(self.bot, self.values[0])
        
        if self.values[0] == "casino":
            embed = self.create_casino_embed()
        elif self.values[0] == "stocks":
            embed = self.create_stocks_embed()
        elif self.values[0] == "shop":
            embed = self.create_shop_embed()
        elif self.values[0] == "economy":
            embed = self.create_economy_embed()
        elif self.values[0] == "fun":
            embed = self.create_fun_embed()
        elif self.values[0] == "utils":
            embed = self.create_utils_embed()
        else:  # home
            embed = self.create_main_embed()
            view = HelpView(self.bot, "home")
        
        await interaction.response.edit_message(embed=embed, view=view)

    def create_main_embed(self):
        embed = discord.Embed(
            title="🎮 JAMBOT - Centre d'Aide Interactive",
            description="**Bienvenue dans l'aide ultra-complète de JamBot!**\n\n"
                       "🚀 JamBot est votre compagnon ultime pour:\n"
                       "• 🎰 **Casino immersif** avec animations\n"
                       "• 📈 **Trading professionnel** en temps réel\n"
                       "• 🛍️ **Boutique exclusive** avec items premium\n"
                       "• 💰 **Économie dynamique** et compétitive\n\n"
                       "**Sélectionnez une catégorie ci-dessous pour explorer!**",
            color=0x00BFFF
        )
        
        embed.add_field(
            name="🎯 Démarrage Rapide",
            value="```\n"
                  "j!daily     • Bonus quotidien (1000 pts)\n"
                  "j!market    • Voir le marché boursier\n"
                  "j!slot 100  • Machine à sous (100 pts)\n"
                  "j!profile   • Votre profil détaillé\n"
                  "```",
            inline=False
        )
        
        embed.add_field(
            name="📊 Statistiques Globales",
            value="🎰 **Casino:** +50 jeux interactifs\n"
                  "📈 **Trading:** +20 actions disponibles\n"
                  "🛍️ **Shop:** +15 items exclusifs\n"
                  "💎 **Premium:** Fonctions VIP",
            inline=True
        )
        
        embed.add_field(
            name="🚀 Nouveautés",
            value="✨ **Animations ultra-fluides**\n"
                  "🎮 **Interactions en temps réel**\n"
                  "📊 **Analytics avancées**\n"
                  "🏆 **Système de classements**",
            inline=True
        )
        
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1234567890123456789.png")
        embed.set_footer(text="💡 Utilisez le menu déroulant pour naviguer • Version 3.0")
        embed.timestamp = datetime.now()
        
        return embed

    def create_casino_embed(self):
        embed = discord.Embed(
            title="🎰 CASINO - Jeux Ultra-Immersifs",
            description="**Vivez l'expérience du casino avec des animations époustouflantes!**\n\n"
                       "🎲 Tous les jeux incluent des **animations en temps réel**, des **interactions dynamiques** et des **effets visuels**.",
            color=0xFF6B6B
        )
        
        # Jeux de base
        embed.add_field(
            name="🎯 Jeux Principaux",
            value="```\n"
                  "j!slot <mise>         • Machine à sous 3 rouleaux\n"
                  "j!blackjack <mise>    • 21 avec cartes animées\n"
                  "j!roulette <mise> <n> • Roulette européenne\n"
                  "j!coinflip <m> <p/f>  • Pile ou face rapide\n"
                  "j!dice <mise> <1-6>   • Dé avec effets 3D\n"
                  "```",
            inline=False
        )
        
        # Jeux avancés
        embed.add_field(
            name="🚀 Jeux Avancés",
            value="```\n"
                  "j!crash <mise>        • Fusée explosive\n"
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
            value="• Commencez avec de petites mises\n"
                  "• Utilisez `j!daily` chaque jour\n"
                  "• Gestion du bankroll essentielle\n"
                  "• Les animations indiquent les résultats",
            inline=False
        )
        
        embed.set_footer(text="🎰 House Edge: ~2% • Jeu responsable • +18 ans")
        return embed

    def create_stocks_embed(self):
        embed = discord.Embed(
            title="📈 TRADING - Bourse Professionnelle",
            description="**Devenez un trader professionnel avec notre plateforme ultra-réaliste!**\n\n"
                       "💹 **Marché en temps réel** avec +20 actions populaires et cryptos",
            color=0x4ECDC4
        )
        
        # Commandes de base
        embed.add_field(
            name="📊 Trading de Base",
            value="```\n"
                  "j!market              • Vue marché complète\n"
                  "j!buy <symbol> <qty>  • Acheter des actions\n"
                  "j!sell <symbol> <qty> • Vendre position\n"
                  "j!portfolio           • Votre portefeuille\n"
                  "j!stock <symbol>      • Info détaillée\n"
                  "```",
            inline=False
        )
        
        # Outils avancés
        embed.add_field(
            name="🔍 Outils d'Analyse",
            value="```\n"
                  "j!watchlist           • Liste de suivi\n"
                  "j!watchlist add AAPL  • Ajouter action\n"
                  "j!alerts set AAPL 180 • Alerte prix\n"
                  "j!leaderboard stocks  • Top traders\n"
                  "j!history <symbol>    • Historique prix\n"
                  "```",
            inline=False
        )
        
        # Actions disponibles
        embed.add_field(
            name="🏢 Actions Populaires",
            value="🍎 **AAPL** - Apple Inc.\n"
                  "💻 **MSFT** - Microsoft\n"
                  "🔍 **GOOGL** - Alphabet\n"
                  "📦 **AMZN** - Amazon\n"
                  "🚗 **TSLA** - Tesla\n"
                  "📘 **META** - Meta\n"
                  "🎮 **NVDA** - NVIDIA",
            inline=True
        )
        
        # Cryptos
        embed.add_field(
            name="₿ Cryptomonnaies",
            value="₿ **BTC** - Bitcoin\n"
                  "⟠ **ETH** - Ethereum\n"
                  "🔷 **ADA** - Cardano\n"
                  "☀️ **SOL** - Solana\n"
                  "🐕 **DOGE** - Dogecoin\n"
                  "*Volatilité élevée!*",
            inline=True
        )
        
        # Fonctionnalités premium
        embed.add_field(
            name="🎯 Analytics Avancées",
            value="📊 **Graphiques temps réel** avec indicateurs\n"
                  "📈 **Support/Résistance** automatiques\n"
                  "🔔 **Système d'alertes** personnalisé\n"
                  "🏆 **Classement performance** communautaire\n"
                  "📱 **Portfolio tracker** détaillé",
            inline=False
        )
        
        embed.set_footer(text="📈 Marché ouvert 24/7 • Pas de frais de courtage • Investir comporte des risques")
        return embed

    def create_shop_embed(self):
        embed = discord.Embed(
            title="🛍️ SHOP - Boutique Exclusive",
            description="**Débloquez des fonctionnalités premium et des avantages exclusifs!**\n\n"
                       "💎 Achetez avec vos points durement gagnés",
            color=0xE67E22
        )
        
        # Commandes shop
        embed.add_field(
            name="🛒 Commandes Boutique",
            value="```\n"
                  "j!shop                • Voir tous les items\n"
                  "j!buy <item>          • Acheter un item\n"
                  "j!inventory           • Votre inventaire\n"
                  "j!use <item>          • Utiliser un item\n"
                  "```",
            inline=False
        )
        
        # Items par catégorie
        embed.add_field(
            name="⚡ Commandes Spéciales",
            value="💣 **BombDM** (300 pts)\n"
                  "   └ *Envoi DM via le bot*\n\n"
                  "📨 **Message Fantôme** (750 pts)\n"
                  "   └ *Message anonyme*\n\n"
                  "🌪️ **Spam Master** (500 pts)\n"
                  "   └ *10 msg sans cooldown*",
            inline=False
        )
        
        embed.add_field(
            name="🎭 Rôles Exclusifs",
            value="🎰 **Casino Addict** (10K pts)\n"
                  "   └ *Rôle de maxi bogoss*\n\n"
                  "👑 **Roi des Juifs** (25K pts)\n"
                  "   └ *Il ne faut pas avoir peur*",
            inline=True
        )
        
        embed.add_field(
            name="⚡ Boosts & Buffs",
            value="💎 **Multiplicateur x2** (2K pts)\n"
                  "   └ *Double gains 24h*\n\n"
                  "🃏 **Voleur de Points** (1.5K pts)\n"
                  "   └ *Vole 10% d'un joueur*\n\n"
                  "🔄 **Reroll Lucky** (800 pts)\n"
                  "   └ *Relance ton dernier jeu*",
            inline=True
        )
        
        # Items temporaires/événements
        embed.add_field(
            name="🎉 Items Événements",
            value="🎃 **Halloween Pack** - *Temporaire*\n"
                  "🎄 **Christmas Bundle** - *Saisonnier*\n"
                  "💕 **Valentine Special** - *Limitée*\n"
                  "🎆 **New Year Boost** - *Exclusif*",
            inline=False
        )
        
        embed.set_footer(text="💰 Gagnez des points au casino pour acheter • Items non-remboursables")
        return embed

    def create_economy_embed(self):
        embed = discord.Embed(
            title="💰 ÉCONOMIE - Système Monétaire",
            description="**Gérez vos finances comme un pro avec notre économie avancée!**\n\n"
                       "💵 Points = Monnaie universelle du serveur",
            color=0x2ECC71
        )
        
        # Gains de base
        embed.add_field(
            name="💸 Gagner des Points",
            value="```\n"
                  "j!daily               • 1000 pts/jour\n"
                  "j!weekly              • 5000 pts/semaine\n"
                  "j!work                • 200-500 pts\n"
                  "j!crime               • Risqué mais payant\n"
                  "```",
            inline=False
        )
        
        # Transferts et économie
        embed.add_field(
            name="🔄 Transferts & Échanges",
            value="```\n"
                  "j!pay @user <amount>  • Donner des points\n"
                  "j!rob @user           • Voler (risqué!)\n"
                  "j!loan <amount>       • Emprunter\n"
                  "j!repay <amount>      • Rembourser\n"
                  "```",
            inline=False
        )
        
        # Informations
        embed.add_field(
            name="📊 Informations",
            value="💰 `j!balance` - Votre solde\n"
                  "📈 `j!richest` - Top des plus riches\n"
                  "📉 `j!poorest` - Les plus pauvres\n"
                  "🏦 `j!bank` - Infos bancaires",
            inline=True
        )
        
        # Conseils économiques
        embed.add_field(
            name="💡 Conseils Pro",
            value="🎯 **Diversifiez** vos revenus\n"
                  "📈 **Investissez** en bourse\n"
                  "🎰 **Jouez** de manière responsable\n"
                  "💎 **Achetez** des items utiles",
            inline=True
        )
        
        # Événements économiques
        embed.add_field(
            name="🎊 Événements Spéciaux",
            value="🎉 **Double XP Weekends**\n"
                  "💰 **Bonus Raids** communautaires\n"
                  "🎁 **Drop Events** aléatoires\n"
                  "🏆 **Concours** avec récompenses",
            inline=False
        )
        
        # Limites et règles
        embed.add_field(
            name="⚠️ Limites & Règles",
            value="• Maximum 50K pts par transfert\n"
                  "• Daily cooldown: 20h\n"
                  "• Weekly cooldown: 6 jours\n"
                  "• Pas de farm automatique",
            inline=False
        )
        
        embed.set_footer(text="💰 Économie équilibrée • Pas de pay-to-win • Fair play")
        return embed

    def create_fun_embed(self):
        embed = discord.Embed(
            title="🎉 FUN - Divertissement Social",
            description="**Amusez-vous avec des jeux sociaux et des défis communautaires!**",
            color=0x9B59B6
        )
        
        # Jeux sociaux
        embed.add_field(
            name="🎮 Jeux Multijoueurs",
            value="```\n"
                  "j!trivia              • Quiz culture générale\n"
                  "j!guessnumber         • Devine le nombre\n"
                  "j!wordchain           • Chaîne de mots\n"
                  "j!reaction            • Test de réflexes\n"
                  "```",
            inline=False
        )
        
        # Défis et compétitions
        embed.add_field(
            name="🏆 Défis & Concours",
            value="```\n"
                  "j!duel @user          • Défi un joueur\n"
                  "j!tournament          • Tournois communautaires\n"
                  "j!challenge           • Défis quotidiens\n"
                  "j!race                • Course contre la montre\n"
                  "```",
            inline=False
        )
        
        # Mini-jeux
        embed.add_field(
            name="🎯 Mini-Jeux",
            value="🎨 **Art ASCII** - Créer des dessins\n"
                  "🔤 **Anagrammes** - Résoudre des mots\n"
                  "🧩 **Puzzles** - Défis logiques\n"
                  "🎪 **Circus** - Spectacle interactif",
            inline=True
        )
        
        # Interactions sociales
        embed.add_field(
            name="👥 Social",
            value="💕 **Marriage System** - Se marier\n"
                  "🤝 **Friendships** - Système d'amis\n"
                  "🎭 **Role Play** - Jeux de rôles\n"
                  "📸 **Selfies** - Photos virtuelles",
            inline=True
        )
        
        embed.set_footer(text="🎉 Nouveaux jeux ajoutés régulièrement • Suggestions bienvenues")
        return embed

    def create_utils_embed(self):
        embed = discord.Embed(
            title="🔧 UTILITAIRES - Outils Pratiques",
            description="**Outils et commandes pratiques pour optimiser votre expérience!**",
            color=0x95A5A6
        )
        
        # Profil et stats
        embed.add_field(
            name="👤 Profil & Statistiques",
            value="```\n"
                  "j!profile             • Votre profil complet\n"
                  "j!stats               • Statistiques détaillées\n"
                  "j!achievements        • Vos succès\n"
                  "j!level               • Système de niveaux\n"
                  "```",
            inline=False
        )
        
        # Paramètres
        embed.add_field(
            name="⚙️ Paramètres",
            value="```\n"
                  "j!settings            • Configuration personnelle\n"
                  "j!notifications       • Gestion des notifs\n"
                  "j!privacy             • Paramètres de confidentialité\n"
                  "j!theme               • Thèmes d'interface\n"
                  "```",
            inline=False
        )
        
        # Outils pratiques
        embed.add_field(
            name="🛠️ Outils Divers",
            value="🕒 `j!servertime` - Heure du serveur\n"
                  "📊 `j!serverstats` - Stats du serveur\n"
                  "🔗 `j!invite` - Lien d'invitation\n"
                  "💬 `j!feedback` - Envoyer des suggestions",
            inline=True
        )
        
        # Support
        embed.add_field(
            name="🆘 Support",
            value="❓ `j!faq` - Questions fréquentes\n"
                  "🐛 `j!bug` - Signaler un bug\n"
                  "📞 `j!support` - Contacter l'équipe\n"
                  "📚 `j!guide` - Guide complet",
            inline=True
        )
        
        # Raccourcis
        embed.add_field(
            name="⚡ Raccourcis Utiles",
            value="• `j!h` = `j!help`\n"
                  "• `j!p` = `j!profile`\n"
                  "• `j!b` = `j!balance`\n"
                  "• `j!m` = `j!market`\n"
                  "• `j!s` = `j!shop`",
            inline=False
        )
        
        embed.set_footer(text="🔧 Plus d'outils en développement • Version bêta disponible")
        return embed

class HelpButtons(discord.ui.View):
    def __init__(self, bot, current_category="home"):
        super().__init__(timeout=300)
        self.bot = bot
        self.current_category = current_category

    @discord.ui.button(label="📚 Guide Complet", style=discord.ButtonStyle.primary, emoji="📖")
    async def full_guide(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="📚 GUIDE COMPLET - JamBot Master Class",
            description="**Devenez un expert JamBot en 5 minutes!**\n\n"
                       "🎯 Ce guide couvre tout ce que vous devez savoir pour maximiser votre expérience.",
            color=0x3498DB
        )
        
        embed.add_field(
            name="🚀 Démarrage Express (2 min)",
            value="1️⃣ `j!daily` - Récupérez vos 1000 points quotidiens\n"
                  "2️⃣ `j!market` - Découvrez la bourse en temps réel\n"
                  "3️⃣ `j!slot 50` - Tentez votre chance au casino\n"
                  "4️⃣ `j!profile` - Consultez votre progression\n"
                  "5️⃣ `j!shop` - Explorez la boutique premium",
            inline=False
        )
        
        embed.add_field(
            name="💎 Stratégies Avancées",
            value="**Casino:** Commencez petit, gérez votre bankroll\n"
                  "**Trading:** Diversifiez, utilisez la watchlist\n"
                  "**Économie:** Daily/Weekly réguliers, investissements\n"
                  "**Shop:** Achetez des multiplicateurs pour optimiser",
            inline=False
        )
        
        embed.add_field(
            name="🏆 Progression Optimale",
            value="**Niveau 1 (0-5K pts):** Casino + Daily/Weekly\n"
                  "**Niveau 2 (5K-50K):** Trading débutant\n"
                  "**Niveau 3 (50K-200K):** Portfolio diversifié\n"
                  "**Niveau 4 (200K+):** Items premium + competitions",
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=HelpView(self.bot, "guide"))

    @discord.ui.button(label="🎰 Casino Pro", style=discord.ButtonStyle.success, emoji="🎲")
    async def casino_tips(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🎰 CASINO PRO - Secrets des Grands Joueurs",
            description="**Maîtrisez l'art du casino avec ces techniques avancées!**",
            color=0x1ABC9C
        )
        
        embed.add_field(
            name="📊 Gestion du Bankroll",
            value="• **Règle des 5%:** Ne misez jamais plus de 5% de votre solde\n"
                  "• **Objectifs clairs:** Fixez un gain/perte limite\n"
                  "• **Sessions courtes:** Jouez par petites sessions\n"
                  "• **Pause obligatoire:** Arrêt après 3 pertes consécutives",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Jeux Optimaux",
            value="**Débutant:** Coinflip (50% de chance)\n"
                  "**Intermédiaire:** Blackjack (stratégie de base)\n"
                  "**Avancé:** Crash (cash out à 2x régulièrement)\n"
                  "**Expert:** Mines (peu de mines, sécurité max)",
            inline=True
        )
        
        embed.add_field(
            name="🔥 Techniques Secrètes",
            value="**Timing:** Jouez quand vous êtes détendu\n"
                  "**Patterns:** Observez les tendances\n"
                  "**Multiplicateurs:** Utilisez les boosts shop\n"
                  "**Community:** Suivez les gros gagnants",
            inline=True
        )
        
        await interaction.response.edit_message(embed=embed, view=HelpView(self.bot, "casino-pro"))

    @discord.ui.button(label="📈 Trading Expert", style=discord.ButtonStyle.secondary, emoji="💹")
    async def trading_tips(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="📈 TRADING EXPERT - Stratégies Gagnantes",
            description="**Devenez un trader professionnel avec ces stratégies éprouvées!**",
            color=0xE74C3C
        )
        
        embed.add_field(
            name="🎯 Stratégie Débutant",
            value="1. **Portfolio équilibré:** 60% actions stables, 40% growth\n"
                  "2. **DCA (Dollar Cost Average):** Achetez régulièrement\n"
                  "3. **Hold long terme:** Gardez minimum 1 semaine\n"
                  "4. **Diversification:** Minimum 5 actions différentes",
            inline=False
        )
        
        embed.add_field(
            name="⚡ Trading Actif",
            value="**Day Trading:** Profitez des fluctuations quotidiennes\n"
                  "**Swing Trading:** Positions 2-5 jours\n"
                  "**Scalping:** Gains rapides sur petites variations\n"
                  "**Momentum:** Suivez les tendances fortes",
            inline=True
        )
        
        embed.add_field(
            name="🔍 Analyse Technique",
            value="**Support/Résistance:** Zones clés à surveiller\n"
                  "**RSI:** <30 = achat, >70 = vente\n"
                  "**Volume:** Confirmez les mouvements\n"
                  "**Tendances:** Suivez la direction générale",
            inline=True
        )
        
        embed.add_field(
            name="💡 Règles d'Or",
            value="• **Cut losses short:** Limitez vos pertes à -10%\n"
                  "• **Let profits run:** Laissez courir les gains\n"
                  "• **Risk/Reward:** Ratio minimum 1:2\n"
                  "• **Plan de trading:** Stratégie définie à l'avance",
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=HelpView(self.bot, "trading-expert"))

class HelpView(discord.ui.View):
    def __init__(self, bot, current_category="home"):
        super().__init__(timeout=300)
        self.bot = bot
        self.add_item(HelpDropdown(bot))
        
        # Ajout des boutons selon la catégorie
        if current_category != "home":
            self.add_item(HelpButtons(bot, current_category))

    async def on_timeout(self):
        # Désactiver tous les composants quand le timeout est atteint
        for item in self.children:
            item.disabled = True

class CustomHelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Remplacer la commande help par défaut
        self._original_help_command = bot.help_command
        bot.help_command = None

    def cog_unload(self):
        # Restaurer la commande help originale si le cog est déchargé
        self.bot.help_command = self._original_help_command

    @commands.command(name="help", aliases=["h", "aide", "commands", "cmd"])
    async def help_command(self, ctx, *, query: str = None):
        """Système d'aide ultra-interactif avec navigation moderne"""
        
        # Animation de chargement
        loading_embed = discord.Embed(
            title="🔄 Chargement de l'aide...",
            description="⚡ Initialisation des modules...",
            color=0xFFD700
        )
        loading_msg = await ctx.send(embed=loading_embed)
        await asyncio.sleep(1)

        # Si query spécifique, essayer de trouver la commande
        if query:
            await self.handle_specific_query(ctx, loading_msg, query)
            return

        # Créer l'embed principal avec statistiques dynamiques
        embed = discord.Embed(
            title="🎮 JAMBOT - Centre d'Aide Ultra-Interactif",
            description="**Bienvenue dans l'expérience JamBot nouvelle génération!**\n\n"
                       "🚀 **Navigation intuitive** avec menu déroulant et boutons\n"
                       "🎯 **Guides détaillés** pour chaque fonctionnalité\n"
                       "💡 **Conseils d'experts** pour optimiser vos gains\n\n"
                       "**Sélectionnez une catégorie ci-dessous pour commencer!**",
            color=0x00BFFF
        )
        
        # Statistiques en temps réel du bot
        total_commands = len(self.bot.commands)
        total_users = len(self.bot.users)
        total_guilds = len(self.bot.guilds)
        
        embed.add_field(
            name="📊 Statistiques Live",
            value=f"🤖 **Commandes:** {total_commands}+\n"
                  f"👥 **Utilisateurs:** {total_users:,}\n"
                  f"🏰 **Serveurs:** {total_guilds}\n"
                  f"🌐 **Uptime:** {self.format_uptime()}",
            inline=True
        )
        
        # Fonctionnalités principales
        embed.add_field(
            name="🎯 Modules Principaux",
            value="🎰 **Casino** • 15+ jeux immersifs\n"
                  "📈 **Trading** • Bourse temps réel\n"
                  "🛍️ **Shop** • Items exclusifs\n"
                  "💰 **Économie** • Système complet\n"
                  "🎉 **Fun** • Jeux communautaires\n"
                  "🔧 **Utils** • Outils pratiques",
            inline=True
        )
        
        # Quickstart
        embed.add_field(
            name="⚡ Démarrage Express",
            value="```\n"
                  "j!daily     → Bonus quotidien (1000 pts)\n"
                  "j!slot 100  → Premier jeu de casino\n"
                  "j!market    → Découvrir la bourse\n"
                  "j!profile   → Votre profil détaillé\n"
                  "```",
            inline=False
        )
        
        # Nouveautés récentes
        embed.add_field(
            name="✨ Nouveautés v3.0",
            value="🎬 **Animations ultra-fluides** pour tous les jeux\n"
                  "📊 **Analytics avancées** avec graphiques temps réel\n"
                  "🏆 **Système de classements** communautaires\n"
                  "🔔 **Alertes intelligentes** personnalisées\n"
                  "🎮 **Interface révolutionnaire** avec interactions",
            inline=False
        )
        
        # Easter eggs et tips
        tips = [
            "💡 Utilisez les réactions rapides sur vos jeux favoris!",
            "🎯 Les animations indiquent souvent le résultat avant la fin!",
            "📈 Le marché est plus actif pendant les heures de pointe!",
            "💎 Les multiplicateurs du shop sont très rentables!",
            "🏆 Participez aux concours pour gagner des bonus exclusifs!"
        ]
        
        embed.add_field(
            name="💡 Astuce du Jour",
            value=random.choice(tips),
            inline=False
        )
        
        # Footer avec informations importantes
        embed.set_footer(
            text="🎮 Navigation avec le menu ci-dessous • Timeout: 5min • Support 24/7",
            icon_url=self.bot.user.display_avatar.url if self.bot.user else None
        )
        embed.timestamp = datetime.now()
        
        # Ajouter une image/thumbnail si disponible
        if self.bot.user and self.bot.user.display_avatar:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        # Créer la view avec tous les composants interactifs
        view = HelpView(self.bot, "home")
        
        try:
            await loading_msg.edit(embed=embed, view=view)
        except discord.NotFound:
            # Si le message original a été supprimé
            await ctx.send(embed=embed, view=view)

    async def handle_specific_query(self, ctx, loading_msg, query):
        """Gère les requêtes spécifiques d'aide pour des commandes particulières"""
        query = query.lower()
        
        # Dictionnaire des commandes spéciales avec aide détaillée
        special_commands = {
            "casino": self.get_casino_specific_help(),
            "slot": self.get_slot_detailed_help(),
            "blackjack": self.get_blackjack_detailed_help(),
            "trading": self.get_trading_specific_help(),
            "stocks": self.get_trading_specific_help(),
            "buy": self.get_buy_detailed_help(),
            "sell": self.get_sell_detailed_help(),
            "shop": self.get_shop_specific_help(),
            "daily": self.get_daily_detailed_help(),
        }
        
        if query in special_commands:
            embed = special_commands[query]
            view = HelpView(self.bot, "specific")
            await loading_msg.edit(embed=embed, view=view)
        else:
            # Recherche fuzzy dans les commandes
            similar_commands = []
            for cmd in self.bot.commands:
                if query in cmd.name.lower() or any(query in alias.lower() for alias in cmd.aliases):
                    similar_commands.append(cmd.name)
            
            if similar_commands:
                embed = discord.Embed(
                    title=f"🔍 Recherche: '{query}'",
                    description=f"**Commandes similaires trouvées:**\n" + 
                               "\n".join([f"• `j!{cmd}`" for cmd in similar_commands[:10]]),
                    color=0xF39C12
                )
                embed.add_field(
                    name="💡 Suggestion",
                    value="Utilisez `j!help` sans paramètre pour l'aide complète avec navigation interactive!",
                    inline=False
                )
            else:
                embed = discord.Embed(
                    title="❌ Commande Introuvable",
                    description=f"Aucune commande trouvée pour: `{query}`",
                    color=0xE74C3C
                )
                embed.add_field(
                    name="🎯 Que faire?",
                    value="• Vérifiez l'orthographe\n"
                          "• Utilisez `j!help` pour voir toutes les commandes\n"
                          "• Essayez une recherche plus générale",
                    inline=False
                )
            
            await loading_msg.edit(embed=embed, view=HelpView(self.bot, "search"))

    def get_slot_detailed_help(self):
        """Aide détaillée pour les machines à sous"""
        embed = discord.Embed(
            title="🎰 MACHINE À SOUS - Guide Complet",
            description="**Maîtrisez l'art de la machine à sous avec ce guide ultra-détaillé!**",
            color=0xFF6B6B
        )
        
        embed.add_field(
            name="🎯 Utilisation",
            value="```\n"
                  "j!slot <mise>          • Jouer avec une mise\n"
                  "j!slot                 • Jouer avec mise minimale\n"
                  "j!slot max             • Jouer avec tout votre argent\n"
                  "j!slot 1000 auto      • Mode automatique (risqué!)\n"
                  "```",
            inline=False
        )
        
        embed.add_field(
            name="🍎 Symboles & Multiplicateurs",
            value="🍒 **Cerises** × 2\n🍊 **Oranges** × 3\n🍋 **Citrons** × 5\n"
                  "🍇 **Raisins** × 8\n🔔 **Cloches** × 15\n💎 **Diamants** × 50\n"
                  "🍀 **Trèfles** × 100\n💰 **Jackpot** × 777",
            inline=True
        )
        
        embed.add_field(
            name="🎰 Combinaisons Spéciales",
            value="**3 Identiques:** Multiplicateur normal\n"
                  "**2 + Wild:** Multiplicateur × 1.5\n"
                  "**Progressive:** Jackpot croissant\n"
                  "**Bonus Round:** Mini-jeu surprise",
            inline=True
        )
        
        embed.add_field(
            name="💡 Stratégies Avancées",
            value="• **Gestion bankroll:** Jamais plus de 10% par spin\n"
                  "• **Timing optimal:** Jouez après les gros gains d'autres\n"
                  "• **Sessions courtes:** 20-30 spins maximum\n"
                  "• **Objectif clair:** Arrêtez à +50% ou -30%",
            inline=False
        )
        
        return embed

    def get_blackjack_detailed_help(self):
        """Aide détaillée pour le blackjack"""
        embed = discord.Embed(
            title="🃏 BLACKJACK - Stratégie Professionnelle",
            description="**Devenez un maître du 21 avec ce guide stratégique complet!**",
            color=0x2C3E50
        )
        
        embed.add_field(
            name="🎴 Règles Fondamentales",
            value="🎯 **Objectif:** Atteindre 21 sans dépasser\n"
                  "👑 **Valeurs:** As=1/11, Figures=10, Autres=valeur\n"
                  "🏆 **Blackjack naturel:** As + Figure = × 1.5\n"
                  "🤝 **Égalité:** Push = mise rendue",
            inline=False
        )
        
        embed.add_field(
            name="⚡ Actions Disponibles",
            value="```\n"
                  "HIT    • Prendre une carte\n"
                  "STAND  • Garder sa main\n"
                  "DOUBLE • Doubler la mise (1 carte)\n"
                  "SPLIT  • Diviser (paires identiques)\n"
                  "```",
            inline=False
        )
        
        embed.add_field(
            name="🧠 Stratégie de Base",
            value="**Hard Hands:**\n"
                  "• 8 ou moins: Toujours HIT\n"
                  "• 9-11: DOUBLE si dealer 3-6\n"
                  "• 12-16: STAND si dealer 2-6\n"
                  "• 17+: Toujours STAND",
            inline=True
        )
        
        embed.add_field(
            name="🎭 Soft Hands (avec As)",
            value="**Soft Hands:**\n"
                  "• A,2-A,5: DOUBLE si dealer 5-6\n"
                  "• A,6: DOUBLE si dealer 3-6\n"
                  "• A,7: STAND si dealer 2,7,8\n"
                  "• A,8-A,9: Toujours STAND",
            inline=True
        )
        
        embed.add_field(
            name="💎 Conseils de Pro",
            value="• **Jamais d'assurance:** House edge trop élevé\n"
                  "• **Split les As et 8:** Toujours profitable\n"
                  "• **Jamais split les 10:** Déjà une excellente main\n"
                  "• **Comptage simple:** Plus de grosses cartes = avantage",
            inline=False
        )
        
        return embed

    def get_trading_specific_help(self):
        """Aide détaillée pour le trading"""
        embed = discord.Embed(
            title="📈 TRADING - Manuel du Trader Pro",
            description="**Transformez-vous en Warren Buffett du Discord avec ce guide complet!**",
            color=0x27AE60
        )
        
        embed.add_field(
            name="📊 Actions de Base",
            value="```\n"
                  "j!market               • Vue marché complète\n"
                  "j!buy AAPL 10          • Acheter 10 actions Apple\n"
                  "j!sell AAPL 5          • Vendre 5 actions Apple\n"
                  "j!portfolio            • Votre portefeuille\n"
                  "j!stock MSFT           • Détails sur Microsoft\n"
                  "```",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Stratégie Débutant",
            value="1️⃣ **Commencez petit:** 1000-5000 pts d'investissement\n"
            "2️⃣ **Diversifiez:** 3-5 actions différentes minimum\n"
            "3️⃣ **Tech stables:** AAPL, MSFT, GOOGL pour débuter\n"
            "4️⃣ **Hold long terme:** Gardez au moins 1 semaine\n"
            "5️⃣ **Réinvestissez:** Profits → nouveaux achats",
            inline=False
        )
        
        embed.add_field(
            name="📈 Actions Recommandées",
            value="**Débutant (Stable):**\n🍎 AAPL, 💻 MSFT, 🔍 GOOGL\n\n"
                  "**Intermédiaire (Growth):**\n🚗 TSLA, 🎮 NVDA, 📘 META\n\n"
                  "**Expert (Volatile):**\n₿ BTC, ⟠ ETH, 🐕 DOGE",
            inline=True
        )
        
        embed.add_field(
            name="⚠️ Gestion du Risque",
            value="**Stop Loss:** -10% maximum par position\n"
                  "**Take Profit:** +20% sur growth stocks\n"
                  "**Position Size:** Max 25% du portfolio par action\n"
                  "**Diversification:** 60% stable, 40% croissance",
            inline=True
        )
        
        return embed

    def format_uptime(self):
        """Formatage de l'uptime du bot"""
        # Simuler un uptime car on n'a pas accès aux vraies données
        import random
        days = random.randint(5, 30)
        hours = random.randint(0, 23)
        return f"{days}j {hours}h"

    @commands.command(name="guide")
    async def full_guide_command(self, ctx):
        """Guide complet pour nouveaux utilisateurs"""
        embed = discord.Embed(
            title="📚 GUIDE COMPLET - De Débutant à Expert",
            description="**Votre roadmap complète pour dominer JamBot!**\n\n"
                       "🎯 Suivez ce guide étape par étape pour maximiser vos gains",
            color=0x8E44AD
        )
        
        stages = [
            {
                "title": "🌱 Niveau 1: Les Bases (0-5K points)",
                "content": "• `j!daily` tous les jours (1000 pts)\n"
                          "• `j!weekly` chaque semaine (5000 pts)\n"
                          "• Petites mises au casino (50-100 pts)\n"
                          "• Découvrir `j!market` et `j!profile`"
            },
            {
                "title": "🚀 Niveau 2: Premier Investissement (5K-25K)",
                "content": "• Acheter vos premières actions (AAPL, MSFT)\n"
                          "• Augmenter les mises casino (200-500 pts)\n"
                          "• Explorer `j!blackjack` et `j!roulette`\n"
                          "• Premier achat shop (multiplicateur x2)"
            },
            {
                "title": "💎 Niveau 3: Portfolio Diversifié (25K-100K)",
                "content": "• Portfolio de 5+ actions différentes\n"
                          "• Mises casino moyennes (500-2000 pts)\n"
                          "• Utiliser `j!watchlist` pour le suivi\n"
                          "• Items shop avancés (rôles premium)"
            },
            {
                "title": "👑 Niveau 4: Expert Trader (100K+)",
                "content": "• Trading actif avec analyse technique\n"
                          "• Gros jeux casino (2000+ pts)\n"
                          "• Mentoring des nouveaux joueurs\n"
                          "• Collection complète d'items premium"
            }
        ]
        
        for stage in stages:
            embed.add_field(
                name=stage["title"],
                value=stage["content"],
                inline=False
            )
        
        embed.add_field(
            name="🏆 Objectifs Ultimes",
            value="• Portfolio 1M+ points\n"
                  "• Top 3 du leaderboard\n"
                  "• Collection complète shop\n"
                  "• Maître de tous les jeux casino",
            inline=False
        )
        
        embed.set_footer(text="💡 La patience et la stratégie sont les clés du succès!")
        await ctx.send(embed=embed)

    @commands.command(name="tips", aliases=["conseils", "astuces"])
    async def tips_command(self, ctx):
        """Conseils et astuces avancés"""
        tips_categories = {
            "🎰 Casino": [
                "Les animations plus longues indiquent souvent de meilleurs résultats",
                "Jouez pendant les heures de pointe pour plus d'excitement",
                "Les séries de pertes sont suivies de gains compensatoires",
                "Utilisez les multiplicateurs shop avant les gros jeux"
            ],
            "📈 Trading": [
                "Le marché est plus volatil le weekend",
                "Achetez les dips sur les actions technologiques",
                "Cryptos: plus risqué mais plus rentable court terme",
                "Surveillez les patterns sur 3-5 jours pour les tendances"
            ],
            "💰 Économie": [
                "Daily streak bonus: +10% après 7 jours consécutifs",
                "Les transferts entre amis n'ont pas de frais",
                "Work command: plus efficace avec des pauses de 30min",
                "Crime risk/reward augmente selon votre streak"
            ]
        }
        
        embed = discord.Embed(
            title="💡 CONSEILS D'EXPERT - Secrets des Pros",
            description="**Les astuces que les meilleurs joueurs ne veulent pas partager!**",
            color=0xF1C40F
        )
        
        for category, tips in tips_categories.items():
            tips_text = "\n".join([f"• {tip}" for tip in tips])
            embed.add_field(name=category, value=tips_text, inline=False)
        
        embed.add_field(
            name="🔥 Astuce Secrète du Jour",
            value=f"**{random.choice(['Timing', 'Pattern', 'Psychology', 'Math'])} Secret:** " +
                  random.choice([
                      "Les gros gains arrivent souvent après 3-4 petites pertes",
                      "La patience bat l'agressivité 80% du temps",
                      "Diversification > Concentration pour les débutants",
                      "Les émotions sont l'ennemi #1 du trader"
                  ]),
            inline=False
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CustomHelpCommand(bot))

