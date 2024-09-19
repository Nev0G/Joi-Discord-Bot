from discord.ext import commands
import discord
import yt_dlp

class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        """Vérifie si la commande est utilisée dans le canal 'DJ'."""
        return ctx.channel.name.lower() == 'dj'

    @commands.command(name="play")
    async def play(self, ctx, url):
        if not ctx.message.author.voice:
            await ctx.send("Vous n'êtes pas connecté à un canal vocal.")
            return
        
        try:
            channel = ctx.message.author.voice.channel
            voice_client = await channel.connect()
        except Exception as e:
            await ctx.send(f"Erreur lors de la connexion au canal vocal: {str(e)}")
            return

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if 'entries' in info:
                    # C'est une playlist, prenons le premier élément
                    url2 = info['entries'][0]['url']
                    title = info['entries'][0]['title']
                else:
                    # C'est une seule vidéo
                    url2 = info['url']
                    title = info['title']
                voice_client.play(discord.FFmpegPCMAudio(url2))
        except Exception as e:
            await ctx.send(f"Erreur lors de la lecture de l'audio: {str(e)}")
            await voice_client.disconnect()
            return

        await ctx.send(f"En train de jouer : {title}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("Cette commande ne peut être utilisée que dans le canal 'DJ'.")

async def setup(bot):
    await bot.add_cog(MusicCog(bot))