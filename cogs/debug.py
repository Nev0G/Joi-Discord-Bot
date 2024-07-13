import discord
from discord.ext import commands
import random

class Exemple(commands.Cog):
    def __init__(self, bot):
        # Le constructeur de la classe
        # 'bot' est l'instance du bot passée lors de l'ajout du Cog
        self.bot = bot
        # Vous pouvez initialiser d'autres variables ici si nécessaire
        self.counter = 0

    # Définition d'un listener (écouteur d'événement)
    @commands.Cog.listener()
    async def on_message(self, message):
        # Cette méthode sera appelée chaque fois qu'un message est envoyé
        if message.author == self.bot.user:
            # Ignorer les messages du bot lui-même
            return
        
        # Exemple : incrémenter un compteur à chaque message
        self.counter += 1

    # Définition d'une commande simple
    @commands.command(name="salut")
    async def say_hello(self, ctx):
        # 'ctx' est le contexte de la commande, il contient des infos utiles
        await ctx.send(f"Salut {ctx.author.mention}!")

    # Commande avec un argument
    @commands.command(name="dire")
    async def echo(self, ctx, *, message: str):
        # '*' permet de capturer tous les mots après la commande en un seul argument
        await ctx.send(f"Vous avez dit : {message}")

    # Commande avec gestion d'erreur intégrée
    @commands.command(name="diviser")
    async def divide(self, ctx, a: int, b: int):
        try:
            result = a / b
            await ctx.send(f"{a} divisé par {b} est égal à {result}")
        except ZeroDivisionError:
            await ctx.send("Erreur : Division par zéro !")

    # Commande avec vérification de permission
    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick_user(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(f"{member.name} a été expulsé.")

    # Gestion d'erreur pour la commande kick
    @kick_user.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("Vous n'avez pas la permission d'utiliser cette commande.")

    # Commande pour afficher le compteur
    @commands.command(name="compteur")
    async def show_counter(self, ctx):
        await ctx.send(f"Le compteur est actuellement à {self.counter}.")

# Fonction de configuration du Cog
async def setup(bot):
    # Cette fonction est appelée lorsque le Cog est chargé
    await bot.add_cog(Exemple(bot))