import logging
from discord.ext import commands
import re
import discord
import asyncio
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import json
from datetime import datetime, timedelta

class EmbedFix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.liens_envoyes = {}  # Dictionnaire avec timestamp pour éviter le spam
        self.cooldown_duration = 300  # 5 minutes de cooldown
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('EmbedFix')
        
        # Configuration des sites supportés avec leurs alternatives
        self.site_configs = {
            "twitter": {
                "patterns": [
                    r"https?://(?:www\.)?(?:twitter\.com|x\.com)/(\w+)/status/(\d+)(?:\S*)?",
                    r"https?://(?:mobile\.)?(?:twitter\.com|x\.com)/(\w+)/status/(\d+)(?:\S*)?",
                ],
                "alternatives": [
                    "https://fxtwitter.com/{}/status/{}",
                    "https://vxtwitter.com/{}/status/{}",
                    "https://fixupx.com/{}/status/{}"
                ],
                "emoji": "🐦",
                "name": "Twitter/X"
            },
            "instagram_post": {
                "patterns": [
                    r"https?://(?:www\.)?instagram\.com/p/([\w-]+)/?(?:\S*)?",
                ],
                "alternatives": [
                    "https://ddinstagram.com/p/{}",
                    "https://imginn.org/p/{}",
                ],
                "emoji": "📸",
                "name": "Instagram Post"
            },
            "instagram_reel": {
                "patterns": [
                    r"https?://(?:www\.)?instagram\.com/reel/([\w-]+)/?(?:\S*)?",
                ],
                "alternatives": [
                    "https://ddinstagram.com/reel/{}",
                    "https://imginn.org/reel/{}",
                ],
                "emoji": "🎬",
                "name": "Instagram Reel"
            },
            "tiktok": {
                "patterns": [
                    r"https?://(?:(?:www|vm|m)\.)?tiktok\.com/(@[\w.-]+/video/\d+|\w+)/?(?:\S*)?",
                    r"https?://(?:www\.)?tiktok\.com/t/(\w+)/?(?:\S*)?",
                ],
                "alternatives": [
                    "https://tnktok.com/{}",
                    "https://tikwm.com/{}",
                ],
                "emoji": "🎵",
                "name": "TikTok"
            },
            "youtube_shorts": {
                "patterns": [
                    r"https?://(?:www\.)?youtube\.com/shorts/([\w-]+)(?:\S*)?",
                    r"https?://youtu\.be/([\w-]+)\?.*?(?:&|\?).*?shorts",
                ],
                "alternatives": [
                    "https://youtube.com/watch?v={}",
                ],
                "emoji": "🎥",
                "name": "YouTube Shorts"
            },
            "reddit": {
                "patterns": [
                    r"https?://(?:www\.)?reddit\.com/r/([\w-]+)/comments/([\w-]+)(?:/[\w-]*)?/?(?:\S*)?",
                    r"https?://(?:old\.)?reddit\.com/r/([\w-]+)/comments/([\w-]+)(?:/[\w-]*)?/?(?:\S*)?",
                ],
                "alternatives": [
                    "https://rxddit.com/r/{}/comments/{}",
                    "https://vxreddit.com/r/{}/comments/{}",
                ],
                "emoji": "🔴",
                "name": "Reddit"
            },
            "pixiv": {
                "patterns": [
                    r"https?://(?:www\.)?pixiv\.net/(?:en/)?artworks/(\d+)(?:\S*)?",
                ],
                "alternatives": [
                    "https://phixiv.net/artworks/{}",
                ],
                "emoji": "🎨",
                "name": "Pixiv"
            },
            "twitch_clip": {
                "patterns": [
                    r"https?://(?:www\.)?twitch\.tv/\w+/clip/([\w-]+)(?:\S*)?",
                    r"https?://clips\.twitch\.tv/([\w-]+)(?:\S*)?",
                ],
                "alternatives": [
                    "https://clips.twitch.tv/embed?clip={}&parent=discord.com",
                ],
                "emoji": "💜",
                "name": "Twitch Clip"
            },
        }

    def clean_cooldowns(self):
        """Nettoie les anciens cooldowns"""
        current_time = datetime.now()
        expired_keys = []
        
        for key, timestamp in self.liens_envoyes.items():
            if current_time - timestamp > timedelta(seconds=self.cooldown_duration):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.liens_envoyes[key]

    def is_on_cooldown(self, url, user_id):
        """Vérifie si l'URL est en cooldown pour cet utilisateur"""
        self.clean_cooldowns()
        key = f"{user_id}:{url}"
        return key in self.liens_envoyes

    def add_to_cooldown(self, url, user_id):
        """Ajoute l'URL au cooldown"""
        key = f"{user_id}:{url}"
        self.liens_envoyes[key] = datetime.now()

    def extract_url_parts(self, url, pattern):
        """Extrait les parties importantes de l'URL selon le pattern"""
        match = re.search(pattern, url)
        if match:
            return match.groups()
        return None

    def build_fixed_url(self, parts, template):
        """Construit l'URL fixée à partir du template"""
        try:
            return template.format(*parts)
        except (IndexError, ValueError) as e:
            self.logger.error(f"Erreur lors de la construction de l'URL: {e}")
            return None

    async def test_url_accessibility(self, url):
        """Teste si l'URL est accessible (simulation)"""
        # Pour l'instant, on retourne True, mais on pourrait ajouter
        # une vérification HTTP plus tard si nécessaire
        return True

    async def process_url(self, original_url, site_type, message):
        """Traite une URL spécifique"""
        config = self.site_configs[site_type]
        
        # Tester chaque pattern jusqu'à trouver une correspondance
        for pattern in config["patterns"]:
            parts = self.extract_url_parts(original_url, pattern)
            if parts:
                self.logger.info(f"Pattern trouvé pour {site_type}: {parts}")
                
                # Tester chaque alternative jusqu'à en trouver une qui marche
                for alternative_template in config["alternatives"]:
                    try:
                        fixed_url = self.build_fixed_url(parts, alternative_template)
                        if fixed_url:
                            # Vérifier le cooldown
                            if self.is_on_cooldown(original_url, message.author.id):
                                await message.channel.send(
                                    f"{message.author.mention}, ce lien a déjà été fixé récemment ! 🔄"
                                )
                                return True
                            
                            # Ajouter au cooldown
                            self.add_to_cooldown(original_url, message.author.id)
                            
                            # Envoyer l'embed fix
                            embed = discord.Embed(
                                title=f"{config['emoji']} {config['name']} Fix",
                                description=f"Lien original transformé pour un meilleur affichage",
                                color=discord.Color.blue(),
                                url=fixed_url
                            )
                            embed.add_field(
                                name="Lien fixé", 
                                value=f"[Cliquez ici]({fixed_url})", 
                                inline=False
                            )
                            embed.add_field(
                                name="Posté par", 
                                value=message.author.mention, 
                                inline=True
                            )
                            embed.set_footer(
                                text=f"Fix automatique • {datetime.now().strftime('%H:%M')}"
                            )
                            
                            await message.channel.send(embed=embed)
                            
                            # Aussi envoyer le lien direct pour certains cas
                            if site_type in ["twitter", "instagram_post", "instagram_reel"]:
                                await message.channel.send(
                                    f"{message.author.mention} - {config['emoji']} - {fixed_url}"
                                )
                            
                            self.logger.info(f"URL {site_type} fixée avec succès: {fixed_url}")
                            return True
                            
                    except Exception as e:
                        self.logger.error(f"Erreur avec l'alternative {alternative_template}: {e}")
                        continue
                
                break  # Sortir de la boucle des patterns si on a trouvé une correspondance
        
        return False

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Ignorer les messages qui commencent par le préfixe du bot
        if message.content.startswith(self.bot.command_prefix):
            return

        self.logger.info(f"Message reçu de {message.author}: {message.content}")

        # Trouver toutes les URLs dans le message
        url_pattern = r"https?://[^\s]+"
        urls = re.findall(url_pattern, message.content)
        
        if not urls:
            return

        urls_fixed = []
        should_delete_message = False

        # Traiter chaque URL trouvée
        for url in urls:
            self.logger.info(f"Traitement de l'URL: {url}")
            
            # Tester chaque type de site
            for site_type in self.site_configs:
                if await self.process_url(url, site_type, message):
                    urls_fixed.append(url)
                    should_delete_message = True
                    break

        # Supprimer le message original si au moins une URL a été fixée
        if should_delete_message:
            try:
                await asyncio.sleep(1)  # Petit délai pour que l'embed apparaisse avant
                await message.delete()
                self.logger.info("Message original supprimé avec succès")
            except discord.errors.Forbidden:
                self.logger.warning(f"Permissions insuffisantes pour supprimer le message dans #{message.channel.name}")
                # Envoyer un message d'information
                await message.channel.send(
                    f"⚠️ Je n'ai pas les permissions pour supprimer le message original. "
                    f"Veuillez me donner la permission 'Gérer les messages'.",
                    delete_after=10
                )
            except discord.errors.NotFound:
                self.logger.info("Message déjà supprimé")
            except Exception as e:
                self.logger.error(f"Erreur lors de la suppression du message: {e}")

        if urls_fixed:
            self.logger.info(f"URLs fixées: {len(urls_fixed)}/{len(urls)}")

    @commands.command(name="testfix")
    @commands.has_permissions(manage_messages=True)
    async def test_fix(self, ctx, *, url: str):
        """Teste le système de fix sur une URL spécifique"""
        # Créer un message temporaire pour tester
        class MockMessage:
            def __init__(self):
                self.author = ctx.author
                self.channel = ctx.channel
                self.content = url

        mock_message = MockMessage()
        
        # Tester le fix
        fixed = False
        for site_type in self.site_configs:
            if await self.process_url(url, site_type, mock_message):
                fixed = True
                break
        
        if not fixed:
            await ctx.send(f"❌ Aucun fix disponible pour cette URL: `{url}`")

    @commands.command(name="fixstats")
    async def fix_stats(self, ctx):
        """Affiche les statistiques du système de fix"""
        embed = discord.Embed(
            title="📊 Statistiques Embed Fix",
            description="Informations sur le système de correction d'embeds",
            color=discord.Color.green()
        )
        
        # Compter les sites supportés
        total_sites = len(self.site_configs)
        total_patterns = sum(len(config["patterns"]) for config in self.site_configs.values())
        total_alternatives = sum(len(config["alternatives"]) for config in self.site_configs.values())
        
        embed.add_field(name="Sites supportés", value=str(total_sites), inline=True)
        embed.add_field(name="Patterns totaux", value=str(total_patterns), inline=True)
        embed.add_field(name="Alternatives", value=str(total_alternatives), inline=True)
        
        # Lister les sites supportés
        sites_list = []
        for site_type, config in self.site_configs.items():
            sites_list.append(f"{config['emoji']} {config['name']}")
        
        embed.add_field(
            name="Sites pris en charge",
            value="\n".join(sites_list),
            inline=False
        )
        
        # Cooldowns actifs
        self.clean_cooldowns()
        active_cooldowns = len(self.liens_envoyes)
        embed.add_field(name="Cooldowns actifs", value=str(active_cooldowns), inline=True)
        
        embed.set_footer(text=f"Cooldown: {self.cooldown_duration // 60} minutes")
        
        await ctx.send(embed=embed)

    @commands.command(name="clearcooldowns")
    @commands.has_permissions(manage_messages=True)
    async def clear_cooldowns(self, ctx):
        """Nettoie tous les cooldowns (admin seulement)"""
        count = len(self.liens_envoyes)
        self.liens_envoyes.clear()
        await ctx.send(f"✅ {count} cooldowns supprimés.")

async def setup(bot):
    await bot.add_cog(EmbedFix(bot))
    logging.getLogger('EmbedFix').info("Cog EmbedFix amélioré chargé avec succès")