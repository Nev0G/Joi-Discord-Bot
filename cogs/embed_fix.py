import logging
from discord.ext import commands
import re
import discord

class EmbedFix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.liens_envoyes = set()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('EmbedFix')

        # Définition centralisée des plateformes
        self.platforms = {
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

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        self.logger.info(f"Message reçu : {message.content}")

        liens_trouves = []

        # Parcours des plateformes et détection des liens
        for platform, config in self.platforms.items():
            for pattern in config["patterns"]:
                matches = re.findall(pattern, message.content)
                if matches:
                    for groups in matches:
                        # Normalisation du tuple s'il n'y a qu'un seul groupe capturé
                        if not isinstance(groups, tuple):
                            groups = (groups,)
                        lien_original = pattern + str(groups)
                        liens_trouves.append({
                            "platform": platform,
                            "groups": groups,
                            "original": lien_original
                        })

        if liens_trouves:
            try:
                await message.delete()
                self.logger.info("Message original supprimé avec succès")
            except discord.errors.Forbidden:
                self.logger.warning(f"Impossible de supprimer le message dans {message.channel.name}")
            except Exception as e:
                self.logger.error(f"Erreur lors de la suppression du message : {str(e)}")

            for lien in liens_trouves:
                platform_data = self.platforms[lien["platform"]]
                lien_original = lien["original"]

                if lien_original in self.liens_envoyes:
                    await message.channel.send(f"{message.author.mention}, Tu t'es fait bouclé salope 🔃")
                    continue

                fixed_url = platform_data["alternative_template"].format(*lien["groups"])
                self.liens_envoyes.add(lien_original)

                await message.channel.send(f"{message.author.mention} - {platform_data['emoji']} - {fixed_url}")
                self.logger.info(f"{fixed_url}")

async def setup(bot):
    await bot.add_cog(EmbedFix(bot))
    logging.getLogger('EmbedFix').info("Cog EmbedFix chargé avec succès")
