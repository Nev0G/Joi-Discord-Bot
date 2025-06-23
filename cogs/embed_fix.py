import logging
from discord.ext import commands
import re
import discord
from datetime import datetime, timedelta

class EmbedFix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.liens_envoyes = {}  # Stockage des liens déjà envoyés
        self.cooldown_duration = 300  # 5 minutes
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('EmbedFix')

        self.site_configs = {
            "twitter": {
                "patterns": [
                    r"https?://(?:www\.)?(?:twitter\.com|x\.com)/(\w+)/status/(\d+)",
                    r"https?://(?:mobile\.)?(?:twitter\.com|x\.com)/(\w+)/status/(\d+)",
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
                    r"https?://(?:www\.)?instagram\.com/p/([\w-]+)/?",
                ],
                "alternatives": [
                    "https://ddinstagram.com/p/{}",
                    "https://imginn.org/p/{}",
                ],
                "emoji": ":camera_with_flash:"
            },
            "instagram_reel": {
                "patterns": [
                    r"https?://(?:www\.)?instagram\.com/reel/([\w-]+)/?",
                ],
                "alternatives": [
                    "https://ddinstagram.com/reel/{}",
                    "https://imginn.org/reel/{}",
                ],
                "emoji": ":clapper:"
            },
            "tiktok": {
                "patterns": [
                    r"https?://(?:www|vm|m)\.tiktok\.com/(@[\w.-]+/video/\d+|\w+)",
                    r"https?://(?:www\.)?tiktok\.com/t/(\w+)",
                ],
                "alternatives": [
                    "https://tnktok.com/{}",
                    "https://tikwm.com/{}",
                ],
                "emoji": ":musical_note:"
            },
            "youtube_shorts": {
                "patterns": [
                    r"https?://(?:www\.)?youtube\.com/shorts/([\w-]+)",
                    r"https?://youtu\.be/([\w-]+)\?.*shorts",
                ],
                "alternatives": [
                    "https://youtube.com/watch?v={}",
                ],
                "emoji": ":movie_camera:"
            },
            "reddit": {
                "patterns": [
                    r"https?://(?:www\.)?reddit\.com/r/([\w-]+)/comments/([\w-]+)",
                    r"https?://(?:old\.)?reddit\.com/r/([\w-]+)/comments/([\w-]+)",
                ],
                "alternatives": [
                    "https://rxddit.com/r/{}/comments/{}",
                    "https://vxreddit.com/r/{}/comments/{}",
                ],
                "emoji": ":red_circle:"
            },
            "pixiv": {
                "patterns": [
                    r"https?://(?:www\.)?pixiv\.net/(?:en/)?artworks/(\d+)",
                ],
                "alternatives": [
                    "https://phixiv.net/artworks/{}",
                ],
                "emoji": ":art:"
            },
            "twitch_clip": {
                "patterns": [
                    r"https?://(?:www\.)?twitch\.tv/\w+/clip/([\w-]+)",
                    r"https?://clips\.twitch\.tv/([\w-]+)",
                ],
                "alternatives": [
                    "https://clips.twitch.tv/embed?clip={}&parent=discord.com",
                ],
                "emoji": ":purple_heart:"
            },
        }

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or message.author.bot:
            return

        for platform, config in self.site_configs.items():
            for pattern in config["patterns"]:
                matches = re.findall(pattern, message.content)

                if matches:
                    for match in matches:
                        # Normalisation du lien extrait pour comparaison
                        lien_normalise = self.normaliser_lien(platform, match)

                        if lien_normalise in self.liens_envoyes:
                            try:
                                await message.delete()
                                await message.channel.send(
                                    "https://www.reddit.com/media?url=https%3A%2F%2Fpreview.redd.it%2Fnothing-ever-happens-v0-8r2pb3wiop6e1.jpeg%3Fwidth%3D1476%26format%3Dpjpg%26auto%3Dwebp%26s%3D46fca25dabbb4217b345de6390a681b8105bf21d"
                                )
                            except Exception as e:
                                self.logger.error(f"Erreur lors de la suppression du message : {e}")
                            return

                        # Stockage du lien
                        self.liens_envoyes[lien_normalise] = {
                            "user": message.author.mention,
                            "platform": config["emoji"],
                            "timestamp": datetime.now()
                        }

                        # Envoi du lien alternatif
                        alternative_link = self.get_alternative_link(match, config["alternatives"])
                        embed = discord.Embed(
                            description=f"{config['emoji']} - {message.author.mention} | {platform} → {alternative_link}"
                        )
                        await message.channel.send(embed=embed)

        self.cleanup_liens_envoyes()

    def normaliser_lien(self, platform, match):
        """
        Génère une version normalisée du lien pour vérification.
        """
        if isinstance(match, tuple):
            return f"{platform}_" + "_".join(match)
        return f"{platform}_{match}"

    def get_alternative_link(self, match, alternatives):
        """
        Génère un lien alternatif basé sur le premier modèle disponible.
        """
        if isinstance(match, tuple):
            return alternatives[0].format(*match)
        return alternatives[0].format(match)

    def cleanup_liens_envoyes(self):
        """
        Nettoie les anciens liens du dictionnaire pour éviter l'accumulation.
        """
        now = datetime.now()
        self.liens_envoyes = {
            lien: info for lien, info in self.liens_envoyes.items()
            if (now - info["timestamp"]).total_seconds() < self.cooldown_duration
        }

async def setup(bot):
    await bot.add_cog(EmbedFix(bot))
    logging.getLogger('EmbedFix').info("Cog EmbedFix chargé avec succès")
