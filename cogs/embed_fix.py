import discord
from discord.ext import commands, tasks
import json
import re
import asyncio
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional, Tuple

class SocialMediaLinksManager(commands.Cog):
    """
    Cog pour détecter et gérer les liens de réseaux sociaux
    Maintient un embed fixe par canal avec les liens détectés
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.data_file = "social_links_data.json"
        self.embed_messages_file = "embed_messages.json"
        
        # Configuration des plateformes supportées
        self.site_configs = {
            "twitter": {
                "patterns": [
                    r"https?://(?:www\.)?(?:twitter\.com|x\.com)/(\w+)/status/(\d+)",
                    r"https?://(?:mobile\.)?(?:twitter\.com|x\.com)/(\w+)/status/(\d+)",
                ],
                "alternative_template": "https://fxtwitter.com/{}/status/{}",
                "emoji": "🐦",
                "name": "Twitter/X"
            },
            "instagram_post": {
                "patterns": [
                    r"https?://(?:www\.)?instagram\.com/p/([\w-]+)/?",
                ],
                "alternative_template": "https://ddinstagram.com/p/{}",
                "emoji": "📸",
                "name": "Instagram Post"
            },
            "instagram_reel": {
                "patterns": [
                    r"https?://(?:www\.)?instagram\.com/reel/([\w-]+)/?",
                ],
                "alternative_template": "https://ddinstagram.com/reel/{}",
                "emoji": "🎬",
                "name": "Instagram Reel"
            },
            "tiktok": {
                "patterns": [
                    r"https?://(?:www|vm|m)\.tiktok\.com/t/([^/]+)/?",
                    r"https?://(?:www|vm|m)\.tiktok\.com/@[\w.-]+/video/(\d+)",
                ],
                "alternative_template": "https://tnktok.com/t/{}",
                "emoji": "🎵",
                "name": "TikTok"
            },
            "youtube_shorts": {
                "patterns": [
                    r"https?://(?:www\.)?youtube\.com/shorts/([\w-]+)",
                ],
                "alternative_template": "https://youtube.com/watch?v={}",
                "emoji": "🎥",
                "name": "YouTube Shorts"
            },
            "reddit": {
                "patterns": [
                    r"https?://(?:www\.|old\.)?reddit\.com/r/([\w-]+)/comments/([\w-]+)",
                ],
                "alternative_template": "https://rxddit.com/r/{}/comments/{}",
                "emoji": "🔴",
                "name": "Reddit"
            }
        }
        
        # Chargement des données au démarrage
        self.links_data = self.load_data()
        self.embed_messages = self.load_embed_messages()
        
        # Démarrage de la tâche de nettoyage automatique
        self.cleanup_task.start()
    
    def load_data(self) -> Dict:
        """Charge les données des liens depuis le fichier JSON"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement des données: {e}")
        return {}
    
    def save_data(self) -> None:
        """Sauvegarde les données des liens dans le fichier JSON"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.links_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des données: {e}")
    
    def load_embed_messages(self) -> Dict:
        """Charge les IDs des messages d'embed par canal"""
        try:
            if os.path.exists(self.embed_messages_file):
                with open(self.embed_messages_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement des embeds: {e}")
        return {}
    
    def save_embed_messages(self) -> None:
        """Sauvegarde les IDs des messages d'embed"""
        try:
            with open(self.embed_messages_file, 'w', encoding='utf-8') as f:
                json.dump(self.embed_messages, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des embeds: {e}")
    
    def detect_social_link(self, text: str) -> Optional[Tuple[str, str, List[str]]]:
        """
        Détecte les liens de réseaux sociaux dans le texte
        Returns: (platform, original_url, extracted_groups) ou None
        """
        for platform, config in self.site_configs.items():
            for pattern in config["patterns"]:
                match = re.search(pattern, text)
                if match:
                    return platform, match.group(0), list(match.groups())
        return None
    
    def generate_alternative_url(self, platform: str, groups: List[str]) -> str:
        """Génère l'URL alternative basée sur la plateforme et les groupes extraits"""
        config = self.site_configs[platform]
        
        # Gestion spéciale pour Reddit (2 groupes)
        if platform == "reddit" and len(groups) >= 2:
            return config["alternative_template"].format(groups[0], groups[1])
        
        # Gestion spéciale pour Twitter (2 groupes)
        elif platform == "twitter" and len(groups) >= 2:
            return config["alternative_template"].format(groups[0], groups[1])
        
        # Gestion standard pour les autres plateformes (1 groupe)
        elif len(groups) >= 1:
            return config["alternative_template"].format(groups[0])
        
        return config["alternative_template"].format(*groups)
    
    def get_link_identifier(self, platform: str, groups: List[str]) -> str:
        """Génère un identifiant unique pour le lien basé sur la plateforme"""
        if platform == "reddit" and len(groups) >= 2:
            return f"{platform}_{groups[0]}_{groups[1]}"
        elif platform == "twitter" and len(groups) >= 2:
            return f"{platform}_{groups[0]}_{groups[1]}"
        elif len(groups) >= 1:
            return f"{platform}_{groups[0]}"
        return f"{platform}_{'_'.join(groups)}"
    
    def is_duplicate_link(self, channel_id: str, link_identifier: str) -> bool:
        """Vérifie si un lien est déjà présent dans ce canal"""
        if channel_id not in self.links_data:
            return False
        
        for link_data in self.links_data[channel_id]:
            if link_data.get("identifier") == link_identifier:
                return True
        return False
    
    def add_link_to_data(self, channel_id: str, link_data: Dict) -> None:
        """Ajoute un lien aux données du canal"""
        if channel_id not in self.links_data:
            self.links_data[channel_id] = []
        
        self.links_data[channel_id].append(link_data)
        self.save_data()
    
    def create_embed(self, channel_id: str) -> discord.Embed:
        """Crée l'embed avec tous les liens du canal"""
        embed = discord.Embed(
            title="🔗 Liens de Réseaux Sociaux",
            description="Liens détectés dans ce canal (dernières 24h)",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        if channel_id not in self.links_data or not self.links_data[channel_id]:
            embed.add_field(
                name="Aucun lien",
                value="Aucun lien détecté pour le moment",
                inline=False
            )
            return embed
        
        # Grouper les liens par plateforme
        platforms = {}
        for link_data in self.links_data[channel_id]:
            platform = link_data["platform"]
            if platform not in platforms:
                platforms[platform] = []
            platforms[platform].append(link_data)
        
        # Ajouter les liens groupés par plateforme
        for platform, links in platforms.items():
            config = self.site_configs[platform]
            value = ""
            for link_data in links[-5:]:  # Limiter à 5 liens par plateforme
                alt_url = link_data["alternative_url"]
                author = link_data["author"]
                value += f"• [Lien]({alt_url}) - par <@{author}>\n"
            
            if len(links) > 5:
                value += f"... et {len(links) - 5} autres liens\n"
            
            embed.add_field(
                name=f"{config['emoji']} {config['name']} ({len(links)})",
                value=value or "Aucun lien",
                inline=False
            )
        
        embed.set_footer(text=f"Total: {sum(len(links) for links in platforms.values())} liens")
        return embed
    
    async def create_response_embed(self, platform: str, alternative_url: str, author: discord.Member) -> discord.Embed:
        """Crée un embed de réponse pour le lien détecté"""
        config = self.site_configs[platform]
        
        embed = discord.Embed(
            title=f"{config['emoji']} {config['name']} détecté",
            description=f"Lien partagé par {author.mention}",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="🔗 Lien alternatif",
            value=f"[Cliquez ici pour accéder au contenu]({alternative_url})",
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ Informations",
            value="Le message original a été remplacé par ce lien alternatif pour une meilleure expérience.",
            inline=False
        )
        
        embed.set_thumbnail(url=author.display_avatar.url)
        embed.set_footer(text=f"Partagé par {author.display_name}")
        
        return embed
    
    async def update_or_create_embed(self, channel) -> None:
        """Met à jour ou crée l'embed dans le canal"""
        try:
            channel_id = str(channel.id)
            embed = self.create_embed(channel_id)
            
            # Vérifier si un message d'embed existe déjà
            if channel_id in self.embed_messages:
                try:
                    message = await channel.fetch_message(self.embed_messages[channel_id])
                    await message.edit(embed=embed)
                    return
                except discord.NotFound:
                    # Le message n'existe plus, en créer un nouveau
                    del self.embed_messages[channel_id]
            
            # Créer un nouveau message d'embed
            message = await channel.send(embed=embed)
            self.embed_messages[channel_id] = message.id
            self.save_embed_messages()
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour de l'embed: {e}")
    
    async def send_duplicate_warning(self, channel, author: discord.Member, platform: str) -> None:
        """Envoie un message d'avertissement pour les doublons"""
        config = self.site_configs[platform]
        
        embed = discord.Embed(
            title="⚠️ Lien déjà partagé",
            description=f"{author.mention}, ce lien de **{config['name']}** a déjà été partagé dans ce canal !",
            color=discord.Color.orange(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="💡 Conseil",
            value="Vérifiez l'embed des liens déjà partagés dans ce canal avant de poster.",
            inline=False
        )
        
        embed.set_thumbnail(url=author.display_avatar.url)
        embed.set_footer(text="Ce message se supprimera automatiquement dans 15 secondes")
        
        # Envoyer le message et le supprimer après 15 secondes
        warning_message = await channel.send(embed=embed)
        await asyncio.sleep(15)
        try:
            await warning_message.delete()
        except discord.NotFound:
            pass  # Le message a déjà été supprimé
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Listener principal pour détecter les liens dans les messages"""
        # Ignorer les messages du bot
        if message.author.bot:
            return
        
        # Vérifier les permissions du bot dans le canal
        permissions = message.channel.permissions_for(message.guild.me)
        if not (permissions.send_messages and permissions.manage_messages and permissions.embed_links):
            return
        
        # Détecter les liens de réseaux sociaux
        detection_result = self.detect_social_link(message.content)
        if not detection_result:
            return
        
        platform, original_url, groups = detection_result
        channel_id = str(message.channel.id)
        
        # Générer l'identifiant unique du lien
        link_identifier = self.get_link_identifier(platform, groups)
        
        # Vérifier si c'est un doublon
        if self.is_duplicate_link(channel_id, link_identifier):
            # Supprimer le message original
            try:
                await message.delete()
            except discord.NotFound:
                pass  # Le message a déjà été supprimé
            except discord.Forbidden:
                print(f"Permissions insuffisantes pour supprimer le message dans {message.channel.name}")
            
            # Envoyer l'avertissement de doublon
            await self.send_duplicate_warning(message.channel, message.author, platform)
            return
        
        # Générer l'URL alternative
        alternative_url = self.generate_alternative_url(platform, groups)
        
        # Supprimer le message original en premier
        try:
            await message.delete()
        except discord.NotFound:
            pass  # Le message a déjà été supprimé
        except discord.Forbidden:
            print(f"Permissions insuffisantes pour supprimer le message dans {message.channel.name}")
            # Si on ne peut pas supprimer, on continue quand même
        
        # Créer l'embed de réponse
        response_embed = await self.create_response_embed(platform, alternative_url, message.author)
        
        # Envoyer l'embed de réponse
        await message.channel.send(embed=response_embed)
        
        # Ajouter le lien aux données
        link_data = {
            "identifier": link_identifier,
            "platform": platform,
            "original_url": original_url,
            "alternative_url": alternative_url,
            "author": message.author.id,
            "timestamp": datetime.utcnow().isoformat(),
            "channel_id": channel_id
        }
        
        self.add_link_to_data(channel_id, link_data)
        
        # Mettre à jour l'embed fixe  
        await self.update_or_create_embed(message.channel)
    
    @tasks.loop(hours=24)
    async def cleanup_task(self):
        """Nettoie automatiquement les liens plus anciens que 24 heures"""
        print("🧹 Début du nettoyage automatique des liens...")
        
        current_time = datetime.utcnow()
        channels_to_update = set()
        
        # Nettoyer les données
        for channel_id, links in list(self.links_data.items()):
            original_count = len(links)
            
            # Filtrer les liens de moins de 24 heures
            self.links_data[channel_id] = [
                link for link in links
                if current_time - datetime.fromisoformat(link["timestamp"]) < timedelta(hours=24)
            ]
            
            # Si des liens ont été supprimés, marquer le canal pour mise à jour
            if len(self.links_data[channel_id]) != original_count:
                channels_to_update.add(channel_id)
            
            # Supprimer les canaux vides
            if not self.links_data[channel_id]:
                del self.links_data[channel_id]
        
        # Sauvegarder les données nettoyées
        self.save_data()
        
        # Mettre à jour les embeds des canaux concernés
        for channel_id in channels_to_update:
            try:
                channel = self.bot.get_channel(int(channel_id))
                if channel:
                    await self.update_or_create_embed(channel)
            except Exception as e:
                print(f"Erreur lors de la mise à jour de l'embed du canal {channel_id}: {e}")
        
        print(f"✅ Nettoyage terminé. {len(channels_to_update)} canaux mis à jour.")
    
    @cleanup_task.before_loop
    async def before_cleanup(self):
        """Attend que le bot soit prêt avant de démarrer le nettoyage"""
        await self.bot.wait_until_ready()
    
    
    @commands.command(name="force_cleanup")
    @commands.has_permissions(manage_messages=True)
    async def force_cleanup_command(self, ctx):
        """Commande pour forcer le nettoyage des liens (admin uniquement)"""
        await ctx.send("🧹 Démarrage du nettoyage forcé...")
        await self.cleanup_task()
        await ctx.send("✅ Nettoyage forcé terminé !")
    
    @commands.command(name="links_stats")
    async def links_stats(self, ctx):
        """Affiche les statistiques des liens détectés"""
        channel_id = str(ctx.channel.id)
        
        if channel_id not in self.links_data or not self.links_data[channel_id]:
            await ctx.send("❌ Aucun lien détecté dans ce canal.")
            return
        
        # Compter les liens par plateforme
        platform_counts = {}
        for link_data in self.links_data[channel_id]:
            platform = link_data["platform"]
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        # Créer l'embed des statistiques
        embed = discord.Embed(
            title="📊 Statistiques des Liens",
            description=f"Statistiques pour {ctx.channel.mention}",
            color=discord.Color.green()
        )
        
        for platform, count in platform_counts.items():
            config = self.site_configs[platform]
            embed.add_field(
                name=f"{config['emoji']} {config['name']}",
                value=f"{count} lien{'s' if count > 1 else ''}",
                inline=True
            )
        
        total_links = sum(platform_counts.values())
        embed.set_footer(text=f"Total: {total_links} liens détectés")
        
        await ctx.send(embed=embed)

async def setup(bot):
    """Fonction de setup pour charger le cog"""
    await bot.add_cog(SocialMediaLinksManager(bot))
