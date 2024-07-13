from discord.ext import commands

class VAtoi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if message.content == "v":
            response = (
                "ＩＭＭＥＮＳＥ　Ｖ　Ａ　ＴＯＩ　　ＭＯＮ　ＡＭＩ！\n"
                "ᵃᵖᵖʳᵉⁿᵈˢ ᵃ ᶜᵒᵖᶦᵉʳ⁻ᶜᵒˡˡᵉʳ ᵖᵒᵛᶜᵒⁿ !\n"
                "https://cdn.discordapp.com/attachments/620701105671634963/835219902167253042/DK5C0hRWkAA5xkW.jpg"
            )
            await message.channel.send(response)

async def setup(bot):
    await bot.add_cog(VAtoi(bot))
