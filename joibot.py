import discord
from discord.ext import commands
import re
import random
import requests
import aiohttp

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
    
    #QUOI-FEUR ===================================

    if message.content.lower().endswith("quoi"):
        random_response = random.choice(["feur", "coubeh", "chi", "driceps", "fure", "ffant", "drilatere", "d", "dri"])
        await message.channel.send(random_response)


    #QUOI-FEUR ===================================

    #V A TOI ===================================

    elif message.content.lower() == "v":
        response = "ＩＭＭＥＮＳＥ　Ｖ　Ａ　ＴＯＩ　　ＭＯＮ　ＡＭＩ！\n" + \
                   "ＩＭＭＥＮＳＥ　Ｖ　Ａ　ＴＯＩ　　ＭＯＮ　ＡＭＩ！\n" + \
                   "ＩＭＭＥＮＳＥ　Ｖ　Ａ　ＴＯＩ　　ＭＯＮ　ＡＭＩ！\n" + \
                   "ＩＭＭＥＮＳＥ　Ｖ　Ａ　ＴＯＩ　　ＭＯＮ　ＡＭＩ！\n" + \
                   "ＩＭＭＥＮＳＥ　Ｖ　Ａ　ＴＯＩ　　ＭＯＮ　ＡＭＩ！\n" + \
                   "ᵃᵖᵖʳᵉⁿᵈˢ ᵃ ᶜᵒᵖᶦᵉʳ⁻ᶜᵒˡˡᵉʳ ᵖᵒᵛᶜᵒⁿ !\n" + \
                   "https://cdn.discordapp.com/attachments/620701105671634963/835219902167253042/DK5C0hRWkAA5xkW.jpg"
        await message.channel.send(response)

    #V A TOI ===================================


    #TWEET-FIX ===================================
    else:
        tweet_url_pattern = r"https://twitter\.com/\w+/status/\d+"
        tweet_urls = re.findall(tweet_url_pattern, message.content)

        x_url_pattern = r"https://x\.com/\w+/status/\d+"
        x_urls = re.findall(x_url_pattern, message.content)

        for tweet_url in tweet_urls:
            if tweet_url in liens_envoyes:
                await message.delete()
                await message.channel.send(f"{message.author.mention}, Tu t'es fait bouclé salope 🔃")
            else:
                fixed_tweet_url = re.sub(r"https://twitter\.com/", r"https://vxtwitter.com/", tweet_url)
                liens_envoyes.add(tweet_url)
                await message.channel.send(f"{message.author.mention} - 🐦 - {fixed_tweet_url}")
                await message.delete()
                
        for x_url in x_urls:
            if x_url in liens_envoyes:
                await message.delete()
                await message.channel.send(f"{message.author.mention}, Tu t'es fait bouclé salope 🔃")
            else:
                fixed_x_url = re.sub(r"https://x\.com/", r"https://fixupx.com/", x_url)
                liens_envoyes.add(x_url)
                await message.channel.send(f"{message.author.mention} - 𝕏 - {fixed_x_url}")
                await message.delete()
    #TWEET-FIX ===================================
    
    # RANDOM TA GUEULE ===========================
            
    if random.uniform(0, 100) < 0.5:
            await message.delete()
            await message.channel.send(f"{message.author.mention}, Allez hop supprimer ta gueule bouffon")

    # RANDOM TA GUEULE ===========================


# Lancer le bot avec son token
bot.run("TOKEN")
