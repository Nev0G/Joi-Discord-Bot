import discord
from discord.ext import commands
import random
import re

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

bot = commands.Bot(command_prefix="j!", intents=intents)

# Créer un ensemble pour stocker les liens déjà envoyés
liens_envoyes = set()

@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user.name}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await handle_quoi_feur(message)
    await handle_v_a_toi(message)
    await handle_tweet_fix(message)

    await bot.process_commands(message)

# Fonction pour gérer la commande "quoi"
async def handle_quoi_feur(message):
    if message.content.lower().endswith("quoi"):
        random_response = random.choice(["feur", "coubeh", "chi", "driceps", "fure", "ffant", "drilatere", "d", "dri"])
        await message.channel.send(random_response)

# Fonction pour gérer la commande "v"
async def handle_v_a_toi(message):
    if message.content.lower() == "v":
        response = "ＩＭＭＥＮＳＥ　Ｖ　Ａ　ＴＯＩ　　ＭＯＮ　ＡＭＩ！\n" + \
                   "ＩＭＭＥＮＳＥ　Ｖ　Ａ　ＴＯＩ　　ＭＯＮ　ＡＭＩ！\n" + \
                   "ＩＭＭＥＮＳＥ　Ｖ　Ａ　ＴＯＩ　　ＭＯＮ　ＡＭＩ！\n" + \
                   "ＩＭＭＥＮＳＥ　Ｖ　Ａ　ＴＯＩ　　ＭＯＮ　ＡＭＩ！\n" + \
                   "ＩＭＭＥＮＳＥ　Ｖ　Ａ　ＴＯＩ　　ＭＯＮ　ＡＭＩ！\n" + \
                   "ᵃᵖᵖʳᵉⁿᵈˢ ᵃ ᶜᵒᵖᶦᵉʳ⁻ᶜᵒˡˡᵉʳ ᵖᵒᵛᶜᵒⁿ !\n" + \
                   "https://cdn.discordapp.com/attachments/620701105671634963/835219902167253042/DK5C0hRWkAA5xkW.jpg"
        await message.channel.send(response)

# Fonction pour gérer le fix des liens Twitter
async def handle_tweet_fix(message):
    tweet_url_pattern = r"https://twitter\.com/\w+/status/\d+"
    tweet_urls = re.findall(tweet_url_pattern, message.content)

    for tweet_url in tweet_urls:
        if tweet_url in liens_envoyes:
            await message.delete()
            await message.channel.send(f"{message.author.mention}, Tu t'es fait bouclé salope 🔃")
        else:
            fixed_tweet_url = re.sub(r"https://twitter\.com/", r"https://vxtwitter.com/", tweet_url)
            liens_envoyes.add(tweet_url)
            await message.channel.send(f"{message.author.mention} - 🐦 - {fixed_tweet_url}")
            await message.delete()

# Lancer le bot avec son token
bot.run("YOUR_BOT_TOKEN")
