from discord.ext import commands
import discord
from youtubesearchpython import VideosSearch

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        """Vérifie si la commande est utilisée dans le canal 'DJ'."""
        return ctx.channel.name.lower() == 'dj'

    @commands.command(name="play")
    async def play(self, ctx, *, query):
        if not ctx.message.author.voice:
            await ctx.send("Vous n'êtes pas connecté à un canal vocal.")
            return
        
        try:
            channel = ctx.message.author.voice.channel
            voice_client = await channel.connect()
        except Exception as e:
            await ctx.send(f"Erreur lors de la connexion au canal vocal: {str(e)}")
            return

        try:
            # Recherche de la vidéo
            videos_search = VideosSearch(query, limit = 1)
            results = await self.bot.loop.run_in_executor(None, videos_search.result)
            
            if not results['result']:
                await ctx.send("Aucune vidéo trouvée.")
                return

            video = results['result'][0]
            title = video['title']
            url = video['link']

            # Lecture de l'audio
            voice_client.play(discord.FFmpegPCMAudio(url))
            await ctx.send(f"En train de jouer : {title}")
        except Exception as e:
            await ctx.send(f"Erreur lors de la lecture de l'audio: {str(e)}")
            await voice_client.disconnect()
            return

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("Cette commande ne peut être utilisée que dans le canal 'DJ'.")

async def setup(bot):
    await bot.add_cog(MusicCog(bot))