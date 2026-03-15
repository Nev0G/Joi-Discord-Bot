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
                    # URLs longues : tiktok.com/@user/video/ID  →  on capture l'ID
                    r"https?://(?:www\.)?tiktok\.com/@[\w.\-]+/video/(\d+)",
                    r"https?://m\.tiktok\.com/@[\w.\-]+/video/(\d+)",
                    # URLs courtes : vm.tiktok.com/ID  ou  tiktok.com/t/ID
                    r"https?://(?:vm|vt)\.tiktok\.com/([\w]+)/?",
                    r"https?://(?:www\.)?tiktok\.com/t/([\w]+)/?",
                ],
                # On utilise toujours le format long /video/ qui fonctionne
                "alternative_template": "https://tnktok.com/@_/video/{}",
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

        # On cherche UN seul match par plateforme (le premier pattern qui matche)
        liens_trouves = []
        seen_platforms = set()

        for platform, config in self.platforms.items():
            for pattern in config["patterns"]:
                match = re.search(pattern, message.content)
                if match and platform not in seen_platforms:
                    groups = match.groups()
                    seen_platforms.add(platform)
                    liens_trouves.append({
                        "platform": platform,
                        "groups": groups,
                    })
                    break  # stop au premier pattern qui matche pour cette plateforme

        if not liens_trouves:
            return

        try:
            await message.delete()
            self.logger.info("Message original supprimé avec succès")
        except discord.errors.Forbidden:
            self.logger.warning(f"Impossible de supprimer le message dans {message.channel.name}")
        except Exception as e:
            self.logger.error(f"Erreur lors de la suppression du message : {str(e)}")

        for lien in liens_trouves:
            platform_data = self.platforms[lien["platform"]]

            # clé d'unicité pour éviter les doublons inter-messages
            cache_key = (lien["platform"], lien["groups"])
            if cache_key in self.liens_envoyes:
                await message.channel.send(f"{message.author.mention}, Tu t'es fait bouclé salope 🔃")
                continue

            fixed_url = platform_data["alternative_template"].format(*lien["groups"])
            self.liens_envoyes.add(cache_key)
            await message.channel.send(
                f"{message.author.mention} - {platform_data['emoji']} - {fixed_url}"
            )
            self.logger.info(f"Lien corrigé envoyé : {fixed_url}")


async def setup(bot):
    if bot.get_cog("EmbedFix"):
        logging.getLogger('EmbedFix').warning("Le Cog EmbedFix est déjà chargé, double chargement évité.")
        return

    await bot.add_cog(EmbedFix(bot))
    logging.getLogger('EmbedFix').info("Cog EmbedFix chargé avec succès")
