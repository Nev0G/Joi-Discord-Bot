import discord
from discord.ext import commands, tasks
import random
import asyncio
import json
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
        try:
            with open(USER_DATA_FILE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_user_data(self):
        with open(USER_DATA_FILE, "w") as f:
            json.dump(self.user_data, f, indent=2)

    def get_user_points(self, user_id):
        with open(USER_DATA_FILE, "r") as f:
            data = json.load(f)
        return round(data.get(str(user_id), {}).get("points", 0), 2)

    def set_user_points(self, user_id, points):
        with open(USER_DATA_FILE, "r") as f:
            data = json.load(f)
        user_id = str(user_id)
        if user_id not in data:
            data[user_id] = {}
        data[user_id]["points"] = round(points, 2)
        with open(USER_DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def update_user_stats(self, user_id, game_type, bet, won, winnings=0):
        """Met à jour les statistiques de jeu d'un utilisateur"""
        with open(USER_DATA_FILE, "r") as f:
            data = json.load(f)
        
        user_id = str(user_id)
        if user_id not in data:
            data[user_id] = {}
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
                await msg.delete()
                
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
        
        with open(USER_DATA_FILE, "r") as f:
            data = json.load(f)
        
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
        
        for _ in range(3):
            for _ in range(3):
                slots = random.choices(symbols, k=3)
                await animation_message.edit(content=f"🎰 {ctx.author.mention} Machine à sous: {' | '.join(slots)}")
                await asyncio.sleep(0.2)
        
        if len(set(slots)) == 1:  # Triple
            winnings = int(bet * (multipliers[slots[0]] + 20))
            self.update_user_stats(user_id, "slot", bet, True, winnings)
            await ctx.send(f"🤑 JACKPOT! Vous avez gagné **{winnings}** points!")
        elif len(set(slots)) == 2:  # Paire
            winnings = int(bet * multipliers[slots[0]] + 1)
            self.update_user_stats(user_id, "slot", bet, True, winnings)
            await ctx.send(f"🎁 Petit gain! Vous récupérez **{winnings}** points!")
        else:  # Aucun doublon
            winnings = int(bet * (multipliers[slots[0]]))
            self.update_user_stats(user_id, "slot", bet, False)
            await ctx.send(f"😭 Perdu ! Vous récupérez **{winnings}** points!")
            random_gif = random.choice([
                "https://media1.tenor.com/m/cn5GW2a9qtUAAAAC/laughing-emoji-laughing.gif",
                "https://media1.tenor.com/m/BbjFm-pfueUAAAAd/laughing-emoji-laughing.gif",
                "https://media1.tenor.com/m/dFDlIvZo544AAAAC/meme-laugh.gif",
            ])
            await ctx.send(random_gif)
        
        new_points = self.get_user_points(user_id) + winnings
        self.set_user_points(user_id, new_points)
        await ctx.send(f"{ctx.author.mention} 📊 Vous avez maintenant **{new_points}** points.")


async def setup(bot):
    await bot.add_cog(Casino(bot))

