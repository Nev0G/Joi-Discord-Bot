import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='alaide', aliases=['h'])
    async def help_command(self, ctx, command_name=None):
        """Affiche l'aide générale ou l'aide d'une commande spécifique"""
            
        embed = discord.Embed(
            title="📚 Guide des Commandes - JuifBot",
            description="Voici toutes les commandes disponibles pour JuifBot :",
            color=0x00ff00
        )
        
        # Économie
        embed.add_field(
            name="💰 Économie",
            value="`j!balance` / `j!bal` - Voir votre argent\n"
                  "`j!work` / `j!travail` - Travailler pour gagner de l'argent\n"
                  "`j!daily` - Récupérer votre bonus quotidien\n"
                  "`j!weekly` - Récupérer votre bonus hebdomadaire\n"
                  "`j!give <@user> <montant>` - Donner de l'argent\n"
                  "`j!top` / `j!leaderboard` - Classement des plus riches",
            inline=False
        )
        
        # Boutique
        embed.add_field(
            name="🛒 Boutique",
            value="`j!shop` - Voir la boutique\n"
                  "`j!buy <item_id>` - Acheter un article\n"
                  "`j!inventory` / `j!inv` - Voir votre inventaire\n"
                  "`j!use <item_id>` - Utiliser un article",
            inline=False
        )
        
        # Bourse/Stocks
        embed.add_field(
            name="📈 Bourse",
            value="`j!stocks` - Voir les actions disponibles\n"
                  "`j!buy_stock <symbol> <quantity>` - Acheter des actions\n"
                  "`j!sell_stock <symbol> <quantity>` - Vendre des actions\n"
                  "`j!portfolio` - Voir votre portefeuille\n"
                  "`j!stock_info <symbol>` - Infos sur une action",
            inline=False
        )
        
        # Casino - NOUVEAU
        embed.add_field(
            name="🎰 Casino",
            value="`j!coinflip <mise>` - Pile ou face\n"
                  "`j!slots <mise>` - Machine à sous\n"
                  "`j!blackjack <mise>` - Jeu de blackjack\n"
                  "`j!mines <mise> [nb_mines]` - Champ de mines\n"
                  "`j!crash <mise>` - Jeu de crash\n"
                  "`j!roulette <mise> <pari>` - Roulette européenne\n"
                  "`j!dice <mise>` - Jeu de dés\n"
                  "`j!lottery` - Voir la loterie actuelle\n"
                  "`j!buyticket <nombre>` - Acheter des tickets de loterie",
            inline=False
        )

        # Sondages - NOUVEAU
        embed.add_field(
            name="📊 Sondages",
            value="`j!poll \"Titre\" \"Option 1\" \"Option 2\" ...` - Créer un sondage\n"
                  "`j!sondage` - Alias de j!poll\n"
                  "`j!vote` - Alias de j!poll",
            inline=False
        )

        embed.set_footer(text="Utilisez j!help <commande> pour plus d'infos sur une commande spécifique")        
        await ctx.send(embed=embed)
        
async def setup(bot):
    await bot.add_cog(Help(bot))