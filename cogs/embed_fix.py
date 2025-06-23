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
                "emoji": ":bird:"
            },
            "instagram_post": {
                "patterns": [
                    r"https?://(?:www\.)?instagram\.com/p/([\w-]+)/?(?:\S*)?",
                ],
                "alternatives": [
                    "https://ddinstagram.com/p/{}",
                    "https://imginn.org/p/{}",
                ],
                "emoji": ":camera_with_flash:"
            },
            "instagram_reel": {
                "patterns": [
                    r"https?://(?:www\.)?instagram\.com/reel/([\w-]+)/?(?:\S*)?",
                ],
                "alternatives": [
                    "https://ddinstagram.com/reel/{}",
                    "https://imginn.org/reel/{}",
                ],
                "emoji": ":clapper:"
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
                "emoji": ":musical_note:"
            },
            "youtube_shorts": {
                "patterns": [
                    r"https?://(?:www\.)?youtube\.com/shorts/([\w-]+)(?:\S*)?",
                    r"https?://youtu\.be/([\w-]+)\?.*?(?:&|\?).*?shorts",
                ],
                "alternatives": [
                    "https://youtube.com/watch?v={}",
                ],
                "emoji": ":movie_camera:"
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
                "emoji": ":red_circle:"
            },
            "pixiv": {
                "patterns": [
                    r"https?://(?:www\.)?pixiv\.net/(?:en/)?artworks/(\d+)(?:\S*)?",
                ],
                "alternatives": [
                    "https://phixiv.net/artworks/{}",
                ],
                "emoji": ":art:"
            },
            "twitch_clip": {
                "patterns": [
                    r"https?://(?:www\.)?twitch\.tv/\w+/clip/([\w-]+)(?:\S*)?",
                    r"https?://clips\.twitch\.tv/([\w-]+)(?:\S*)?",
                ],
                "alternatives": [
                    "https://clips.twitch.tv/embed?clip={}&parent=discord.com",
                ],
                "emoji": ":purple_heart:"
            },
        }

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        for platform, config in self.site_configs.items():
            for pattern in config["patterns"]:
                matches = re.findall(pattern, message.content)
                if matches:
                    # Vérifier si le lien a déjà été envoyé
                    lien = message.content
                    if lien in self.liens_envoyes:
                        try:
                            await message.delete()
                            await message.channel.send("https://www.reddit.com/media?url=https%3A%2F%2Fpreview.redd.it%2Fnothing-ever-happens-v0-8r2pb3wiop6e1.jpeg%3Fwidth%3D1476%26format%3Dpjpg%26auto%3Dwebp%26s%3D46fca25dabbb4217b345de6390a681b8105bf21d")
                        except Exception as e:
                            self.logger.error(f"Erreur lors de la suppression du message : {e}")
                        return

                    # Stocker l'info sur l'utilisateur et la plateforme
                    self.liens_envoyes[lien] = {
                        "user": message.author.mention,
                        "platform": config["emoji"],
                        "timestamp": datetime.now()
                    }

                    # Traitement ultérieur (fixing embed, etc.)
                    alternative_link = self.get_alternative_link(matches[0], config["alternatives"])
                    embed = discord.Embed(description=f"({config['emoji']} - {message.author.mention}) [{platform}] {alternative_link}")
                    await message.channel.send(embed=embed)

                    # Nettoyage régulier des anciens liens
                    self.cleanup_liens_envoyes()

    def get_alternative_link(self, match, alternatives):
        # Cette fonction doit être implémentée pour gérer les différents groupes de capture
        # Pour simplifier, on suppose que le premier groupe est utilisé
        return alternatives[0].format(*match)

    def cleanup_liens_envoyes(self):
        now = datetime.now()
        self.liens_envoyes = {lien: info for lien, info in self.liens_envoyes.items() if (now - info["timestamp"]).total_seconds() < self.cooldown_duration}

async def setup(bot):
    await bot.add_cog(EmbedFix(bot))
    logging.getLogger('EmbedFix').info("Cog EmbedFix simplifié chargé avec succès")
