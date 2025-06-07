import discord
from discord.ext import commands, tasks
import json
import asyncio
from datetime import datetime, timedelta
import math

class PollSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.polls_file = 'polls.json'
        self.polls = self.load_polls()
        self.poll_channel_id = 1380946636494209214  # Remplacez par l'ID de votre channel "🗳️║Polls"
        self.update_task.start()

    def load_polls(self):
        try:
            with open(self.polls_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_polls(self):
        with open(self.polls_file, 'w') as f:
            json.dump(self.polls, f, indent=2)

    async def get_poll_message(self, poll_id):
        channel = self.bot.get_channel(self.poll_channel_id)
        if channel:
            try:
                return await channel.fetch_message(poll_id)
            except discord.NotFound:
                return None
        return None

    async def update_poll_embeds(self):
        for poll_id in list(self.polls.keys()):
            poll = self.polls[poll_id]
            message = await self.get_poll_message(poll_id)
            if message:
                await self.update_poll_embed(message, poll)

    @tasks.loop(seconds=30)
    async def update_task(self):
        await self.update_poll_embeds()

    async def calculate_odds(self, poll):
        total_bets = sum(option['total_bet'] for option in poll['options'])
        if total_bets == 0:
            return [1.0 for _ in poll['options']]

        odds = []
        for option in poll['options']:
            if option['total_bet'] == 0:
                odds.append(1.0)
            else:
                odds.append(total_bets / option['total_bet'])
        return odds

    async def update_poll_embed(self, message, poll):
        odds = await self.calculate_odds(poll)

        embed = discord.Embed(
            title=f"📊 Sondage: {poll['title']}",
            description=poll['description'],
            color=discord.Color.blue()
        )

        for i, option in enumerate(poll['options']):
            embed.add_field(
                name=f"Option {i+1}: {option['name']}",
                value=(
                    f"Cote: {odds[i]:.2f}\n"
                    f"Mises totales: {option['total_bet']} points\n"
                    f"Votes: {len(option['voters'])}"
                ),
                inline=False
            )

        time_left = poll['end_time'] - datetime.now().timestamp()
        if time_left > 0:
            embed.set_footer(text=f"Temps restant: {timedelta(seconds=int(time_left))}")

        await message.edit(embed=embed)

    @commands.group(name="poll", invoke_without_command=True)
    async def poll(self, ctx):
        await ctx.send("Utilisez `!poll create` pour créer un nouveau sondage.")

    @poll.command(name="create")
    @commands.has_permissions(administrator=True)
    async def create_poll(self, ctx, title: str, duration: int, *, description: str):
        """Créer un nouveau sondage avec plusieurs options."""
        if ctx.channel.id != self.poll_channel_id:
            await ctx.send(f"Les sondages ne peuvent être créés que dans <#{self.poll_channel_id}>.")
            return

        poll_id = str(ctx.author.id) + str(datetime.now().timestamp())

        self.polls[poll_id] = {
            "id": poll_id,
            "creator": ctx.author.id,
            "title": title,
            "description": description,
            "options": [],
            "start_time": datetime.now().timestamp(),
            "end_time": datetime.now().timestamp() + duration * 60,
            "active": True
        }

        self.save_polls()

        await ctx.send(f"Sondage créé avec l'ID: {poll_id}. Utilisez `!poll addoption {poll_id} [nom de l'option]` pour ajouter des options.")

    @poll.command(name="addoption")
    @commands.has_permissions(administrator=True)
    async def add_option(self, ctx, poll_id: str, *, option_name: str):
        """Ajouter une option à un sondage."""
        if poll_id not in self.polls:
            await ctx.send("Sondage introuvable.")
            return

        self.polls[poll_id]['options'].append({
            "name": option_name,
            "total_bet": 0,
            "voters": []
        })

        self.save_polls()
        await ctx.send(f"Option ajoutée au sondage {poll_id}.")

    @poll.command(name="start")
    @commands.has_permissions(administrator=True)
    async def start_poll(self, ctx, poll_id: str):
        """Démarrer un sondage."""
        if poll_id not in self.polls:
            await ctx.send("Sondage introuvable.")
            return

        poll = self.polls[poll_id]
        if not poll['options']:
            await ctx.send("Le sondage doit avoir au moins une option.")
            return

        channel = self.bot.get_channel(self.poll_channel_id)
        if not channel:
            await ctx.send("Channel de sondage introuvable.")
            return

        embed = discord.Embed(
            title=f"📊 Sondage: {poll['title']}",
            description=poll['description'],
            color=discord.Color.blue()
        )

        for i, option in enumerate(poll['options']):
            embed.add_field(
                name=f"Option {i+1}: {option['name']}",
                value="Cote: 1.0\nMises totales: 0 points\nVotes: 0",
                inline=False
            )

        time_left = poll['end_time'] - datetime.now().timestamp()
        embed.set_footer(text=f"Temps restant: {timedelta(seconds=int(time_left))}")

        message = await channel.send(embed=embed)

        for i in range(len(poll['options'])):
            await message.add_reaction(f"{i+1}\N{combining enclosing keycap}")

        self.polls[poll_id]['message_id'] = message.id
        self.save_polls()

        await ctx.send(f"Sondage {poll_id} démarré avec succès!")

    @poll.command(name="bet")
    async def bet_on_poll(self, ctx, poll_id: str, option_number: int, amount: int):
        """Miser des points sur une option de sondage."""
        if poll_id not in self.polls:
            await ctx.send("Sondage introuvable.")
            return

        poll = self.polls[poll_id]
        if not poll['active']:
            await ctx.send("Ce sondage est terminé.")
            return

        if option_number < 1 or option_number > len(poll['options']):
            await ctx.send("Numéro d'option invalide.")
            return

        option = poll['options'][option_number - 1]

        # Vérification des points de l'utilisateur (à adapter selon votre système)
        user_points = 1000  # Remplacez par votre système de points
        if user_points < amount:
            await ctx.send("Vous n'avez pas assez de points.")
            return

        # Mettre à jour les points de l'utilisateur (à adapter selon votre système)
        # user_points -= amount

        option['total_bet'] += amount
        if ctx.author.id not in option['voters']:
            option['voters'].append(ctx.author.id)

        self.save_polls()
        await self.update_poll_embed(await self.get_poll_message(poll_id), poll)
        await ctx.send(f"Vous avez misé {amount} points sur l'option {option_number}.")

    @poll.command(name="end")
    @commands.has_permissions(administrator=True)
    async def end_poll(self, ctx, poll_id: str):
        """Terminer un sondage manuellement."""
        if poll_id not in self.polls:
            await ctx.send("Sondage introuvable.")
            return

        poll = self.polls[poll_id]
        poll['active'] = False
        poll['end_time'] = datetime.now().timestamp()

        message = await self.get_poll_message(poll_id)
        if message:
            await self.update_poll_embed(message, poll)

        self.save_polls()
        await ctx.send(f"Sondage {poll_id} terminé.")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.channel_id != self.poll_channel_id:
            return

        message = await self.get_poll_message(payload.message_id)
        if not message:
            return

        poll_id = str(payload.message_id)
        if poll_id not in self.polls:
            return

        poll = self.polls[poll_id]
        if not poll['active']:
            return

        emoji = str(payload.emoji)
        if emoji in [f"{i}\N{combining enclosing keycap}" for i in range(1, len(poll['options']) + 1)]:
            option_number = int(emoji[0])
            option = poll['options'][option_number - 1]

            if payload.user_id not in option['voters']:
                option['voters'].append(payload.user_id)
                self.save_polls()
                await self.update_poll_embed(message, poll)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.channel_id != self.poll_channel_id:
            return

        message = await self.get_poll_message(payload.message_id)
        if not message:
            return

        poll_id = str(payload.message_id)
        if poll_id not in self.polls:
            return

        poll = self.polls[poll_id]
        if not poll['active']:
            return

        emoji = str(payload.emoji)
        if emoji in [f"{i}\N{combining enclosing keycap}" for i in range(1, len(poll['options']) + 1)]:
            option_number = int(emoji[0])
            option = poll['options'][option_number - 1]

            if payload.user_id in option['voters']:
                option['voters'].remove(payload.user_id)
                self.save_polls()
                await self.update_poll_embed(message, poll)

def setup(bot):
    bot.add_cog(PollSystem(bot))
