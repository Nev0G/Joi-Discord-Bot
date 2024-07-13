import discord
from discord.ext import commands
import json

class DMSender(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def bombDM(self, ctx, target: discord.Member, *, content: str):
        # Charger les données utilisateur
        with open('user_data.json', 'r') as f:
            user_data = json.load(f)

        # Vérifier si l'utilisateur a l'item "BombDM" dans son inventaire
        if str(ctx.author.id) in user_data and 'inventory' in user_data[str(ctx.author.id)]:
            if "BombDM" in user_data[str(ctx.author.id)]['inventory']:
                try:
                    # Envoyer le message privé
                    await target.send(content)
                    await ctx.send(f"Message envoyé à {target.name} avec succès!")
                    
                    # Retirer l'item de l'inventaire après utilisation
                    user_data[str(ctx.author.id)]['inventory'].remove("BombDM")
                    
                    # Sauvegarder les données mises à jour
                    with open('user_data.json', 'w') as f:
                        json.dump(user_data, f, indent=2)
                except discord.Forbidden:
                    await ctx.send("Je n'ai pas pu envoyer de message privé à cet utilisateur.")
            else:
                await ctx.send("Vous n'avez pas l'item 'BombDM' dans votre inventaire.")
        else:
            await ctx.send("Vous n'avez pas d'inventaire ou l'item requis.")

async def setup(bot):
    await bot.add_cog(DMSender(bot))