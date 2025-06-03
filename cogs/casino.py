import discord
from discord.ext import commands
import json
import os
import random
import asyncio

USER_DATA_FILE = "user_data.json"

class Casino(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_user_data(self, user_id):
        try:
            if os.path.exists(USER_DATA_FILE):
                with open(USER_DATA_FILE, "r") as f:
                    data = json.load(f)
                return data.get(str(user_id), {})
            return {}
        except Exception as e:
            print(f"Erreur lors de la lecture des données utilisateur: {e}")
            return {}

    def get_user_points(self, user_id):
        user_data = self.get_user_data(user_id)
        return user_data.get("points", 1000)

    def set_user_points(self, user_id, points):
        try:
            data = {}
            if os.path.exists(USER_DATA_FILE):
                with open(USER_DATA_FILE, "r") as f:
                    data = json.load(f)
            user_id_str = str(user_id)
            if user_id_str not in data:
                data[user_id_str] = {"points": 0, "stats": {}}
            data[user_id_str]["points"] = round(points, 2)
            with open(USER_DATA_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des points: {e}")

    def update_user_stats(self, user_id, game_type, bet_amount, won, winnings=0):
        try:
            data = {}
            if os.path.exists(USER_DATA_FILE):
                with open(USER_DATA_FILE, "r") as f:
                    data = json.load(f)
            user_id_str = str(user_id)
            if user_id_str not in data:
                data[user_id_str] = {"points": 1000, "stats": {}}
            if "stats" not in data[user_id_str]:
                data[user_id_str]["stats"] = {}
            if game_type not in data[user_id_str]["stats"]:
                data[user_id_str]["stats"][game_type] = {
                    "games_played": 0,
                    "games_won": 0,
                    "total_bet": 0,
                    "total_winnings": 0
                }
            game_stats = data[user_id_str]["stats"][game_type]
            game_stats["games_played"] += 1
            game_stats["total_bet"] += bet_amount
            if won:
                game_stats["games_won"] += 1
                game_stats["total_winnings"] += winnings
            with open(USER_DATA_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Erreur lors de la mise à jour des statistiques: {e}")

    @commands.command(name="casinohelp", aliases=["chelp"])
    async def casino_help(self, ctx):
        embed = discord.Embed(
            title="🌀 Aide du Casino",
            description="Voici la liste des commandes disponibles :",
            color=0xFFD700
        )
        embed.add_field(name="🎰 Machine à sous", value="`j!slot <mise>`", inline=False)
        embed.add_field(name="🃏 Blackjack", value="`j!blackjack <mise>`", inline=False)
        embed.add_field(name="🎯 Roulette", value="`j!roulette <mise> <choix>`", inline=False)
        embed.add_field(name="🪙 Pile ou Face", value="`j!coinflip <mise> <pile/face>`", inline=False)
        embed.add_field(name="🎲 Dé", value="`j!dice <mise> <nombre entre 1-6>`", inline=False)
        embed.add_field(name="📉 Limbo", value="`j!limbo <mise> <multiplicateur>`", inline=False)
        embed.add_field(name="🚀 Crash", value="`j!crash <mise>`", inline=False)
        embed.add_field(name="💣 Mines", value="`j!mines <mise> <mines>`", inline=False)
        embed.add_field(name="🍋 Bonus quotidien", value="`j!daily`", inline=False)
        embed.add_field(name="🍌 Bonus hebdomadaire", value="`j!weekly`", inline=False)
        embed.add_field(name="📈 Statistiques", value="`j!stats [@membre]`", inline=False)
        embed.add_field(name="💸 Voir les points", value="`j!balance [@membre]`", inline=False)
        embed.set_footer(text="Tape j!chelp pour revoir cette aide.")
        await ctx.send(embed=embed)

    # Les autres commandes comme slot, roulette, blackjack, etc. seront ajoutées ici.
    # Pour alléger la réponse, dis-moi si tu veux que je colle chaque jeu un par un ou tous à la suite directement.

    @commands.command(name="stats")
    async def stats(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        user_id = member.id
        user_data = self.get_user_data(user_id)

        if not user_data:
            await ctx.send("❌ Aucune donnée trouvée pour cet utilisateur.")
            return

        points = user_data.get("points", 0)
        stats = user_data.get("stats", {})

        embed = discord.Embed(
            title=f"📊 Statistiques de {member.display_name}",
            color=0x00ff00
        )
        embed.add_field(name="💰 Points", value=f"**{points}**", inline=True)

        total_games = 0
        total_bet = 0
        total_won = 0
        total_winnings = 0

        for game_type, game_stats in stats.items():
            games_played = game_stats.get("games_played", 0)
            games_won = game_stats.get("games_won", 0)
            total_bet_game = game_stats.get("total_bet", 0)
            total_winnings_game = game_stats.get("total_winnings", 0)

            total_games += games_played
            total_bet += total_bet_game
            total_won += games_won
            total_winnings += total_winnings_game

            if games_played > 0:
                win_rate = (games_won / games_played) * 100
                embed.add_field(
                    name=f"🎮 {game_type.title()}",
                    value=f"Parties: {games_played}\nVictoires: {games_won} ({win_rate:.1f}%)\nMise: {total_bet_game}\nGains: {total_winnings_game}",
                    inline=True
                )

        if total_games > 0:
            overall_win_rate = (total_won / total_games) * 100
            net_result = total_winnings - total_bet
            embed.add_field(
                name="📈 Global",
                value=f"Total parties: {total_games}\nTaux de victoire: {overall_win_rate:.1f}%\nRésultat net: {net_result:+.2f}",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name="balance", aliases=["points", "bal"])
    async def balance(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        points = self.get_user_points(member.id)
        await ctx.send(f"💰 {member.display_name} a **{points}** points.")

    @commands.command(name="daily")
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx):
        user_id = ctx.author.id
        bonus = 500
        current_points = self.get_user_points(user_id)
        self.set_user_points(user_id, current_points + bonus)
        await ctx.send(f"🎁 {ctx.author.mention} Vous avez reçu **{bonus}** points aujourd'hui. Total: **{current_points + bonus}**")

    @commands.command(name="weekly")
    @commands.cooldown(1, 604800, commands.BucketType.user)
    async def weekly(self, ctx):
        user_id = ctx.author.id
        bonus = 2000
        current_points = self.get_user_points(user_id)
        self.set_user_points(user_id, current_points + bonus)
        await ctx.send(f"🎁 {ctx.author.mention} Vous avez reçu **{bonus}** points cette semaine. Total: **{current_points + bonus}**")

async def setup(bot):
    print("🔧 Chargement du cog Casino...")
    await bot.add_cog(Casino(bot))
