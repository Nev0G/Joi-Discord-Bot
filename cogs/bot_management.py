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
        
    def manag_unload(self):
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
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "avatar": None,
                "name": None, 
                "status": None
            }

    def save_temp_changes(self):
        """Sauvegarde les changements temporaires"""
        with open(self.temp_changes_file, 'w') as f:
            json.dump(self.temp_changes, f, indent=2)

    def load_user_data(self):
        """Charge les données utilisateur"""
        try:
            with open('user_data.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_user_data(self, data):
        """Sauvegarde les données utilisateur"""
        with open('user_data.json', 'w') as f:
            json.dump(data, f, indent=2)

    def deduct_user_points(self, user_id, points):
        """Déduit des points de l'utilisateur"""
        user_data = self.load_user_data()
        user_id = str(user_id)
        
        if user_id not in user_data:
            return False
        
        if user_data[user_id].get('points', 0) < points:
            return False
        
        user_data[user_id]['points'] -= points
        self.save_user_data(user_data)
        return True

    async def save_original_values(self):
        """Sauvegarde les valeurs originales du bot"""
        if self.original_avatar is None and self.bot.user.avatar:
            self.original_avatar = await self.bot.user.avatar.read()
        
        if self.original_name is None:
            self.original_name = self.bot.user.name
            
        if self.original_status is None:
            self.original_status = {
                'activity': self.bot.activity,
                'status': self.bot.status
            }

    @tasks.loop(minutes=30)
    async def cleanup_task(self):
        """Tâche de nettoyage pour restaurer les valeurs originales"""
        try:
            current_time = datetime.now()
            changes_made = False

            # Vérifier l'avatar
            if (self.temp_changes["avatar"] and 
                datetime.fromisoformat(self.temp_changes["avatar"]["expires_at"]) <= current_time):
                
                if self.original_avatar:
                    try:
                        await self.bot.user.edit(avatar=self.original_avatar)
                        print("✅ Avatar du bot restauré automatiquement")
                    except Exception as e:
                        print(f"❌ Erreur lors de la restauration de l'avatar: {e}")
                
                self.temp_changes["avatar"] = None
                changes_made = True

            # Vérifier le nom
            if (self.temp_changes["name"] and 
                datetime.fromisoformat(self.temp_changes["name"]["expires_at"]) <= current_time):
                
                if self.original_name:
                    try:
                        await self.bot.user.edit(username=self.original_name)
                        print("✅ Nom du bot restauré automatiquement")
                    except Exception as e:
                        print(f"❌ Erreur lors de la restauration du nom: {e}")
                
                self.temp_changes["name"] = None
                changes_made = True

            # Vérifier le statut
            if (self.temp_changes["status"] and 
                datetime.fromisoformat(self.temp_changes["status"]["expires_at"]) <= current_time):
                
                if self.original_status:
                    try:
                        await self.bot.change_presence(
                            activity=self.original_status['activity'],
                            status=self.original_status['status']
                        )
                        print("✅ Statut du bot restauré automatiquement")
                    except Exception as e:
                        print(f"❌ Erreur lors de la restauration du statut: {e}")
                
                self.temp_changes["status"] = None
                changes_made = True

            if changes_made:
                self.save_temp_changes()

        except Exception as e:
            print(f"❌ Erreur dans cleanup_task: {e}")

    @cleanup_task.before_loop
    async def before_cleanup_task(self):
        await self.bot.wait_until_ready()

    @commands.command(name="avatar")
    @commands.cooldown(1, 300, commands.BucketType.user)  # 5 min cooldown
    async def change_avatar(self, ctx, url: str = None):
        """Change l'avatar du bot temporairement (6h) - 5000 points"""
        await self.save_original_values()
        
        if not url:
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url
            else:
                embed = discord.Embed(
                    title="❌ Erreur",
                    description="Veuillez fournir une URL d'image ou joindre une image !",
                    color=0xe74c3c
                )
                await ctx.send(embed=embed)
                return

        # Vérifier les points
        if not self.deduct_user_points(ctx.author.id, 5000):
            embed = discord.Embed(
                title="❌ Points insuffisants",
                description="Il vous faut **5,000 points** pour changer l'avatar du bot !",
                color=0xe74c3c
            )
            await ctx.send(embed=embed)
            return

        try:
            # Télécharger l'image
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        raise Exception("Impossible de télécharger l'image")
                    
                    avatar_bytes = await resp.read()
                    
                    if len(avatar_bytes) > 8 * 1024 * 1024:  # 8MB max
                        raise Exception("Image trop volumineuse (max 8MB)")

            # Changer l'avatar
            await self.bot.user.edit(avatar=avatar_bytes)
            
            # Enregistrer le changement temporaire
            expires_at = datetime.now() + timedelta(hours=6)
            self.temp_changes["avatar"] = {
                "user_id": ctx.author.id,
                "expires_at": expires_at.isoformat(),
                "original_url": url
            }
            self.save_temp_changes()

            embed = discord.Embed(
                title="✅ Avatar Modifié",
                description=f"L'avatar du bot a été changé par {ctx.author.mention} !\n"
                           f"**Expiration :** <t:{int(expires_at.timestamp())}:R>\n"
                           f"**Coût :** 5,000 points",
                color=0x2ecc71
            )
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            await ctx.send(embed=embed)

        except discord.HTTPException as e:
            embed = discord.Embed(
                title="❌ Erreur Discord",
                description=f"Impossible de changer l'avatar : {str(e)}\n"
                           "*(Vos points ont été remboursés)*",
                color=0xe74c3c
            )
            # Rembourser les points
            user_data = self.load_user_data()
            user_data[str(ctx.author.id)]['points'] += 5000
            self.save_user_data(user_data)
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur : {str(e)}\n*(Vos points ont été remboursés)*",
                color=0xe74c3c
            )
            # Rembourser les points
            user_data = self.load_user_data()
            user_data[str(ctx.author.id)]['points'] += 5000
            self.save_user_data(user_data)
            await ctx.send(embed=embed)

    @commands.command(name="name", aliases=["botname"])
    @commands.cooldown(1, 600, commands.BucketType.user)  # 10 min cooldown
    async def change_name(self, ctx, *, new_name: str):
        """Change le nom du bot temporairement (6h) - 7500 points"""
        await self.save_original_values()
        
        if len(new_name) > 32:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Le nom ne peut pas dépasser 32 caractères !",
                color=0xe74c3c
            )
            await ctx.send(embed=embed)
            return

        # Vérifier les points
        if not self.deduct_user_points(ctx.author.id, 7500):
            embed = discord.Embed(
                title="❌ Points insuffisants",
                description="Il vous faut **7,500 points** pour changer le nom du bot !",
                color=0xe74c3c
            )
            await ctx.send(embed=embed)
            return

        try:
            old_name = self.bot.user.name
            await self.bot.user.edit(username=new_name)
            
            # Enregistrer le changement temporaire
            expires_at = datetime.now() + timedelta(hours=6)
            self.temp_changes["name"] = {
                "user_id": ctx.author.id,
                "expires_at": expires_at.isoformat(),
                "new_name": new_name,
                "old_name": old_name
            }
            self.save_temp_changes()

            embed = discord.Embed(
                title="✅ Nom Modifié",
                description=f"Le nom du bot a été changé par {ctx.author.mention} !\n"
                           f"**Ancien nom :** {old_name}\n"
                           f"**Nouveau nom :** {new_name}\n"
                           f"**Expiration :** <t:{int(expires_at.timestamp())}:R>\n"
                           f"**Coût :** 7,500 points",
                color=0x2ecc71
            )
            await ctx.send(embed=embed)

        except discord.HTTPException as e:
            embed = discord.Embed(
                title="❌ Erreur Discord",
                description=f"Impossible de changer le nom : {str(e)}\n"
                           "*(Vos points ont été remboursés)*",
                color=0xe74c3c
            )
            # Rembourser les points
            user_data = self.load_user_data()
            user_data[str(ctx.author.id)]['points'] += 7500
            self.save_user_data(user_data)
            await ctx.send(embed=embed)

    @commands.command(name="status", aliases=["presence"])
    async def change_status(self, ctx, activity_type: str = None, *, text: str = None):
        """Change le statut du bot temporairement
        Types: playing, listening, watching, streaming, competing
        Usage: j!status playing Minecraft
        """
        await self.save_original_values()
        
        if not activity_type or not text:
            embed = discord.Embed(
                title="❌ Usage Incorrect",
                description="**Usage:** `j!status <type> <texte>`\n\n"
                           "**Types disponibles:**\n"
                           "• `playing` - Joue à... (3,500 pts - 6h)\n"
                           "• `listening` - Écoute... (3,500 pts - 6h)\n"
                           "• `watching` - Regarde... (3,500 pts - 6h)\n"
                           "• `streaming` - Streame... (6,000 pts - 12h)\n"
                           "• `competing` - Participe à... (6,000 pts - 12h)\n\n"
                           "**Exemple:** `j!status playing Minecraft`",
                color=0xe74c3c
            )
            await ctx.send(embed=embed)
            return

        # Déterminer le coût et la durée
        activity_type = activity_type.lower()
        if activity_type in ['playing', 'listening', 'watching']:
            cost = 3500
            duration_hours = 6
        elif activity_type in ['streaming', 'competing']:
            cost = 6000
            duration_hours = 12
        else:
            embed = discord.Embed(
                title="❌ Type Invalide",
                description="Types valides: `playing`, `listening`, `watching`, `streaming`, `competing`",
                color=0xe74c3c
            )
            await ctx.send(embed=embed)
            return

        # Vérifier les points
        if not self.deduct_user_points(ctx.author.id, cost):
            embed = discord.Embed(
                title="❌ Points insuffisants",
                description=f"Il vous faut **{cost:,} points** pour ce type de statut !",
                color=0xe74c3c
            )
            await ctx.send(embed=embed)
            return

        try:
            # Créer l'activité appropriée
            if activity_type == 'playing':
                activity = discord.Game(name=text)
            elif activity_type == 'listening':
                activity = discord.Activity(type=discord.ActivityType.listening, name=text)
            elif activity_type == 'watching':
                activity = discord.Activity(type=discord.ActivityType.watching, name=text)
            elif activity_type == 'streaming':
                activity = discord.Streaming(name=text, url="https://twitch.tv/discord")
            elif activity_type == 'competing':
                activity = discord.Activity(type=discord.ActivityType.competing, name=text)

            # Changer le statut
            await self.bot.change_presence(activity=activity, status=discord.Status.online)
            
            # Enregistrer le changement temporaire
            expires_at = datetime.now() + timedelta(hours=duration_hours)
            self.temp_changes["status"] = {
                "user_id": ctx.author.id,
                "expires_at": expires_at.isoformat(),
                "activity_type": activity_type,
                "text": text
            }
            self.save_temp_changes()

            # Emojis pour chaque type
            type_emojis = {
                'playing': '🎮',
                'listening': '🎵',
                'watching': '👀',
                'streaming': '🟣',
                'competing': '🏆'
            }

            embed = discord.Embed(
                title="✅ Statut Modifié",
                description=f"{type_emojis.get(activity_type, '📱')} Nouveau statut défini par {ctx.author.mention} !\n\n"
                           f"**Type :** {activity_type.title()}\n"
                           f"**Texte :** {text}\n"
                           f"**Durée :** {duration_hours}h\n"
                           f"**Expiration :** <t:{int(expires_at.timestamp())}:R>\n"
                           f"**Coût :** {cost:,} points",
                color=0x2ecc71
            )
            await ctx.send(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Impossible de changer le statut : {str(e)}\n"
                           "*(Vos points ont été remboursés)*",
                color=0xe74c3c
            )
            # Rembourser les points
            user_data = self.load_user_data()
            user_data[str(ctx.author.id)]['points'] += cost
            self.save_user_data(user_data)
            await ctx.send(embed=embed)

    @commands.command(name="reset_status", aliases=["resetstatus"])
    async def reset_status(self, ctx):
        """Remet le statut du bot par défaut - 500 points"""
        if not self.deduct_user_points(ctx.author.id, 500):
            embed = discord.Embed(
                title="❌ Points insuffisants",
                description="Il vous faut **500 points** pour reset le statut !",
                color=0xe74c3c
            )
            await ctx.send(embed=embed)
            return

        try:
            # Restaurer le statut original
            if self.original_status:
                await self.bot.change_presence(
                    activity=self.original_status['activity'],
                    status=self.original_status['status']
                )
            else:
                await self.bot.change_presence(activity=None, status=discord.Status.online)
            
            # Supprimer le changement temporaire
            self.temp_changes["status"] = None
            self.save_temp_changes()

            embed = discord.Embed(
                title="✅ Statut Restauré",
                description=f"Le statut du bot a été remis par défaut par {ctx.author.mention}\n"
                           f"**Coût :** 500 points",
                color=0x2ecc71
            )
            await ctx.send(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Erreur : {str(e)}\n*(Vos points ont été remboursés)*",
                color=0xe74c3c
            )
            # Rembourser les points
            user_data = self.load_user_data()
            user_data[str(ctx.author.id)]['points'] += 500
            self.save_user_data(user_data)
            await ctx.send(embed=embed)

    @commands.command(name="presets", aliases=["statuspresets"])
    async def status_presets(self, ctx):
        """Affiche les statuts pré-définis populaires"""
        embed = discord.Embed(
            title="🎮 Statuts Pré-définis",
            description="Copiez-collez ces commandes populaires !",
            color=0x9b59b6
        )

        presets = {
            "🎮 Gaming": [
                "j!status playing Minecraft",
                "j!status playing Among Us", 
                "j!status playing Valorant",
                "j!status competing dans Ranked"
            ],
            "🎵 Musique": [
                "j!status listening to Spotify",
                "j!status listening to Lofi Hip Hop",
                "j!status listening to vos playlists"
            ],
            "📺 Divertissement": [
                "j!status watching Netflix",
                "j!status watching YouTube",
                "j!status watching les membres",
                "j!status streaming Just Chatting"
            ],
            "😎 Fun": [
                "j!status playing avec mes circuits",
                "j!status watching le serveur Discord",
                "j!status competing pour l'attention",
                "j!status listening to vos conversations"
            ]
        }

        for category, commands in presets.items():
            embed.add_field(
                name=category,
                value="\n".join([f"`{cmd}`" for cmd in commands]),
                inline=True
            )

        embed.add_field(
            name="💡 Astuce",
            value="Les statuts `streaming` et `competing` durent 12h au lieu de 6h !",
            inline=False
        )

        await ctx.send(embed=embed)

    @commands.command(name="botstatus", aliases=["status_info"])
    async def show_bot_status_info(self, ctx):
        """Affiche toutes les modifications actives du bot"""
        embed = discord.Embed(
            title="🤖 État du Bot",
            description="Informations sur les modifications actives",
            color=0x3498db,
            timestamp=datetime.now()
        )

        # Informations actuelles
        embed.add_field(
            name="📊 Informations Actuelles",
            value=f"**Nom :** {self.bot.user.name}\n"
                  f"**Statut :** {self.bot.status}\n"
                  f"**Activité :** {self.bot.activity.name if self.bot.activity else 'Aucune'}",
            inline=False
        )

        # Vérifier les modifications actives
        active_changes = []
        
        if self.temp_changes.get("avatar"):
            expires = datetime.fromisoformat(self.temp_changes["avatar"]["expires_at"])
            user_id = self.temp_changes["avatar"]["user_id"]
            user = self.bot.get_user(user_id)
            active_changes.append(f"🖼️ **Avatar** - Par {user.mention if user else 'Utilisateur inconnu'}\nExpire <t:{int(expires.timestamp())}:R>")

        if self.temp_changes.get("name"):
            expires = datetime.fromisoformat(self.temp_changes["name"]["expires_at"])
            user_id = self.temp_changes["name"]["user_id"]
            user = self.bot.get_user(user_id)
            active_changes.append(f"📝 **Nom** - Par {user.mention if user else 'Utilisateur inconnu'}\nExpire <t:{int(expires.timestamp())}:R>")

        if self.temp_changes.get("status"):
            expires = datetime.fromisoformat(self.temp_changes["status"]["expires_at"])
            user_id = self.temp_changes["status"]["user_id"]
            user = self.bot.get_user(user_id)
            status_type = self.temp_changes["status"]["activity_type"]
            status_text = self.temp_changes["status"]["text"]
            active_changes.append(f"🎮 **Statut** - Par {user.mention if user else 'Utilisateur inconnu'}\n{status_type}: {status_text}\nExpire <t:{int(expires.timestamp())}:R>")

        if active_changes:
            embed.add_field(
                name="🔄 Modifications Actives",
                value="\n\n".join(active_changes),
                inline=False
            )
        else:
            embed.add_field(
                name="✅ État Normal",
                value="Aucune modification temporaire active",
                inline=False
            )

        # Informations sur les originaux
        if self.original_name or self.original_avatar or self.original_status:
            original_info = []
            if self.original_name:
                original_info.append(f"**Nom original :** {self.original_name}")
            if self.original_avatar:
                original_info.append("**Avatar original :** Sauvegardé")
            if self.original_status:
                original_info.append("**Statut original :** Sauvegardé")
            
            embed.add_field(
                name="💾 Valeurs de Sauvegarde",
                value="\n".join(original_info),
                inline=False
            )

        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(BotManagement(bot))
