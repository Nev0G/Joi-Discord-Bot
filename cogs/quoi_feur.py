from discord.ext import commands
import random

class QuoiFeur(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if message.content.lower().endswith("quoi"):
            random_response = random.choice(
                ["feur", "coubeh", "chi", "driceps", "fure", "ffant", "drilatere", "d", "dri"]
            )
            await message.channel.send(random_response)

async def setup(bot):
    await bot.add_cog(QuoiFeur(bot))
