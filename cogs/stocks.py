# cogs/stocks.py
import discord
from discord.ext import commands, tasks
import json
import random
import asyncio

class Stocks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stocks = {}
        self.load_stocks()
        self.update_stocks.start()
        self.previous_prices = {}

    def cog_unload(self):
        self.update_stocks.cancel()

    def load_stocks(self):
        with open('stocks.json', 'r') as f:
            self.stocks = json.load(f)
        self.previous_prices = {symbol: stock['current_price'] for symbol, stock in self.stocks.items()}

    def save_stocks(self):
        with open('stocks.json', 'w') as f:
            json.dump(self.stocks, f, indent=2)

    def load_user_data(self):
        with open('user_data.json', 'r') as f:
            data = json.load(f)
        return {user_id: {**user_data, "points": round(user_data.get("points", 0), 2)} for user_id, user_data in data.items()}

    def save_user_data(self, data):
        rounded_data = {user_id: {**user_data, "points": round(user_data.get("points", 0), 2)} for user_id, user_data in data.items()}
        with open('user_data.json', 'w') as f:
            json.dump(rounded_data, f, indent=2)

    @tasks.loop(minutes=5)
    async def update_stocks(self):
        for symbol, stock in self.stocks.items():
            self.previous_prices[symbol] = stock['current_price']
            change = random.uniform(-stock['volatility'], stock['volatility'])
            stock['current_price'] = round(stock['current_price'] * (1 + change), 2)
        self.save_stocks()

    @commands.command()
    async def stocks(self, ctx):
        embed = discord.Embed(title="Actions disponibles", color=discord.Color.blue())
        
        for symbol, stock in self.stocks.items():
            current_price = stock['current_price']
            previous_price = self.previous_prices.get(symbol, current_price)
            
            if current_price > previous_price:
                arrow = "🟢 ↗️"  # Flèche verte vers le haut
            elif current_price < previous_price:
                arrow = "🔴 ↘️"  # Flèche rouge vers le bas
            else:
                arrow = "⚪ ➡️"  # Flèche blanche horizontale (pas de changement)
            
            change_percent = ((current_price - previous_price) / previous_price) * 100
            
            value = f"{arrow} Prix: {current_price:.2f}€ ({change_percent:+.2f}%)"
            
            embed.add_field(name=f"{stock['name']} ({symbol})", 
                            value=value, inline=False)
        
        await ctx.send(embed=embed)
        
    @commands.command(name="stocksbuy", aliases=["sb"])
    async def stocksbuy(self, ctx, symbol: str, amount: int):
        symbol = symbol.upper()
        if symbol not in self.stocks:
            await ctx.send("Cette action n'existe pas.")
            return

        user_data = self.load_user_data()
        user_id = str(ctx.author.id)

        if user_id not in user_data:
            user_data[user_id] = {"points": 0, "inventory": {}}

        total_cost = round(self.stocks[symbol]['current_price'] * amount, 2)
        if user_data[user_id].get('points', 0) < total_cost:
            await ctx.send("Vous n'avez pas assez de points pour cet achat.")
            return

        user_data[user_id]['points'] = user_data[user_id].get('points', 0) - total_cost
        
        if 'inventory' not in user_data[user_id] or not isinstance(user_data[user_id]['inventory'], dict):
            user_data[user_id]['inventory'] = {}
        if symbol not in user_data[user_id]['inventory']:
            user_data[user_id]['inventory'][symbol] = {'amount': 0, 'avg_price': 0}
        
        current_amount = user_data[user_id]['inventory'][symbol]['amount']
        current_avg_price = user_data[user_id]['inventory'][symbol]['avg_price']
        new_amount = current_amount + amount
        new_avg_price = (current_amount * current_avg_price + amount * self.stocks[symbol]['current_price']) / new_amount
        
        user_data[user_id]['inventory'][symbol]['amount'] = new_amount
        user_data[user_id]['inventory'][symbol]['avg_price'] = new_avg_price

        self.save_user_data(user_data)
        await ctx.send(f"Vous avez acheté {amount} actions de {self.stocks[symbol]['name']} pour {total_cost:.2f} points.")

    @commands.command(name="stockssell", aliases=["ss"])
    async def stockssell(self, ctx, symbol: str, amount: int):
        symbol = symbol.upper()
        if symbol not in self.stocks:
            await ctx.send("Cette action n'existe pas.")
            return

        user_data = self.load_user_data()
        user_id = str(ctx.author.id)

        if user_id not in user_data:
            await ctx.send("Vous n'avez pas d'actions à vendre.")
            return

        if 'inventory' not in user_data[user_id] or not isinstance(user_data[user_id]['inventory'], dict):
            await ctx.send("Vous n'avez pas d'actions à vendre.")
            return

        if symbol not in user_data[user_id]['inventory']:
            await ctx.send("Vous n'avez pas d'actions de ce type à vendre.")
            return

        stock_data = user_data[user_id]['inventory'][symbol]
        if isinstance(stock_data, dict):
            current_amount = stock_data.get('amount', 0)
        else:
            current_amount = stock_data

        if current_amount < amount:
            await ctx.send("Vous n'avez pas assez d'actions à vendre.")
            return

        total_value = round(self.stocks[symbol]['current_price'] * amount, 2)
        user_data[user_id]['points'] = user_data[user_id].get('points', 0) + total_value

        if isinstance(stock_data, dict):
            stock_data['amount'] -= amount
            if stock_data['amount'] == 0:
                del user_data[user_id]['inventory'][symbol]
        else:
            new_amount = current_amount - amount
            if new_amount == 0:
                del user_data[user_id]['inventory'][symbol]
            else:
                user_data[user_id]['inventory'][symbol] = new_amount

        self.save_user_data(user_data)
        await ctx.send(f"Vous avez vendu {amount} actions de {self.stocks[symbol]['name']} pour {total_value:.2f} points.")

    @commands.command(name="portfolio", aliases=["pf"])
    async def portfolio(self, ctx):
        user_data = self.load_user_data()
        user_id = str(ctx.author.id)

        if user_id not in user_data or 'inventory' not in user_data[user_id] or not user_data[user_id]['inventory']:
            await ctx.send("Vous n'avez pas d'actions dans votre portefeuille.")
            return

        embed = discord.Embed(title="Votre portefeuille", color=discord.Color.green())
        total_value = 0
        total_cost = 0

        inventory = user_data[user_id]['inventory']
        
        for symbol, stock_data in inventory.items():
            if symbol in self.stocks:
                current_price = self.stocks[symbol]['current_price']
                
                if isinstance(stock_data, dict):
                    amount = stock_data.get('amount', 0)
                    avg_price = stock_data.get('avg_price', current_price)
                else:
                    amount = stock_data
                    avg_price = current_price  # Nous n'avons pas cette information, donc on utilise le prix actuel
                
                stock_value = current_price * amount
                stock_cost = avg_price * amount
                total_value += stock_value
                total_cost += stock_cost
                
                profit_loss = stock_value - stock_cost
                profit_loss_percent = (profit_loss / stock_cost) * 100 if stock_cost > 0 else 0
                
                if current_price > avg_price:
                    arrow = "🟢 ↗️"
                elif current_price < avg_price:
                    arrow = "🔴 ↘️"
                else:
                    arrow = "⚪ ➡️"
                
                value_text = f"Quantité: {amount}\n"
                value_text += f"Prix moyen d'achat: {avg_price:.2f}€\n"
                value_text += f"Prix actuel: {current_price:.2f}€\n"
                value_text += f"Valeur: {stock_value:.2f}€\n"
                value_text += f"{arrow} P/L: {profit_loss:+.2f}€ ({profit_loss_percent:+.2f}%)"
                
                embed.add_field(name=f"{self.stocks[symbol]['name']} ({symbol})",
                                value=value_text, inline=False)
            else:
                if isinstance(stock_data, dict):
                    amount = stock_data.get('amount', 0)
                else:
                    amount = stock_data
                embed.add_field(name=f"Action inconnue ({symbol})",
                                value=f"Quantité: {amount}\nValeur: Inconnue", inline=False)

        total_profit_loss = total_value - total_cost
        total_profit_loss_percent = (total_profit_loss / total_cost) * 100 if total_cost > 0 else 0

        embed.add_field(name="Résumé", value=f"Valeur totale: {total_value:.2f}€\n"
                                            f"Coût total: {total_cost:.2f}€\n"
                                            f"P/L total: {total_profit_loss:+.2f}€ ({total_profit_loss_percent:+.2f}%)", inline=False)
        embed.add_field(name="Points disponibles", value=f"{user_data[user_id].get('points', 0):.2f}", inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Stocks(bot))