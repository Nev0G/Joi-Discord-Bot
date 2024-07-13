# shop.py
import discord
from discord.ext import commands
import json
import os

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shop_file = 'shop_items.json'
        self.user_data_file = 'user_data.json'
        self.shop_items = self.load_shop_items()

    def load_shop_items(self):
        if os.path.exists(self.shop_file):
            with open(self.shop_file, 'r') as f:
                return json.load(f)
        return {"items": []}

    def load_user_data(self):
        if os.path.exists(self.user_data_file):
            with open(self.user_data_file, 'r') as f:
                return json.load(f)
        return {}

    def save_user_data(self, user_data):
        with open(self.user_data_file, 'w') as f:
            json.dump(user_data, f, indent=4)

    @commands.command(name="shop")
    async def shop(self, ctx):
        """Affiche les articles disponibles à l'achat."""
        embed = discord.Embed(title="Boutique", description="Articles disponibles à l'achat", color=0x00ff00)
        for item in self.shop_items.get('items', []):
            embed.add_field(name=f"{item['name']} - {item['price']} points", value=item['description'], inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="buy")
    async def buy(self, ctx, *, item_name: str):
        """Permet d'acheter un article de la boutique."""
        user_id = str(ctx.author.id)
        user_data = self.load_user_data()

        if user_id not in user_data:
            user_data[user_id] = {"points": 0, "inventory": []}

        item = next((item for item in self.shop_items.get('items', []) if item['name'].lower() == item_name.lower()), None)
        if not item:
            await ctx.send("Cet article n'existe pas dans la boutique.")
            return

        if user_data[user_id]["points"] < item['price']:
            await ctx.send("Vous n'avez pas assez de points pour acheter cet article.")
            return

        user_data[user_id]["points"] -= item['price']

        if 'inventory' not in user_data[user_id]:
            user_data[user_id]['inventory'] = []

        if item['type'] == 'command':
            user_data[user_id]["inventory"].append(item['name'])
            await ctx.send(f"Vous avez acheté **{item['name']}** pour {item['price']} points ! Il est maintenant dans votre inventaire.")
        elif item['type'] == 'role':
            role = ctx.guild.get_role(int(item['role_id']))
            if role:
                await ctx.author.add_roles(role)
                user_data[user_id]["inventory"].append(item['name'])
                await ctx.send(f"Félicitations {ctx.author.mention} ! Vous avez acheté le rôle **{role.name}** pour {item['price']} points.")
            else:
                await ctx.send("Le rôle spécifié n'existe pas.")
                return

        self.save_user_data(user_data)

    @commands.command(name="inventory", aliases=["inv"])
    async def inventory(self, ctx):
        """Affiche l'inventaire de l'utilisateur."""
        user_id = str(ctx.author.id)
        user_data = self.load_user_data()

        if user_id not in user_data or not user_data[user_id].get("inventory"):
            await ctx.send("Votre inventaire est vide.")
            return

        embed = discord.Embed(title="Votre inventaire", color=0x00ff00)
        for item in user_data[user_id]["inventory"]:
            embed.add_field(name="Objet", value=item, inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Shop(bot))