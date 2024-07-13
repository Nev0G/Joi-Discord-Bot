import discord
from discord.ext import commands, tasks
import random
import asyncio
import json
from typing import List, Tuple
from collections import defaultdict


USER_DATA_FILE = "user_data.json"

class Casino(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_data = self.load_user_data()
        self.bounty_channels = []
        self.bot = bot
        self.user_data = self.load_user_data()
        self.bounty_channels = []
        # self.post_bounty.start()  # Décommentez pour activer les bounties

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

    # Commande de test pour vérifier si le cog fonctionne
    @commands.command(name="test")
    async def test_command(self, ctx):
        await ctx.send("Le cog Casino fonctionne!")

    # Commande de machine à sous
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
            "🍒": 0.2,
            "🍊": 0.3,
            "🍋": 0.4,
            "🍇": 0.5,
            "🍎": 0.6,
            "🍉": 0.7,
            "💎": 0.8,
            "🎰": 0.9,
            "👑": 1.0,
            "🌟": 1.1,
        }
        
        animation_message = await ctx.send(f"🎰 {ctx.author.mention} Machine à sous: {' | '.join(['❓', '❓', '❓'])}")
        
        for _ in range(3):
            for _ in range(3):
                slots = random.choices(symbols, k=3)
                await animation_message.edit(content=f"🎰 {ctx.author.mention} Machine à sous: {' | '.join(slots)}")
                await asyncio.sleep(0.2)
        
        if len(set(slots)) == 1:  # Si tous les symboles sont identiques (triple)
            winnings = int(bet * (multipliers[slots[0]] + 20))  # Ajoute 20 au multiplicateur pour un triple
            await ctx.send(f"🤑 JACKPOT! Vous avez gagné **{winnings}** points!")
        elif len(set(slots)) == 2:  # Si deux symboles sont identiques (paire)
            winnings = int(bet * multipliers[slots[0]] + 1)  # Utilise le multiplicateur du premier symbole pour une paire
            await ctx.send(f"🎁 Petit gain! Vous récupérez **{winnings}** points!")
        else:  # Aucun doublon
            winnings = int(bet * (multipliers[slots[0]]))
            await ctx.send(f"😭 Perdu bouffon! Vous récupérez **{winnings}** points!")
            random_gif = random.choice([
                "https://media1.tenor.com/m/cn5GW2a9qtUAAAAC/laughing-emoji-laughing.gif",
                "https://media1.tenor.com/m/BbjFm-pfueUAAAAd/laughing-emoji-laughing.gif",
                "https://media1.tenor.com/m/dFDlIvZo544AAAAC/meme-laugh.gif",
            ])
            await ctx.send(random_gif)
        
        new_points = self.get_user_points(user_id) + winnings
        self.set_user_points(user_id, new_points)
        await ctx.send(f"{ctx.author.mention} 📊 Vous avez maintenant **{new_points}** points.")

    @slotmachine.error
    async def slotmachine_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"{ctx.author.mention} ⏳ Veuillez attendre {error.retry_after:.1f} secondes avant de réutiliser la commande slotmachine.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"{ctx.author.mention} ⚠️ Erreur : l'argument doit être un nombre entier. Exemple : `j!slotmachine 10`")
        else:
            await ctx.send(f"{ctx.author.mention} Une erreur est survenue : {error}")
            raise error

    # Événement on_ready pour initialiser les canaux de bounty
    @commands.Cog.listener()
    async def on_ready(self):
        self.bounty_channels = [channel.id for guild in self.bot.guilds for channel in guild.text_channels]
        print(f"Bounty channels initialized: {self.bounty_channels}")

    # Tâche de bounty (commentée par défaut)
    @tasks.loop(minutes=random.randint(10, 60))
    async def post_bounty(self):
        if not self.bounty_channels:
            print("No bounty channels available.")
            return
        
        channel_id = random.choice(self.bounty_channels)
        channel = self.bot.get_channel(channel_id)

        if channel is None:
            print(f"Channel with ID {channel_id} not found.")
            return

        bounty_points = random.randint(50, 200)

        try:
            bounty_message = await channel.send(f"🎯 **Bounty** 🎯\nRéagissez avec 🎯 pour gagner **{bounty_points} points** !")
            await bounty_message.add_reaction("🎯")

            def check(reaction, user):
                return user != self.bot.user and str(reaction.emoji) == "🎯" and reaction.message.id == bounty_message.id

            reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=300.0)

            if reaction:
                user_id = user.id
                current_points = self.get_user_points(user_id)
                new_points = current_points + bounty_points
                self.set_user_points(user_id, new_points)
                congratmess = await channel.send(f"🎉 {user.mention} a gagné **{bounty_points} points** en attrapant le bounty !")
                await asyncio.sleep(5)
                await bounty_message.delete()
                await congratmess.delete()
        except asyncio.TimeoutError:
            congratmess = await channel.send("🚫 Aucun bounty n'a été réclamé à temps.")
            await bounty_message.delete()
            await congratmess.delete()
        except Exception as e:
            print(f"Erreur lors de l'envoi du bounty : {e}")

    @post_bounty.before_loop
    async def before_post_bounty(self):
        await self.bot.wait_until_ready()
        print("Bot ready, starting bounty task.")

    # Commande pour afficher les points d'un utilisateur
    @commands.command(name="points")
    async def points(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        points = self.get_user_points(member.id)
        await ctx.send(f"🏆 {member.mention} a **{points}** points.")

    # Commande pour afficher le classement des utilisateurs
    @commands.command(name="leaderboard", aliases=["lb"])
    async def leaderboard(self, ctx):
        leaderboard = sorted(self.user_data.items(), key=lambda x: x[1].get("points", 0), reverse=True)

        if not leaderboard:
            await ctx.send("Le classement est vide.")
            return

        first_place_user = await self.bot.fetch_user(int(leaderboard[0][0]))
        if first_place_user:
            first_place_embed = discord.Embed(
                title=f"🏆 {first_place_user.name} est en tête du classement !",
                color=0xFFD700
            )
            avatar_url = first_place_user.avatar.url if first_place_user.avatar else first_place_user.default_avatar.url
            first_place_embed.set_thumbnail(url=avatar_url)
            first_place_embed.add_field(name="Points", value=f"{leaderboard[0][1].get('points', 0)} points", inline=False)
            first_place_embed.set_footer(text=f"Félicitations, {first_place_user.name} !")
            await ctx.send(embed=first_place_embed)

        embed = discord.Embed(title="Classement des utilisateurs", color=0x00ff00)

        for i, (user_id, user_data) in enumerate(leaderboard[1:6], start=2):  # Limit to top 5 after first place
            try:
                user = await self.bot.fetch_user(int(user_id))
                name = user.name if user else f"Utilisateur inconnu (ID: {user_id})"
                embed.add_field(
                    name=f"{i}. {name}",
                    value=f"{user_data.get('points', 0)} points",
                    inline=False
                )
            except discord.HTTPException as e:
                print(f"Erreur lors de la récupération de l'utilisateur {user_id}: {e}")

        await ctx.send(embed=embed)

    # Commande RSA pour recevoir des points gratuits
    @commands.command(name="rsa")
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def rsa(self, ctx):
        user_id = ctx.author.id
        current_points = self.get_user_points(user_id)
        new_points = current_points + 100
        self.set_user_points(user_id, new_points)
        await ctx.send(f"{ctx.author.mention} 💰 Vous avez reçu **100 points** ! Votre nouveau solde est de **{new_points}** points.")

    # Gestion des erreurs pour la commande RSA
    @rsa.error
    async def rsa_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            minutes, seconds = divmod(error.retry_after, 60)
            await ctx.author.send(f"⏳ Vous devez attendre {int(minutes)} minutes et {int(seconds)} secondes avant de pouvoir recevoir à nouveau les points RSA.")
        else:
            await ctx.send(f"Une erreur est survenue : {error}")

    # Commande de duel entre joueurs
    @commands.command(name="duel")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def duel(self, ctx, opponent: discord.Member, bet: float):
        if opponent == ctx.author:
            await ctx.send("Vous ne pouvez pas vous défier vous-même ! ❌")
            return

        if bet <= 0:
            await ctx.send("Le pari doit être supérieur à 0 points. 🛑")
            return

        challenger_points = self.get_user_points(ctx.author.id)
        opponent_points = self.get_user_points(opponent.id)

        if challenger_points < bet or opponent_points < bet:
            await ctx.send("❌ L'un des joueurs n'a pas assez de points pour ce duel.")
            return

        await ctx.send(f"{opponent.mention}, {ctx.author.mention} vous défie pour un duel de **{bet}** points. Acceptez-vous ? (oui/non) ⚔️")

        try:
            msg = await self.bot.wait_for('message', check=lambda m: m.author == opponent and m.content.lower() in ["oui", "non"], timeout=60.0)
        except asyncio.TimeoutError:
            await ctx.send(f"⏳ {opponent.mention} n'a pas répondu à temps. Le duel est annulé.")
            return

        if msg.content.lower() == "non":
            await ctx.send(f"🚫 {opponent.mention} a refusé le duel.")
            return

        duel_msg = await ctx.send("Le duel commence ! Lancement de la pièce...")
        await asyncio.sleep(1)
        for _ in range(2):
            for phase in ["🌑", "🌒", "🌓", "🌔"]:
                await duel_msg.edit(content=f"La pièce tourne... {phase}")
                await asyncio.sleep(0.5)

        winner, loser = random.choice([(ctx.author, opponent), (opponent, ctx.author)])

        self.set_user_points(winner.id, self.get_user_points(winner.id) + bet)
        self.set_user_points(loser.id, self.get_user_points(loser.id) - bet)

        await ctx.send(f"🎉 {winner.mention} a gagné le duel et remporte **{bet}** points ! Félicitations !")

    # Gestion des erreurs pour la commande de duel
    @duel.error
    async def duel_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{ctx.author.mention}, veuillez mentionner un adversaire et le montant de votre pari. Utilisation : `j!duel @adversaire montant`")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"{ctx.author.mention}, cette commande est en cooldown. Veuillez réessayer dans {error.retry_after:.2f} secondes.")
        else:
            await ctx.send(f"Une erreur est survenue : {error}")
            raise error

    # Commande pour donner des points à un autre joueur
    @commands.command(name="donner")
    async def donner(self, ctx, member: discord.Member, amount: float):
        donneur_id = str(ctx.author.id)
        receveur_id = str(member.id)
        
        donneur_points = self.get_user_points(donneur_id)
        receveur_points = self.get_user_points(receveur_id)
        
        if donneur_points < amount:
            await ctx.send("Vous n'avez pas assez de points pour faire ce don.")
            return
        
        self.set_user_points(donneur_id, donneur_points - amount)
        self.set_user_points(receveur_id, receveur_points + amount)
        
        await ctx.send(f"{ctx.author.mention} a donné {amount} points à {member.mention}!")

    # Commande pour voler des points à un autre joueur
    @commands.command(name="vol")
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def steal(self, ctx, victim: discord.Member, amount: float):
        thief_id = str(ctx.author.id)
        victim_id = str(victim.id)

        if thief_id == victim_id:
            await ctx.send(f"{ctx.author.mention}, vous ne pouvez pas voler vos propres points.")
            return

        if amount <= 0:
            await ctx.send(f"{ctx.author.mention}, veuillez spécifier un montant positif à voler.")
            return

        victim_points = self.get_user_points(victim_id)
        if victim_points < amount:
            await ctx.send(f"{victim.mention} n'a pas assez de points pour être volé.")
            return

        message = await ctx.send(f"🕵️‍♂️ {ctx.author.mention} prépare son coup pour voler {victim.mention}...")

        await asyncio.sleep(2)
        await message.edit(content=f"🔍 {ctx.author.mention} En train d'observer les alentours...")

        await asyncio.sleep(2)
        await message.edit(content=f"⏳ {ctx.author.mention} Attendre le bon moment...")

        await asyncio.sleep(2)

        stolen_points = min(amount, random.uniform(0, 1000))
        success_chance = 0.4

        if random.random() < success_chance:
            self.set_user_points(thief_id, self.get_user_points(thief_id) + stolen_points)
            self.set_user_points(victim_id, victim_points - stolen_points)
            await ctx.send(f"💰 {ctx.author.mention} a réussi à voler **{stolen_points} points** de {victim.mention} ! 🎉")
        else:
            donation_amount = stolen_points // 2
            self.set_user_points(thief_id, self.get_user_points(thief_id) - donation_amount)
            self.set_user_points(victim_id, victim_points + donation_amount)
            await ctx.send(f"🚨 {ctx.author.mention} a été attrapé(e) en train de voler {victim.mention} et a échoué ! 😱 Vous payez un dédommagement de **{donation_amount} points** à {victim.mention}.")

    @steal.error
    async def steal_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{ctx.author.mention}, veuillez mentionner une victime et le montant à voler. Utilisation : `j!vol @victime montant`")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"{ctx.author.mention}, veuillez spécifier un montant valide à voler.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"{ctx.author.mention}, cette commande est en cooldown. Veuillez réessayer dans {error.retry_after:.2f} secondes.")
        else:
            await ctx.send(f"Une erreur est survenue : {error}")
            raise error
        
    # Commande pour jouer au blackjack
    @commands.command(name="blackjack", aliases=["bj"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def blackjack(self, ctx, bet: float):
        user_id = ctx.author.id
        user_points = self.get_user_points(user_id)

        if bet <= 0:
            await ctx.send(f"{ctx.author.mention} 🚫 Vous devez parier au moins 1 point.")
            return

        if user_points < bet:
            await ctx.send(f"{ctx.author.mention} ❌ Vous n'avez pas assez de points pour ce pari.")
            return

        self.set_user_points(user_id, user_points - bet)

        deck = self.create_deck()
        player_hand = []
        dealer_hand = []

        # Distribution initiale
        player_hand.append(self.draw_card(deck))
        dealer_hand.append(self.draw_card(deck))
        player_hand.append(self.draw_card(deck))
        dealer_hand.append(self.draw_card(deck))

        game_message = await ctx.send("Préparation du jeu...")
        await asyncio.sleep(1)

        while True:
            player_value = self.calculate_hand_value(player_hand)
            dealer_value = self.calculate_hand_value(dealer_hand)

            if player_value == 21:
                await self.update_game_message(game_message, player_hand, dealer_hand, True)
                await ctx.send(f"{ctx.author.mention} 🎉 Blackjack ! Vous gagnez **{float(bet * 1.5)}** points !")
                self.set_user_points(user_id, user_points + float(bet * 2.5))
                return

            await self.update_game_message(game_message, player_hand, dealer_hand)

            # Demander au joueur de tirer ou de rester
            question_message = await ctx.send(f"{ctx.author.mention}, voulez-vous tirer (t) ou rester (r) ?")

            def check(m):
                return m.author == ctx.author and m.content.lower() in ['t', 'r']

            try:
                choice = await self.bot.wait_for('message', check=check, timeout=30.0)
                await choice.delete()  # Supprimer la réponse du joueur
                await question_message.delete()  # Supprimer la question
            except asyncio.TimeoutError:
                await question_message.delete()  # Supprimer la question en cas de timeout
                await ctx.send(f"{ctx.author.mention} Temps écoulé. Vous restez automatiquement.", delete_after=5)
                break

            if choice.content.lower() == 't':
                player_hand.append(self.draw_card(deck))
                if self.calculate_hand_value(player_hand) > 21:
                    await self.update_game_message(game_message, player_hand, dealer_hand, True)
                    await ctx.send(f"{ctx.author.mention} 💥 Vous avez dépassé 21. Vous perdez.")
                    return
            else:
                break

        # Tour du croupier
        while dealer_value < 17:
            dealer_hand.append(self.draw_card(deck))
            dealer_value = self.calculate_hand_value(dealer_hand)

        await self.update_game_message(game_message, player_hand, dealer_hand, True)

        # Déterminer le gagnant
        player_value = self.calculate_hand_value(player_hand)
        if dealer_value > 21 or player_value > dealer_value:
            await ctx.send(f"🎉 Vous gagnez ! Vous recevez **{bet * 2}** points.")
            self.set_user_points(user_id, user_points + bet * 2)
        elif player_value < dealer_value:
            await ctx.send(f"{ctx.author.mention} 😢 Le croupier gagne. Vous perdez votre mise.")
        else:
            await ctx.send(f"{ctx.author.mention} 🤝 Égalité. Vous récupérez votre mise.")
            self.set_user_points(user_id, user_points + bet)

    def create_deck(self) -> List[Tuple[str, str]]:
        suits = ['♠️', '♥️', '♦️', '♣️']
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        return [(rank, suit) for suit in suits for rank in ranks]

    def draw_card(self, deck: List[Tuple[str, str]]) -> Tuple[str, str]:
        return deck.pop(random.randint(0, len(deck) - 1))

    def calculate_hand_value(self, hand: List[Tuple[str, str]]) -> int:
        value = 0
        aces = 0
        for card in hand:
            if card[0] in ['J', 'Q', 'K']:
                value += 10
            elif card[0] == 'A':
                aces += 1
            else:
                value += int(card[0])
        
        for _ in range(aces):
            if value + 11 <= 21:
                value += 11
            else:
                value += 1
        
        return value

    async def update_game_message(self, message: discord.Message, player_hand: List[Tuple[str, str]], dealer_hand: List[Tuple[str, str]], show_all: bool = False):
        player_cards = ' '.join([f"{card[0]}{card[1]}" for card in player_hand])
        if show_all:
            dealer_cards = ' '.join([f"{card[0]}{card[1]}" for card in dealer_hand])
        else:
            dealer_cards = f"{dealer_hand[0][0]}{dealer_hand[0][1]} 🂠"
        
        embed = discord.Embed(title="Blackjack", color=0x00ff00)
        embed.add_field(name="Votre main", value=f"{player_cards} (Valeur: {self.calculate_hand_value(player_hand)})", inline=False)
        embed.add_field(name="Main du croupier", value=dealer_cards, inline=False)
        
        await message.edit(content="", embed=embed)

    @blackjack.error
    async def blackjack_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Veuillez entrer un montant valide pour votre pari.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Cette commande est en cooldown. Réessayez dans {error.retry_after:.2f} secondes.")
        else:
            await ctx.send(f"Une erreur est survenue : {error}")
            raise error
        




async def setup(bot):
    await bot.add_cog(Casino(bot))
