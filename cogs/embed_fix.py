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

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        self.logger.info(f"Message reçu : {message.content}")

        # Définitions des motifs de recherche pour les URLs
        tweet_url_pattern = r"https://(?:twitter\.com|x\.com)/\w+/status/\d+"
        instagram_url_pattern = r"https://(?:www\.)?instagram\.com/p/[\w-]+/?\S*"
        tiktok_url_pattern = r"https://(?:(?:www|vm)\.)?tiktok\.com/\S+"

        # Trouver tous les liens correspondants dans le message
        tweet_urls = re.findall(tweet_url_pattern, message.content)
        instagram_urls = re.findall(instagram_url_pattern, message.content)
        tiktok_urls = re.findall(tiktok_url_pattern, message.content)

        self.logger.info(f"URLs trouvées : Tweet: {tweet_urls}, Instagram: {instagram_urls}, TikTok: {tiktok_urls}")

        if tweet_urls or instagram_urls or tiktok_urls:
            try:
                await message.delete()
                self.logger.info("Message original supprimé avec succès")
            except discord.errors.Forbidden:
                self.logger.error(f"Impossible de supprimer le message dans {message.channel.name}")
            except Exception as e:
                self.logger.error(f"Erreur lors de la suppression du message : {str(e)}")

        for url, pattern, prefix, fixed_domain in [
            (tweet_urls, r"https://(?:twitter\.com|x\.com)/", "🐦", "fxtwitter.com"),
            (instagram_urls, r"https://(?:www\.)?instagram\.com/", "📸", "ddinstagram.com"),
            (tiktok_urls, r"https://(?:(?:www|vm)\.)?tiktok\.com/", "🎵", "tnktok.com")
        ]:
            for original_url in url:
                    if original_url in self.liens_envoyes:
                        await message.channel.send(f"{message.author.mention}, Tu t'es fait bouclé salope 🔃")
                    else:
                        # Modification ici pour préserver les paramètres d'URL
                        fixed_url = re.sub(pattern, f"https://{fixed_domain}/", original_url)
                        self.liens_envoyes.add(original_url)
                        await message.channel.send(f"{message.author.mention} - {prefix} - {fixed_url}")

async def setup(bot):
    await bot.add_cog(EmbedFix(bot))
    logging.getLogger('EmbedFix').info("Cog EmbedFix chargé avec succès")