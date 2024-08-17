from discord.ext import commands
import discord

class Chined(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="maozedong")
    async def sayas(self, ctx, member: discord.Member, *, message):
        # On efface le message original pour garder l'effet d'imitation
        await ctx.message.delete()
        
        # On envoie le message avec le nom et l'avatar de la personne spécifiée
        webhook = await ctx.channel.create_webhook(name=member.display_name, avatar=await member.avatar.read())
        await webhook.send(message)
        await webhook.delete()

async def setup(bot):
    await bot.add_cog(Chined(bot))
