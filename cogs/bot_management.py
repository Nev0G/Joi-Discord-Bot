import discord
from discord.ext import commands, tasks
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
import os

class BotManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.temp_changes_file = 'temp_bot_changes.json'
        self.original_avatar = None
        self.original_name = None
        self.original_status = None
        self.temp_changes = self.load_temp_changes()
        self.cleanup_task.start()
        
    def cog_unload(self):
        self.cleanup_task.cancel()

    def load_temp_changes(self):
        """Charge les changements temporaires depuis le fichier JSON"""
        try:
            with open(self.temp_changes_file, 'r') as f:
                data = json.load(f)
                # Assurer la compatibilité avec l'ancien format
                if "status" not in data:
                    data["status"] = None
                return data
        except FileNotFoundError:
            return {"avatar": None, "name": None, "status": None}

    def save_temp_changes(self):
        """Sauvegarde les changements temporaires"""
        with open(self.temp_changes_file, 'w') as f:
            json.dump(self.temp_changes, f, indent=2)

    def load_user_data(self):
        """Charge les données utilisateur"""
        try:
            with open('user_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_user_data(self, data):
        """Sauvegarde les données utilisateur"""
        with open('user_data.json', 'w') as f:
            json.dump(data, f, indent=2)

    # ... (garder les méthodes avatar et name existantes) ...

    @commands.command(name="change_status", aliases=["status"])
    async def change_bot_status(self, ctx, activity_type: str = None, *, status_text: str = None):
        """Change le statut/rich presence du bot temporairement
        
        Types d'activités disponibles :
        - playing : Joue à ...
        - listening : Écoute ...
        - watching : Regarde ...
        - streaming : Streame ...
        - competing : Participe à ...
        """
        user_data = self.load_user_data()
        user_id = str(ctx.author.id)
        
        # Si aucun argument, afficher l'aide
        if not activity_type:
            embed = discord.Embed(
                title="🎮 Changer le Statut du Bot",
                description="**Usage :** `j!status <type> <texte>`\n\n"
                           "**Types disponibles :**\n"
                           "🎮 `playing` - Joue à ...\n"
                           "🎵 `listening` - Écoute ...\n"
                           "📺 `watching` - Regarde ...\n"
                           "🔴 `streaming` - Streame ...\n"
                           "🏆 `competing` - Participe à ...\n\n"
                           "**Exemples :**\n"
                           "`j!status playing Minecraft`\n"
                           "`j!status listening de la musique`\n"
                           "`j!status watching Netflix`",
                color=0x3498db
            )
            embed.add_field(
                name="💰 Prix",
                value="**Statut simple :** 3,500 points (6h)\n**Statut premium :** 6,000 points (12h)",
                inline=False
            )
            return await ctx.send(embed=embed)

        if not status_text:
            return await ctx.send("❌ Veuillez spécifier le texte du statut.")

        # Vérifier le type d'activité
        activity_types = {
            'playing': discord.ActivityType.playing,
            'listening': discord.ActivityType.listening,
            'watching': discord.ActivityType.watching,
            'streaming': discord.ActivityType.streaming,
            'competing': discord.ActivityType.competing
        }
        
        if activity_type.lower() not in activity_types:
            return await ctx.send("❌ Type d'activité invalide. Types disponibles : " + 
                                ", ".join(activity_types.keys()))

        # Vérifier les points (prix différent selon la durée)
        user_points = user_data.get(user_id, {}).get('points', 0)
        
        # Proposer les deux options
        embed = discord.Embed(
            title="🎮 Choisir la durée du statut",
            description=f"**Statut demandé :** {activity_type.title()} {status_text}\n\n"
                       "Choisissez la durée :",
            color=0x3498db
        )
        embed.add_field(
            name="⏰ Option 1 - Standard",
            value="**3,500 points** - 6 heures\n🅰️ Réagissez avec 🅰️",
            inline=True
        )
        embed.add_field(
            name="⏰ Option 2 - Premium", 
            value="**6,000 points** - 12 heures\n🅱️ Réagissez avec 🅱️",
            inline=True
        )
        embed.add_field(
            name="💰 Vos points",
            value=f"{user_points:,} points",
            inline=False
        )

        message = await ctx.send(embed=embed)
        await message.add_reaction('🅰️')
        await message.add_reaction('🅱️')

        def check(reaction, user):
            return (user == ctx.author and 
                   str(reaction.emoji) in ['🅰️', '🅱️'] and 
                   reaction.message.id == message.id)

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
            
            if str(reaction.emoji) == '🅰️':
                required_points = 3500
                duration_hours = 6
            else:
                required_points = 6000
                duration_hours = 12

            if user_points < required_points:
                embed = discord.Embed(
                    title="❌ Points insuffisants",
                    description=f"Il vous faut **{required_points:,} points**.\n"
                               f"Vous avez actuellement **{user_points:,} points**.",
                    color=0xff0000
                )
                return await message.edit(embed=embed)

            # Sauvegarder le statut original
            if not self.original_status:
                current_activity = self.bot.activity
                if current_activity:
                    self.original_status = {
                        'type': current_activity.type.name,
                        'name': current_activity.name
                    }
                else:
                    self.original_status = None

            # Créer et appliquer la nouvelle activité
            activity = discord.Activity(
                type=activity_types[activity_type.lower()],
                name=status_text
            )
            
            await self.bot.change_presence(activity=activity)
            
            # Déduire les points
            user_data[user_id]['points'] -= required_points
            self.save_user_data(user_data)
            
            # Enregistrer le changement temporaire
            expiry_time = datetime.now() + timedelta(hours=duration_hours)
            self.temp_changes["status"] = {
                "expires_at": expiry_time.isoformat(),
                "changed_by": ctx.author.id,
                "activity_type": activity_type.lower(),
                "activity_name": status_text,
                "duration": duration_hours
            }
            self.save_temp_changes()
            
            embed = discord.Embed(
                title="✅ Statut modifié !",
                description=f"**Nouveau statut :** {activity_type.title()} {status_text}\n"
                           f"**Coût :** {required_points:,} points\n"
                           f"**Durée :** {duration_hours} heures\n"
                           f"**Points restants :** {user_data[user_id]['points']:,}",
                color=0x00ff00
            )
            await message.edit(embed=embed)
            
        except asyncio.TimeoutError:
            embed = discord.Embed(
                title="⏰ Temps écoulé",
                description="Vous avez mis trop de temps à réagir.",
                color=0xff6b6b
            )
            await message.edit(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Erreur lors du changement de statut : {e}")

    @commands.command(name="reset_status")
    async def reset_bot_status(self, ctx):
        """Remet le statut du bot par défaut"""
        user_data = self.load_user_data()
        user_id = str(ctx.author.id)
        
        # Vérifier les points
        user_points = user_data.get(user_id, {}).get('points', 0)
        required_points = 500
        
        if user_points < required_points:
            embed = discord.Embed(
                title="❌ Points insuffisants",
                description=f"Il vous faut **{required_points:,} points** pour reset le statut.\n"
                           f"Vous avez actuellement **{user_points:,} points**.",
                color=0xff0000
            )
            return await ctx.send(embed=embed)

        try:
            # Restaurer le statut original ou enlever l'activité
            if self.original_status:
                activity_types = {
                    'playing': discord.ActivityType.playing,
                    'listening': discord.ActivityType.listening,
                    'watching': discord.ActivityType.watching,
                    'streaming': discord.ActivityType.streaming,
                    'competing': discord.ActivityType.competing
                }
                
                original_activity = discord.Activity(
                    type=activity_types.get(self.original_status['type'], discord.ActivityType.playing),
                    name=self.original_status['name']
                )
                await self.bot.change_presence(activity=original_activity)
            else:
                await self.bot.change_presence(activity=None)
            
            # Déduire les points
            user_data[user_id]['points'] -= required_points
            self.save_user_data(user_data)
            
            # Supprimer le changement temporaire
            self.temp_changes["status"] = None
            self.save_temp_changes()
            
            embed = discord.Embed(
                title="✅ Statut réinitialisé !",
                description=f"Le statut du bot a été remis par défaut.\n"
                           f"**Coût :** {required_points:,} points\n"
                           f"**Points restants :** {user_data[user_id]['points']:,}",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de la réinitialisation du statut : {e}")

    @commands.command(name="status_presets", aliases=["presets"])
    async def status_presets(self, ctx):
        """Affiche des statuts pré-définis populaires"""
        embed = discord.Embed(
            title="🎮 Statuts Pré-définis Populaires",
            description="Copiez-collez ces commandes populaires :",
            color=0x3498db
        )
        
        presets = [
            ("🎮 Gaming", [
                "`j!status playing Minecraft`",
                "`j!status playing Among Us`", 
                "`j!status playing Fortnite`",
                "`j!status competing in Ranked`"
            ]),
            ("🎵 Musique", [
                "`j!status listening to Spotify`",
                "`j!status listening to Lo-Fi Hip Hop`",
                "`j!status listening to your requests`"
            ]),
            ("📺 Divertissement", [
                "`j!status watching Netflix`",
                "`j!status watching YouTube`",
                "`j!status watching the server`"
            ]),
            ("🤖 Bot", [
                "`j!status playing with commands`",
                "`j!status watching over the server`",
                "`j!status listening to your problems`"
            ])
        ]
        
        for category, commands in presets:
            embed.add_field(
                name=category,
                value="\n".join(commands),
                inline=False
            )
        
        await ctx.send(embed=embed)

    @commands.command(name="bot_status")
    async def bot_status_info(self, ctx):
        """Affiche le statut actuel du bot (changements temporaires)"""
        embed = discord.Embed(
            title="🤖 Statut du Bot",
            color=0x3498db
        )
        
        # Vérifier les changements d'avatar
        if self.temp_changes.get("avatar"):
            avatar_data = self.temp_changes["avatar"]
            expires_at = datetime.fromisoformat(avatar_data["expires_at"])
            time_left = expires_at - datetime.now()
            
            if time_left.total_seconds() > 0:
                hours, remainder = divmod(int(time_left.total_seconds()), 3600)
                minutes = remainder // 60
                embed.add_field(
                    name="🖼️ Avatar Personnalisé",
                    value=f"**Actif encore :** {hours}h {minutes}m\n"
                          f"**Changé par :** <@{avatar_data['changed_by']}>",
                    inline=False
                )
        
        # Vérifier les changements de nom
        if self.temp_changes.get("name"):
            name_data = self.temp_changes["name"]
            expires_at = datetime.fromisoformat(name_data["expires_at"])
            time_left = expires_at - datetime.now()
            
            if time_left.total_seconds() > 0:
                hours, remainder = divmod(int(time_left.total_seconds()), 3600)
                minutes = remainder // 60
                embed.add_field(
                    name="🏷️ Nom Personnalisé",
                    value=f"**Nom actuel :** {self.bot.user.display_name}\n"
                          f"**Actif encore :** {hours}h {minutes}m\n"
                          f"**Changé par :** <@{name_data['changed_by']}>",
                    inline=False
                )
        
        # Vérifier les changements de statut
        if self.temp_changes.get("status"):
            status_data = self.temp_changes["status"]
            expires_at = datetime.fromisoformat(status_data["expires_at"])
            time_left = expires_at - datetime.now()
            
            if time_left.total_seconds() > 0:
                hours, remainder = divmod(int(time_left.total_seconds()), 3600)
                minutes = remainder // 60
                
                activity_icons = {
                    'playing': '🎮',
                    'listening': '🎵', 
                    'watching': '📺',
                    'streaming': '🔴',
                    'competing': '🏆'
                }
                
                icon = activity_icons.get(status_data['activity_type'], '🎮')
                embed.add_field(
                    name=f"{icon} Statut Personnalisé",
                    value=f"**Statut :** {status_data['activity_type'].title()} {status_data['activity_name']}\n"
                          f"**Actif encore :** {hours}h {minutes}m\n"
                          f"**Durée totale :** {status_data['duration']}h\n"
                          f"**Changé par :** <@{status_data['changed_by']}>",
                    inline=False
                )
        
        if not embed.fields:
            embed.description = "Aucune modification temporaire active."
            
        # Ajouter le statut actuel
        current_activity = self.bot.activity
        if current_activity:
            activity_name = f"{current_activity.type.name.title()} {current_activity.name}"
        else:
            activity_name = "Aucune activité"
            
        embed.add_field(
            name="📊 Statut Actuel",
            value=f"**Activité :** {activity_name}\n"
                  f"**En ligne :** {self.bot.status.name.title()}",
            inline=False
        )
        
        await ctx.send(embed=embed)

    @tasks.loop(minutes=5)
    async def cleanup_task(self):
        """Tâche qui s'exécute toutes les 5 minutes pour nettoyer les changements expirés"""
        current_time = datetime.now()
        changed = False
        
        # Vérifier l'avatar
        if self.temp_changes.get("avatar"):
            expires_at = datetime.fromisoformat(self.temp_changes["avatar"]["expires_at"])
            if current_time >= expires_at:
                try:
                    if self.original_avatar:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(self.original_avatar) as response:
                                if response.status == 200:
                                    avatar_bytes = await response.read()
                                    await self.bot.user.edit(avatar=avatar_bytes)
                    else:
                        await self.bot.user.edit(avatar=None)
                    self.temp_changes["avatar"] = None
                    changed = True
                    print("✅ Avatar du bot restauré automatiquement")
                except Exception as e:
                    print(f"❌ Erreur lors de la restauration de l'avatar : {e}")
        
        # Vérifier le nom
        if self.temp_changes.get("name"):
            expires_at = datetime.fromisoformat(self.temp_changes["name"]["expires_at"])
            if current_time >= expires_at:
                try:
                    await self.bot.user.edit(username=self.original_name or "JackBot")
                    self.temp_changes["name"] = None  
                    changed = True
                    print("✅ Nom du bot restauré automatiquement")
                except Exception as e:
                    print(f"❌ Erreur lors de la restauration du nom : {e}")
        
        # Vérifier le statut
        if self.temp_changes.get("status"):
            expires_at = datetime.fromisoformat(self.temp_changes["status"]["expires_at"])
            if current_time >= expires_at:
                try:
                    if self.original_status:
                        activity_types = {
                            'playing': discord.ActivityType.playing,
                            'listening': discord.ActivityType.listening,
                            'watching': discord.ActivityType.watching,
                            'streaming': discord.ActivityType.streaming,
                            'competing': discord.ActivityType.competing
                        }
                        
                        original_activity = discord.Activity(
                            type=activity_types.get(self.original_status['type'], discord.ActivityType.playing),
                            name=self.original_status['name']
                        )
                        await self.bot.change_presence(activity=original_activity)
                    else:
                        await self.bot.change_presence(activity=None)
                    
                    self.temp_changes["status"] = None
                    changed = True
                    print("✅ Statut du bot restauré automatiquement")
                except Exception as e:
                    print(f"❌ Erreur lors de la restauration du statut : {e}")
        
        if changed:
            self.save_temp_changes()

    @cleanup_task.before_loop
    async def before_cleanup_task(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(BotManagement(bot))
