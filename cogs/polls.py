import discord
from discord.ext import commands
import json
import os

class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_polls_file = 'active_polls.json'
        self.active_polls = self.load_active_polls()

    def load_user_data(self):
        try:
            with open('user_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}  # Retourne un dictionnaire vide si le fichier est corrompu

    def save_user_data(self, data):
        with open('user_data.json', 'w') as f:
            json.dump(data, f, indent=2)

    def load_active_polls(self):
        try:
            if os.path.exists(self.active_polls_file):
                with open(self.active_polls_file, 'r') as f:
                    content = f.read()
                    if content.strip():  # Vérifie si le fichier n'est pas vide
                        return json.loads(content)
                    else:
                        return {}  # Retourne un dictionnaire vide si le fichier est vide
            else:
                return {}
        except json.JSONDecodeError:
            return {}  # Retourne un dictionnaire vide si le fichier est corrompu

    def save_active_polls(self):
        with open(self.active_polls_file, 'w') as f:
            json.dump(self.active_polls, f, indent=2)

    @commands.command(name="poll")
    @commands.has_permissions(administrator=True)  # Vérification de permissions
    async def create_poll(self, ctx, question: str, option1: str, option2: str):
        """Crée un sondage avec paris. Usage: j!poll "Question ?" "Option1" "Option2" """
        embed = discord.Embed(title="Sondage avec Paris", description=question, color=discord.Color.blue())
        embed.add_field(name="Option 1", value=option1, inline=True)
        embed.add_field(name="Option 2", value=option2, inline=True)
        embed.add_field(name="Comment parier", value="Utilisez j!pollbet [ID du sondage] [numéro d'option] [montant]", inline=False)

        poll_message = await ctx.send(embed=embed)
        
        poll_data = {
            "question": question,
            "options": [option1, option2],
            "bets": {1: {}, 2: {}},
            "total_bets": {1: 0, 2: 0},
            "message_id": poll_message.id,
            "channel_id": ctx.channel.id
        }

        self.active_polls[poll_message.id] = poll_data
        self.save_active_polls()

        # Ajoute l'ID du sondage dans l'embed après sa création
        embed.add_field(name="ID du Sondage", value=poll_message.id, inline=False)
        await poll_message.edit(embed=embed)

    @commands.command(name="pollbet")
    async def place_bet(self, ctx, poll_id: int, option: int, amount: float):
        """Place un pari sur une option d'un sondage actif. Usage: j!pollbet [ID du sondage] [1 ou 2] [montant]"""
        if poll_id not in self.active_polls:
            await ctx.send(f"Le sondage avec l'ID {poll_id} n'est pas actif.")
            return

        poll = self.active_polls[poll_id]

        if option not in [1, 2]:
            await ctx.send("Option invalide. Choisissez 1 ou 2.")
            return

        user_data = self.load_user_data()
        user_id = str(ctx.author.id)

        if user_id not in user_data:
            user_data[user_id] = {"points": 0}

        if user_data[user_id]["points"] < amount:
            await ctx.send("Vous n'avez pas assez de points pour ce pari.")
            return

        user_data[user_id]["points"] -= amount
        self.save_user_data(user_data)

        poll["bets"][option][user_id] = poll["bets"][option].get(user_id, 0) + amount
        poll["total_bets"][option] += amount

        self.save_active_polls()

        await ctx.send(f"Pari de {amount} points placé sur l'option {option} ({poll['options'][option-1]}) pour le sondage {poll_id}.")

    async def resolve_poll(self, ctx, poll_id, automatic=False):
        poll = self.active_polls.pop(poll_id, None)
        if not poll:
            await ctx.send(f"Le sondage avec l'ID {poll_id} n'a pas été trouvé.")
            return

        total_bets = sum(poll["total_bets"].values())
        if total_bets == 0:
            await ctx.send("Le sondage est terminé, mais aucun pari n'a été placé.")
            self.save_active_polls()
            return

        winning_option = max(poll["total_bets"], key=poll["total_bets"].get) if automatic else None
        losing_option = 3 - winning_option if winning_option else None

        user_data = self.load_user_data()

        if automatic and winning_option:
            for user_id, bet_amount in poll["bets"][winning_option].items():
                winnings = bet_amount + (bet_amount / poll["total_bets"][winning_option]) * poll["total_bets"][losing_option]
                user_data[user_id]["points"] = round(user_data[user_id].get("points", 0) + winnings, 2)
        elif automatic and not winning_option:
            await ctx.send("Le sondage est terminé automatiquement. Utilisez `j!endpoll` pour déclarer un gagnant.")

        self.save_user_data(user_data)

        embed = discord.Embed(title="Résultats du Sondage", description=poll["question"], color=discord.Color.green())
        if winning_option:
            embed.add_field(name=f"Option gagnante: {poll['options'][winning_option-1]}",
                            value=f"Total des paris: {poll['total_bets'][winning_option]:.2f} points", inline=False)
            embed.add_field(name=f"Option perdante: {poll['options'][losing_option-1]}",
                            value=f"Total des paris: {poll['total_bets'][losing_option]:.2f} points", inline=False)
        else:
            embed.add_field(name="Aucun gagnant", value="Utilisez `j!endpoll` pour déclarer un gagnant.", inline=False)

        poll_channel = self.bot.get_channel(poll["channel_id"])
        if poll_channel:
            await poll_channel.send(embed=embed)
            await poll_channel.send("Les gains ont été distribués aux gagnants." if winning_option else "Veuillez déclarer un gagnant manuellement.")

        self.save_active_polls()

    @commands.command(name="endpoll")
    @commands.has_permissions(administrator=True)  # Vérification de permissions
    async def resolve_poll_manual(self, ctx, poll_id: int, winning_option: int):
        """Résout manuellement un sondage actif en spécifiant l'option gagnante. Usage: j!endpoll [ID du sondage] [1 ou 2]"""
        if poll_id not in self.active_polls:
            await ctx.send(f"Le sondage avec l'ID {poll_id} n'est pas actif.")
            return

        poll = self.active_polls.pop(poll_id, None)

        if not poll:
            await ctx.send(f"Le sondage avec l'ID {poll_id} n'a pas été trouvé.")
            return

        if winning_option not in [1, 2]:
            await ctx.send("Option invalide. Choisissez 1 ou 2.")
            return

        total_bets = sum(poll["total_bets"].values())
        if total_bets == 0:
            await ctx.send("Le sondage est terminé, mais aucun pari n'a été placé.")
            self.save_active_polls()
            return

        losing_option = 3 - winning_option  # Si winning_option est 1, losing_option sera 2, et vice versa

        user_data = self.load_user_data()

        for user_id, bet_amount in poll["bets"][winning_option].items():
            winnings = bet_amount + (bet_amount / poll["total_bets"][winning_option]) * poll["total_bets"][losing_option]
            user_data[user_id]["points"] = round(user_data[user_id].get("points", 0) + winnings, 2)

        self.save_user_data(user_data)

        embed = discord.Embed(title="Résultats du Sondage", description=poll["question"], color=discord.Color.green())
        embed.add_field(name=f"Option gagnante: {poll['options'][winning_option-1]}", 
                        value=f"Total des paris: {poll['total_bets'][winning_option]:.2f} points", inline=False)
        embed.add_field(name=f"Option perdante: {poll['options'][losing_option-1]}", 
                        value=f"Total des paris: {poll['total_bets'][losing_option]:.2f} points", inline=False)

        poll_channel = self.bot.get_channel(poll["channel_id"])
        if poll_channel:
            await poll_channel.send(embed=embed)
            await poll_channel.send("Les gains ont été distribués aux gagnants.")

        self.save_active_polls()

    @commands.command(name="list_polls")
    async def list_polls(self, ctx):
        """Affiche la liste de tous les sondages actifs."""
        if not self.active_polls:
            await ctx.send("Il n'y a actuellement aucun sondage actif.")
            return

        embed = discord.Embed(title="Sondages Actifs", color=discord.Color.blue())
        for poll_id, poll in self.active_polls.items():
            options = "\n".join([f"Option {i+1}: {opt}" for i, opt in enumerate(poll["options"])])
            embed.add_field(name=f"Sondage ID: {poll_id}", 
                            value=f"Question: {poll['question']}\nOptions:\n{options}", 
                            inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Poll(bot))
