import discord
from discord.ext import commands
import json
import re

class BanlistCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.banlist = set()
        self.load_banlist()
        self.warning_messages = [
            "(‿ˠ‿) Mate moi ce cul plutot au lieu de dire de la merde salope",
            "Attention ! Alerte a la bite ! 😈εつ▄█▀█🥵",
            "╭∩╮( •̀_•́ )╭∩╮ Ta gueule",
            "💩🧻",
            "▄︻デ══━一💥 👩 <=== Ta mere cette salope"
        ]

    def load_banlist(self):
        try:
            with open('banlist.json', 'r') as f:
                self.banlist = set(json.load(f))
        except FileNotFoundError:
            print("Fichier banlist.json non trouvé. Création d'une nouvelle banlist.")
        except json.JSONDecodeError:
            print("Erreur lors du chargement de la banlist. Création d'une nouvelle banlist.")

    def save_banlist(self):
        with open('banlist.json', 'w') as f:
            json.dump(list(self.banlist), f)

    def contains_banned_word(self, message):
        words = message.lower().split()
        for word in words:
            clean_word = re.sub(r'[^a-z]', '', word)
            if clean_word in self.banlist or any(banned_word in clean_word for banned_word in self.banlist):
                return True
        return False

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if self.contains_banned_word(message.content):
            try:
                await message.delete()
                warning = random.choice(self.warning_messages)
                await message.channel.send(f"{message.author.mention}, {warning}", delete_after=5)
            except discord.errors.Forbidden:
                print(f"Impossible de supprimer le message dans {message.guild.name}")

    @commands.command(name="addban")
    @commands.has_permissions(manage_messages=True)
    async def add_ban(self, ctx, word: str):
        word = word.lower()
        self.banlist.add(word)
        self.save_banlist()
        await ctx.send(f"Le mot '{word}' a été ajouté à la banlist.")

    @commands.command(name="removeban")
    @commands.has_permissions(manage_messages=True)
    async def remove_ban(self, ctx, word: str):
        word = word.lower()
        if word in self.banlist:
            self.banlist.remove(word)
            self.save_banlist()
            await ctx.send(f"Le mot '{word}' a été retiré de la banlist.")
        else:
            await ctx.send(f"Le mot '{word}' n'est pas dans la banlist.")

    @commands.command(name="listban")
    @commands.has_permissions(manage_messages=True)
    async def list_ban(self, ctx):
        if self.banlist:
            await ctx.send(f"Mots bannis : {', '.join(self.banlist)}")
        else:
            await ctx.send("La banlist est vide.")

async def setup(bot):
    await bot.add_cog(BanlistCog(bot))