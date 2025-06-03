import logging
from discord.ext import commands
import re
import discord
import asyncio
from datetime import datetime, timedelta

class EmbedFix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.liens_envoyes = {}  # Dictionnaire avec timestamp pour éviter le spam
        self.cooldown_duration = 300  # 5 minutes de cooldown
        self.message_data = {}  # Stockage des données pour les réactions
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
                "emoji": "🐦"
            },
            "instagram_post": {
                "patterns": [
                    r"https?://(?:www\.)?instagram\.com/p/([\w-]+)/?(?:\S*)?",
                ],
                "alternatives": [
                    "https://ddinstagram.com/p/{}",
                    "https://imginn.org/p/{}",
                ],
                "emoji": "📸"
            },
            "instagram_reel": {
                "patterns": [
                    r"https?://(?:www\.)?instagram\.com/reel/([\w-]+)/?(?:\S*)?",
                ],
                "alternatives": [
                    "https://ddinstagram.com/reel/{}",
                    "https://imginn.org/reel/{}",
                ],
                "emoji": "🎬"
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
                "emoji": "🎵"
            },
            "youtube_shorts": {
                "patterns": [
                    r"https?://(?:www\.)?youtube\.com/shorts/([\w-]+)(?:\S*)?",
                    r"https?://youtu\.be/([\w-]+)\?.*?(?:&|\?).*?shorts",
                ],
                "alternatives": [
                    "https://youtube.com/watch?v={}",
                ],
                "emoji": "🎥"
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
                "emoji": "🔴"
            },
            "pixiv": {
                "patterns": [
                    r"https?://(?:www\.)?pixiv\.net/(?:en/)?artworks/(\d+)(?:\S*)?",
                ],
                "alternatives": [
                    "https://phixiv.net/artworks/{}",
                ],
                "emoji": "🎨"
            },
            "twitch_clip": {
                "patterns": [
                    r"https?://(?:www\.)?twitch\.tv/\w+/clip/([\w-]+)(?:\S*)?",
                    r"https?://clips\.twitch\.tv/([\w-]+)(?:\S*)?",
                ],
                "alternatives": [
                    "https://clips.twitch.tv/embed?clip={}&parent=discord.com",
                ],
                "emoji": "💜"
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
        
        # Nettoyer aussi les données de messages
        self.clean_message_data()

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

    async def process_url(self, original_url, site_type, message, alternative_index=0):
        """Traite une URL spécifique"""
        config = self.site_configs[site_type]
        
        # Tester chaque pattern jusqu'à trouver une correspondance
        for pattern in config["patterns"]:
            parts = self.extract_url_parts(original_url, pattern)
            if parts:
                self.logger.info(f"Pattern trouvé pour {site_type}: {parts}")
                
                # Utiliser l'alternative spécifiée par l'index
                if alternative_index < len(config["alternatives"]):
                    alternative_template = config["alternatives"][alternative_index]
                    try:
                        fixed_url = self.build_fixed_url(parts, alternative_template)
                        if fixed_url:
                            # Vérifier le cooldown seulement pour le premier essai
                            if alternative_index == 0 and self.is_on_cooldown(original_url, message.author.id):
                                return None
                            
                            # Ajouter au cooldown seulement pour le premier essai
                            if alternative_index == 0:
                                self.add_to_cooldown(original_url, message.author.id)
                            
                            # Envoyer SEULEMENT le lien fixé
                            sent_message = await message.channel.send(fixed_url)
                            
                            # Ajouter une réaction pour refresh si il y a d'autres alternatives
                            if len(config["alternatives"]) > 1:
                                await sent_message.add_reaction("🔄")
                                
                                # Stocker les données pour la réaction
                                self.message_data[sent_message.id] = {
                                    "original_url": original_url,
                                    "site_type": site_type,
                                    "parts": parts,
                                    "current_alternative": alternative_index,
                                    "author_id": message.author.id,
                                    "timestamp": datetime.now()
                                }
                            
                            self.logger.info(f"URL {site_type} fixée avec succès: {fixed_url} (alternative {alternative_index + 1})")
                            return sent_message
                            
                    except Exception as e:
                        self.logger.error(f"Erreur avec l'alternative {alternative_template}: {e}")
                        return None
                
                break  # Sortir de la boucle des patterns si on a trouvé une correspondance
        
        return None

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
                sent_message = await self.process_url(url, site_type, message)
                if sent_message:
                    urls_fixed.append(url)
                    should_delete_message = True
                    break

        # Supprimer le message original si au moins une URL a été fixée
        if should_delete_message:
            try:
                await asyncio.sleep(1)  # Petit délai pour que le lien apparaisse avant
                await message.delete()
                self.logger.info("Message original supprimé avec succès")
            except discord.errors.Forbidden:
                self.logger.warning(f"Permissions insuffisantes pour supprimer le message dans #{message.channel.name}")
            except discord.errors.NotFound:
                self.logger.info("Message déjà supprimé")
            except Exception as e:
                self.logger.error(f"Erreur lors de la suppression du message: {e}")

        if urls_fixed:
            self.logger.info(f"URLs fixées: {len(urls_fixed)}/{len(urls)}")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Gère les réactions pour refresh les liens"""
        if user.bot:
            return
        
        if str(reaction.emoji) != "🔄":
            return
        
        message_id = reaction.message.id
        if message_id not in self.message_data:
            return
        
        data = self.message_data[message_id]
        
        # Vérifier que c'est l'auteur original ou un admin qui réagit
        if user.id != data["author_id"]:
            # Vérifier les permissions d'admin
            try:
                member = reaction.message.guild.get_member(user.id)
                if not member.guild_permissions.manage_messages:
                    await reaction.remove(user)
                    return
            except:
                await reaction.remove(user)
                return
        
        # Vérifier que le message n'est pas trop ancien (30 minutes)
        if datetime.now() - data["timestamp"] > timedelta(minutes=30):
            await reaction.message.edit(content=f"~~{reaction.message.content}~~ *(Lien expiré)*")
            del self.message_data[message_id]
            return
        
        # Passer à l'alternative suivante
        config = self.site_configs[data["site_type"]]
        next_alternative = (data["current_alternative"] + 1) % len(config["alternatives"])
        
        try:
            # Construire le nouveau lien
            alternative_template = config["alternatives"][next_alternative]
            new_fixed_url = self.build_fixed_url(data["parts"], alternative_template)
            
            if new_fixed_url:
                # Éditer le message avec le nouveau lien
                await reaction.message.edit(content=new_fixed_url)
                
                # Mettre à jour les données
                data["current_alternative"] = next_alternative
                
                # Retirer la réaction de l'utilisateur
                await reaction.remove(user)
                
                self.logger.info(f"Lien refreshé vers l'alternative {next_alternative + 1}: {new_fixed_url}")
            else:
                await reaction.remove(user)
                
        except Exception as e:
            self.logger.error(f"Erreur lors du refresh: {e}")
            await reaction.remove(user)

    def clean_message_data(self):
        """Nettoie les anciennes données de messages"""
        current_time = datetime.now()
        expired_keys = []
        
        for message_id, data in self.message_data.items():
            if current_time - data["timestamp"] > timedelta(minutes=30):
                expired_keys.append(message_id)
        
        for key in expired_keys:
            del self.message_data[key]

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
        fixed_message = None
        for site_type in self.site_configs:
            fixed_message = await self.process_url(url, site_type, mock_message)
            if fixed_message:
                break
        
        if not fixed_message:
            await ctx.send(f"❌ Aucun fix disponible pour cette URL: `{url}`")

    @commands.command(name="clearcooldowns")
    @commands.has_permissions(manage_messages=True)
    async def clear_cooldowns(self, ctx):
        """Nettoie tous les cooldowns (admin seulement)"""
        cooldown_count = len(self.liens_envoyes)
        message_count = len(self.message_data)
        
        self.liens_envoyes.clear()
        self.message_data.clear()
        
        await ctx.send(f"✅ {cooldown_count} cooldowns et {message_count} données de messages supprimés.")

    @commands.command(name="fixinfo")
    async def fix_info(self, ctx):
        """Affiche les informations sur le système de refresh"""
        embed = discord.Embed(
            title="🔄 Système de Refresh des Liens",
            description="Comment utiliser le système de refresh automatique",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🔄 Refresh",
            value="Cliquez sur 🔄 pour essayer une autre alternative de fix si le lien ne fonctionne pas",
            inline=False
        )
        
        embed.add_field(
            name="⏰ Durée",
            value="Les liens peuvent être refreshés pendant 30 minutes après l'envoi",
            inline=True
        )
        
        embed.add_field(
            name="👤 Permissions",
            value="Seul l'auteur du lien original ou un modérateur peut refresh",
            inline=True
        )
        
        # Lister les sites avec plusieurs alternatives
        sites_with_alternatives = []
        for site_type, config in self.site_configs.items():
            if len(config["alternatives"]) > 1:
                sites_with_alternatives.append(f"{config['emoji']} {len(config['alternatives'])} alternatives")
        
        if sites_with_alternatives:
            embed.add_field(
                name="Sites avec alternatives multiples",
                value="\n".join(sites_with_alternatives),
                inline=False
            )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EmbedFix(bot))
    logging.getLogger('EmbedFix').info("Cog EmbedFix simplifié chargé avec succès")