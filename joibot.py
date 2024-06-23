import discord
from discord.ext import commands
import re
import random
import asyncio

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

bot = commands.Bot(command_prefix="j!", intents=intents)

# Créer un ensemble pour stocker les liens déjà envoyés
liens_envoyes = set()
# Dictionnaire pour suivre les tâches de harcèlement actives
harcèlement_tasks = {}


@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user.name}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # QUOI-FEUR ===================================
    if message.content.lower().endswith("quoi"):
        random_response = random.choice(
            [
                "feur",
                "coubeh",
                "chi",
                "driceps",
                "fure",
                "ffant",
                "drilatere",
                "d",
                "dri",
            ]
        )
        await message.channel.send(random_response)

    # V A TOI ===================================
    elif message.content.lower() == "^^":
        response = (
            ":warning: Attention :warning:  L'emploi de ˆˆ indique que vous êtes certainement un criminel recherché par la police. Nous vous demanderons de vous abstenir dans le chat et nous signalerons les autorités compétentes pour la sécurité d'autrui !\n"
            + "https://tenor.com/view/alert-siren-warning-light-gif-15160785"
        )
        await message.channel.send(response)

    # ALERTE PEDO ===================================
    elif message.content.lower() == "v":
        response = (
            "ＩＭＭＥＮＳＥ　Ｖ　Ａ　ＴＯＩ　　ＭＯＮ　ＡＭＩ！\n"
            + "ＩＭＭＥＮＳＥ　Ｖ　Ａ　ＴＯＩ　　ＭＯＮ　ＡＭＩ！\n"
            + "ＩＭＭＥＮＳＥ　Ｖ　Ａ　ＴＯＩ　　ＭＯＮ　ＡＭＩ！\n"
            + "ＩＭＭＥＮＳＥ　Ｖ　Ａ　ＴＯＩ　　ＭＯＮ　ＡＭＩ！\n"
            + "ＩＭＭＥＮＳＥ　Ｖ　Ａ　ＴＯＩ　　ＭＯＮ　ＡＭＩ！\n"
            + "ᵃᵖᵖʳᵉⁿᵈˢ ᵃ ᶜᵒᵖᶦᵉʳ⁻ᶜᵒˡˡᵉʳ ᵖᵒᵛᶜᵒⁿ !\n"
            + "https://cdn.discordapp.com/attachments/620701105671634963/835219902167253042/DK5C0hRWkAA5xkW.jpg"
        )
        await message.channel.send(response)

    # TWEET-FIX ===================================
    else:
        tweet_url_pattern = r"https://twitter\.com/\w+/status/\d+"
        tweet_urls = re.findall(tweet_url_pattern, message.content)

        x_url_pattern = r"https://x\.com/\w+/status/\d+"
        x_urls = re.findall(x_url_pattern, message.content)

        for tweet_url in tweet_urls:
            if tweet_url in liens_envoyes:
                await message.delete()
                await message.channel.send(
                    f"{message.author.mention}, Tu t'es fait bouclé salope 🔃"
                )
            else:
                fixed_tweet_url = re.sub(
                    r"https://twitter\.com/", r"https://fxtwitter.com/", tweet_url
                )
                liens_envoyes.add(tweet_url)
                await message.channel.send(
                    f"{message.author.mention} - 🐦 - {fixed_tweet_url}"
                )
                await message.delete()

        for x_url in x_urls:
            if x_url in liens_envoyes:
                await message.delete()
                await message.channel.send(
                    f"{message.author.mention}, Tu t'es fait bouclé salope 🔃"
                )
            else:
                fixed_x_url = re.sub(r"https://x\.com/", r"https://fixupx.com/", x_url)
                liens_envoyes.add(x_url)
                await message.channel.send(
                    f"{message.author.mention} - 𝕏 - {fixed_x_url}"
                )
                await message.delete()

    # RANDOM TA GUEULE ===========================
    if random.uniform(0, 100) < 0.01:
        await message.delete()
        await message.channel.send(
            f"{message.author.mention}, Allez hop supprimer ta gueule bouffon"
        )

    # RANDOM TA GUEULE ===========================

    await bot.process_commands(
        message
    )  # Ne pas oublier cette ligne pour traiter les commandes

    # HARCELEMENT ===========================


# Commande pour harcèlement
@bot.command()
async def harcelement(
    ctx, member: discord.Member, interval: int, *, message="spam de harcèlement !"
):
    # Vérifier que l'intervalle est supérieur à 0
    if interval < 1:
        await ctx.send("L'intervalle doit être supérieur à 0 seconde.")
        return

    # Vérifier que le membre n'est pas déjà harcelé
    if member.id in harcèlement_tasks:
        await ctx.send(
            f"{member.mention} est déjà en train de se faire harceler. Utilisez `!stop_harcelement` pour arrêter le spam."
        )
        return

    async def harceler():
        while True:
            try:
                # Envoyer un message dans le canal texte
                await ctx.send(f"{member.mention} {message}")

                # Essayer d'envoyer un DM
                await member.send(
                    f"{member.mention}, {message} dans {ctx.guild.name} par {ctx.author.name} !"
                )

            except discord.Forbidden:
                # Si les DMs sont désactivés ou interdits
                await ctx.send(f"{member.mention} a désactivé les DMs cette sasa.")

            except Exception as e:
                # Journaliser les autres exceptions
                await ctx.send(f"Une erreur est survenue : {e}")

            await asyncio.sleep(interval)

    # Démarrer la tâche de harcèlement
    task = bot.loop.create_task(harceler())
    harcèlement_tasks[member.id] = task
    await ctx.send(
        f"Début du harcèlement de ce sale type toutes les {interval} secondes."
    )


# Commande pour arrêter le harcèlement
@bot.command()
async def stop_harcelement(ctx, member: discord.Member):
    # Vérifier si le membre est actuellement harcelé
    if member.id not in harcèlement_tasks:
        await ctx.send(f"{member.mention} n'est pas actuellement harcelé.")
        return

    # Annuler la tâche de harcèlement
    task = harcèlement_tasks.pop(member.id)
    task.cancel()
    await ctx.send(f"Arrêt du harcèlement de {member.mention}.")

    # HARCELEMENT ===========================


# Lancer le bot avec son token
bot.run("TOKEN DISCORD")
