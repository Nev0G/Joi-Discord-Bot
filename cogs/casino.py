import discord
from discord.ext import commands
import json
import os
import random
import asyncio
from datetime import datetime, timedelta

USER_DATA_FILE = "user_data.json"

class Casino(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}  # Pour stocker les jeux en cours

    def load_user_data(self):
        """Charge les données des utilisateurs depuis le fichier JSON"""
        try:
            if os.path.exists(USER_DATA_FILE):
                with open(USER_DATA_FILE, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Erreur lors de la lecture des données: {e}")
            return {}

    def save_user_data(self, data):
        """Sauvegarde les données des utilisateurs"""
        try:
            with open(USER_DATA_FILE, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")

    def get_user_data(self, user_id):
        """Récupère les données d'un utilisateur spécifique"""
        data = self.load_user_data()
        user_str = str(user_id)
        
        if user_str not in data:
            data[user_str] = {
                "points": 1000,
                "daily_claimed": None,
                "weekly_claimed": None
            }
            self.save_user_data(data)
        
        return data[user_str]

    def update_user_points(self, user_id, points):
        """Met à jour les points d'un utilisateur"""
        data = self.load_user_data()
        user_str = str(user_id)
        
        if user_str not in data:
            data[user_str] = {"points": 1000, "daily_claimed": None, "weekly_claimed": None}
        
        data[user_str]["points"] = points
        self.save_user_data(data)

    def get_user_points(self, user_id):
        """Récupère les points d'un utilisateur"""
        user_data = self.get_user_data(user_id)
        return user_data.get("points", 1000)

    def card_value(self, card):
        """Calcule la valeur d'une carte pour le blackjack"""
        if card in ['J', 'Q', 'K']:
            return 10
        elif card == 'A':
            return 11
        else:
            return int(card)

    def hand_value(self, hand):
        """Calcule la valeur totale d'une main au blackjack"""
        value = 0
        aces = 0
        
        for card in hand:
            if card == 'A':
                aces += 1
                value += 11
            else:
                value += self.card_value(card)
        
        # Gestion des As
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        
        return value

    @commands.command(name="points", aliases=["balance", "bal"])
    async def check_points(self, ctx):
        """Vérifie le solde de points de l'utilisateur"""
        points = self.get_user_points(ctx.author.id)
        embed = discord.Embed(
            title="💰 Votre solde",
            description=f"Vous avez **{points:,}** points !",
            color=0x00FF00
        )
        await ctx.send(embed=embed)

    @commands.command(name="slot", aliases=["slots"])
    async def slot_machine(self, ctx, bet: int = None):
        """Machine à sous"""
        if bet is None:
            await ctx.send("❌ Vous devez spécifier une mise ! Exemple: `j!slot 100`")
            return
        
        if bet < 10:
            await ctx.send("❌ La mise minimum est de 10 points !")
            return
        
        user_points = self.get_user_points(ctx.author.id)
        
        if bet > user_points:
            await ctx.send("❌ Vous n'avez pas assez de points !")
            return
        
        symbols = ["🍎", "🍊", "🍇", "🍒", "🍋", "⭐", "💎"]
        weights = [25, 25, 20, 15, 10, 4, 1]
        
        result = random.choices(symbols, weights=weights, k=3)
        
        multiplier = 0
        if result[0] == result[1] == result[2]:
            if result[0] == "💎":
                multiplier = 10
            elif result[0] == "⭐":
                multiplier = 5
            elif result[0] == "🍋":
                multiplier = 3
            else:
                multiplier = 2
        elif result[0] == result[1] or result[1] == result[2] or result[0] == result[2]:
            multiplier = 0.5
        
        winnings = int(bet * multiplier)
        new_points = user_points - bet + winnings
        self.update_user_points(ctx.author.id, new_points)
        
        embed = discord.Embed(title="🎰 Machine à sous", color=0xFFD700)
        embed.add_field(name="Résultat", value=f"{result[0]} {result[1]} {result[2]}", inline=False)
        
        if winnings > bet:
            embed.add_field(name="🎉 Vous avez gagné !", value=f"+{winnings-bet} points", inline=False)
            embed.color = 0x00FF00
        elif winnings == bet:
            embed.add_field(name="🔄 Égalité", value="Mise récupérée", inline=False)
            embed.color = 0xFFFF00
        else:
            embed.add_field(name="💸 Vous avez perdu", value=f"-{bet} points", inline=False)
            embed.color = 0xFF0000
        
        embed.add_field(name="💰 Nouveau solde", value=f"{new_points:,} points", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="blackjack", aliases=["bj"])
    async def blackjack(self, ctx, bet: int = None):
        """Jeu de Blackjack"""
        if bet is None:
            await ctx.send("❌ Usage: `j!blackjack <mise>`")
            return
        
        if bet < 10:
            await ctx.send("❌ La mise minimum est de 10 points !")
            return
        
        user_points = self.get_user_points(ctx.author.id)
        if bet > user_points:
            await ctx.send("❌ Vous n'avez pas assez de points !")
            return
        
        # Initialisation du jeu
        deck = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] * 4
        random.shuffle(deck)
        
        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]
        
        game_data = {
            'deck': deck,
            'player_hand': player_hand,
            'dealer_hand': dealer_hand,
            'bet': bet,
            'finished': False
        }
        
        self.active_games[ctx.author.id] = game_data
        
        player_value = self.hand_value(player_hand)
        dealer_visible = self.hand_value([dealer_hand[0]])
        
        embed = discord.Embed(title="🃏 Blackjack", color=0x000000)
        embed.add_field(name="Votre main", value=f"{' '.join(player_hand)} (Valeur: {player_value})", inline=False)
        embed.add_field(name="Main du croupier", value=f"{dealer_hand[0]} ? (Valeur visible: {dealer_visible})", inline=False)
        
        if player_value == 21:
            # Blackjack naturel
            embed.add_field(name="🎉 BLACKJACK !", value="Vous avez gagné !", inline=False)
            winnings = int(bet * 2.5)
            new_points = user_points + winnings - bet
            self.update_user_points(ctx.author.id, new_points)
            embed.add_field(name="💰 Gain", value=f"+{winnings-bet} points", inline=False)
            embed.color = 0x00FF00
            del self.active_games[ctx.author.id]
        else:
            embed.add_field(name="Actions", value="Tapez `j!hit` pour tirer une carte ou `j!stand` pour rester", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(name="hit")
    async def blackjack_hit(self, ctx):
        """Tirer une carte au blackjack"""
        if ctx.author.id not in self.active_games:
            await ctx.send("❌ Vous n'avez pas de partie de blackjack en cours !")
            return
        
        game = self.active_games[ctx.author.id]
        if game['finished']:
            await ctx.send("❌ Cette partie est terminée !")
            return
        
        # Tirer une carte
        card = game['deck'].pop()
        game['player_hand'].append(card)
        
        player_value = self.hand_value(game['player_hand'])
        
        embed = discord.Embed(title="🃏 Blackjack - Carte tirée", color=0x000000)
        embed.add_field(name="Votre main", value=f"{' '.join(game['player_hand'])} (Valeur: {player_value})", inline=False)
        
        if player_value > 21:
            # Bust
            embed.add_field(name="💥 BUST !", value="Vous avez dépassé 21 !", inline=False)
            embed.color = 0xFF0000
            user_points = self.get_user_points(ctx.author.id)
            new_points = user_points - game['bet']
            self.update_user_points(ctx.author.id, new_points)
            embed.add_field(name="💸 Perte", value=f"-{game['bet']} points", inline=False)
            del self.active_games[ctx.author.id]
        elif player_value == 21:
            embed.add_field(name="🎯 21 !", value="Parfait ! Tapez `j!stand` pour voir le résultat", inline=False)
        else:
            embed.add_field(name="Actions", value="Tapez `j!hit` pour tirer une carte ou `j!stand` pour rester", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(name="stand")
    async def blackjack_stand(self, ctx):
        """Rester au blackjack"""
        if ctx.author.id not in self.active_games:
            await ctx.send("❌ Vous n'avez pas de partie de blackjack en cours !")
            return
        
        game = self.active_games[ctx.author.id]
        
        # Le croupier tire jusqu'à 17
        while self.hand_value(game['dealer_hand']) < 17:
            game['dealer_hand'].append(game['deck'].pop())
        
        player_value = self.hand_value(game['player_hand'])
        dealer_value = self.hand_value(game['dealer_hand'])
        
        embed = discord.Embed(title="🃏 Blackjack - Résultat final", color=0x000000)
        embed.add_field(name="Votre main", value=f"{' '.join(game['player_hand'])} (Valeur: {player_value})", inline=False)
        embed.add_field(name="Main du croupier", value=f"{' '.join(game['dealer_hand'])} (Valeur: {dealer_value})", inline=False)
        
        user_points = self.get_user_points(ctx.author.id)
        
        if dealer_value > 21:
            # Croupier bust
            embed.add_field(name="🎉 Victoire !", value="Le croupier a dépassé 21 !", inline=False)
            winnings = game['bet'] * 2
            new_points = user_points + winnings - game['bet']
            embed.color = 0x00FF00
            embed.add_field(name="💰 Gain", value=f"+{game['bet']} points", inline=False)
        elif player_value > dealer_value:
            # Joueur gagne
            embed.add_field(name="🎉 Victoire !", value="Votre main est plus forte !", inline=False)
            winnings = game['bet'] * 2
            new_points = user_points + winnings - game['bet']
            embed.color = 0x00FF00
            embed.add_field(name="💰 Gain", value=f"+{game['bet']} points", inline=False)
        elif player_value == dealer_value:
            # Égalité
            embed.add_field(name="🤝 Égalité", value="Même valeur !", inline=False)
            new_points = user_points  # Pas de perte
            embed.color = 0xFFFF00
        else:
            # Croupier gagne
            embed.add_field(name="😞 Défaite", value="Le croupier a une main plus forte", inline=False)
            new_points = user_points - game['bet']
            embed.color = 0xFF0000
            embed.add_field(name="💸 Perte", value=f"-{game['bet']} points", inline=False)
        
        self.update_user_points(ctx.author.id, new_points)
        embed.add_field(name="💰 Nouveau solde", value=f"{new_points:,} points", inline=False)
        del self.active_games[ctx.author.id]
        await ctx.send(embed=embed)

    @commands.command(name="roulette")
    async def roulette(self, ctx, bet: int = None, choice: str = None):
        """Jeu de la roulette"""
        if bet is None or choice is None:
            embed = discord.Embed(title="🎡 Roulette - Aide", color=0x800080)
            embed.add_field(name="Usage", value="`j!roulette <mise> <choix>`", inline=False)
            embed.add_field(name="Choix disponibles", value="""
            • **Nombres** : 0-36 (x36)
            • **rouge** : Cases rouges (x2)
            • **noir** : Cases noires (x2)
            • **pair** : Nombres pairs (x2)
            • **impair** : Nombres impairs (x2)
            • **bas** : 1-18 (x2)
            • **haut** : 19-36 (x2)
            """, inline=False)
            await ctx.send(embed=embed)
            return
        
        if bet < 10:
            await ctx.send("❌ La mise minimum est de 10 points !")
            return
        
        user_points = self.get_user_points(ctx.author.id)
        if bet > user_points:
            await ctx.send("❌ Vous n'avez pas assez de points !")
            return
        
        # Numéros rouges et noirs
        red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        black_numbers = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
        
        result = random.randint(0, 36)
        choice = choice.lower()
        
        embed = discord.Embed(title="🎡 Roulette", color=0x800080)
        embed.add_field(name="Numéro gagnant", value=f"**{result}**", inline=True)
        
        # Couleur du résultat
        if result == 0:
            color_name = "Vert"
        elif result in red_numbers:
            color_name = "Rouge"
        else:
            color_name = "Noir"
        
        embed.add_field(name="Couleur", value=color_name, inline=True)
        embed.add_field(name="Votre mise", value=choice.capitalize(), inline=True)
        
        won = False
        multiplier = 0
        
        # Vérifier les gains
        if choice.isdigit() and 0 <= int(choice) <= 36:
            if int(choice) == result:
                won = True
                multiplier = 36
        elif choice == "rouge" and result in red_numbers:
            won = True
            multiplier = 2
        elif choice == "noir" and result in black_numbers:
            won = True
            multiplier = 2
        elif choice == "pair" and result != 0 and result % 2 == 0:
            won = True
            multiplier = 2
        elif choice == "impair" and result % 2 == 1:
            won = True
            multiplier = 2
        elif choice == "bas" and 1 <= result <= 18:
            won = True
            multiplier = 2
        elif choice == "haut" and 19 <= result <= 36:
            won = True
            multiplier = 2
        
        if won:
            winnings = bet * multiplier
            new_points = user_points + winnings - bet
            embed.add_field(name="🎉 Vous avez gagné !", value=f"+{winnings-bet} points", inline=False)
            embed.color = 0x00FF00
        else:
            new_points = user_points - bet
            embed.add_field(name="💸 Vous avez perdu", value=f"-{bet} points", inline=False)
            embed.color = 0xFF0000
        
        embed.add_field(name="💰 Nouveau solde", value=f"{new_points:,} points", inline=False)
        self.update_user_points(ctx.author.id, new_points)
        await ctx.send(embed=embed)

    @commands.command(name="mines")
    async def mines(self, ctx, bet: int = None, mines_count: int = None):
        """Jeu du démineur"""
        if bet is None or mines_count is None:
            await ctx.send("❌ Usage: `j!mines <mise> <nombre de mines (1-24)>`")
            return
        
        if bet < 10:
            await ctx.send("❌ La mise minimum est de 10 points !")
            return
        
        if not 1 <= mines_count <= 24:
            await ctx.send("❌ Le nombre de mines doit être entre 1 et 24 !")
            return
        
        user_points = self.get_user_points(ctx.author.id)
        if bet > user_points:
            await ctx.send("❌ Vous n'avez pas assez de points !")
            return
        
        # Créer la grille 5x5
        grid = ['💎'] * 25
        mine_positions = random.sample(range(25), mines_count)
        
        for pos in mine_positions:
            grid[pos] = '💣'
        
        game_data = {
            'grid': grid,
            'revealed': [False] * 25,
            'bet': bet,
            'mines_count': mines_count,
            'gems_found': 0,
            'multiplier': 1.0,
            'finished': False
        }
        
        self.active_games[ctx.author.id] = game_data
        
        embed = discord.Embed(title="💣 Mines", color=0x8B4513)
        embed.add_field(name="Grille", value=self.format_mines_grid(game_data), inline=False)
        embed.add_field(name="Info", value=f"💣 {mines_count} mines | 💎 {25-mines_count} gemmes", inline=False)
        embed.add_field(name="Instructions", value="Tapez `j!pick <numéro>` pour révéler une case (1-25)\nTapez `j!cashout` pour encaisser vos gains", inline=False)
        
        await ctx.send(embed=embed)

    def format_mines_grid(self, game_data):
        """Formate la grille du jeu mines"""
        grid_display = []
        for i in range(25):
            if game_data['revealed'][i]:
                if game_data['grid'][i] == '💣':
                    grid_display.append('💥')
                else:
                    grid_display.append('💎')
            else:
                grid_display.append(f'{i+1:02d}')
        
        # Formater en grille 5x5
        formatted = ""
        for i in range(5):
            row = []
            for j in range(5):
                idx = i * 5 + j
                row.append(grid_display[idx])
            formatted += " ".join(row) + "\n"
        
        return f"```{formatted}```"

    @commands.command(name="pick")
    async def mines_pick(self, ctx, position: int = None):
        """Révéler une case dans le jeu mines"""
        if ctx.author.id not in self.active_games:
            await ctx.send("❌ Vous n'avez pas de partie de mines en cours !")
            return
        
        if position is None:
            await ctx.send("❌ Spécifiez une position (1-25) !")
            return
        
        if not 1 <= position <= 25:
            await ctx.send("❌ La position doit être entre 1 et 25 !")
            return
        
        game = self.active_games[ctx.author.id]
        if game['finished']:
            await ctx.send("❌ Cette partie est terminée !")
            return
        
        pos_idx = position - 1
        
        if game['revealed'][pos_idx]:
            await ctx.send("❌ Cette case a déjà été révélée !")
            return
        
        game['revealed'][pos_idx] = True
        
        embed = discord.Embed(title="💣 Mines", color=0x8B4513)
        
        if game['grid'][pos_idx] == '💣':
            # Mine touchée !
            embed.add_field(name="💥 BOOM !", value="Vous avez touché une mine !", inline=False)
            embed.add_field(name="Grille", value=self.format_mines_grid(game), inline=False)
            embed.color = 0xFF0000
            
            user_points = self.get_user_points(ctx.author.id)
            new_points = user_points - game['bet']
            self.update_user_points(ctx.author.id, new_points)
            embed.add_field(name="💸 Perte", value=f"-{game['bet']} points", inline=False)
            embed.add_field(name="💰 Nouveau solde", value=f"{new_points:,} points", inline=False)
            del self.active_games[ctx.author.id]
        else:
            # Gemme trouvée !
            game['gems_found'] += 1
            
            # Calculer le multiplicateur
            gems_remaining = 25 - game['mines_count'] - game['gems_found']
            if gems_remaining > 0:
                game['multiplier'] = round(1 + (game['gems_found'] * 0.5), 2)
            
            potential_winnings = int(game['bet'] * game['multiplier'])
            
            embed.add_field(name="💎 Gemme trouvée !", value=f"Gemmes trouvées: {game['gems_found']}", inline=False)
            embed.add_field(name="Grille", value=self.format_mines_grid(game), inline=False)
            embed.add_field(name="💰 Gains potentiels", value=f"{potential_winnings-game['bet']} points (x{game['multiplier']})", inline=False)
            
            if gems_remaining == 0:
                # Toutes les gemmes trouvées !
                embed.add_field(name="🏆 PARFAIT !", value="Vous avez trouvé toutes les gemmes !", inline=False)
                user_points = self.get_user_points(ctx.author.id)
                final_winnings = int(game['bet'] * (game['multiplier'] + 1))  # Bonus pour perfection
                new_points = user_points + final_winnings - game['bet']
                self.update_user_points(ctx.author.id, new_points)
                embed.add_field(name="🎉 Gain final", value=f"+{final_winnings-game['bet']} points (bonus parfait !)", inline=False)
                embed.color = 0x00FF00
                del self.active_games[ctx.author.id]
            else:
                embed.add_field(name="Actions", value="Tapez `j!pick <numéro>` pour continuer ou `j!cashout` pour encaisser", inline=False)
                embed.color = 0x00AA00
        
        await ctx.send(embed=embed)

    @commands.command(name="cashout")
    async def mines_cashout(self, ctx):
        """Encaisser les gains du jeu mines"""
        if ctx.author.id not in self.active_games:
            await ctx.send("❌ Vous n'avez pas de partie de mines en cours !")
            return
        
        game = self.active_games[ctx.author.id]
        
        if game['gems_found'] == 0:
            await ctx.send("❌ Vous devez trouver au moins une gemme avant d'encaisser !")
            return
        
        user_points = self.get_user_points(ctx.author.id)
        winnings = int(game['bet'] * game['multiplier'])
        new_points = user_points + winnings - game['bet']
        self.update_user_points(ctx.author.id, new_points)
        
        embed = discord.Embed(title="💰 Encaissement réussi !", color=0x00FF00)
        embed.add_field(name="Gemmes trouvées", value=f"{game['gems_found']}", inline=True)
        embed.add_field(name="Multiplicateur", value=f"x{game['multiplier']}", inline=True)
        embed.add_field(name="Gain", value=f"+{winnings-game['bet']} points", inline=False)
        embed.add_field(name="💰 Nouveau solde", value=f"{new_points:,} points", inline=False)
        
        del self.active_games[ctx.author.id]
        await ctx.send(embed=embed)

    @commands.command(name="crash")
    async def crash_game(self, ctx, bet: int = None):
        """Jeu Crash"""
        if bet is None:
            await ctx.send("❌ Usage: `j!crash <mise>`")
            return
        
        if bet < 10:
            await ctx.send("❌ La mise minimum est de 10 points !")
            return
        
        user_points = self.get_user_points(ctx.author.id)
        if bet > user_points:
            await ctx.send("❌ Vous n'avez pas assez de points !")
            return
        
        # Générer le multiplicateur de crash (entre 1.0 et 100.0)
        # Plus de chances d'avoir un crash bas
        crash_point = round(random.uniform(1.0, 100.0) ** (1/3), 2)
        
        embed = discord.Embed(title="🚀 Crash Game", color=0xFF4500)
        embed.add_field(name="🚀 Décollage !", value="L'avion décolle...", inline=False)
        
        message = await ctx.send(embed=embed)
        
        current_multiplier = 1.0
        
        # Animation du multiplicateur qui monte
        for _ in range(20):  # 20 étapes
            await asyncio.sleep(0.8)
            current_multiplier += random.uniform(0.1, 0.5)
            
            embed = discord.Embed(title="🚀 Crash Game", color=0xFF4500)
            embed.add_field(name="Multiplicateur actuel", value=f"**{current_multiplier:.2f}x**", inline=False)
            
            if current_multiplier >= crash_point:
                # CRASH !
                embed.add_field(name="💥 CRASH !", value=f"L'avion s'est écrasé à **{crash_point}x** !", inline=False)
                embed.add_field(name="💸 Résultat", value="Vous avez perdu votre mise", inline=False)
                embed.color = 0xFF0000
                
                new_points = user_points - bet
                self.update_user_points(ctx.author.id, new_points)
                embed.add_field(name="💰 Nouveau solde", value=f"{new_points:,} points", inline=False)
                await message.edit(embed=embed)
                return
            
            # Chance de sortir automatiquement (35%)
            if random.random() < 0.35:
                # Sortie automatique !
                winnings = int(bet * current_multiplier)
                embed.add_field(name="✅ Sortie automatique !", value=f"Vous avez encaissé à **{current_multiplier:.2f}x** !", inline=False)
                embed.add_field(name="🎉 Gain", value=f"+{winnings-bet} points", inline=False)
                embed.color = 0x00FF00
                
                new_points = user_points + winnings - bet
                self.update_user_points(ctx.author.id, new_points)
                embed.add_field(name="💰 Nouveau solde", value=f"{new_points:,} points", inline=False)
                await message.edit(embed=embed)
                return
            
            await message.edit(embed=embed)
        
        # Si on arrive ici, c'est un très gros multiplicateur
        winnings = int(bet * current_multiplier)
        embed = discord.Embed(title="🚀 Crash Game - JACKPOT !", color=0xFFD700)
        embed.add_field(name="🏆 INCROYABLE !", value=f"Vous avez encaissé à **{current_multiplier:.2f}x** !", inline=False)
        embed.add_field(name="🎉 MEGA GAIN", value=f"+{winnings-bet} points", inline=False)
        
        new_points = user_points + winnings - bet
        self.update_user_points(ctx.author.id, new_points)
        embed.add_field(name="💰 Nouveau solde", value=f"{new_points:,} points", inline=False)
        await message.edit(embed=embed)

    @commands.command(name="coinflip", aliases=["pf"])
    async def coinflip(self, ctx, bet: int = None, choice: str = None):
        """Pile ou Face"""
        if bet is None or choice is None:
            await ctx.send("❌ Usage: `j!coinflip <mise> <pile/face>`")
            return
        
        if bet < 10:
            await ctx.send("❌ La mise minimum est de 10 points !")
            return
        
        user_points = self.get_user_points(ctx.author.id)
        if bet > user_points:
            await ctx.send("❌ Vous n'avez pas assez de points !")
            return
        
        choice = choice.lower()
        if choice not in ['pile', 'face']:
            await ctx.send("❌ Choisissez 'pile' ou 'face' !")
            return
        
        result = random.choice(['pile', 'face'])
        
        embed = discord.Embed(title="🪙 Pile ou Face", color=0xFFD700)
        embed.add_field(name="Votre choix", value=choice.capitalize(), inline=True)
        embed.add_field(name="Résultat", value=result.capitalize(), inline=True)
        
        if choice == result:
            winnings = bet * 2
            new_points = user_points + winnings - bet
            embed.add_field(name="🎉 Vous avez gagné !", value=f"+{bet} points", inline=False)
            embed.color = 0x00FF00
        else:
            new_points = user_points - bet
            embed.add_field(name="💸 Vous avez perdu", value=f"-{bet} points", inline=False)
            embed.color = 0xFF0000
        
        embed.add_field(name="💰 Nouveau solde", value=f"{new_points:,} points", inline=False)
        self.update_user_points(ctx.author.id, new_points)
        await ctx.send(embed=embed)

    @commands.command(name="dice", aliases=["dé"])
    async def dice_game(self, ctx, bet: int = None, guess: int = None):
        """Jeu de dés"""
        if bet is None or guess is None:
            await ctx.send("❌ Usage: `j!dice <mise> <nombre entre 1-6>`")
            return
        
        if bet < 10:
            await ctx.send("❌ La mise minimum est de 10 points !")
            return
        
        if not 1 <= guess <= 6:
            await ctx.send("❌ Le nombre doit être entre 1 et 6 !")
            return
        
        user_points = self.get_user_points(ctx.author.id)
        if bet > user_points:
            await ctx.send("❌ Vous n'avez pas assez de points !")
            return
        
        result = random.randint(1, 6)
        
        embed = discord.Embed(title="🎲 Jeu de Dés", color=0x8B4513)
        embed.add_field(name="Votre nombre", value=str(guess), inline=True)
        embed.add_field(name="Résultat", value=str(result), inline=True)
        
        if guess == result:
            winnings = bet * 6
            new_points = user_points + winnings - bet
            embed.add_field(name="🎯 Parfait !", value=f"+{winnings-bet} points (x6)", inline=False)
            embed.color = 0x00FF00
        else:
            new_points = user_points - bet
            embed.add_field(name="💸 Raté", value=f"-{bet} points", inline=False)
            embed.color = 0xFF0000
        
        embed.add_field(name="💰 Nouveau solde", value=f"{new_points:,} points", inline=False)
        self.update_user_points(ctx.author.id, new_points)
        await ctx.send(embed=embed)

    @commands.command(name="limbo")
    async def limbo_game(self, ctx, bet: int = None, target: float = None):
        """Jeu Limbo"""
        if bet is None or target is None:
            await ctx.send("❌ Usage: `j!limbo <mise> <multiplicateur target (1.1-100)>`")
            return
        
        if bet < 10:
            await ctx.send("❌ La mise minimum est de 10 points !")
            return
        
        if not 1.1 <= target <= 100:
            await ctx.send("❌ Le multiplicateur doit être entre 1.1 et 100 !")
            return
        
        user_points = self.get_user_points(ctx.author.id)
        if bet > user_points:
            await ctx.send("❌ Vous n'avez pas assez de points !")
            return
        
        # Générer un nombre aléatoire avec une distribution qui favorise les petits nombres
        result = round(random.uniform(1.0, 1000.0) ** (1/2.5), 2)
        
        embed = discord.Embed(title="📉 Limbo", color=0x9932CC)
        embed.add_field(name="Votre target", value=f"{target}x", inline=True)
        embed.add_field(name="Résultat", value=f"{result}x", inline=True)
        
        if result >= target:
            winnings = int(bet * target)
            new_points = user_points + winnings - bet
            embed.add_field(name="🎉 Gagné !", value=f"+{winnings-bet} points", inline=False)
            embed.color = 0x00FF00
        else:
            new_points = user_points - bet
            embed.add_field(name="💸 Perdu", value=f"-{bet} points", inline=False)
            embed.color = 0xFF0000
        
        embed.add_field(name="💰 Nouveau solde", value=f"{new_points:,} points", inline=False)
        self.update_user_points(ctx.author.id, new_points)
        await ctx.send(embed=embed)

    @commands.command(name="wheel", aliases=["roue"])
    async def wheel_game(self, ctx, bet: int = None):
        """Roue de la fortune"""
        if bet is None:
            await ctx.send("❌ Usage: `j!wheel <mise>`")
            return
        
        if bet < 10:
            await ctx.send("❌ La mise minimum est de 10 points !")
            return
        
        user_points = self.get_user_points(ctx.author.id)
        if bet > user_points:
            await ctx.send("❌ Vous n'avez pas assez de points !")
            return
        
        # Segments de la roue avec leurs probabilités et multiplicateurs
        segments = [
            {"name": "💸 Banqueroute", "multiplier": 0, "weight": 5},
            {"name": "😐 x0.5", "multiplier": 0.5, "weight": 15},
            {"name": "🔄 x1", "multiplier": 1, "weight": 25},
            {"name": "🎉 x2", "multiplier": 2, "weight": 20},
            {"name": "💰 x3", "multiplier": 3, "weight": 15},
            {"name": "🏆 x5", "multiplier": 5, "weight": 10},
            {"name": "💎 x10", "multiplier": 10, "weight": 8},
            {"name": "🌟 x50", "multiplier": 50, "weight": 2}
        ]
        
        # Animation de la roue
        embed = discord.Embed(title="🎡 Roue de la Fortune", description="🎲 La roue tourne...", color=0xFF69B4)
        message = await ctx.send(embed=embed)
        
        for i in range(8):
            await asyncio.sleep(0.5)
            fake_segment = random.choice(segments)
            embed.description = f"🎲 {fake_segment['name']}"
            await message.edit(embed=embed)
        
        # Résultat final
        result = random.choices(segments, weights=[s["weight"] for s in segments])[0]
        
        embed = discord.Embed(title="🎡 Roue de la Fortune", color=0xFF69B4)
        embed.add_field(name="Résultat", value=result["name"], inline=False)
        
        if result["multiplier"] == 0:
            new_points = user_points - bet
            embed.add_field(name="💸 Perte totale", value=f"-{bet} points", inline=False)
            embed.color = 0xFF0000
        else:
            winnings = int(bet * result["multiplier"])
            gain_loss = winnings - bet
            new_points = user_points + gain_loss
            
            if gain_loss > 0:
                embed.add_field(name="🎉 Gain", value=f"+{gain_loss} points", inline=False)
                embed.color = 0x00FF00
            elif gain_loss < 0:
                embed.add_field(name="💸 Perte", value=f"{gain_loss} points", inline=False)
                embed.color = 0xFF0000
            else:
                embed.add_field(name="🔄 Égalité", value="Mise récupérée", inline=False)
                embed.color = 0xFFFF00
        
        embed.add_field(name="💰 Nouveau solde", value=f"{new_points:,} points", inline=False)
        self.update_user_points(ctx.author.id, new_points)
        await message.edit(embed=embed)

    @commands.command(name="daily")
    async def daily_bonus(self, ctx):
        """Bonus quotidien"""
        user_data = self.get_user_data(ctx.author.id)
        now = datetime.now()
        
        if user_data.get("daily_claimed"):
            last_claim = datetime.fromisoformat(user_data["daily_claimed"])
            if (now - last_claim).total_seconds() < 86400:  # 24 heures
                next_claim = last_claim + timedelta(days=1)
                embed = discord.Embed(
                    title="⏰ Bonus quotidien déjà réclamé",
                    description=f"Prochain bonus disponible : <t:{int(next_claim.timestamp())}:R>",
                    color=0xFF0000
                )
                await ctx.send(embed=embed)
                return
        
        bonus = random.randint(500, 1000)
        data = self.load_user_data()
        user_str = str(ctx.author.id)
        
        if user_str not in data:
            data[user_str] = {"points": 1000, "daily_claimed": None, "weekly_claimed": None}
        
        data[user_str]["points"] += bonus
        data[user_str]["daily_claimed"] = now.isoformat()
        self.save_user_data(data)
        
        embed = discord.Embed(
            title="🍋 Bonus quotidien réclamé !",
            description=f"Vous avez reçu **{bonus}** points !\nNouveau solde: **{data[user_str]['points']:,}** points",
            color=0x00FF00
        )
        await ctx.send(embed=embed)

    @commands.command(name="weekly")
    async def weekly_bonus(self, ctx):
        """Bonus hebdomadaire"""
        user_data = self.get_user_data(ctx.author.id)
        now = datetime.now()
        
        if user_data.get("weekly_claimed"):
            last_claim = datetime.fromisoformat(user_data["weekly_claimed"])
            if (now - last_claim).total_seconds() < 604800:  # 7 jours
                next_claim = last_claim + timedelta(weeks=1)
                embed = discord.Embed(
                    title="⏰ Bonus hebdomadaire déjà réclamé",
                    description=f"Prochain bonus disponible : <t:{int(next_claim.timestamp())}:R>",
                    color=0xFF0000
                )
                await ctx.send(embed=embed)
                return
        
        bonus = random.randint(2000, 5000)
        data = self.load_user_data()
        user_str = str(ctx.author.id)
        
        if user_str not in data:
            data[user_str] = {"points": 1000, "daily_claimed": None, "weekly_claimed": None}
        
        data[user_str]["points"] += bonus
        data[user_str]["weekly_claimed"] = now.isoformat()
        self.save_user_data(data)
        
        embed = discord.Embed(
            title="🍌 Bonus hebdomadaire réclamé !",
            description=f"Vous avez reçu **{bonus}** points !\nNouveau solde: **{data[user_str]['points']:,}** points",
            color=0x00FF00
        )
        await ctx.send(embed=embed)

    @commands.command(name="leaderboard", aliases=["lb", "top"])
    async def leaderboard(self, ctx):
        """Classement des joueurs"""
        data = self.load_user_data()
        
        if not data:
            await ctx.send("❌ Aucun joueur trouvé !")
            return
        
        # Trier par points
        sorted_users = sorted(data.items(), key=lambda x: x[1].get("points", 0), reverse=True)
        
        embed = discord.Embed(title="🏆 Classement des Joueurs", color=0xFFD700)
        
        for i, (user_id, user_data) in enumerate(sorted_users[:10]):  # Top 10
            try:
                user = self.bot.get_user(int(user_id))
                username = user.display_name if user else f"Utilisateur {user_id}"
            except:
                username = f"Utilisateur {user_id}"
            
            points = user_data.get("points", 0)
            
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
                value=f"{points:,} points",
                inline=False
            )
        
        await ctx.send(embed=embed)

    @commands.command(name="casinohelp", aliases=["chelp"])
    async def casino_help(self, ctx):
        """Aide du casino"""
        embed = discord.Embed(
            title="🌀 Aide du Casino",
            description="Voici la liste des commandes disponibles :",
            color=0xFFD700
        )
        embed.add_field(name="💰 Solde", value="`j!points` ou `j!balance`", inline=False)
        embed.add_field(name="🎰 Machine à sous", value="`j!slot <mise>`", inline=False)
        embed.add_field(name="🃏 Blackjack", value="`j!blackjack <mise>`", inline=False)
        embed.add_field(name="🎡 Roulette", value="`j!roulette <mise> <choix>`", inline=False)
        embed.add_field(name="🪙 Pile ou Face", value="`j!coinflip <mise> <pile/face>`", inline=False)
        embed.add_field(name="🎲 Dé", value="`j!dice <mise> <nombre 1-6>`", inline=False)
        embed.add_field(name="📉 Limbo", value="`j!limbo <mise> <multiplicateur>`", inline=False)
        embed.add_field(name="🚀 Crash", value="`j!crash <mise>`", inline=False)
        embed.add_field(name="💣 Mines", value="`j!mines <mise> <nb mines>`", inline=False)
        embed.add_field(name="🎡 Roue Fortune", value="`j!wheel <mise>`", inline=False)
        embed.add_field(name="🍋 Bonus quotidien", value="`j!daily`", inline=False)
        embed.add_field(name="🍌 Bonus hebdomadaire", value="`j!weekly`", inline=False)
        embed.add_field(name="🏆 Classement", value="`j!leaderboard`", inline=False)
        
        embed.set_footer(text="Mise minimum: 10 points | Solde de départ: 1000 points")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Casino(bot))

