import discord
from discord.ext import commands, tasks
import asyncio
import os
import random
import json

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

bot = commands.Bot(command_prefix="j!", intents=intents)

def update_user_points(user_id, points_to_add):
    try:
        with open('user_data.json', 'r') as f:
            user_data = json.load(f)
    except FileNotFoundError:
        user_data = {}

    if str(user_id) not in user_data:
        user_data[str(user_id)] = {"points": 0}

    user_data[str(user_id)]["points"] = round(user_data[str(user_id)].get("points", 0) + points_to_add, 2)

    with open('user_data.json', 'w') as f:
        json.dump(user_data, f, indent=2)

async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'Extension chargée : {filename}')
            except Exception as e:
                print(f'Erreur lors du chargement de {filename}: {type(e).__name__} - {e}')

@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if not message.content.startswith(bot.command_prefix):
        update_user_points(message.author.id, 0.1)

    await bot.process_commands(message)


async def main():
    await load_extensions()
    await bot.start("TOKEN")

if __name__ == "__main__":
    asyncio.run(main())