import discord
from discord.ext import commands
import json
import os
from datetime import timedelta
import asyncio

class TimeoutShop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_data_file = 'user_data.json'
        self.base_price = 500  # Prix de base pour 1 minute
        self.max_duration = 1440  # Durée maximale de 24 heures (en minutes)
        self.anti_timeout_price = 7000  # Prix de l'Anti-Timeout

    def load_user_data(self):
        if os.path.exists(self.user_data_file):
            with open(self.user_data_file, 'r') as f:
                return json.load(f)
        return {}

    def save_user_data(self, user_data):
        with open(self.user_data_file, 'w') as f:
            json.dump(user_data, f, indent=4)

    def calculate_price(self, duration):
        return int(self.base_price * (duration ** 0.8))  # Prix non linéaire

    @commands.command(name="timeout_shop")
    async def timeout_shop(self, ctx):
        """Affiche les options disponibles dans la boutique de timeout."""
        embed = discord.Embed(title="Boutique de Timeout", description="Options disponibles", color=0xff0000)
        
        # Exemples de prix pour les timeouts
        durations = [5, 15, 30, 60, 120, 240, 480]
        for duration in durations:
            price = self.calculate_price(duration)
            embed.add_field(name=f"Timeout {duration} minutes", value=f"{price} points", inline=False)
        
        # Option Anti-Timeout
        embed.add_field(name="Anti-Timeout", value=f"{self.anti_timeout_price} points\nProtège contre un timeout et le renvoie à l'acheteur", inline=False)
        
        embed.set_footer(text="Utilisez !buy_timeout @membre <durée> pour un timeout ou !buy_anti_timeout pour l'Anti-Timeout")
        await ctx.send(embed=embed)

    @commands.command(name="buy_timeout")
    @commands.has_permissions(manage_messages=True)
    async def buy_timeout(self, ctx, member: discord.Member, duration: int):
        """Permet d'acheter un timeout personnalisé pour un membre du serveur."""
        if duration <= 0 or duration > self.max_duration:
            await ctx.send(f"La durée doit être entre 1 et {self.max_duration} minutes.")
            return

        price = self.calculate_price(duration)
        user_data = self.load_user_data()
        user_id = str(ctx.author.id)
        target_id = str(member.id)

        if user_id not in user_data:
            user_data[user_id] = {"points": 0}

        if user_data[user_id].get("points", 0) < price:
            await ctx.send(f"Vous n'avez pas assez de points. Prix du timeout : {price} points.")
            return

        if member.top_role >= ctx.author.top_role or member.id == ctx.guild.owner_id:
            await ctx.send("Vous ne pouvez pas mettre ce membre en timeout.")
            return

        # Vérifier si la cible a un Anti-Timeout
        if target_id in user_data and user_data[target_id].get("anti_timeout", 0) > 0:
            user_data[target_id]["anti_timeout"] -= 1
            self.save_user_data(user_data)
            await ctx.send(f"{member.mention} a utilisé un Anti-Timeout! Le timeout est renvoyé à {ctx.author.mention}.")
            member = ctx.author  # Rediriger le timeout vers l'acheteur original

        # Demander confirmation
        confirm_msg = await ctx.send(f"Voulez-vous acheter un timeout de {duration} minutes pour {member.mention} au prix de {price} points ? Réagissez avec 👍 pour confirmer ou 👎 pour annuler.")
        await confirm_msg.add_reaction("👍")
        await confirm_msg.add_reaction("👎")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["👍", "👎"] and reaction.message.id == confirm_msg.id

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Temps écoulé. Transaction annulée.")
            return

        if str(reaction.emoji) == "👎":
            await ctx.send("Transaction annulée.")
            return

        user_data[user_id]["points"] -= price
        self.save_user_data(user_data)

        try:
            await member.timeout(timedelta(minutes=duration), reason=f"Timeout acheté par {ctx.author}")
            await ctx.send(f"{member.mention} a été mis en timeout pour {duration} minutes. Coût : {price} points.")
        except discord.errors.Forbidden:
            await ctx.send("Je n'ai pas les permissions nécessaires pour mettre ce membre en timeout.")
            user_data[user_id]["points"] += price
            self.save_user_data(user_data)

    @commands.command(name="buy_at")
    async def buy_anti_timeout(self, ctx):
        """Permet d'acheter un Anti-Timeout."""
        user_data = self.load_user_data()
        user_id = str(ctx.author.id)

        if user_id not in user_data:
            user_data[user_id] = {"points": 0}

        if user_data[user_id].get("points", 0) < self.anti_timeout_price:
            await ctx.send(f"Vous n'avez pas assez de points. Prix de l'Anti-Timeout : {self.anti_timeout_price} points.")
            return

        # Demander confirmation
        confirm_msg = await ctx.send(f"Voulez-vous acheter un Anti-Timeout au prix de {self.anti_timeout_price} points ? Réagissez avec 👍 pour confirmer ou 👎 pour annuler.")
        await confirm_msg.add_reaction("👍")
        await confirm_msg.add_reaction("👎")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["👍", "👎"] and reaction.message.id == confirm_msg.id

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Temps écoulé. Transaction annulée.")
            return

        if str(reaction.emoji) == "👎":
            await ctx.send("Transaction annulée.")
            return

        user_data[user_id]["points"] -= self.anti_timeout_price
        user_data[user_id]["anti_timeout"] = user_data[user_id].get("anti_timeout", 0) + 1
        self.save_user_data(user_data)

        await ctx.send(f"Félicitations ! Vous avez acheté un Anti-Timeout. Vous en avez maintenant {user_data[user_id]['anti_timeout']}.")

async def setup(bot):
    await bot.add_cog(TimeoutShop(bot))