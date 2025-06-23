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
    Répond uniquement avec l'URL alternative et l'utilisateur
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.data_file = "social_links_data.json"
        
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
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Listener principal pour détecter les liens dans les messages"""
        # Ignorer les messages du bot
        if message.author.bot:
            return
        
        # Vérifier les permissions du bot dans le canal
        if not message.channel.permissions_for(message.guild.me).send_messages:
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
            await message.reply(
                f"BOUCLED ❌ Ce lien de **{self.site_configs[platform]['name']}** a déjà été partagé salope !",
                delete_after=10
            )
            return
        
        # Générer l'URL alternative
        alternative_url = self.generate_alternative_url(platform, groups)
        
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
        
        # Créer le message avec emoji, plateforme, utilisateur et lien
        config = self.site_configs[platform]
        embed_fix_message = f"{config['emoji']} {config['name']} - @{message.author.display_name} {alternative_url}"
        
        # Envoyer uniquement le message texte
        await message.channel.send(embed_fix_message)
    
    @tasks.loop(hours=24)
    async def cleanup_task(self):
        """Nettoie automatiquement les liens plus anciens que 24 heures"""
        print("🧹 Début du nettoyage automatique des liens...")
        
        current_time = datetime.utcnow()
        
        # Nettoyer les données
        for channel_id, links in list(self.links_data.items()):
            # Filtrer les liens de moins de 24 heures
            self.links_data[channel_id] = [
                link for link in links
                if current_time - datetime.fromisoformat(link["timestamp"]) < timedelta(hours=24)
            ]
            
            # Supprimer les canaux vides
            if not self.links_data[channel_id]:
                del self.links_data[channel_id]
        
        # Sauvegarder les données nettoyées
        self.save_data()
        print("✅ Nettoyage terminé.")
    
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
