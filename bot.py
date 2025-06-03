import discord
from discord.ext import commands
import asyncio
import os
import json

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="j!", intents=intents)

def update_user_points(user_id, points_to_add):
    try:
        with open('user_data.json', 'r', encoding='utf-8') as f:
            try:
                user_data = json.load(f)
            except json.JSONDecodeError:
                user_data = {}
    except FileNotFoundError:
        user_data = {}

    user_id_str = str(user_id)
    if user_id_str not in user_data:
        user_data[user_id_str] = {"points": 0}

    user_data[user_id_str]["points"] = round(user_data[user_id_str].get("points", 0) + points_to_add, 2)

    with open('user_data.json', 'w', encoding='utf-8') as f:
        json.dump(user_data, f, indent=2)

async def load_extensions():
    if not os.path.exists("./cogs"):
        print("Le dossier 'cogs/' est introuvable.")
        return

    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'✅ Cog chargé : {filename}')
            except Exception as e:
                print(f'❌ Erreur lors du chargement de {filename}: {type(e).__name__} - {e}')

@bot.event
async def on_ready():
    print(f'✅ Connecté en tant que {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if not message.content.startswith(bot.command_prefix):
        update_user_points(message.author.id, 0.1)

    await bot.process_commands(message)

async def main():
    await load_extensions()
    await bot.start("TOKEN")  # remplace par ton token réel

if __name__ == "__main__":
    asyncio.run(main())
