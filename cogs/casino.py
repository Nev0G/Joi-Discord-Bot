import discord
from discord.ext import commands, tasks
import random
import asyncio
import json
import os
from typing import List, Tuple
from collections import defaultdict
import math


USER_DATA_FILE = "user_data.json"

class Casino(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_data = self.load_user_data()
        self.bounty_channels = []
        self.active_games = {}  # Pour suivre les jeux en cours
        # self.post_bounty.start()  # Décommentez pour activer les bounties

    @commands.command(name="casinohelp", aliases=["chelp"])
    async def casino_help(self, ctx):
        embed = discord.Embed(
            title="🎰 Casino de Joi - Guide Complet 🎰",
            description="Voici tous les jeux disponibles dans notre casino :",
            color=0xFFD700
        )
        
        # Jeux de base
        embed.add_field(
            name="🎰 **JEUX CLASSIQUES**",
            value=(
                "• `j!slot <mise>` - Machine à sous\n"
                "• `j!blackjack <mise>` - Blackjack classique\n"
                "• `j!roulette <mise> <choix>` - Roulette européenne\n"
                "• `j!duel @joueur <mise>` - Duel entre joueurs"
            ),
            inline=False
        )
        
        # Nouveaux jeux
        embed.add_field(
            name="🎲 **NOUVEAUX JEUX**",
            value=(
                "• `j!crash <mise>` - Jeu de crash avec multiplicateur\n"
                "• `j!mines <mise> <mines>` - Démineur (1-24 mines)\n"
                "• `j!coinflip <mise> <face/pile>` - Pile ou face\n"
                "• `j!dice <mise> <nombre>` - Devinez le dé (1-6)\n"
                "• `j!lottery <prix_ticket>` - Loterie commune\n"
                "• `j!wheel <mise>` - Roue de la fortune"
            ),
            inline=False
        )
        
        # Jeux avancés
        embed.add_field(
            name="🎯 **JEUX AVANCÉS**",
            value=(
                "• `j!poker <mise>` - Poker vidéo\n"
                "• `j!baccarat <mise> <joueur/banquier/égalité>` - Baccarat\n"
                "• `j!limbo <mise> <multi>` - Limbo (multiplicateur)\n"
                "• `j!keno <mise> <num1 num2...>` - Keno (max 10 numéros)"
            ),
            inline=False
        )
        
        # Utilitaires
        embed.add_field(
            name="💰 **UTILITAIRES**",
            value=(
                "• `j!points [@joueur]` - Voir les points\n"
                "• `j!leaderboard` - Classement\n"
                "• `j!rsa` - Aide sociale (100pts/h)\n"
                "• `j!donner @joueur <montant>` - Donner des points\n"
                "• `j!vol @joueur <montant>` - Tenter un vol\n"
                "• `j!stats` - Vos statistiques de jeu"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🎁 **BONUS QUOTIDIENS**",
            value="• `j!daily` - Bonus quotidien (500pts)\n• `j!weekly` - Bonus hebdomadaire (2000pts)",
            inline=False
        )
        
        embed.set_footer(text="🍀 Bonne chance et jouez de manière responsable ! 🍀")
        await ctx.send(embed=embed)

    def load_user_data(self):
        """Charge les données utilisateur depuis le fichier JSON"""
        try:
            if os.path.exists(USER_DATA_FILE):
                with open(USER_DATA_FILE, "r") as f:
                    return json.load(f)
            else:
                return {}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_user_data(self):
        """Sauvegarde les données utilisateur dans le fichier JSON"""
        try:
            with open(USER_DATA_FILE, "w") as f:
                json.dump(self.user_data, f, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")

    def get_user_points(self, user_id):
        """Récupère les points d'un utilisateur"""
        try:
            if os.path.exists(USER_DATA_FILE):
                with open(USER_DATA_FILE, "r") as f:
                    data = json.load(f)
                return round(data.get(str(user_id), {}).get("points", 0), 2)
            else:
                return 0
        except (FileNotFoundError, json.JSONDecodeError):
            return 0

    def set_user_points(self, user_id, points):
        """Définit les points d'un utilisateur"""
        try:
            if os.path.exists(USER_DATA_FILE):
                with open(USER_DATA_FILE, "r") as f:
                    data = json.load(f)
            else:
                data = {}
            
            user_id = str(user_id)
            if user_id not in data:
                data[user_id] = {"points": 0}
            
            data[user_id]["points"] = round(points, 2)
            
            with open(USER_DATA_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Erreur lors de la définition des points: {e}")

    def update_user_stats(self, user_id, game_type, bet, won, winnings=0):
        """Met à jour les statistiques de jeu d'un utilisateur"""
        try:
            if os.path.exists(USER_DATA_FILE):
                with open(USER_DATA_FILE, "r") as f:
                    data = json.load(f)
            else:
                data = {}
            
            user_id = str(user_id)
            if user_id not in data:
                data[user_id] = {"points": 0}
            if "stats" not in data[user_id]:
                data[user_id]["stats"] = {
                    "games_played": 0,
                    "total_bet": 0,
                    "total_won": 0,
                    "biggest_win": 0,
                    "games": {}
                }
            
            stats = data[user_id]["stats"]
            stats["games_played"] += 1
            stats["total_bet"] += bet
            if won:
                stats["total_won"] += winnings
                if winnings > stats["biggest_win"]:
                    stats["biggest_win"] = winnings
            
            if game_type not in stats["games"]:
                stats["games"][game_type] = {"played": 0, "won": 0}
            
            stats["games"][game_type]["played"] += 1
            if won:
                stats["games"][game_type]["won"] += 1
            
            with open(USER_DATA_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Erreur lors de la mise à jour des stats: {e}")

    @commands.command(name="points", aliases=["balance", "bal"])
    async def check_points(self, ctx, member: discord.Member = None):
        """Vérifier les points d'un utilisateur"""
        member = member or ctx.author
        points = self.get_user_points(member.id)
        await ctx.send(f"💰 {member.display_name} a **{points}** points.")

    # ===== NOUVEAUX JEUX =====

    @commands.command(name="crash")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def crash(self, ctx, bet: float):
        """Jeu de crash - Arrêtez-vous avant que ça crash !"""
        user_id = ctx.author.id
        user_points = self.get_user_points(user_id)
        
        if bet <= 0:
            await ctx.send("🚫 Vous devez parier au moins 1 point.")
            return
        
        if user_points < bet:
            await ctx.send("❌ Vous n'avez pas assez de points pour ce pari.")
            return
        
        self.set_user_points(user_id, user_points - bet)
        
        # Le crash peut arriver entre 1.0x et 10.0x
        crash_point = round(random.uniform(1.01, 10.0), 2)
        current_multiplier = 1.0
        
        embed = discord.Embed(
            title="🚀 CRASH GAME",
            description=f"Mise: **{bet}** points\nMultiplicateur: **{current_multiplier}x**",
            color=0x00ff00
        )
        embed.add_field(name="Instructions", value="Réagissez avec 💰 pour encaisser avant le crash !", inline=False)
        
        game_msg = await ctx.send(embed=embed)
        await game_msg.add_reaction("💰")
        
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == "💰" and reaction.message.id == game_msg.id
        
        crashed = False
        while current_multiplier < crash_point and not crashed:
            current_multiplier = round(current_multiplier + 0.1, 2)
            
            embed.description = f"Mise: **{bet}** points\nMultiplicateur: **{current_multiplier}x**\nGain potentiel: **{round(bet * current_multiplier, 2)}** points"
            embed.color = 0x00ff00 if current_multiplier < crash_point * 0.8 else 0xff9900
            
            await game_msg.edit(embed=embed)
            
            try:
                await self.bot.wait_for('reaction_add', check=check, timeout=0.8)
                # Joueur a encaissé
                winnings = round(bet * current_multiplier, 2)
                self.set_user_points(user_id, self.get_user_points(user_id) + winnings)
                self.update_user_stats(user_id, "crash", bet, True, winnings)
                
                embed.title = "💰 ENCAISSÉ !"
                embed.description = f"Vous avez encaissé à **{current_multiplier}x**\nGain: **{winnings}** points"
                embed.color = 0x00ff00
                await game_msg.edit(embed=embed)
                return
                
            except asyncio.TimeoutError:
                continue
        
        # Le jeu a crashé
        self.update_user_stats(user_id, "crash", bet, False)
        embed.title = "💥 CRASH !"
        embed.description = f"Le multiplicateur a crashé à **{crash_point}x**\nVous avez perdu **{bet}** points"
        embed.color = 0xff0000
        await game_msg.edit(embed=embed)

    @commands.command(name="mines")
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def mines(self, ctx, bet: float, num_mines: int = 3):
        """Jeu de démineur - Évitez les mines !"""
        user_id = ctx.author.id
        user_points = self.get_user_points(user_id)
        
        if bet <= 0:
            await ctx.send("🚫 Vous devez parier au moins 1 point.")
            return
        
        if user_points < bet:
            await ctx.send("❌ Vous n'avez pas assez de points pour ce pari.")
            return
        
        if not 1 <= num_mines <= 24:
            await ctx.send("❌ Le nombre de mines doit être entre 1 et 24.")
            return
        
        self.set_user_points(user_id, user_points - bet)
        
        # Créer le champ de mines (25 cases, 5x5)
        mines_positions = random.sample(range(25), num_mines)
        revealed = []
        game_over = False
        
        def create_field():
            field = ""
            for i in range(25):
                if i in revealed:
                    if i in mines_positions:
                        field += "💥"
                    else:
                        field += "💎"
                else:
                    field += f"{i+1:02d}⃣" if i < 9 else f"{i+1}⃣" if i < 19 else "🔢"
                
                if (i + 1) % 5 == 0:
                    field += "\n"
                else:
                    field += " "
            return field
        
        embed = discord.Embed(
            title=f"💣 MINES - {num_mines} mines cachées",
            description=f"Mise: **{bet}** points\nCases révélées: **{len(revealed)}**",
            color=0x00ff00
        )
        embed.add_field(name="Champ de mines", value=create_field(), inline=False)
        embed.add_field(name="Instructions", value="Tapez un numéro (1-25) pour révéler une case\nTapez 'stop' pour encaisser", inline=False)
        
        game_msg = await ctx.send(embed=embed)
        
        while not game_over and len(revealed) < 25 - num_mines:
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            
            try:
                msg = await self.bot.wait_for('message', check=check, timeout=60.0)
                choice = msg.content.lower()
                
                try:
                    await msg.delete()
                except:
                    pass  # Ignore si impossible de supprimer
                
                if choice == 'stop':
                    # Encaisser
                    multiplier = (25 / (25 - num_mines)) ** len(revealed)
                    winnings = round(bet * multiplier, 2)
                    self.set_user_points(user_id, self.get_user_points(user_id) + winnings)
                    self.update_user_stats(user_id, "mines", bet, True, winnings)
                    
                    embed.title = "💰 ENCAISSÉ !"
                    embed.description = f"Vous avez encaissé avec **{len(revealed)}** cases révélées\nGain: **{winnings}** points"
                    embed.color = 0x00ff00
                    await game_msg.edit(embed=embed)
                    return
                
                try:
                    position = int(choice) - 1
                    if not 0 <= position <= 24:
                        await ctx.send("❌ Numéro invalide (1-25)", delete_after=3)
                        continue
                    
                    if position in revealed:
                        await ctx.send("❌ Case déjà révélée", delete_after=3)
                        continue
                    
                    revealed.append(position)
                    
                    if position in mines_positions:
                        # Boom !
                        revealed.extend(mines_positions)  # Révéler toutes les mines
                        self.update_user_stats(user_id, "mines", bet, False)
                        
                        embed.title = "💥 BOOM !"
                        embed.description = f"Vous avez touché une mine !\nVous avez perdu **{bet}** points"
                        embed.color = 0xff0000
                        embed.clear_fields()
                        embed.add_field(name="Champ de mines", value=create_field(), inline=False)
                        await game_msg.edit(embed=embed)
                        return
                    
                    # Case sûre
                    multiplier = (25 / (25 - num_mines)) ** len(revealed)
                    potential_win = round(bet * multiplier, 2)
                    
                    embed.description = f"Mise: **{bet}** points\nCases révélées: **{len(revealed)}**\nGain potentiel: **{potential_win}** points"
                    embed.clear_fields()
                    embed.add_field(name="Champ de mines", value=create_field(), inline=False)
                    embed.add_field(name="Instructions", value="Tapez un numéro (1-25) pour révéler une case\nTapez 'stop' pour encaisser", inline=False)
                    await game_msg.edit(embed=embed)
                    
                except ValueError:
                    await ctx.send("❌ Veuillez entrer un numéro valide ou 'stop'", delete_after=3)
                    continue
                    
            except asyncio.TimeoutError:
                await ctx.send("⏰ Temps écoulé ! Vous perdez votre mise.", delete_after=5)
                self.update_user_stats(user_id, "mines", bet, False)
                return

    @commands.command(name="coinflip", aliases=["cf"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def coinflip(self, ctx, bet: float, choice: str):
        """Pile ou face simple"""
        user_id = ctx.author.id
        user_points = self.get_user_points(user_id)
        
        if bet <= 0:
            await ctx.send("🚫 Vous devez parier au moins 1 point.")
            return
        
        if user_points < bet:
            await ctx.send("❌ Vous n'avez pas assez de points pour ce pari.")
            return
        
        if choice.lower() not in ['pile', 'face']:
            await ctx.send("❌ Choisissez 'pile' ou 'face'")
            return
        
        self.set_user_points(user_id, user_points - bet)
        
        result = random.choice(['pile', 'face'])
        
        # Animation
        animation_msg = await ctx.send("🪙 La pièce tourne...")
        for _ in range(3):
            for emoji in ["🌑", "🌕"]:
                await animation_msg.edit(content=f"🪙 La pièce tourne... {emoji}")
                await asyncio.sleep(0.3)
        
        won = choice.lower() == result
        
        if won:
            winnings = bet * 2
            self.set_user_points(user_id, self.get_user_points(user_id) + winnings)
            self.update_user_stats(user_id, "coinflip", bet, True, winnings)
            await animation_msg.edit(content=f"🎉 {result.upper()} ! Vous gagnez **{winnings}** points !")
        else:
            self.update_user_stats(user_id, "coinflip", bet, False)
            await animation_msg.edit(content=f"😞 {result.upper()} ! Vous perdez **{bet}** points.")

    @commands.command(name="dice")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def dice(self, ctx, bet: float, guess: int):
        """Devinez le résultat du dé (1-6)"""
        user_id = ctx.author.id
        user_points = self.get_user_points(user_id)
        
        if bet <= 0:
            await ctx.send("🚫 Vous devez parier au moins 1 point.")
            return
        
        if user_points < bet:
            await ctx.send("❌ Vous n'avez pas assez de points pour ce pari.")
            return
        
        if not 1 <= guess <= 6:
            await ctx.send("❌ Choisissez un nombre entre 1 et 6")
            return
        
        self.set_user_points(user_id, user_points - bet)
        
        result = random.randint(1, 6)
        dice_faces = ["", "⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
        
        # Animation
        animation_msg = await ctx.send("🎲 Le dé roule...")
        for _ in range(3):
            for face in dice_faces[1:]:
                await animation_msg.edit(content=f"🎲 Le dé roule... {face}")
                await asyncio.sleep(0.2)
        
        won = guess == result
        
        if won:
            winnings = bet * 6  # Paiement 6:1
            self.set_user_points(user_id, self.get_user_points(user_id) + winnings)
            self.update_user_stats(user_id, "dice", bet, True, winnings)
            await animation_msg.edit(content=f"🎉 {dice_faces[result]} Parfait ! Vous gagnez **{winnings}** points !")
        else:
            self.update_user_stats(user_id, "dice", bet, False)
            await animation_msg.edit(content=f"😞 {dice_faces[result]} Pas cette fois ! Vous perdez **{bet}** points.")

    @commands.command(name="wheel")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def wheel(self, ctx, bet: float):
        """Roue de la fortune avec différents multiplicateurs"""
        user_id = ctx.author.id
        user_points = self.get_user_points(user_id)
        
        if bet <= 0:
            await ctx.send("🚫 Vous devez parier au moins 1 point.")
            return
        
        if user_points < bet:
            await ctx.send("❌ Vous n'avez pas assez de points pour ce pari.")
            return
        
        self.set_user_points(user_id, user_points - bet)
        
        # Segments de la roue avec leurs probabilités
        segments = [
            ("💀", 0, 0.05),      # Perte totale
            ("😢", 0.5, 0.15),    # Récupère 50%
            ("😐", 1.0, 0.25),    # Récupère la mise
            ("😊", 1.5, 0.20),    # x1.5
            ("😁", 2.0, 0.15),    # x2
            ("🤑", 3.0, 0.10),    # x3
            ("💎", 5.0, 0.07),    # x5
            ("🌟", 10.0, 0.03)    # x10
        ]
        
        # Choisir un segment selon les probabilités
        rand = random.random()
        cumulative = 0
        result_segment = segments[0]
        
        for segment in segments:
            cumulative += segment[2]
            if rand <= cumulative:
                result_segment = segment
                break
        
        emoji, multiplier, _ = result_segment
        
        # Animation
        animation_msg = await ctx.send("🎡 La roue tourne...")
        for _ in range(4):
            for seg in segments:
                await animation_msg.edit(content=f"🎡 La roue tourne... {seg[0]}")
                await asyncio.sleep(0.3)
        
        winnings = round(bet * multiplier, 2)
        
        if multiplier > 0:
            self.set_user_points(user_id, self.get_user_points(user_id) + winnings)
            self.update_user_stats(user_id, "wheel", bet, multiplier >= 1, winnings if multiplier >= 1 else 0)
            
            if multiplier >= 1:
                await animation_msg.edit(content=f"🎉 {emoji} Vous gagnez **{winnings}** points ! (x{multiplier})")
            else:
                await animation_msg.edit(content=f"😐 {emoji} Vous récupérez **{winnings}** points...")
        else:
            self.update_user_stats(user_id, "wheel", bet, False)
            await animation_msg.edit(content=f"💀 {emoji} Perte totale ! Vous perdez **{bet}** points.")

    @commands.command(name="daily")
    @commands.cooldown(1, 86400, commands.BucketType.user)  # 24 heures
    async def daily(self, ctx):
        """Bonus quotidien"""
        user_id = ctx.author.id
        bonus = 500
        current_points = self.get_user_points(user_id)
        self.set_user_points(user_id, current_points + bonus)
        
        await ctx.send(f"🎁 {ctx.author.mention} Vous avez reçu votre bonus quotidien de **{bonus}** points !\nVotre solde: **{current_points + bonus}** points")

    @commands.command(name="weekly")
    @commands.cooldown(1, 604800, commands.BucketType.user)  # 7 jours
    async def weekly(self, ctx):
        """Bonus hebdomadaire"""
        user_id = ctx.author.id
        bonus = 2000
        current_points = self.get_user_points(user_id)
        self.set_user_points(user_id, current_points + bonus)
        
        await ctx.send(f"🎁 {ctx.author.mention} Vous avez reçu votre bonus hebdomadaire de **{bonus}** points !\nVotre solde: **{current_points + bonus}** points")

    @commands.command(name="stats")
    async def stats(self, ctx, member: discord.Member = None):
        """Voir les statistiques de jeu"""
        member = member or ctx.author
        
        try:
            if os.path.exists(USER_DATA_FILE):
                with open(USER_DATA_FILE, "r") as f:
                    data = json.load(f)
            else:
                await ctx.send(f"{member.mention} n'a pas encore de statistiques de jeu.")
                return
        except (FileNotFoundError, json.JSONDecodeError):
            await ctx.send(f"{member.mention} n'a pas encore de statistiques de jeu.")
            return
        
        user_data = data.get(str(member.id), {})
        stats = user_data.get("stats", {})
        
        if not stats:
            await ctx.send(f"{member.mention} n'a pas encore de statistiques de jeu.")
            return
        
        embed = discord.Embed(
            title=f"📊 Statistiques de {member.display_name}",
            color=0x00ff00
        )
        
        embed.add_field(
            name="Général",
            value=(
                f"Parties jouées: **{stats.get('games_played', 0)}**\n"
                f"Total misé: **{stats.get('total_bet', 0)}** points\n"
                f"Total gagné: **{stats.get('total_won', 0)}** points\n"
                f"Plus gros gain: **{stats.get('biggest_win', 0)}** points\n"
                f"Profit/Perte: **{stats.get('total_won', 0) - stats.get('total_bet', 0)}** points"
            ),
            inline=False
        )
        
        games_stats = stats.get("games", {})
        if games_stats:
            games_text = ""
            for game, game_data in games_stats.items():
                played = game_data.get("played", 0)
                won = game_data.get("won", 0)
                win_rate = (won / played * 100) if played > 0 else 0
                games_text += f"**{game.capitalize()}**: {played} parties, {win_rate:.1f}% victoires\n"
            
            embed.add_field(name="Par jeu", value=games_text or "Aucune donnée", inline=False)
        
        await ctx.send(embed=embed)

    # ===== JEUX EXISTANTS AMÉLIORÉS =====

    @commands.command(name="slot")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def slotmachine(self, ctx, bet: float):
        user_id = ctx.author.id
        user_points = self.get_user_points(user_id)
        
        if bet <= 0:
            await ctx.send("🚫 Vous devez parier au moins 1 point.")
            return
        
        if user_points < bet:
            await ctx.send("❌ Vous n'avez pas assez de points pour ce pari.")
            return
        
        self.set_user_points(user_id, user_points - bet)
        
        symbols = ["🍒", "🍊", "🍋", "🍇", "🍎", "🍉", "💎", "🎰", "👑", "🌟"]
        multipliers = {
            "🍒": 0.2, "🍊": 0.3, "🍋": 0.4, "🍇": 0.5, "🍎": 0.6,
            "🍉": 0.7, "💎": 0.8, "🎰": 0.9, "👑": 1.0, "🌟": 1.1,
        }
        
        animation_message = await ctx.send(f"🎰 {ctx.author.mention} Machine à sous: {' | '.join(['❓', '❓', '❓'])}")
        
        slots = []
        for _ in range(3):
            for _ in range(3):
                slots = random.choices(symbols, k=3)
                await animation_message.edit(content=f"🎰 {ctx.author.mention} Machine à sous: {' | '.join(slots)}")
                await asyncio.sleep(0.5)
        
        # Vérifier les combinaisons gagnantes
        if slots[0] == slots[1] == slots[2]:
            # Triple
            multiplier = multipliers.get(slots[0], 1.0)
            if slots[0] == "🌟":
                multiplier = 50  # Jackpot
            elif slots[0] == "👑":
                multiplier = 25
            elif slots[0] == "💎":
                multiplier = 10
            else:
                multiplier = 5
            
            winnings = round(bet * multiplier, 2)
            self.set_user_points(user_id, self.get_user_points(user_id) + winnings)
            self.update_user_stats(user_id, "slot", bet, True, winnings)
            
            if slots[0] == "🌟":
                await animation_message.edit(content=f"🎉🎰 JACKPOT ! {' | '.join(slots)} 🎰🎉\n{ctx.author.mention} gagne **{winnings}** points ! (x{multiplier})")
            else:
                await animation_message.edit(content=f"🎉 Triple {slots[0]} ! {' | '.join(slots)}\n{ctx.author.mention} gagne **{winnings}** points ! (x{multiplier})")
        
        elif slots[0] == slots[1] or slots[1] == slots[2] or slots[0] == slots[2]:
            # Double
            winnings = round(bet * 2, 2)
            self.set_user_points(user_id, self.get_user_points(user_id) + winnings)
            self.update_user_stats(user_id, "slot", bet, True, winnings)
            await animation_message.edit(content=f"😊 Double ! {' | '.join(slots)}\n{ctx.author.mention} gagne **{winnings}** points ! (x2)")
        
        else:
            # Perte
            self.update_user_stats(user_id, "slot", bet, False)
            await animation_message.edit(content=f"😞 Pas de chance... {' | '.join(slots)}\n{ctx.author.mention} perd **{bet}** points.")

    @commands.command(name="blackjack", aliases=["bj"])
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def blackjack(self, ctx, bet: float):
        """Jeu de blackjack classique"""
        user_id = ctx.author.id
        user_points = self.get_user_points(user_id)
        
        if bet <= 0:
            await ctx.send("🚫 Vous devez parier au moins 1 point.")
            return
        
        if user_points < bet:
            await ctx.send("❌ Vous n'avez pas assez de points pour ce pari.")
            return
        
        if user_id in self.active_games:
            await ctx.send("❌ Vous avez déjà un jeu en cours !")
            return
        
        self.set_user_points(user_id, user_points - bet)
        
        # Créer le deck
        suits = ['♠️', '♥️', '♦️', '♣️']
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        deck = [(rank, suit) for suit in suits for rank in ranks]
        random.shuffle(deck)
        
        # Distribuer les cartes
        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]
        
        def card_value(hand):
            value = 0
            aces = 0
            for card in hand:
                rank = card[0]
                if rank in ['J', 'Q', 'K']:
                    value += 10
                elif rank == 'A':
                    aces += 1
                    value += 11
                else:
                    value += int(rank)
            
            while value > 21 and aces:
                value -= 10
                aces -= 1
            return value
        
        def format_hand(hand, hide_first=False):
            if hide_first:
                return f"🎴 {hand[1][0]}{hand[1][1]}"
            return " ".join([f"{card[0]}{card[1]}" for card in hand])
        
        self.active_games[user_id] = {
            'type': 'blackjack',
            'deck': deck,
            'player_hand': player_hand,
            'dealer_hand': dealer_hand,
            'bet': bet
        }
        
        player_value = card_value(player_hand)
        
        # Vérifier blackjack naturel
        if player_value == 21:
            dealer_value = card_value(dealer_hand)
            if dealer_value == 21:
                # Égalité
                self.set_user_points(user_id, self.get_user_points(user_id) + bet)
                await ctx.send(f"🤝 Égalité ! Blackjack vs Blackjack\nVotre main: {format_hand(player_hand)} (21)\nCroupier: {format_hand(dealer_hand)} (21)")
            else:
                # Blackjack joueur
                winnings = round(bet * 2.5, 2)
                self.set_user_points(user_id, self.get_user_points(user_id) + winnings)
                self.update_user_stats(user_id, "blackjack", bet, True, winnings)
                await ctx.send(f"🎉 BLACKJACK ! Vous gagnez **{winnings}** points !\nVotre main: {format_hand(player_hand)} (21)\nCroupier: {format_hand(dealer_hand)} ({dealer_value})")
            
            del self.active_games[user_id]
            return
        
        embed = discord.Embed(
            title="🃏 BLACKJACK",
            color=0x00ff00
        )
        embed.add_field(name="Votre main", value=f"{format_hand(player_hand)} = **{player_value}**", inline=False)
        embed.add_field(name="Croupier", value=f"{format_hand(dealer_hand, True)} = **?**", inline=False)
        embed.add_field(name="Actions", value="Réagissez avec:\n👊 **Hit** (Prendre une carte)\n✋ **Stand** (Rester)", inline=False)
        
        game_msg = await ctx.send(embed=embed)
        await game_msg.add_reaction("👊")
        await game_msg.add_reaction("✋")
        
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["👊", "✋"] and reaction.message.id == game_msg.id
        
        while user_id in self.active_games:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=60.0)
                
                if str(reaction.emoji) == "👊":
                    # Hit
                    game_data = self.active_games[user_id]
                    game_data['player_hand'].append(game_data['deck'].pop())
                    player_value = card_value(game_data['player_hand'])
                    
                    if player_value > 21:
                        # Bust
                        self.update_user_stats(user_id, "blackjack", bet, False)
                        embed.title = "💥 BUST !"
                        embed.clear_fields()
                        embed.add_field(name="Votre main", value=f"{format_hand(game_data['player_hand'])} = **{player_value}**", inline=False)
                        embed.add_field(name="Résultat", value=f"Vous avez dépassé 21 ! Vous perdez **{bet}** points.", inline=False)
                        embed.color = 0xff0000
                        await game_msg.edit(embed=embed)
                        del self.active_games[user_id]
                        break
                    
                    embed.clear_fields()
                    embed.add_field(name="Votre main", value=f"{format_hand(game_data['player_hand'])} = **{player_value}**", inline=False)
                    embed.add_field(name="Croupier", value=f"{format_hand(game_data['dealer_hand'], True)} = **?**", inline=False)
                    embed.add_field(name="Actions", value="Réagissez avec:\n👊 **Hit** (Prendre une carte)\n✋ **Stand** (Rester)", inline=False)
                    await game_msg.edit(embed=embed)
                
                elif str(reaction.emoji) == "✋":
                    # Stand - Tour du croupier
                    game_data = self.active_games[user_id]
                    
                    dealer_value = card_value(game_data['dealer_hand'])
                    while dealer_value < 17:
                        game_data['dealer_hand'].append(game_data['deck'].pop())
                        dealer_value = card_value(game_data['dealer_hand'])
                    
                    player_value = card_value(game_data['player_hand'])
                    
                    # Déterminer le gagnant
                    if dealer_value > 21:
                        # Croupier bust
                        winnings = bet * 2
                        self.set_user_points(user_id, self.get_user_points(user_id) + winnings)
                        self.update_user_stats(user_id, "blackjack", bet, True, winnings)
                        result_text = f"Le croupier a dépassé 21 ! Vous gagnez **{winnings}** points !"
                        embed.color = 0x00ff00
                        embed.title = "🎉 VICTOIRE !"
                    elif player_value > dealer_value:
                        # Joueur gagne
                        winnings = bet * 2
                        self.set_user_points(user_id, self.get_user_points(user_id) + winnings)
                        self.update_user_stats(user_id, "blackjack", bet, True, winnings)
                        result_text = f"Vous gagnez **{winnings}** points !"
                        embed.color = 0x00ff00
                        embed.title = "🎉 VICTOIRE !"
                    elif player_value == dealer_value:
                        # Égalité
                        self.set_user_points(user_id, self.get_user_points(user_id) + bet)
                        result_text = "Égalité ! Vous récupérez votre mise."
                        embed.color = 0xffff00
                        embed.title = "🤝 ÉGALITÉ"
                    else:
                        # Croupier gagne
                        self.update_user_stats(user_id, "blackjack", bet, False)
                        result_text = f"Le croupier gagne ! Vous perdez **{bet}** points."
                        embed.color = 0xff0000
                        embed.title = "😞 DÉFAITE"
                    
                    embed.clear_fields()
                    embed.add_field(name="Votre main", value=f"{format_hand(game_data['player_hand'])} = **{player_value}**", inline=False)
                    embed.add_field(name="Croupier", value=f"{format_hand(game_data['dealer_hand'])} = **{dealer_value}**", inline=False)
                    embed.add_field(name="Résultat", value=result_text, inline=False)
                    await game_msg.edit(embed=embed)
                    del self.active_games[user_id]
                    break
                
                try:
                    await game_msg.remove_reaction(reaction.emoji, user)
                except:
                    pass
                
            except asyncio.TimeoutError:
                if user_id in self.active_games:
                    del self.active_games[user_id]
                await ctx.send("⏰ Temps écoulé ! Vous perdez votre mise.", delete_after=5)
                break

    @commands.command(name="roulette")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def roulette(self, ctx, bet: float, choice: str):
        """Roulette européenne"""
        user_id = ctx.author.id
        user_points = self.get_user_points(user_id)
        
        if bet <= 0:
            await ctx.send("🚫 Vous devez parier au moins 1 point.")
            return
        
        if user_points < bet:
            await ctx.send("❌ Vous n'avez pas assez de points pour ce pari.")
            return
        
        self.set_user_points(user_id, user_points - bet)
        
        # Numéros de la roulette européenne (0-36)
        numbers = list(range(37))  # 0 à 36
        red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        black_numbers = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
        
        result = random.choice(numbers)
        
        # Animation
        animation_msg = await ctx.send("🎰 La roulette tourne...")
        for _ in range(5):
            fake_result = random.choice(numbers)
            await animation_msg.edit(content=f"🎰 La roulette tourne... **{fake_result}**")
            await asyncio.sleep(0.4)
        
        # Déterminer la couleur du résultat
        if result == 0:
            result_color = "🟢 VERT"
        elif result in red_numbers:
            result_color = "🔴 ROUGE"
        else:
            result_color = "⚫ NOIR"
        
        won = False
        multiplier = 0
        
        choice = choice.lower()
        
        # Vérifier les différents types de paris
        if choice.isdigit() and 0 <= int(choice) <= 36:
            # Pari sur un numéro spécifique
            if int(choice) == result:
                won = True
                multiplier = 35
        elif choice in ["rouge", "red"]:
            if result in red_numbers:
                won = True
                multiplier = 1
        elif choice in ["noir", "black"]:
            if result in black_numbers:
                won = True
                multiplier = 1
        elif choice in ["pair", "even"]:
            if result != 0 and result % 2 == 0:
                won = True
                multiplier = 1
        elif choice in ["impair", "odd"]:
            if result != 0 and result % 2 == 1:
                won = True
                multiplier = 1
        elif choice == "manque" or choice == "low":  # 1-18
            if 1 <= result <= 18:
                won = True
                multiplier = 1
        elif choice == "passe" or choice == "high":  # 19-36
            if 19 <= result <= 36:
                won = True
                multiplier = 1
        else:
            await ctx.send("❌ Choix invalide ! Options: numéro (0-36), rouge/noir, pair/impair, manque/passe")
            self.set_user_points(user_id, self.get_user_points(user_id) + bet)  # Rembourser
            return
        
        if won:
            winnings = round(bet * (multiplier + 1), 2)  # +1 pour inclure la mise
            self.set_user_points(user_id, self.get_user_points(user_id) + winnings)
            self.update_user_stats(user_id, "roulette", bet, True, winnings)
            await animation_msg.edit(content=f"🎉 **{result}** {result_color}\nVous gagnez **{winnings}** points ! (x{multiplier + 1})")
        else:
            self.update_user_stats(user_id, "roulette", bet, False)
            await animation_msg.edit(content=f"😞 **{result}** {result_color}\nVous perdez **{bet}** points.")

    @commands.command(name="lottery")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def lottery(self, ctx, ticket_price: float = 100):
        """Système de loterie commune"""
        user_id = ctx.author.id
        user_points = self.get_user_points(user_id)
        
        if ticket_price < 10:
            await ctx.send("🚫 Le prix minimum d'un ticket est de 10 points.")
            return
        
        if user_points < ticket_price:
            await ctx.send("❌ Vous n'avez pas assez de points pour acheter ce ticket.")
            return
        
        self.set_user_points(user_id, user_points - ticket_price)
        
        # Simuler une loterie avec d'autres participants
        participants = random.randint(5, 20)  # Entre 5 et 20 participants
        total_pot = ticket_price * participants
        
        # 10% de chance de gagner
        if random.random() < 0.1:
            winnings = round(total_pot * 0.8, 2)  # 80% du pot (20% pour la maison)
            self.set_user_points(user_id, self.get_user_points(user_id) + winnings)
            self.update_user_stats(user_id, "lottery", ticket_price, True, winnings)
            
            embed = discord.Embed(
                title="🎫 LOTERIE - GAGNANT !",
                description=f"🎉 Félicitations {ctx.author.mention} !\nVous remportez **{winnings}** points !",
                color=0x00ff00
            )
            embed.add_field(name="Détails", value=f"Participants: {participants}\nPot total: {total_pot}\nVotre gain: {winnings}", inline=False)
        else:
            self.update_user_stats(user_id, "lottery", ticket_price, False)
            embed = discord.Embed(
                title="🎫 LOTERIE - Pas gagnant",
                description=f"😞 Pas de chance cette fois {ctx.author.mention}...",
                color=0xff0000
            )
            embed.add_field(name="Détails", value=f"Participants: {participants}\nPot total: {total_pot}\nVotre ticket: {ticket_price} points", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(name="poker")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def poker(self, ctx, bet: float):
        """Poker vidéo simple"""
        user_id = ctx.author.id
        user_points = self.get_user_points(user_id)
        
        if bet <= 0:
            await ctx.send("🚫 Vous devez parier au moins 1 point.")
            return
        
        if user_points < bet:
            await ctx.send("❌ Vous n'avez pas assez de points pour ce pari.")
            return
        
        self.set_user_points(user_id, user_points - bet)
        
        # Créer un deck
        suits = ['♠️', '♥️', '♦️', '♣️']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        deck = [(rank, suit) for suit in suits for rank in ranks]
        random.shuffle(deck)
        
        # Distribuer 5 cartes
        hand = [deck.pop() for _ in range(5)]
        
        def format_hand(cards):
            return " ".join([f"{card[0]}{card[1]}" for card in cards])
        
        def evaluate_hand(cards):
            # Convertir les rangs en valeurs numériques pour l'évaluation
            rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                          '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
            
            ranks = [card[0] for card in cards]
            suits = [card[1] for card in cards]
            rank_counts = {}
            
            for rank in ranks:
                rank_counts[rank] = rank_counts.get(rank, 0) + 1
            
            # Vérifier les combinaisons
            is_flush = len(set(suits)) == 1
            rank_values_sorted = sorted([rank_values[rank] for rank in ranks])
            is_straight = (rank_values_sorted == list(range(rank_values_sorted[0], rank_values_sorted[0] + 5))) or \
                         (rank_values_sorted == [2, 3, 4, 5, 14])  # As-2-3-4-5
            
            counts = sorted(rank_counts.values(), reverse=True)
            
            if is_straight and is_flush:
                if rank_values_sorted == [10, 11, 12, 13, 14]:
                    return ("Quinte Flush Royale", 250)
                return ("Quinte Flush", 50)
            elif counts == [4, 1]:
                return ("Carré", 25)
            elif counts == [3, 2]:
                return ("Full House", 9)
            elif is_flush:
                return ("Couleur", 6)
            elif is_straight:
                return ("Quinte", 4)
            elif counts == [3, 1, 1]:
                return ("Brelan", 3)
            elif counts == [2, 2, 1]:
                return ("Double Paire", 2)
            elif counts == [2, 1, 1, 1]:
                # Vérifier si c'est une paire de Valets ou mieux
                for rank, count in rank_counts.items():
                    if count == 2 and rank_values[rank] >= 11:
                        return ("Paire de Figures", 1)
                return ("Paire Faible", 0)
            else:
                return ("Hauteur", 0)
        
        hand_name, multiplier = evaluate_hand(hand)
        
        embed = discord.Embed(
            title="🃏 POKER VIDÉO",
            color=0x00ff00 if multiplier > 0 else 0xff0000
        )
        embed.add_field(name="Votre main", value=format_hand(hand), inline=False)
        embed.add_field(name="Combinaison", value=f"**{hand_name}**", inline=False)
        
        if multiplier > 0:
            winnings = round(bet * (multiplier + 1), 2)
            self.set_user_points(user_id, self.get_user_points(user_id) + winnings)
            self.update_user_stats(user_id, "poker", bet, True, winnings)
            embed.add_field(name="Résultat", value=f"🎉 Vous gagnez **{winnings}** points ! (x{multiplier + 1})", inline=False)
        else:
            self.update_user_stats(user_id, "poker", bet, False)
            embed.add_field(name="Résultat", value=f"😞 Pas de combinaison gagnante. Vous perdez **{bet}** points.", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(name="limbo")
    @commands.cooldown(1, 8, commands.BucketType.user)
    async def limbo(self, ctx, bet: float, target_multiplier: float):
        """Jeu limbo - Devinez si le résultat sera au-dessus de votre multiplicateur"""
        user_id = ctx.author.id
        user_points = self.get_user_points(user_id)
        
        if bet <= 0:
            await ctx.send("🚫 Vous devez parier au moins 1 point.")
            return
        
        if user_points < bet:
            await ctx.send("❌ Vous n'avez pas assez de points pour ce pari.")
            return
        
        if target_multiplier < 1.01 or target_multiplier > 100:
            await ctx.send("❌ Le multiplicateur doit être entre 1.01 et 100.")
            return
        
        self.set_user_points(user_id, user_points - bet)
        
        # Générer un résultat aléatoire
        result = round(random.uniform(1.0, 100.0), 2)
        
        # Animation
        animation_msg = await ctx.send(f"🎯 LIMBO - Cible: {target_multiplier}x")
        await asyncio.sleep(1)
        
        for _ in range(3):
            fake_result = round(random.uniform(1.0, 50.0), 2)
            await animation_msg.edit(content=f"🎯 LIMBO - Résultat: {fake_result}x...")
            await asyncio.sleep(0.5)
        
        if result >= target_multiplier:
            winnings = round(bet * target_multiplier, 2)
            self.set_user_points(user_id, self.get_user_points(user_id) + winnings)
            self.update_user_stats(user_id, "limbo", bet, True, winnings)
            await animation_msg.edit(content=f"🎉 GAGNÉ ! Résultat: **{result}x** (Cible: {target_multiplier}x)\nVous gagnez **{winnings}** points !")
        else:
            self.update_user_stats(user_id, "limbo", bet, False)
            await animation_msg.edit(content=f"😞 PERDU ! Résultat: **{result}x** (Cible: {target_multiplier}x)\nVous perdez **{bet}** points.")

    @commands.command(name="leaderboard", aliases=["lb", "top"])
    async def leaderboard(self, ctx):
        """Affiche le classement des joueurs"""
        try:
            if not os.path.exists(USER_DATA_FILE):
                await ctx.send("❌ Aucune donnée de joueur trouvée.")
                return
            
            with open(USER_DATA_FILE, "r") as f:
                data = json.load(f)
            
            # Trier les joueurs par points
            sorted_players = sorted(data.items(), key=lambda x: x[1].get("points", 0), reverse=True)
            
            if not sorted_players:
                await ctx.send("❌ Aucun joueur dans le classement.")
                return
            
            embed = discord.Embed(
                title="🏆 CLASSEMENT DES JOUEURS",
                color=0xFFD700
            )
            
            # Afficher le top 10
            for i, (user_id, user_data) in enumerate(sorted_players[:10]):
                try:
                    user = self.bot.get_user(int(user_id))
                    username = user.display_name if user else f"Utilisateur {user_id}"
                    points = user_data.get("points", 0)
                    
                    medal = ""
                    if i == 0:
                        medal = "🥇"
                    elif i == 1:
                        medal = "🥈"
                    elif i == 2:
                        medal = "🥉"
                    else:
                        medal = f"{i+1}."
                    
                    embed.add_field(
                        name=f"{medal} {username}",
                        value=f"**{points}** points",
                        inline=True
                    )
                except:
                    continue
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de l'affichage du classement: {e}")

    @commands.command(name="rsa")
    @commands.cooldown(1, 3600, commands.BucketType.user)  # 1 heure
    async def rsa(self, ctx):
        """Aide sociale - 100 points par heure"""
        user_id = ctx.author.id
        current_points = self.get_user_points(user_id)
        
        if current_points > 50:
            await ctx.send("❌ Vous avez plus de 50 points, vous n'êtes pas éligible au RSA !")
            return
        
        bonus = 100
        self.set_user_points(user_id, current_points + bonus)
        await ctx.send(f"🆘 {ctx.author.mention} Vous recevez une aide de **{bonus}** points !\nVotre solde: **{current_points + bonus}** points")

    @commands.command(name="donner", aliases=["give"])
    async def give_points(self, ctx, member: discord.Member, amount: float):
        """Donner des points à un autre joueur"""
        if member == ctx.author:
            await ctx.send("❌ Vous ne pouvez pas vous donner des points à vous-même !")
            return
        
        if amount <= 0:
            await ctx.send("❌ Vous devez donner au moins 1 point.")
            return
        
        giver_points = self.get_user_points(ctx.author.id)
        if giver_points < amount:
            await ctx.send("❌ Vous n'avez pas assez de points pour donner cette somme.")
            return
        
        # Effectuer le transfert
        self.set_user_points(ctx.author.id, giver_points - amount)
        receiver_points = self.get_user_points(member.id)
        self.set_user_points(member.id, receiver_points + amount)
        
        await ctx.send(f"✅ {ctx.author.mention} a donné **{amount}** points à {member.mention} !")

    @commands.command(name="stats")
    async def user_stats(self, ctx, member: discord.Member = None):
        """Affiche les statistiques d'un joueur"""
        if member is None:
            member = ctx.author
        
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
                    value=f"Parties: {games_played}\nVictoires: {games_won} ({win_rate:.1f}%)\nMisé: {total_bet_game}\nGagné: {total_winnings_game}",
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

    def get_user_data(self, user_id):
        """Récupère toutes les données d'un utilisateur"""
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
        """Récupère les points d'un utilisateur"""
        user_data = self.get_user_data(user_id)
        return user_data.get("points", 1000)  # 1000 points par défaut pour les nouveaux joueurs

    def set_user_points(self, user_id, points):
        """Définit les points d'un utilisateur"""
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
        """Met à jour les statistiques d'un utilisateur"""
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

    @commands.command(name="balance", aliases=["bal", "points"])
    async def balance(self, ctx, member: discord.Member = None):
        """Affiche le solde de points d'un utilisateur"""
        if member is None:
            member = ctx.author
        
        points = self.get_user_points(member.id)
        
        if member == ctx.author:
            await ctx.send(f"💰 {ctx.author.mention} Vous avez **{points}** points.")
        else:
            await ctx.send(f"💰 {member.display_name} a **{points}** points.")

    @commands.command(name="reset_points")
    @commands.has_permissions(administrator=True)
    async def reset_points(self, ctx, member: discord.Member = None):
        """Reset les points d'un utilisateur (Admin seulement)"""
        if member is None:
            member = ctx.author
        
        self.set_user_points(member.id, 1000)
        await ctx.send(f"✅ Les points de {member.display_name} ont été remis à 1000.")

    @commands.command(name="add_points")
    @commands.has_permissions(administrator=True)
    async def add_points(self, ctx, member: discord.Member, amount: float):
        """Ajoute des points à un utilisateur (Admin seulement)"""
        current_points = self.get_user_points(member.id)
        new_points = current_points + amount
        self.set_user_points(member.id, new_points)
        await ctx.send(f"✅ {amount} points ajoutés à {member.display_name}. Nouveau solde: {new_points}")

    @commands.command(name="casino_help", aliases=["chelp"])
    async def casino_help(self, ctx):
        """Affiche l'aide du casino"""
        embed = discord.Embed(
            title="🎰 AIDE DU CASINO",
            description="Voici tous les jeux disponibles:",
            color=0x00ff00
        )
        
        embed.add_field(
            name="🎰 Machine à sous",
            value="`!slot <mise>` - Alignez 3 symboles identiques!",
            inline=False
        )
        
        embed.add_field(
            name="🃏 Blackjack",
            value="`!blackjack <mise>` - Atteignez 21 sans dépasser!",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Roulette",
            value="`!roulette <mise> <choix>` - Rouge/noir, pair/impair, numéro...",
            inline=False
        )
        
        embed.add_field(
            name="🎫 Loterie",
            value="`!lottery <prix_ticket>` - 10% de chance de gagner le gros lot!",
            inline=False
        )
        
        embed.add_field(
            name="🃏 Poker",
            value="`!poker <mise>` - Obtenez la meilleure combinaison!",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Limbo",
            value="`!limbo <mise> <multiplicateur>` - Pariez sur un multiplicateur!",
            inline=False
        )
        
        embed.add_field(
            name="💰 Commandes utiles",
            value=f"`!balance` - Voir vos points\n`!stats` - Vos statistiques\n`!leaderboard` - Classement\n`!donner <@user> <montant>` - Donner des points\n`!rsa` - Aide sociale (100pts/h si <50pts)",
            inline=False
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Casino(bot))