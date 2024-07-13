import discord
from discord.ext import commands
import asyncio

class Harcelement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.harcèlement_tasks = {}

    @commands.command()
    async def harcelement(self, ctx, member: discord.Member, interval: int, *, message="spam de harcèlement !"):
        if interval < 1:
            await ctx.send("L'intervalle doit être supérieur à 0 seconde.")
            return

        if member.id in self.harcèlement_tasks:
            await ctx.send(f"{member.mention} est déjà en train de se faire harceler. Utilisez `j!stop_harcelement` pour arrêter le spam.")
            return

        async def harceler():
            while True:
                try:
                    await ctx.send(f"{member.mention} {message}")
                    await member.send(f"{member.mention}, {message} dans {ctx.guild.name} par {ctx.author.name} !")
                except discord.Forbidden:
                    await ctx.send(f"{member.mention} a désactivé les DMs.")
                except Exception as e:
                    await ctx.send(f"Une erreur est survenue : {e}")
                await asyncio.sleep(interval)

        task = self.bot.loop.create_task(harceler())
        self.harcèlement_tasks[member.id] = task
        await ctx.send(f"Début du harcèlement de {member.mention} toutes les {interval} secondes.")

    @commands.command()
    async def stop_harcelement(self, ctx, member: discord.Member):
        if member.id not in self.harcèlement_tasks:
            await ctx.send(f"{member.mention} n'est pas actuellement harcelé.")
            return

        task = self.harcèlement_tasks.pop(member.id)
        task.cancel()
        await ctx.send(f"Arrêt du harcèlement de {member.mention}.")

async def setup(bot):
    await bot.add_cog(Harcelement(bot))
