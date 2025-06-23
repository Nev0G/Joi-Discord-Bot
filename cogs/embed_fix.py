import logging
from discord.ext import commands
import re
import discord
from datetime import datetime, timedelta

class EmbedFix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.liens_envoyes = {}  # Stockage des liens déjà envoyés
        self.cooldown_duration = 1500  # 5 minutes
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('EmbedFix')

        self.site_configs = {
            "twitter": {
                "patterns": [
                    r"https?://(?:www\.)?(?:twitter\.com|x\.com)/(\w+)/status/(\d+)",
                    r"https?://(?:mobile\.)?(?:twitter\.com|x\.com)/(\w+)/status/(\d+)",
                ],
                "alternative_template": "https://fxtwitter.com/{}/status/{}",
                "emoji": "🐦"
            },
            "instagram_post": {
                "patterns": [
                    r"https?://(?:www\.)?instagram\.com/p/([\w-]+)/?",
                ],
                "alternative_template": "https://ddinstagram.com/p/{}",
                "emoji": "📸"
            },
            "instagram_reel": {
                "patterns": [
                    r"https?://(?:www\.)?instagram\.com/reel/([\w-]+)/?",
                ],
                "alternative_template": "https://ddinstagram.com/reel/{}",
                "emoji": "🎬"
            },
            "tiktok": {
                "patterns": [
                    r"https?://(?:www|vm|m)\.tiktok\.com/@[\w.-]+/video/(\d+)",
                    r"https?://(?:www\.)?tiktok\.com/t/(\w+)",
                    r"https?://vm\.tiktok\.com/(\w+)",
                ],
                "alternative_template": "https://tnktok.com/t/{}",
                "emoji": "🎵"
            },
            "youtube_shorts": {
                "patterns": [
                    r"https?://(?:www\.)?youtube\.com/shorts/([\w-]+)",
                ],
                "alternative_template": "https://youtube.com/watch?v={}",
                "emoji": "🎥"
            },
            "reddit": {
                "patterns": [
                    r"https?://(?:www\.|old\.)?reddit\.com/r/([\w-]+)/comments/([\w-]+)",
                ],
                "alternative_template": "https://rxddit.com/r/{}/comments/{}",
                "emoji": "🔴"
            }
        }

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignorer les bots et le bot lui-même
        if message.author == self.bot.user or message.author.bot:
            return

        # Nettoyer les anciens liens
        self.cleanup_liens_envoyes()

        original_content = message.content
        liens_found = []

        # Chercher tous les liens dans le message
        for platform, config in self.site_configs.items():
            for pattern in config["patterns"]:
                matches = re.finditer(pattern, original_content)
                
                for match in matches:
                    # Créer l'identifiant unique du lien
                    if len(match.groups()) == 2:  # Twitter, Reddit (2 groupes)
                        lien_id = f"{platform}_{match.group(1)}_{match.group(2)}"
                        alternative_link = config["alternative_template"].format(match.group(1), match.group(2))
                    else:  # Autres plateformes (1 groupe)
                        lien_id = f"{platform}_{match.group(1)}"
                        alternative_link = config["alternative_template"].format(match.group(1))
                    
                    liens_found.append({
                        'id': lien_id,
                        'platform': platform,
                        'emoji': config['emoji'],
                        'alternative': alternative_link,
                        'original': match.group(0)
                    })

        # Traiter les liens trouvés
        if liens_found:
            for link_info in liens_found:
                # Vérifier si le lien a déjà été envoyé
                if link_info['id'] in self.liens_envoyes:
                    # Lien déjà envoyé -> envoyer "boucled"
                    try:
                        await message.delete()
                        embed = discord.Embed(
                            title="🔄 Lien déjà partagé",
                            description="**BOUCLED** - Ce lien a déjà été envoyé récemment",
                            color=0xFF6B6B
                        )
                        embed.add_field(
                            name="Envoyé par",
                            value=self.liens_envoyes[link_info['id']]['user'],
                            inline=True
                        )
                        embed.add_field(
                            name="Quand",
                            value=f"<t:{int(self.liens_envoyes[link_info['id']]['timestamp'].timestamp())}:R>",
                            inline=True
                        )
                        await message.channel.send(embed=embed, delete_after=10)
                    except discord.errors.NotFound:
                        pass
                    except Exception as e:
                        self.logger.error(f"Erreur lors de la suppression/envoi : {e}")
                    return

            # Si aucun lien n'est en doublon, traiter normalement
            try:
                # Supprimer le message original
                await message.delete()
                
                # Créer l'embed avec les liens alternatifs
                embed = discord.Embed(
                    title="🔗 Lien(s) optimisé(s)",
                    color=0x00D166
                )
                
                # Ajouter le contenu du message s'il y en a un (sans les liens)
                message_text = original_content
                for link_info in liens_found:
                    message_text = message_text.replace(link_info['original'], '')
                
                message_text = message_text.strip()
                if message_text:
                    embed.add_field(
                        name="💬 Message",
                        value=message_text[:1000],  # Limite Discord
                        inline=False
                    )
                
                # Ajouter les liens alternatifs
                links_text = ""
                for i, link_info in enumerate(liens_found):
                    links_text += f"{link_info['emoji']} **{link_info['platform'].title()}**: {link_info['alternative']}\n"
                    
                    # Enregistrer le lien comme envoyé
                    self.liens_envoyes[link_info['id']] = {
                        'user': message.author.mention,
                        'timestamp': datetime.now()
                    }
                
                embed.add_field(
                    name="🔗 Liens",
                    value=links_text,
                    inline=False
                )
                
                embed.set_footer(
                    text=f"Envoyé par {message.author.display_name}",
                    icon_url=message.author.avatar.url if message.author.avatar else None
                )
                embed.timestamp = datetime.now()
                
                await message.channel.send(embed=embed)
                
            except discord.errors.NotFound:
                # Le message a déjà été supprimé
                pass
            except Exception as e:
                self.logger.error(f"Erreur lors du traitement du message : {e}")

    def cleanup_liens_envoyes(self):
        """Nettoie les liens expirés du cache"""
        now = datetime.now()
        expired_keys = []
        
        for lien_id, data in self.liens_envoyes.items():
            if now - data['timestamp'] > timedelta(seconds=self.cooldown_duration):
                expired_keys.append(lien_id)
        
        for key in expired_keys:
            del self.liens_envoyes[key]

# Fonction pour ajouter le cog au bot
async def setup(bot):
    await bot.add_cog(EmbedFix(bot))
