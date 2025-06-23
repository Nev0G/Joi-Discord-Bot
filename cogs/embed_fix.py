import discord
from discord.ext import commands, tasks
import re
import json
import os
from datetime import datetime, timedelta

class LinkTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
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
                    r"https?://(?:www|vm|m)\.tiktok\.com/t/([^/]+)/?",
                    r"https?://(?:www|vm|m)\.tiktok\.com/@[\w.-]+/video/(\d+)",
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
        self.links_file = "links.json"
        self.embed_messages_file = "embed_messages.json"
        self.load_data()
        self.clean_links.start()

    def load_data(self):
        if os.path.exists(self.links_file):
            with open(self.links_file, 'r') as f:
                self.links = json.load(f)
        else:
            self.links = {}
            self.save_links()

        if os.path.exists(self.embed_messages_file):
            with open(self.embed_messages_file, 'r') as f:
                self.embed_messages = json.load(f)
        else:
            self.embed_messages = {}
            self.save_embed_messages()

    def save_links(self):
        with open(self.links_file, 'w') as f:
            json.dump(self.links, f, indent=4)

    def save_embed_messages(self):
        with open(self.embed_messages_file, 'w') as f:
            json.dump(self.embed_messages, f, indent=4)

    @tasks.loop(hours=24)
    async def clean_links(self):
        try:
            now = datetime.utcnow()
            channels_to_update = set()
            for channel_id in list(self.links.keys()):
                for platform in list(self.links[channel_id].keys()):
                    for link_id in list(self.links[channel_id][platform].keys()):
                        link_time = datetime.fromisoformat(self.links[channel_id][platform][link_id]["timestamp"])
                        if now - link_time > timedelta(hours=24):
                            del self.links[channel_id][platform][link_id]
                    if not self.links[channel_id][platform]:
                        del self.links[channel_id][platform]
                if not self.links[channel_id]:
                    del self.links[channel_id]
                else:
                    channels_to_update.add(channel_id)
            self.save_links()

            for channel_id in channels_to_update:
                await self.update_embed(channel_id)
            print(f"Links cleaned at {now}")
        except Exception as e:
            print(f"Error cleaning links: {e}")

    @clean_links.before_loop
    async def before_clean_links(self):
        await self.bot.wait_until_ready()

    async def update_embed(self, channel_id):
        channel = self.bot.get_channel(int(channel_id))
        if not channel:
            print(f"Canal {channel_id} non trouvé ou inaccessible, suppression des données.")
            if channel_id in self.links:
                del self.links[channel_id]
                self.save_links()
            if channel_id in self.embed_messages:
                del self.embed_messages[channel_id]
                self.save_embed_messages()
            return

        embed = discord.Embed(
            title="Liens Partagés",
            description="Liste des liens soumis dans ce canal.",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )

        if channel_id in self.links:
            for platform, links in self.links[channel_id].items():
                platform_name = platform.replace("_", " ").title()
                emoji = self.site_configs[platform]["emoji"]
                entries = [f"{emoji} [{platform_name}]({data['alternative_url']}) - Ajouté par : <@{data['author_id']}>" 
                          for link_id, data in links.items()]
                if entries:
                    embed.add_field(name=platform_name, value="\n".join(entries), inline=False)

        if not embed.fields:
            embed.description = "Aucun lien soumis pour le moment."

        try:
            if channel_id in self.embed_messages and self.embed_messages[channel_id]:
                message = await channel.fetch_message(int(self.embed_messages[channel_id]))
                await message.edit(embed=embed)
            else:
                message = await channel.send(embed=embed)
                self.embed_messages[channel_id] = str(message.id)
                self.save_embed_messages()
        except discord.NotFound:
            message = await channel.send(embed=embed)
            self.embed_messages[channel_id] = str(message.id)
            self.save_embed_messages()
        except discord.Forbidden:
            print(f"Permissions insuffisantes dans le canal {channel_id}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.channel.permissions_for(message.guild.me).send_messages:
            return

        channel_id = str(message.channel.id)
        content = message.content
        for platform, config in self.site_configs.items():
            for pattern in config["patterns"]:
                matches = re.search(pattern, content)
                if matches:
                    groups = matches.groups()
                    if platform in ["twitter", "reddit"]:
                        link_id = f"{groups[0]}.{groups[1]}"
                        alternative_url = config["alternative_template"].format(*groups)
                    else:
                        link_id = groups[0]
                        alternative_url = config["alternative_template"].format(groups[0])

                    if (channel_id in self.links and 
                        platform in self.links[channel_id] and 
                        link_id in self.links[channel_id][platform]):
                        await message.reply(f"Ce lien {platform.replace('_', ' ').title()} a déjà été soumis dans ce canal !")
                        return

                    if channel_id not in self.links:
                        self.links[channel_id] = {}
                    if platform not in self.links[channel_id]:
                        self.links[channel_id][platform] = {}
                    self.links[channel_id][platform][link_id] = {
                        "original_url": content,
                        "alternative_url": alternative_url,
                        "author_id": str(message.author.id),
                        "author_name": message.author.display_name,
                        "timestamp": datetime.utcnow().isoformat()
                    }

                    self.save_links()
                    await self.update_embed(channel_id)
                    await message.add_reaction("✅")
                    return

    async def cog_load(self):
        for channel_id in list(self.links.keys()):
            await self.update_embed(channel_id)

async def setup(bot):
    await bot.add_cog(LinkTracker(bot))
