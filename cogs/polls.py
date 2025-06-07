import discord
from discord.ext import commands
import json
import os
import asyncio
from datetime import datetime, timedelta

class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_polls_file = 'active_polls.json'
        self.active_polls = self.load_active_polls()

    def load_active_polls(self):
        """Charge les sondages actifs depuis le fichier JSON"""
        try:
            with open(self.active_polls_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}

    def save_active_polls(self):
        """Sauvegarde les sondages actifs"""
        with open(self.active_polls_file, 'w') as f:
            json.dump(self.active_polls, f, indent=2)

    def load_user_data(self):
        """Charge les données utilisateur"""
        try:
            with open('user_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}

    def save_user_data(self, data):
        """Sauvegarde les données utilisateur"""
        with open('user_data.json', 'w') as f:
            json.dump(data, f, indent=2)

    def update_user_points(self, user_id, points):
        """Met à jour les points d'un utilisateur"""
        user_data = self.load_user_data()
        user_id = str(user_id)
        
        if user_id not in user_data:
            user_data[user_id] = {
                'points': 0,
                'last_daily': None,
                'total_won': 0,
                'total_lost': 0,
                'games_played': 0
            }
        
        user_data[user_id]['points'] += points
        self.save_user_data(user_data)

    @commands.command(name="poll", aliases=["sondage", "vote"])
    async def create_poll(self, ctx, title, *options):
        """Créer un sondage interactif
        Usage: j!poll "Titre du sondage" "Option 1" "Option 2" "Option 3" ...
        """
        if len(options) < 2:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Vous devez fournir au moins 2 options pour le sondage !",
                color=0xe74c3c
            )
            await ctx.send(embed=embed)
            return

        if len(options) > 10:
            embed = discord.Embed(
                title="❌ Erreur", 
                description="Maximum 10 options par sondage !",
                color=0xe74c3c
            )
            await ctx.send(embed=embed)
            return

        # Émojis pour les réactions
        emoji_numbers = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        
        # Créer l'embed du sondage
        embed = discord.Embed(
            title=f"🗳️ {title}",
            description="Votez en cliquant sur les réactions !",
            color=0x3498db,
            timestamp=datetime.utcnow()
        )
        
        # Ajouter les options
        options_text = ""
        for i, option in enumerate(options):
            options_text += f"{emoji_numbers[i]} {option}\n"
        
        embed.add_field(
            name="Options:", 
            value=options_text,
            inline=False
        )
        
        embed.add_field(
            name="📊 Votes:",
            value="Aucun vote pour le moment",
            inline=False
        )
        
        embed.set_footer(
            text=f"Sondage créé par {ctx.author.display_name}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else None
        )

        # Envoyer le message
        poll_message = await ctx.send(embed=embed)
        
        # Ajouter les réactions
        for i in range(len(options)):
            await poll_message.add_reaction(emoji_numbers[i])
        
        # Ajouter une réaction pour fermer le sondage
        await poll_message.add_reaction('🔒')

        # Sauvegarder le sondage
        poll_data = {
            'title': title,
            'options': list(options),
            'creator_id': ctx.author.id,
            'channel_id': ctx.channel.id,
            'message_id': poll_message.id,
            'votes': {},
            'created_at': datetime.utcnow().isoformat(),
            'active': True
        }
        
        self.active_polls[str(poll_message.id)] = poll_data
        self.save_active_polls()

        # Récompenser le créateur
        self.update_user_points(ctx.author.id, 10)

    @commands.command(name="quickpoll", aliases=["qpoll"])
    async def quick_poll(self, ctx, *, question):
        """Créer un sondage oui/non rapide
        Usage: j!quickpoll Votre question ?
        """
        embed = discord.Embed(
            title="🗳️ Sondage Rapide",
            description=f"**{question}**",
            color=0x2ecc71,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="Options:",
            value="👍 Oui\n👎 Non",
            inline=False
        )
        
        embed.set_footer(
            text=f"Sondage créé par {ctx.author.display_name}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else None
        )

        message = await ctx.send(embed=embed)
        await message.add_reaction('👍')
        await message.add_reaction('👎')

        # Récompenser le créateur
        self.update_user_points(ctx.author.id, 5)

    @commands.command(name="pollresult", aliases=["results"])
    async def poll_results(self, ctx, message_id: int):
        """Voir les résultats d'un sondage
        Usage: j!pollresult <ID_du_message>
        """
        poll_id = str(message_id)
        
        if poll_id not in self.active_polls:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Sondage introuvable !",
                color=0xe74c3c
            )
            await ctx.send(embed=embed)
            return

        poll = self.active_polls[poll_id]
        
        try:
            channel = self.bot.get_channel(poll['channel_id'])
            message = await channel.fetch_message(message_id)
        except:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Impossible de récupérer le message du sondage !",
                color=0xe74c3c
            )
            await ctx.send(embed=embed)
            return

        # Compter les votes
        emoji_numbers = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        vote_counts = []
        total_votes = 0

        for i, option in enumerate(poll['options']):
            reaction = discord.utils.get(message.reactions, emoji=emoji_numbers[i])
            count = reaction.count - 1 if reaction else 0  # -1 pour enlever la réaction du bot
            vote_counts.append(count)
            total_votes += count

        # Créer l'embed des résultats
        embed = discord.Embed(
            title=f"📊 Résultats : {poll['title']}",
            color=0xf39c12,
            timestamp=datetime.utcnow()
        )

        if total_votes == 0:
            embed.add_field(
                name="Résultats:",
                value="Aucun vote pour le moment",
                inline=False
            )
        else:
            results_text = ""
            for i, (option, count) in enumerate(zip(poll['options'], vote_counts)):
                percentage = (count / total_votes) * 100 if total_votes > 0 else 0
                bar_length = int(percentage / 10)
                bar = "█" * bar_length + "░" * (10 - bar_length)
                results_text += f"{emoji_numbers[i]} **{option}**\n{bar} {count} votes ({percentage:.1f}%)\n\n"
            
            embed.add_field(
                name="Résultats:",
                value=results_text,
                inline=False
            )

        embed.add_field(
            name="📈 Statistiques:",
            value=f"**Total des votes:** {total_votes}\n"
                  f"**Statut:** {'🟢 Actif' if poll['active'] else '🔴 Fermé'}",
            inline=False
        )

        await ctx.send(embed=embed)

    @commands.command(name="closepoll", aliases=["endpoll"])
    async def close_poll(self, ctx, message_id: int):
        """Fermer un sondage (créateur uniquement)
        Usage: j!closepoll <ID_du_message>
        """
        poll_id = str(message_id)
        
        if poll_id not in self.active_polls:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Sondage introuvable !",
                color=0xe74c3c
            )
            await ctx.send(embed=embed)
            return

        poll = self.active_polls[poll_id]
        
        # Vérifier si l'utilisateur peut fermer le sondage
        if poll['creator_id'] != ctx.author.id and not ctx.author.guild_permissions.manage_messages:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Seul le créateur du sondage ou un modérateur peut le fermer !",
                color=0xe74c3c
            )
            await ctx.send(embed=embed)
            return

        # Marquer comme fermé
        self.active_polls[poll_id]['active'] = False
        self.save_active_polls()

        # Afficher les résultats finaux
        await self.poll_results(ctx, message_id)

        embed = discord.Embed(
            title="🔒 Sondage Fermé",
            description=f"Le sondage **{poll['title']}** a été fermé par {ctx.author.mention}",
            color=0x95a5a6
        )
        await ctx.send(embed=embed)

    @commands.command(name="mypolls", aliases=["mesondages"])
    async def my_polls(self, ctx):
        """Voir vos sondages actifs"""
        user_polls = []
        
        for poll_id, poll in self.active_polls.items():
            if poll['creator_id'] == ctx.author.id and poll['active']:
                user_polls.append((poll_id, poll))

        if not user_polls:
            embed = discord.Embed(
                title="📋 Vos Sondages",
                description="Vous n'avez aucun sondage actif.",
                color=0x95a5a6
            )
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title="📋 Vos Sondages Actifs",
            color=0x3498db
        )

        for poll_id, poll in user_polls[:10]:  # Limiter à 10
            created_date = datetime.fromisoformat(poll['created_at']).strftime("%d/%m/%Y %H:%M")
            embed.add_field(
                name=f"🗳️ {poll['title']}",
                value=f"**ID:** {poll_id}\n"
                      f"**Créé:** {created_date}\n"
                      f"**Options:** {len(poll['options'])}",
                inline=True
            )

        embed.set_footer(text="Utilisez j!pollresult <ID> pour voir les résultats")
        await ctx.send(embed=embed)


    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Gérer les votes sur les sondages"""
        if user.bot:
            return

        message = reaction.message
        poll_id = str(message.id)

        if poll_id in self.active_polls and self.active_polls[poll_id]['active']:
            # Récompenser le votant
            self.update_user_points(user.id, 1)

    async def cleanup_old_polls(self):
        """Nettoie les anciens sondages (optionnel - à appeler manuellement)"""
        current_time = datetime.utcnow()
        to_remove = []

        for poll_id, poll in self.active_polls.items():
            created_time = datetime.fromisoformat(poll['created_at'])
            if (current_time - created_time).days > 30:  # Supprimer après 30 jours
                to_remove.append(poll_id)

        for poll_id in to_remove:
            del self.active_polls[poll_id]

        if to_remove:
            self.save_active_polls()

async def setup(bot):
    await bot.add_cog(Poll(bot))
