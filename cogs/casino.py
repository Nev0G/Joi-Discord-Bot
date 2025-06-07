import discord
from discord.ext import commands
import json
import os
import random
import asyncio
from datetime import datetime, timedelta
import math

USER_DATA_FILE = "user_data.json"

class Casino(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}  # Pour éviter le spam des jeux
        
        # Emojis pour les animations
        self.slot_symbols = ["🍒", "🍋", "🍊", "🍇", "⭐", "🔔", "💎"]
        self.card_suits = ["♠️", "♥️", "♦️", "♣️"]
        self.numbers = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        
        # Animations
        self.loading_states = ["⚪", "🔵", "🟡", "🟠", "🔴", "🟣"]
        self.spinning_states = ["🎰", "🎯", "🎲", "🎭", "🎪", "🎨"]

    def load_user_data(self):
        try:
            if os.path.exists(USER_DATA_FILE):
                with open(USER_DATA_FILE, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Erreur lecture données: {e}")
            return {}

    def save_user_data(self, data):
        try:
            with open(USER_DATA_FILE, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Erreur sauvegarde: {e}")

    def get_user_points(self, user_id):
        data = self.load_user_data()
        return data.get(str(user_id), {}).get("points", 1000)

    def update_user_points(self, user_id, new_points):
        data = self.load_user_data()
        user_str = str(user_id)
        if user_str not in data:
            data[user_str] = {"points": 1000}
        data[user_str]["points"] = new_points
        self.save_user_data(data)

    def get_user_stats(self, user_id):
        """Récupère les statistiques d'un joueur"""
        data = self.load_user_data()
        user_data = data.get(str(user_id), {})
        return {
            "games_played": user_data.get("games_played", 0),
            "total_won": user_data.get("total_won", 0),
            "total_lost": user_data.get("total_lost", 0),
            "biggest_win": user_data.get("biggest_win", 0),
            "win_streak": user_data.get("win_streak", 0),
            "favorite_game": user_data.get("favorite_game", "slot")
        }

    def update_user_stats(self, user_id, game_name, bet, winnings):
        """Met à jour les statistiques après une partie"""
        data = self.load_user_data()
        user_str = str(user_id)
        if user_str not in data:
            data[user_str] = {"points": 1000}
        
        stats = data[user_str]
        stats["games_played"] = stats.get("games_played", 0) + 1
        
        if winnings > bet:
            stats["total_won"] = stats.get("total_won", 0) + (winnings - bet)
            stats["win_streak"] = stats.get("win_streak", 0) + 1
            if winnings - bet > stats.get("biggest_win", 0):
                stats["biggest_win"] = winnings - bet
        else:
            stats["total_lost"] = stats.get("total_lost", 0) + bet
            stats["win_streak"] = 0
        
        stats["favorite_game"] = game_name
        self.save_user_data(data)

    async def animated_countdown(self, message, title, duration=3):
        """Compte à rebours animé"""
        for i in range(duration, 0, -1):
            embed = discord.Embed(title=f"{title} - {i}", color=0xFFD700)
            embed.description = "🎲" * (4 - i) + "⚪" * i
            await message.edit(embed=embed)
            await asyncio.sleep(1)

    async def spinning_animation(self, message, title, steps=5):
        """Animation de rotation"""
        for i in range(steps):
            embed = discord.Embed(
                title=title,
                description=f"{self.spinning_states[i % len(self.spinning_states)]} En cours...",
                color=0xFFD700
            )
            await message.edit(embed=embed)
            await asyncio.sleep(0.5)

    @commands.command(name="slot", aliases=["slots", "machine"])
    async def slot_machine_enhanced(self, ctx, bet: int = None):
        """Machine à sous avec animation ultra-réaliste"""
        if bet is None:
            await ctx.send("❌ Usage: `j!slot <mise>`")
            return

        if bet < 10:
            await ctx.send("❌ Mise minimum : 10 points !")
            return

        user_points = self.get_user_points(ctx.author.id)
        if bet > user_points:
            await ctx.send("❌ Fonds insuffisants !")
            return

        # Vérifier si le joueur a un jeu en cours
        if ctx.author.id in self.active_games:
            await ctx.send("❌ Vous avez déjà un jeu en cours !")
            return

        self.active_games[ctx.author.id] = True

        try:
            # Animation d'introduction
            embed = discord.Embed(
                title="🎰 MACHINE À SOUS PREMIUM",
                description="🎲 Insertion de la mise...",
                color=0xFF1493
            )
            embed.add_field(name="💰 Mise", value=f"{bet:,} points", inline=True)
            embed.add_field(name="🎯 Joueur", value=ctx.author.display_name, inline=True)
            message = await ctx.send(embed=embed)

            await asyncio.sleep(1)

            # Animation des rouleaux
            slots = [["❓", "❓", "❓"] for _ in range(3)]
            
            for spin_round in range(8):  # 8 tours d'animation
                # Faire tourner chaque rouleau
                for reel in range(3):
                    if spin_round < 5 or reel <= spin_round - 5:  # Les rouleaux s'arrêtent progressivement
                        for pos in range(3):
                            slots[reel][pos] = random.choice(self.slot_symbols)
                
                # Créer l'affichage visuel
                display = ""
                display += "╔═══════════════╗\n"
                display += f"║  {slots[0][0]} │ {slots[1][0]} │ {slots[2][0]}  ║\n"
                display += f"║ **{slots[0][1]}** │**{slots[1][1]}** │**{slots[2][1]}** ║ ⭐\n"
                display += f"║  {slots[0][2]} │ {slots[1][2]} │ {slots[2][2]}  ║\n"
                display += "╚═══════════════╝\n"

                embed = discord.Embed(
                    title="🎰 MACHINE À SOUS - SPINNING!",
                    description=display,
                    color=0xFF1493
                )
                
                spin_intensity = "🔥" * min(spin_round + 1, 5)
                embed.add_field(name="⚡ Intensité", value=spin_intensity, inline=True)
                embed.add_field(name="🎲 Tour", value=f"{spin_round + 1}/8", inline=True)
                
                await message.edit(embed=embed)
                await asyncio.sleep(0.4 + (spin_round * 0.1))  # Ralentit progressivement

            # Résultat final
            final_slots = [slots[0][1], slots[1][1], slots[2][1]]  # Ligne du milieu
            
            # Calculer les gains
            winnings = 0
            win_type = ""
            
            if final_slots[0] == final_slots[1] == final_slots[2]:
                if final_slots[0] == "💎":
                    winnings = bet * 50
                    win_type = "💎 DIAMOND JACKPOT! 💎"
                elif final_slots[0] == "⭐":
                    winnings = bet * 25
                    win_type = "⭐ SUPER STAR! ⭐"
                elif final_slots[0] == "🔔":
                    winnings = bet * 15
                    win_type = "🔔 MEGA BELL! 🔔"
                else:
                    winnings = bet * 8
                    win_type = f"{final_slots[0]} TRIPLE WIN! {final_slots[0]}"
            elif final_slots[0] == final_slots[1] or final_slots[1] == final_slots[2] or final_slots[0] == final_slots[2]:
                winnings = bet * 2
                win_type = "🎊 DOUBLE MATCH! 🎊"
            elif "💎" in final_slots:
                winnings = bet * 3
                win_type = "💎 Diamond Bonus! 💎"
            else:
                winnings = 0
                win_type = "💔 Pas de chance..."

            # Affichage du résultat avec effet dramatique
            if winnings > 0:
                embed = discord.Embed(title="🎉 VICTOIRE! 🎉", color=0x00FF00)
                embed.add_field(name="🎊 TYPE DE VICTOIRE", value=win_type, inline=False)
                embed.add_field(name="💰 GAIN", value=f"+{winnings - bet:,} points", inline=True)
                
                # Calcul du multiplicateur pour l'affichage
                multiplier = winnings / bet if bet > 0 else 0
                embed.add_field(name="📈 MULTIPLICATEUR", value=f"x{multiplier:.1f}", inline=True)
                
            else:
                embed = discord.Embed(title="💔 Défaite", color=0xFF0000)
                embed.add_field(name="💸 PERTE", value=f"-{bet:,} points", inline=False)

            # Affichage final des rouleaux
            final_display = ""
            final_display += "╔═══════════════╗\n"
            final_display += f"║  {slots[0][0]} │ {slots[1][0]} │ {slots[2][0]}  ║\n"
            final_display += f"║ **{final_slots[0]}** │**{final_slots[1]}** │**{final_slots[2]}** ║ ⭐\n"
            final_display += f"║  {slots[0][2]} │ {slots[1][2]} │ {slots[2][2]}  ║\n"
            final_display += "╚═══════════════╝"
            
            embed.description = final_display

            # Mise à jour des points et stats
            new_points = user_points - bet + winnings
            self.update_user_points(ctx.author.id, new_points)
            self.update_user_stats(ctx.author.id, "slot", bet, winnings)
            
            embed.add_field(name="💳 Nouveau solde", value=f"{new_points:,} points", inline=False)
            
            # Streak info
            stats = self.get_user_stats(ctx.author.id)
            if stats["win_streak"] > 1:
                embed.add_field(name="🔥 Série", value=f"{stats['win_streak']} victoires!", inline=True)

            await message.edit(embed=embed)

        finally:
            # Retirer le joueur des jeux actifs après 2 secondes
            await asyncio.sleep(2)
            self.active_games.pop(ctx.author.id, None)

    @commands.command(name="blackjack", aliases=["bj", "21"])
    async def blackjack_enhanced(self, ctx, bet: int = None):
        """Blackjack interactif avec animations"""
        if bet is None:
            await ctx.send("❌ Usage: `j!blackjack <mise>`")
            return

        if bet < 10:
            await ctx.send("❌ Mise minimum : 10 points !")
            return

        user_points = self.get_user_points(ctx.author.id)
        if bet > user_points:
            await ctx.send("❌ Fonds insuffisants !")
            return

        if ctx.author.id in self.active_games:
            await ctx.send("❌ Vous avez déjà un jeu en cours !")
            return

        self.active_games[ctx.author.id] = True

        try:
            # Créer le deck
            deck = []
            for suit in self.card_suits:
                for number in self.numbers:
                    deck.append(f"{number}{suit}")
            random.shuffle(deck)

            def card_value(card):
                number = card[:-2] if card[:-2] in ["10"] else card[:-1]
                if number in ["J", "Q", "K"]:
                    return 10
                elif number == "A":
                    return 11
                else:
                    return int(number)

            def hand_value(hand):
                total = sum(card_value(card) for card in hand)
                aces = sum(1 for card in hand if card[:-1] == "A" or card[:-2] == "A")
                while total > 21 and aces > 0:
                    total -= 10
                    aces -= 1
                return total

            # Distribution initiale avec animation
            embed = discord.Embed(
                title="🃏 BLACKJACK PREMIUM",
                description="📋 Préparation de la table...",
                color=0x2E8B57
            )
            message = await ctx.send(embed=embed)
            await asyncio.sleep(1)

            # Cartes initiales
            player_hand = [deck.pop(), deck.pop()]
            dealer_hand = [deck.pop(), deck.pop()]

            # Animation de distribution
            for i in range(4):
                embed = discord.Embed(
                    title="🃏 BLACKJACK - Distribution",
                    description=f"🎴 Distribution des cartes... {i+1}/4",
                    color=0x2E8B57
                )
                await message.edit(embed=embed)
                await asyncio.sleep(0.8)

            async def update_game_display(reveal_dealer=False):
                player_total = hand_value(player_hand)
                dealer_total = hand_value(dealer_hand)

                embed = discord.Embed(title="🃏 BLACKJACK EN COURS", color=0x2E8B57)
                
                # Main du joueur
                player_cards = " ".join(player_hand)
                embed.add_field(
                    name=f"🎴 Votre main ({player_total})",
                    value=player_cards,
                    inline=False
                )

                # Main du croupier
                if reveal_dealer:
                    dealer_cards = " ".join(dealer_hand)
                    embed.add_field(
                        name=f"🎭 Croupier ({dealer_total})",
                        value=dealer_cards,
                        inline=False
                    )
                else:
                    hidden_cards = f"{dealer_hand[0]} 🂠"
                    embed.add_field(
                        name="🎭 Croupier (?)",
                        value=hidden_cards,
                        inline=False
                    )

                # Informations de jeu
                embed.add_field(name="💰 Mise", value=f"{bet:,} points", inline=True)
                embed.add_field(name="💳 Solde", value=f"{user_points:,} points", inline=True)

                return embed, player_total, dealer_total

            # Affichage initial
            embed, player_total, dealer_total = await update_game_display()
            
            # Vérifier blackjack naturel
            if player_total == 21:
                embed.title = "🎉 BLACKJACK NATUREL!"
                embed.color = 0xFFD700
                winnings = int(bet * 2.5)
                new_points = user_points + winnings - bet
                self.update_user_points(ctx.author.id, new_points)
                embed.add_field(name="🏆 GAIN", value=f"+{winnings-bet:,} points", inline=False)
                await message.edit(embed=embed)
                return

            # Ajouter les boutons d'action
            embed.add_field(
                name="🎯 Actions disponibles",
                value="🇭 **Hit** - Tirer une carte\n🇸 **Stand** - Rester",
                inline=False
            )
            await message.edit(embed=embed)
            await message.add_reaction("🇭")
            await message.add_reaction("🇸")

            if len(player_hand) == 2 and player_total in [9, 10, 11]:
                await message.add_reaction("🇩")  # Double down
                embed.set_footer(text="🇩 = Double Down (doubler la mise)")

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["🇭", "🇸", "🇩"] and reaction.message.id == message.id

            # Boucle de jeu du joueur
            while player_total < 21:
                try:
                    reaction, _ = await self.bot.wait_for("reaction_add", timeout=30.0, check=check)
                    await message.remove_reaction(reaction.emoji, ctx.author)

                    if str(reaction.emoji) == "🇭":  # Hit
                        # Animation de tirage
                        embed.add_field(name="🎴 Action", value="Tirage d'une carte...", inline=False)
                        await message.edit(embed=embed)
                        await asyncio.sleep(1)

                        player_hand.append(deck.pop())
                        embed, player_total, dealer_total = await update_game_display()
                        
                        if player_total > 21:
                            embed.title = "💥 BUST! Vous avez dépassé 21!"
                            embed.color = 0xFF0000
                            break
                        elif player_total == 21:
                            embed.title = "🎯 21! Parfait!"
                            embed.color = 0xFFD700
                            break
                        else:
                            embed.add_field(
                                name="🎯 Actions disponibles",
                                value="🇭 **Hit** - Tirer une carte\n🇸 **Stand** - Rester",
                                inline=False
                            )
                        
                        await message.edit(embed=embed)

                    elif str(reaction.emoji) == "🇸":  # Stand
                        break

                    elif str(reaction.emoji) == "🇩" and len(player_hand) == 2:  # Double Down
                        if user_points >= bet * 2:
                            bet *= 2
                            player_hand.append(deck.pop())
                            embed, player_total, dealer_total = await update_game_display()
                            embed.add_field(name="🎲 Double Down!", value=f"Mise doublée: {bet:,} points", inline=False)
                            await message.edit(embed=embed)
                            break
                        else:
                            await ctx.send("❌ Fonds insuffisants pour doubler !", delete_after=3)

                except asyncio.TimeoutError:
                    await ctx.send("⏰ Temps écoulé! Stand automatique.", delete_after=5)
                    break

            # Jeu du croupier avec animation
            if player_total <= 21:
                embed, player_total, dealer_total = await update_game_display(reveal_dealer=True)
                embed.add_field(name="🎭 Tour du croupier", value="Le croupier révèle ses cartes...", inline=False)
                await message.edit(embed=embed)
                await asyncio.sleep(2)

                while dealer_total < 17:
                    embed.add_field(name="🎴 Tirage croupier", value="Le croupier tire une carte...", inline=False)
                    await message.edit(embed=embed)
                    await asyncio.sleep(1.5)
                    
                    dealer_hand.append(deck.pop())
                    embed, player_total, dealer_total = await update_game_display(reveal_dealer=True)
                    await message.edit(embed=embed)
                    await asyncio.sleep(1)

            # Déterminer le gagnant avec animation dramatique
            embed = discord.Embed(title="🎊 RÉSULTAT FINAL", color=0xFFD700)
            
            # Affichage final des mains
            embed.add_field(
                name=f"🎴 Votre main ({player_total})",
                value=" ".join(player_hand),
                inline=False
            )
            embed.add_field(
                name=f"🎭 Croupier ({dealer_total})",
                value=" ".join(dealer_hand),
                inline=False
            )

            # Calcul du résultat
            if player_total > 21:
                result = "💥 BUST! Vous avez perdu!"
                winnings = 0
                embed.color = 0xFF0000
            elif dealer_total > 21:
                result = "🎉 Le croupier a fait BUST! Vous gagnez!"
                winnings = bet * 2
                embed.color = 0x00FF00
            elif player_total > dealer_total:
                result = "🏆 VICTOIRE! Votre main est supérieure!"
                winnings = bet * 2
                embed.color = 0x00FF00
            elif player_total < dealer_total:
                result = "😔 DÉFAITE! La main du croupier est supérieure!"
                winnings = 0
                embed.color = 0xFF0000
            else:
                result = "🤝 ÉGALITÉ! Mise remboursée!"
                winnings = bet
                embed.color = 0xFFD700

            embed.add_field(name="🎯 Résultat", value=result, inline=False)
            
            # Calcul des gains/pertes
            if winnings > bet:
                embed.add_field(name="💰 GAIN", value=f"+{winnings-bet:,} points", inline=True)
            elif winnings < bet:
                embed.add_field(name="💸 PERTE", value=f"-{bet:,} points", inline=True)
            else:
                embed.add_field(name="🔄 REMBOURSÉ", value=f"{bet:,} points", inline=True)

            # Mise à jour des points
            new_points = user_points - bet + winnings
            self.update_user_points(ctx.author.id, new_points)
            self.update_user_stats(ctx.author.id, "blackjack", bet, winnings)
            
            embed.add_field(name="💳 Nouveau solde", value=f"{new_points:,} points", inline=True)
            
            await message.edit(embed=embed)
            await message.clear_reactions()

        finally:
            await asyncio.sleep(3)
            self.active_games.pop(ctx.author.id, None)

    @commands.command(name="crash")
    async def crash_enhanced(self, ctx, bet: int = None):
        """Jeu Crash avec tension maximale et animations en temps réel"""
        if bet is None:
            await ctx.send("❌ Usage: `j!crash <mise>`")
            return

        if bet < 10:
            await ctx.send("❌ Mise minimum : 10 points !")
            return

        user_points = self.get_user_points(ctx.author.id)
        if bet > user_points:
            await ctx.send("❌ Fonds insuffisants !")
            return

        if ctx.author.id in self.active_games:
            await ctx.send("❌ Vous avez déjà un jeu en cours !")
            return

        self.active_games[ctx.author.id] = True

        try:
            # Point de crash prédéterminé
            crash_point = round(random.uniform(1.01, 50.0), 2)
            
            # Animation de démarrage
            embed = discord.Embed(
                title="🚀 CRASH GAME - PRÉPARATION",
                description="🎯 Préparation du lancement...",
                color=0xFF4500
            )
            embed.add_field(name="💰 Mise", value=f"{bet:,} points", inline=True)
            embed.add_field(name="🎮 Joueur", value=ctx.author.display_name, inline=True)
            message = await ctx.send(embed=embed)

            # Compte à rebours dramatique
            for i in range(3, 0, -1):
                embed = discord.Embed(
                    title=f"🚀 CRASH GAME - LANCEMENT EN {i}",
                    description="🔥" * (4-i) + "⚪" * i,
                    color=0xFF4500
                )
                await message.edit(embed=embed)
                await asyncio.sleep(1)

            # Lancement!
            embed = discord.Embed(
                title="🚀 DÉCOLLAGE!",
                description="🚀🌟🚀🌟🚀",
                color=0x00FF00
            )
            await message.edit(embed=embed)
            await asyncio.sleep(0.5)

            # Ajouter le bouton cash out
            await message.add_reaction("💰")
            
            current_multiplier = 1.00
            cashed_out = False
            
            # Animation du multiplicateur qui monte
            while current_multiplier < crash_point and not cashed_out:
                # Calcul de l'incrément (accélère avec le temps)
                if current_multiplier < 2:
                    increment = 0.01
                elif current_multiplier < 5:
                    increment = 0.02
                elif current_multiplier < 10:
                    increment = 0.05
                else:
                    increment = 0.1

                current_multiplier += increment
                current_multiplier = round(current_multiplier, 2)

                # Couleur qui change selon le risque
                if current_multiplier < 1.5:
                    color = 0x00FF00  # Vert
                elif current_multiplier < 3:
                    color = 0xFFFF00  # Jaune  
                elif current_multiplier < 5:
                    color = 0xFF8000  # Orange
                else:
                    color = 0xFF0000  # Rouge

                # Graphique ASCII simple
                bars = int(min(current_multiplier * 2, 20))
                graph = "🟩" * bars + "⬜" * (20 - bars)

                embed = discord.Embed(
                    title="🚀 CRASH GAME EN COURS",
                    color=color
                )

                # Multiplicateur principal en gros
                embed.add_field(
                    name="📈 MULTIPLICATEUR ACTUEL",
                    value=f"# **{current_multiplier:.2f}x**",
                    inline=False
                )

                # Gain potentiel
                potential_win = int(bet * current_multiplier)
                embed.add_field(
                    name="💰 GAIN POTENTIEL",
                    value=f"{potential_win:,} points (+{potential_win-bet:,})",
                    inline=True
                )

                # Graphique
                embed.add_field(
                    name="📊 Progression",
                    value=graph,
                    inline=False
                )

                # Tension selon le niveau
                if current_multiplier >= 10:
                    tension = "🔥🔥🔥 EXTRÊME! 🔥🔥🔥"
                elif current_multiplier >= 5:
                    tension = "⚡⚡ HAUTE TENSION! ⚡⚡"
                elif current_multiplier >= 2:
                    tension = "⚠️ Attention! ⚠️"
                else:
                    tension = "✅ Sécurisé"

                embed.add_field(name="🌡️ Niveau de risque", value=tension, inline=True)
                embed.set_footer(text="💰 Cliquez sur 💰 pour encaisser!")

                await message.edit(embed=embed)

                # Vérifier si l'utilisateur a cash out
                try:
                    def check(reaction, user):
                        return user == ctx.author and str(reaction.emoji) == "💰" and reaction.message.id == message.id

                    await self.bot.wait_for("reaction_add", timeout=0.3, check=check)
                    cashed_out = True
                    await message.remove_reaction("💰", ctx.author)
                    
                    # Animation de cash out
                    embed = discord.Embed(
                        title="💰 CASH OUT RÉUSSI!",
                        color=0xFFD700
                    )
                    embed.add_field(
                        name="🎯 Multiplicateur final",
                        value=f"**{current_multiplier:.2f}x**",
                        inline=True
                    )
                    
                    winnings = int(bet * current_multiplier)
                    profit = winnings - bet
                    embed.add_field(
                        name="💎 GAIN TOTAL",
                        value=f"+{profit:,} points",
                        inline=True
                    )
                    
                    new_points = user_points + winnings - bet
                    self.update_user_points(ctx.author.id, new_points)
                    embed.add_field(name="💳 Nouveau solde", value=f"{new_points:,} points", inline=False)
                    
                    await message.edit(embed=embed)
                    break

                except asyncio.TimeoutError:
                    continue  # Continue l'animation si pas de cash out

                # Vitesse d'animation qui augmente
                sleep_time = max(0.1, 0.5 - (current_multiplier * 0.05))
                await asyncio.sleep(sleep_time)

            # Si pas cashed out et qu'on atteint le crash point
            if not cashed_out:
                # Animation de crash dramatique
                crash_msgs = [
                    "💥 ALERTE CRASH!",
                    "🔥 SYSTÈME EN PANNE!", 
                    "💀 CRASH TOTAL!",
                    "⚡ EXPLOSION!"
                ]
                
                for msg in crash_msgs:
                    embed = discord.Embed(
                        title=msg,
                        description="🚀💥🔥💀⚡",
                        color=0xFF0000
                    )
                    await message.edit(embed=embed)
                    await asyncio.sleep(0.3)

                # Résultat final du crash
                embed = discord.Embed(
                    title=f"💥 CRASH À {crash_point:.2f}x!",
                    description="🔥 La fusée a explosé! 🔥",
                    color=0xFF0000
                )
                embed.add_field(
                    name="💸 PERTE",
                    value=f"-{bet:,} points",
                    inline=True
                )
                embed.add_field(
                    name="📉 Point de crash",
                    value=f"{crash_point:.2f}x",
                    inline=True
                )
                
                new_points = user_points - bet
                self.update_user_points(ctx.author.id, new_points)
                embed.add_field(name="💳 Nouveau solde", value=f"{new_points:,} points", inline=False)
                
                # Message de consolation
                if crash_point < 1.2:
                    embed.set_footer(text="😤 Crash instantané! Pas de chance...")
                elif current_multiplier >= crash_point * 0.9:
                    embed.set_footer(text="😭 Si proche du succès!")
                else:
                    embed.set_footer(text="💪 Retry! La prochaine sera la bonne!")

                await message.edit(embed=embed)

            # Mise à jour des stats
            if cashed_out:
                self.update_user_stats(ctx.author.id, "crash", bet, int(bet * current_multiplier))
            else:
                self.update_user_stats(ctx.author.id, "crash", bet, 0)

        finally:
            await asyncio.sleep(3)
            await message.clear_reactions()
            self.active_games.pop(ctx.author.id, None)

    @commands.command(name="mines", aliases=["minesweeper", "mine"])
    async def mines_enhanced(self, ctx, bet: int = None, num_mines: int = 3):
        """Jeu de mines interactif avec plateau visuel"""
        if bet is None:
            await ctx.send("❌ Usage: `j!mines <mise> [nombre_mines]`")
            return

        if bet < 10:
            await ctx.send("❌ Mise minimum : 10 points !")
            return

        if num_mines < 1 or num_mines > 20:
            await ctx.send("❌ Nombre de mines : entre 1 et 20 !")
            return

        user_points = self.get_user_points(ctx.author.id)
        if bet > user_points:
            await ctx.send("❌ Fonds insuffisants !")
            return

        if ctx.author.id in self.active_games:
            await ctx.send("❌ Vous avez déjà un jeu en cours !")
            return

        self.active_games[ctx.author.id] = True

        try:
            # Générer le plateau 5x5
            grid_size = 25
            mines_positions = random.sample(range(grid_size), num_mines)
            revealed = set()
            game_over = False

            # Emojis pour l'affichage
            def get_cell_emoji(pos):
                if pos in revealed:
                    if pos in mines_positions:
                        return "💥"
                    else:
                        return "💎"
                else:
                    return f"{pos+1:02d}"  # Numéro de la case

            def create_grid_display():
                grid_lines = []
                for row in range(5):
                    line = ""
                    for col in range(5):
                        pos = row * 5 + col
                        emoji = get_cell_emoji(pos)
                        line += f"|{emoji}"
                    line += "|"
                    grid_lines.append(line)
                return "\n".join(grid_lines)

            def calculate_multiplier():
                gems_found = len([pos for pos in revealed if pos not in mines_positions])
                if gems_found == 0:
                    return 1.0
                # Formule de multiplicateur basée sur le risque
                safe_spots = grid_size - num_mines
                multiplier = 1.0 + (gems_found * num_mines * 0.3)
                return round(multiplier, 2)

            # Animation de préparation
            embed = discord.Embed(
                title="💣 MINES - PRÉPARATION DU TERRAIN",
                description="⛏️ Placement des mines en cours...",
                color=0x8B4513
            )
            embed.add_field(name="💰 Mise", value=f"{bet:,} points", inline=True)
            embed.add_field(name="💣 Mines", value=f"{num_mines}/25", inline=True)
            message = await ctx.send(embed=embed)

            # Animation du placement des mines
            for i in range(num_mines):
                await asyncio.sleep(0.5)
                embed.description = f"💣 Mine {i+1}/{num_mines} placée..."
                embed.add_field(
                    name="⚠️ Danger Level", 
                    value="🔴" * (i+1) + "⚪" * (num_mines-i-1), 
                    inline=False
                )
                await message.edit(embed=embed)

            await asyncio.sleep(1)

            # Début du jeu
            while not game_over:
                current_multiplier = calculate_multiplier()
                potential_win = int(bet * current_multiplier)
                
                embed = discord.Embed(
                    title="💣 MINES - CHAMP DE BATAILLE",
                    color=0x8B4513
                )

                # Affichage du plateau
                grid_display = create_grid_display()
                embed.add_field(
                    name="🗺️ PLATEAU (Cliquez un numéro pour creuser)",
                    value=f"```{grid_display}```",
                    inline=False
                )

                # Statistiques
                gems_found = len([pos for pos in revealed if pos not in mines_positions])
                embed.add_field(name="💎 Gemmes trouvées", value=f"{gems_found}", inline=True)
                embed.add_field(name="💣 Mines restantes", value=f"{num_mines}", inline=True)
                embed.add_field(name="📈 Multiplicateur", value=f"{current_multiplier:.2f}x", inline=True)
                embed.add_field(name="💰 Gain potentiel", value=f"{potential_win:,} points", inline=True)

                # Options
                if gems_found > 0:
                    embed.add_field(
                        name="💰 Cash Out disponible!",
                        value="Tapez `cash` pour encaisser vos gains",
                        inline=False
                    )

                embed.set_footer(text="Tapez un numéro (1-25) pour creuser, ou 'cash' pour encaisser")
                await message.edit(embed=embed)

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                try:
                    response = await self.bot.wait_for("message", timeout=60.0, check=check)
                    await response.delete()
                    
                    user_input = response.content.lower().strip()

                    if user_input == "cash" and gems_found > 0:
                        # Cash out avec animation
                        embed = discord.Embed(
                            title="💰 CASH OUT RÉUSSI!",
                            color=0xFFD700
                        )
                        
                        profit = potential_win - bet
                        embed.add_field(name="💎 Gemmes récupérées", value=f"{gems_found}", inline=True)
                        embed.add_field(name="📈 Multiplicateur final", value=f"{current_multiplier:.2f}x", inline=True)
                        embed.add_field(name="🏆 GAIN TOTAL", value=f"+{profit:,} points", inline=False)
                        
                        new_points = user_points + profit
                        self.update_user_points(ctx.author.id, new_points)
                        embed.add_field(name="💳 Nouveau solde", value=f"{new_points:,} points", inline=False)
                        
                        await message.edit(embed=embed)
                        game_over = True

                    elif user_input.isdigit():
                        pos = int(user_input) - 1
                        
                        if pos < 0 or pos >= grid_size:
                            await ctx.send("❌ Numéro invalide! (1-25)", delete_after=3)
                            continue
                        
                        if pos in revealed:
                            await ctx.send("❌ Case déjà révélée!", delete_after=3)
                            continue

                        # Animation de creusage
                        embed = discord.Embed(
                            title="⛏️ CREUSAGE EN COURS...",
                            description=f"🔍 Exploration de la case {pos+1}...",
                            color=0x8B4513
                        )
                        await message.edit(embed=embed)
                        await asyncio.sleep(1.5)

                        # Révéler la case
                        revealed.add(pos)

                        if pos in mines_positions:
                            # BOOM! Animation d'explosion
                            explosion_frames = ["💥", "🔥💥🔥", "💀🔥💥🔥💀", "☠️💀🔥💥🔥💀☠️"]
                            
                            for frame in explosion_frames:
                                embed = discord.Embed(
                                    title="💣 EXPLOSION!",
                                    description=frame,
                                    color=0xFF0000
                                )
                                await message.edit(embed=embed)
                                await asyncio.sleep(0.4)

                            # Révéler tout le plateau
                            revealed.update(range(grid_size))
                            
                            embed = discord.Embed(
                                title="💥 GAME OVER - MINE TOUCHÉE!",
                                color=0xFF0000
                            )
                            
                            final_grid = create_grid_display()
                            embed.add_field(
                                name="🗺️ PLATEAU FINAL",
                                value=f"```{final_grid}```",
                                inline=False
                            )
                            
                            embed.add_field(name="💸 PERTE", value=f"-{bet:,} points", inline=True)
                            embed.add_field(name="💎 Gemmes trouvées", value=f"{gems_found}", inline=True)
                            
                            new_points = user_points - bet
                            self.update_user_points(ctx.author.id, new_points)
                            embed.add_field(name="💳 Nouveau solde", value=f"{new_points:,} points", inline=False)
                            
                            if gems_found >= 5:
                                embed.set_footer(text="😤 Impressionnant! Vous étiez si proche!")
                            elif gems_found >= 2:
                                embed.set_footer(text="💪 Pas mal! Retry pour faire mieux!")
                            else:
                                embed.set_footer(text="🍀 La chance tournera!")
                            
                            await message.edit(embed=embed)
                            game_over = True

                        else:
                            # Gemme trouvée! Animation de succès
                            success_frames = ["✨", "💎✨", "🌟💎✨"]
                            
                            for frame in success_frames:
                                embed = discord.Embed(
                                    title="💎 GEMME DÉCOUVERTE!",
                                    description=frame,
                                    color=0x00FF00
                                )
                                await message.edit(embed=embed)
                                await asyncio.sleep(0.3)

                            # Vérifier si toutes les cases sûres sont trouvées
                            safe_positions = [i for i in range(grid_size) if i not in mines_positions]
                            safe_revealed = [pos for pos in revealed if pos not in mines_positions]
                            
                            if len(safe_revealed) == len(safe_positions):
                                # Victoire parfaite!
                                embed = discord.Embed(
                                    title="🏆 VICTOIRE PARFAITE!",
                                    description="🎉 Toutes les gemmes trouvées! 🎉",
                                    color=0xFFD700
                                )
                                
                                perfect_multiplier = current_multiplier + 1.0  # Bonus parfait
                                perfect_win = int(bet * perfect_multiplier)
                                profit = perfect_win - bet
                                
                                embed.add_field(name="💎 Gemmes parfaites", value=f"{len(safe_revealed)}/{len(safe_positions)}", inline=True)
                                embed.add_field(name="🎊 Bonus parfait", value="+1.0x", inline=True)
                                embed.add_field(name="🏆 GAIN TOTAL", value=f"+{profit:,} points", inline=False)
                                
                                new_points = user_points + profit
                                self.update_user_points(ctx.author.id, new_points)
                                embed.add_field(name="💳 Nouveau solde", value=f"{new_points:,} points", inline=False)
                                
                                await message.edit(embed=embed)
                                game_over = True

                    else:
                        await ctx.send("❌ Commande invalide! Tapez un numéro (1-25) ou 'cash'", delete_after=3)

                except asyncio.TimeoutError:
                    await ctx.send("⏰ Temps écoulé! Auto cash-out...", delete_after=5)
                    if gems_found > 0:
                        profit = potential_win - bet
                        new_points = user_points + profit
                        self.update_user_points(ctx.author.id, new_points)
                        
                        embed = discord.Embed(
                            title="⏰ AUTO CASH-OUT",
                            description=f"Gains automatiquement encaissés: +{profit:,} points",
                            color=0xFFD700
                        )
                        await message.edit(embed=embed)
                    else:
                        new_points = user_points - bet
                        self.update_user_points(ctx.author.id, new_points)
                    game_over = True

            # Mise à jour des statistiques
            final_winnings = potential_win if gems_found > 0 else 0
            self.update_user_stats(ctx.author.id, "mines", bet, final_winnings)

        finally:
            await asyncio.sleep(5)
            self.active_games.pop(ctx.author.id, None)

    @commands.command(name="roulette")
    async def roulette_enhanced(self, ctx, bet: int = None, choice: str = None):
        """Roulette européenne avec animation de roue réaliste"""
        if bet is None or choice is None:
            help_embed = discord.Embed(
                title="🎡 ROULETTE - AIDE",
                description="Comment jouer à la roulette:",
                color=0x8B0000
            )
            help_embed.add_field(
                name="📋 Usage",
                value="`j!roulette <mise> <choix>`",
                inline=False
            )
            help_embed.add_field(
                name="🎯 Choix disponibles",
                value="• **Numéros**: 0-36\n• **Couleurs**: rouge, noir\n• **Parité**: pair, impair\n• **Moitiés**: 1-18, 19-36",
                inline=False
            )
            help_embed.add_field(
                name="💰 Gains",
                value="• Numéro: x36\n• Couleur/Parité: x2\n• Moitiés: x2",
                inline=False
            )
            await ctx.send(embed=help_embed)
            return

        if bet < 10:
            await ctx.send("❌ Mise minimum : 10 points !")
            return

        user_points = self.get_user_points(ctx.author.id)
        if bet > user_points:
            await ctx.send("❌ Fonds insuffisants !")
            return

        if ctx.author.id in self.active_games:
            await ctx.send("❌ Vous avez déjà un jeu en cours !")
            return

        self.active_games[ctx.author.id] = True

        try:
            # Configuration de la roulette européenne
            red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
            black_numbers = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
            
            # Validation du choix
            choice = choice.lower()
            valid_choice = False
            bet_type = ""
            
            if choice.isdigit() and 0 <= int(choice) <= 36:
                valid_choice = True
                bet_type = "number"
                choice = int(choice)
            elif choice in ["rouge", "red", "r"]:
                valid_choice = True
                bet_type = "red"
            elif choice in ["noir", "black", "b"]:
                valid_choice = True
                bet_type = "black"
            elif choice in ["pair", "even", "e"]:
                valid_choice = True
                bet_type = "even"
            elif choice in ["impair", "odd", "o"]:
                valid_choice = True
                bet_type = "odd"
            elif choice in ["1-18", "bas", "low", "l"]:
                valid_choice = True
                bet_type = "low"
            elif choice in ["19-36", "haut", "high", "h"]:
                valid_choice = True
                bet_type = "high"
            
            if not valid_choice:
                await ctx.send("❌ Choix invalide! Utilisez `j!roulette` pour voir l'aide.")
                return

            # Animation de préparation
            embed = discord.Embed(
                title="🎡 ROULETTE EUROPÉENNE",
                description="🎯 Préparation de la table...",
                color=0x8B0000
            )
            embed.add_field(name="💰 Mise", value=f"{bet:,} points", inline=True)
            if bet_type == "number":
                embed.add_field(name="🎯 Paris", value=f"Numéro {choice}", inline=True)
            else:
                embed.add_field(name="🎯 Paris", value=choice.upper(), inline=True)
            message = await ctx.send(embed=embed)

            await asyncio.sleep(1)

            # Animation "Rien ne va plus"
            embed = discord.Embed(
                title="🎡 RIEN NE VA PLUS!",
                description="🚫 Les jeux sont faits! 🚫",
                color=0xFF0000
            )
            await message.edit(embed=embed)
            await asyncio.sleep(2)

            # Animation de la roue qui tourne
            spin_animation = ["🎡", "🌀", "🎯", "⚡", "✨"]
            
            for i in range(15):  # 15 frames d'animation
                embed = discord.Embed(
                    title="🎡 ROUE EN ROTATION",
                    description=f"{spin_animation[i % len(spin_animation)]} La roue tourne...",
                    color=0xFFD700
                )
                
                # Effet de vitesse décroissante
                speed_bar = "🔥" * max(1, 10 - i//2)
                embed.add_field(name="💨 Vitesse", value=speed_bar, inline=False)
                
                await message.edit(embed=embed)
                sleep_time = 0.2 + (i * 0.05)  # Ralentit progressivement
                await asyncio.sleep(sleep_time)

            # Résultat final
            winning_number = random.randint(0, 36)
            
            # Déterminer les propriétés du numéro gagnant
            if winning_number == 0:
                color_result = "🟢 VERT"
                number_color = 0x00FF00
            elif winning_number in red_numbers:
                color_result = "🔴 ROUGE"
                number_color = 0xFF0000
            else:
                color_result = "⚫ NOIR"  
                number_color = 0x2C2C2C

            # Animation du résultat qui apparaît
            result_frames = ["❓", "🎯", f"**{winning_number}**"]
            
            for frame in result_frames:
                embed = discord.Embed(
                    title="🎡 RÉSULTAT",
                    description=f"🎯 {frame}",
                    color=number_color
                )
                await message.edit(embed=embed)
                await asyncio.sleep(0.7)

            # Affichage final avec tous les détails
            embed = discord.Embed(
                title="🎡 ROULETTE - RÉSULTAT FINAL",
                color=number_color
            )
            
            # Affichage visuel du numéro
            embed.add_field(
                name="🎯 NUMÉRO GAGNANT",
                value=f"# **{winning_number}**",
                inline=True
            )
            embed.add_field(
                name="🎨 COULEUR",
                value=color_result,
                inline=True
            )

            # Propriétés du numéro
            properties = []
            if winning_number != 0:
                properties.append("PAIR" if winning_number % 2 == 0 else "IMPAIR")
                properties.append("1-18" if winning_number <= 18 else "19-36")
            else:
                properties.append("ZÉRO")
            
            embed.add_field(
                name="📊 Propriétés",
                value=" | ".join(properties),
                inline=False
            )

            # Vérifier les gains
            winnings = 0
            win_message = ""
            
            if bet_type == "number" and choice == winning_number:
                winnings = bet * 36
                win_message = f"🎊 NUMÉRO PLEIN! Gain x36!"
            elif bet_type == "red" and winning_number in red_numbers:
                winnings = bet * 2
                win_message = "🔴 ROUGE GAGNANT!"
            elif bet_type == "black" and winning_number in black_numbers:
                winnings = bet * 2
                win_message = "⚫ NOIR GAGNANT!"
            elif bet_type == "even" and winning_number != 0 and winning_number % 2 == 0:
                winnings = bet * 2
                win_message = "🎯 PAIR GAGNANT!"
            elif bet_type == "odd" and winning_number != 0 and winning_number % 2 == 1:
                winnings = bet * 2
                win_message = "🎯 IMPAIR GAGNANT!"
            elif bet_type == "low" and 1 <= winning_number <= 18:
                winnings = bet * 2
                win_message = "📉 1-18 GAGNANT!"
            elif bet_type == "high" and 19 <= winning_number <= 36:
                winnings = bet * 2
                win_message = "📈 19-36 GAGNANT!"
            else:
                winnings = 0
                win_message = "💔 Pas de chance cette fois..."

            # Affichage du résultat
            if winnings > 0:
                embed.add_field(
                    name="🏆 VICTOIRE!",
                    value=win_message,
                    inline=False
                )
                embed.add_field(
                    name="💰 GAIN",
                    value=f"+{winnings - bet:,} points",
                    inline=True
                )
                embed.color = 0x00FF00
            else:
                embed.add_field(
                    name="😔 DÉFAITE",
                    value=win_message,
                    inline=False
                )
                embed.add_field(
                    name="💸 PERTE",
                    value=f"-{bet:,} points",
                    inline=True
                )
                embed.color = 0xFF0000

            # Mise à jour des points
            new_points = user_points - bet + winnings
            self.update_user_points(ctx.author.id, new_points)
            self.update_user_stats(ctx.author.id, "roulette", bet, winnings)
            
            embed.add_field(name="💳 Nouveau solde", value=f"{new_points:,} points", inline=True)
            
            # Historique des 5 derniers numéros (simulation)
            recent_numbers = [random.randint(0, 36) for _ in range(5)]
            recent_numbers[-1] = winning_number  # Le dernier est le numéro actuel
            
            embed.add_field(
                name="📈 Historique récent",
                value=" → ".join(map(str, recent_numbers)),
                inline=False
            )

            await message.edit(embed=embed)

        finally:
            await asyncio.sleep(4)
            self.active_games.pop(ctx.author.id, None)

    @commands.command(name="wheel", aliases=["roue", "fortune"])
    async def wheel_of_fortune(self, ctx, bet: int = None):
        """Roue de la Fortune avec segments colorés et animations"""
        if bet is None:
            await ctx.send("❌ Usage: `j!wheel <mise>`")
            return

        if bet < 10:
            await ctx.send("❌ Mise minimum : 10 points !")
            return

        user_points = self.get_user_points(ctx.author.id)
        if bet > user_points:
            await ctx.send("❌ Fonds insuffisants !")
            return

        if ctx.author.id in self.active_games:
            await ctx.send("❌ Vous avez déjà un jeu en cours !")
            return

        self.active_games[ctx.author.id] = True

        try:
            # Segments de la roue avec probabilités
            wheel_segments = [
                {"name": "💥 BOOM", "multiplier": 0, "probability": 0.2, "color": 0xFF0000},
                {"name": "😢 Echec", "multiplier": 0, "probability": 0.15, "color": 0x808080},
                {"name": "🔄 Remboursé", "multiplier": 1, "probability": 0.15, "color": 0xFFD700},
                {"name": "🎯 x1.5", "multiplier": 1.5, "probability": 0.2, "color": 0x00FF00},
                {"name": "🎊 x2", "multiplier": 2, "probability": 0.15, "color": 0x00BFFF},
                {"name": "⭐ x3", "multiplier": 3, "probability": 0.08, "color": 0xFF69B4},
                {"name": "💎 x5", "multiplier": 5, "probability": 0.05, "color": 0x9932CC},
                {"name": "👑 x10", "multiplier": 10, "probability": 0.015, "color": 0xFFD700},
                {"name": "🔥 MEGA", "multiplier": 25, "probability": 0.005, "color": 0xFF4500}
            ]

            # Animation de préparation
            embed = discord.Embed(
                title="🎡 ROUE DE LA FORTUNE",
                description="🎯 Préparation du grand spin...",
                color=0xFFD700
            )
            embed.add_field(name="💰 Mise", value=f"{bet:,} points", inline=True)
            embed.add_field(name="🎮 Joueur", value=ctx.author.display_name, inline=True)
            message = await ctx.send(embed=embed)

            await asyncio.sleep(1)

            # Affichage de la roue
            wheel_display = "```\n    🎡 ROUE DE LA FORTUNE 🎡\n"
            wheel_display += "┌─────────────────────────────┐\n"
            wheel_display += "│ 💥  😢  🔄  🎯  🎊  ⭐  💎 │\n"
            wheel_display += "│ x0  x0  x1 x1.5 x2  x3  x5 │\n"
            wheel_display += "│          👑  🔥            │\n"
            wheel_display += "│         x10 x25            │\n"
            wheel_display += "└─────────────────────────────┘\n```"

            embed = discord.Embed(
                title="🎡 LANCEZ LA ROUE!",
                description=wheel_display,
                color=0xFFD700
            )
            embed.set_footer(text="🎲 Cliquez sur 🎲 pour faire tourner la roue!")
            await message.edit(embed=embed)
            await message.add_reaction("🎲")

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) == "🎲" and reaction.message.id == message.id

            await self.bot.wait_for("reaction_add", timeout=30.0, check=check)
            await message.remove_reaction("🎲", ctx.author)

            # Animation de rotation ultra-dynamique
            rotation_frames = [
                "🎡", "🌀", "💫", "⚡", "✨", "🌟", "💥", "🔥"
            ]
            
            # 20 frames d'animation avec ralentissement progressif
            for i in range(20):
                frame = rotation_frames[i % len(rotation_frames)]
                
                embed = discord.Embed(
                    title="🎡 ROUE EN ROTATION!",
                    description=f"# {frame}",
                    color=random.choice([0xFF0000, 0x00FF00, 0x0000FF, 0xFFD700, 0xFF69B4])
                )
                
                # Barre de vitesse qui diminue
                speed = max(1, 15 - i)
                speed_bar = "🔥" * (speed // 3) + "⚡" * (speed % 3)
                embed.add_field(name="💨 Vitesse", value=speed_bar or "🌪️", inline=False)
                
                # Suspense qui monte
                if i > 15:
                    embed.add_field(name="⏳ Suspense", value="🔥🔥🔥 RALENTIT! 🔥🔥🔥", inline=False)
                elif i > 10:
                    embed.add_field(name="⏳ Suspense", value="⚡⚡ ATTENTION! ⚡⚡", inline=False)
                
                await message.edit(embed=embed)
                
                # Ralentissement progressif + effet aléatoire
                sleep_time = 0.1 + (i * 0.08) + random.uniform(0, 0.1)
                await asyncio.sleep(sleep_time)

            # Sélection du résultat basé sur les probabilités
            rand = random.random()
            cumulative_prob = 0
            selected_segment = wheel_segments[-1]  # Par défaut le dernier
            
            for segment in wheel_segments:
                cumulative_prob += segment["probability"]
                if rand <= cumulative_prob:
                    selected_segment = segment
                    break

            # Animation de révélation dramatique
            reveal_frames = ["❓", "🎯", selected_segment["name"]]
            
            for frame in reveal_frames:
                embed = discord.Embed(
                    title="🎡 RÉSULTAT DE LA ROUE",
                    description=f"# {frame}",
                    color=selected_segment["color"]
                )
                await message.edit(embed=embed)
                await asyncio.sleep(0.8)

            # Résultat final avec effets spéciaux
            multiplier = selected_segment["multiplier"]
            winnings = int(bet * multiplier)
            profit = winnings - bet

            embed = discord.Embed(
                title="🎡 ROUE DE LA FORTUNE - RÉSULTAT",
                color=selected_segment["color"]
            )

            # Affichage du segment gagnant
            embed.add_field(
                name="🎯 SEGMENT GAGNANT",
                value=f"## {selected_segment['name']}",
                inline=False
            )

            if multiplier == 0:
                # Échec avec consolation
                embed.add_field(name="💸 RÉSULTAT", value="AUCUN GAIN", inline=True)
                embed.add_field(name="😔 PERTE", value=f"-{bet:,} points", inline=True)
                
                if selected_segment["name"] == "💥 BOOM":
                    embed.set_footer(text="💥 La roue a explosé! Pas de chance...")
                else:
                    embed.set_footer(text="😢 Retry! La fortune vous sourira!")
                    
            elif multiplier == 1:
                # Remboursement
                embed.add_field(name="🔄 RÉSULTAT", value="REMBOURSEMENT", inline=True)
                embed.add_field(name="💰 RÉCUPÉRATION", value=f"{bet:,} points", inline=True)
                embed.set_footer(text="🍀 Pas de perte, pas de gain!")
                
            else:
                # Gain!
                embed.add_field(name="🏆 MULTIPLICATEUR", value=f"**x{multiplier}**", inline=True)
                embed.add_field(name="💎 GAIN TOTAL", value=f"+{profit:,} points", inline=True)
                
                # Messages spéciaux selon le gain
                if multiplier >= 25:
                    embed.set_footer(text="🔥🔥🔥 MÉGA JACKPOT LÉGENDAIRE! 🔥🔥🔥")
                elif multiplier >= 10:
                    embed.set_footer(text="👑 JACKPOT ROYAL! Incroyable! 👑")
                elif multiplier >= 5:
                    embed.set_footer(text="💎 SUPER GAIN! Fantastique! 💎")
                elif multiplier >= 3:
                    embed.set_footer(text="⭐ Excellent gain! Bien joué! ⭐")
                else:
                    embed.set_footer(text="🎊 Joli gain! Continue! 🎊")

            # Mise à jour des points
            new_points = user_points - bet + winnings
            self.update_user_points(ctx.author.id, new_points)
            embed.add_field(name="💳 Nouveau solde", value=f"{new_points:,} points", inline=False)

            # Statistiques de probabilité
            prob_percent = selected_segment["probability"] * 100
            embed.add_field(name="📊 Probabilité", value=f"{prob_percent:.1f}%", inline=True)
            
            if prob_percent < 5:
                embed.add_field(name="🎲 Chance", value="ULTRA-RARE! 🔥", inline=True)
            elif prob_percent < 15:
                embed.add_field(name="🎲 Chance", value="Rare! ⭐", inline=True)
            else:
                embed.add_field(name="🎲 Chance", value="Standard 🎯", inline=True)

            await message.edit(embed=embed)

            # Mise à jour des stats
            self.update_user_stats(ctx.author.id, "wheel", bet, winnings)

        except asyncio.TimeoutError:
            embed = discord.Embed(
                title="⏰ TEMPS ÉCOULÉ",
                description="Vous n'avez pas lancé la roue à temps!",
                color=0xFF0000
            )
            await message.edit(embed=embed)
        
        finally:
            await asyncio.sleep(4)
            await message.clear_reactions()
            self.active_games.pop(ctx.author.id, None)

    @commands.command(name="stats", aliases=["statistiques", "profil"])
    async def player_stats(self, ctx, user: discord.Member = None):
        """Affiche les statistiques détaillées d'un joueur"""
        target_user = user or ctx.author
        stats = self.get_user_stats(target_user.id)
        current_points = self.get_user_points(target_user.id)

        embed = discord.Embed(
            title=f"📊 Profil Joueur: {target_user.display_name}",
            color=0xFFD700
        )
        embed.set_thumbnail(url=target_user.display_avatar.url)

        # Statistiques principales
        embed.add_field(
            name="💰 Points actuels",
            value=f"{current_points:,}",
            inline=True
        )
        embed.add_field(
            name="🎮 Parties jouées",
            value=f"{stats['games_played']}",
            inline=True
        )
        embed.add_field(
            name="🔥 Série actuelle",
            value=f"{stats['win_streak']} victoires",
            inline=True
        )

        # Gains et pertes
        total_net = stats['total_won'] - stats['total_lost']
        embed.add_field(
            name="📈 Total gagné",
            value=f"{stats['total_won']:,}",
            inline=True
        )
        embed.add_field(
            name="📉 Total perdu",
            value=f"{stats['total_lost']:,}",
            inline=True
        )
        embed.add_field(
            name="💎 Bilan net",
            value=f"{'+' if total_net >= 0 else ''}{total_net:,}",
            inline=True
        )

        # Statistiques avancées
        if stats['games_played'] > 0:
            win_rate = (stats['total_won'] / max(stats['total_won'] + stats['total_lost'], 1)) * 100
            avg_bet = (stats['total_won'] + stats['total_lost']) / stats['games_played']
            
            embed.add_field(
                name="🎯 Taux de réussite",
                value=f"{win_rate:.1f}%",
                inline=True
            )
            embed.add_field(
                name="💸 Mise moyenne",
                value=f"{avg_bet:.0f} points",
                inline=True
            )

        embed.add_field(
            name="🏆 Plus gros gain",
            value=f"{stats['biggest_win']:,} points",
            inline=True
        )

        # Jeu favori
        embed.add_field(
            name="🎲 Jeu favori",
            value=stats['favorite_game'].title(),
            inline=True
        )

        # Niveau du joueur basé sur les parties
        if stats['games_played'] < 10:
            level = "🐣 Débutant"
        elif stats['games_played'] < 50:
            level = "🎯 Intermédiaire"
        elif stats['games_played'] < 200:
            level = "⭐ Expérimenté"
        elif stats['games_played'] < 500:
            level = "🔥 Expert"
        else:
            level = "👑 Légende"

        embed.add_field(
            name="🎖️ Niveau",
            value=level,
            inline=True
        )

        # Graphique de progression (simulation)
        if total_net > 0:
            progress = "📈📈📈"
        elif total_net == 0:
            progress = "📊📊📊"
        else:
            progress = "📉📉📉"

        embed.add_field(
            name="📊 Tendance",
            value=progress,
            inline=True
        )

        # Footer avec date
        embed.set_footer(text=f"Statistiques mises à jour • Casino Bot", icon_url=ctx.bot.user.display_avatar.url)
        embed.timestamp = datetime.now()

        await ctx.send(embed=embed)

    @commands.command(name="cleaderboard", aliases=["lb", "ctop", "cclassement"])
    async def leaderboard(self, ctx, category: str = "points"):
        """Affiche le classement des joueurs"""
        data = self.load_user_data()
        
        if not data:
            await ctx.send("❌ Aucune donnée disponible!")
            return

        # Préparer les données selon la catégorie
        if category.lower() in ["points", "p"]:
            sorted_users = sorted(data.items(), key=lambda x: x[1].get("points", 0), reverse=True)
            title = "💰 TOP FORTUNE"
            field_name = "Points"
        elif category.lower() in ["games", "g", "parties"]:
            sorted_users = sorted(data.items(), key=lambda x: x[1].get("games_played", 0), reverse=True)
            title = "🎮 TOP JOUEURS"
            field_name = "Parties"
        elif category.lower() in ["wins", "w", "gains"]:
            sorted_users = sorted(data.items(), key=lambda x: x[1].get("total_won", 0), reverse=True)
            title = "🏆 TOP GAGNANTS"
            field_name = "Gains totaux"
        else:
            await ctx.send("❌ Catégories: `points`, `games`, `wins`")
            return

        # Créer l'embed
        embed = discord.Embed(
            title=f"🏆 {title}",
            description="Classement des meilleurs joueurs",
            color=0xFFD700
        )

        # Afficher le top 10
        top_10 = sorted_users[:10]
        leaderboard_text = ""
        
        medals = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
        
        for i, (user_id, user_data) in enumerate(top_10):
            try:
                user = await self.bot.fetch_user(int(user_id))
                username = user.display_name
            except:
                username = f"Utilisateur {user_id[:8]}..."

            if category.lower() in ["points", "p"]:
                value = f"{user_data.get('points', 0):,}"
            elif category.lower() in ["games", "g", "parties"]:
                value = f"{user_data.get('games_played', 0):,}"
            else:
                value = f"{user_data.get('total_won', 0):,}"

            leaderboard_text += f"{medals[i]} **{username}** • {value}\n"

        embed.add_field(
            name=f"🎯 {field_name}",
            value=leaderboard_text or "Aucun joueur",
            inline=False
        )

        # Position du joueur actuel
        user_position = None
        for i, (user_id, _) in enumerate(sorted_users):
            if user_id == str(ctx.author.id):
                user_position = i + 1
                break

        if user_position:
            embed.add_field(
                name="📍 Votre position",
                value=f"#{user_position}",
                inline=True
            )

        # Statistiques globales
        total_players = len(data)
        if category.lower() in ["points", "p"]:
            total_value = sum(user_data.get("points", 0) for user_data in data.values())
            avg_value = total_value / total_players
            embed.add_field(
                name="📊 Moyenne",
                value=f"{avg_value:,.0f} points",
                inline=True
            )
        
        embed.add_field(
            name="👥 Total joueurs",
            value=f"{total_players}",
            inline=True
        )

        embed.set_footer(text="🔄 Utilisez j!lb points/games/wins pour changer de catégorie")
        embed.timestamp = datetime.now()

        await ctx.send(embed=embed)

    @commands.command(name="casinohelp", aliases=["chelp", "aide"])
    async def casino_help_enhanced(self, ctx):
        """Aide complète du casino avec navigation par réactions"""
        
        # Page principale
        main_embed = discord.Embed(
            title="🎰 GUIDE COMPLET DU CASINO 🎰",
            description="Bienvenue dans le casino le plus animé de Discord!",
            color=0xFFD700
        )
        
        main_embed.add_field(
            name="🎮 JEUX DISPONIBLES",
            value=(
                "🎰 **Slots** - Machine à sous classique\n"
                "🃏 **Blackjack** - Battez le croupier!\n"
                "🎡 **Roulette** - Européenne authentique\n"
                "🪙 **Pile ou Face** - Simple et efficace\n"
                "🎲 **Dés** - Devinez le bon numéro\n"
                "📉 **Limbo** - Plus haut, plus risqué\n"
                "🚀 **Crash** - Encaissez avant le crash\n"
                "💣 **Mines** - Trouvez les gemmes\n"
                "🎡 **Wheel** - Roue de la fortune"
            ),
            inline=False
        )
        
        main_embed.add_field(
            name="💰 SYSTÈME DE POINTS",
            value=(
                "• Départ: **1000 points** gratuits\n"
                "• Mise minimum: **10 points**\n"
                "• Gains automatiquement ajoutés\n"
                "• `j!daily` - Bonus quotidien\n"
                "• `j!weekly` - Bonus hebdomadaire"
            ),
            inline=True
        )
        
        main_embed.add_field(
            name="📊 STATISTIQUES",
            value=(
                "• `j!stats` - Votre profil\n"
                "• `j!leaderboard` - Classements\n"
                "• `j!balance` - Solde actuel\n"
                "• Suivi automatique des gains/pertes"
            ),
            inline=True
        )

        main_embed.set_footer(text="🎯 Réagissez avec les emojis pour voir les détails de chaque jeu!")
        
        message = await ctx.send(embed=main_embed)
        
        # Ajouter les réactions pour la navigation
        reactions = ["🎰", "🃏", "🎡", "🪙", "🎲", "📉", "🚀", "💣", "🎡", "❓"]
        for reaction in reactions:
            await message.add_reaction(reaction)

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in reactions and reaction.message.id == message.id

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
                await message.remove_reaction(reaction.emoji, user)

                # Détails pour chaque jeu
                if str(reaction.emoji) == "🎰":
                    embed = discord.Embed(title="🎰 MACHINE À SOUS", color=0xFF4500)
                    embed.add_field(name="🎯 Comment jouer", value="`j!slot <mise>`", inline=False)
                    embed.add_field(name="🎊 Gains", value="🍒🍒🍒 = x10\n💎💎💎 = x50\n⭐⭐⭐ = x100", inline=False)
                    embed.add_field(name="💡 Conseil", value="Les symboles rares donnent plus!", inline=False)
                
                elif str(reaction.emoji) == "🃏":
                    embed = discord.Embed(title="🃏 BLACKJACK", color=0x2C2C2C)
                    embed.add_field(name="🎯 Comment jouer", value="`j!blackjack <mise>`", inline=False)
                    embed.add_field(name="🎊 Objectif", value="Se rapprocher de 21 sans dépasser", inline=False)
                    embed.add_field(name="⚡ Actions", value="Hit (carte) / Stand (arrêt)", inline=False)
                
                elif str(reaction.emoji) == "🎡":
                    embed = discord.Embed(title="🎡 ROULETTE", color=0x8B0000)
                    embed.add_field(name="🎯 Comment jouer", value="`j!roulette <mise> <choix>`", inline=False)
                    embed.add_field(name="🎊 Choix", value="0-36, rouge/noir, pair/impair", inline=False)
                    embed.add_field(name="💰 Gains", value="Numéro: x36, Couleur: x2", inline=False)

                # [Continuer pour les autres jeux...]
                
                await message.edit(embed=embed)
                await asyncio.sleep(3)
                await message.edit(embed=main_embed)

            except asyncio.TimeoutError:
                await message.clear_reactions()
                break

async def setup(bot):
    await bot.add_cog(Casino(bot))

                

