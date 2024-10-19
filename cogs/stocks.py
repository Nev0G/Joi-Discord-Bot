import discord
from discord.ext import commands, tasks
import json
import aiohttp
import asyncio
from datetime import datetime, timedelta

class Stocks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stocks = {}
        self.load_stocks()
        self.update_stocks.start()
        self.previous_prices = {}
        self.last_api_call = {}
        self.api_key = "EZ89SRMIUGJQKETY"  # Replace with your Alpha Vantage API key

    def cog_unload(self):
        self.update_stocks.cancel()

    def load_stocks(self):
        self.stocks = {
            "BTC": {"name": "Bitcoin", "symbol": "BTCUSD"},
            "UBI": {"name": "Ubisoft", "symbol": "UBI.PA"},
            "LMT": {"name": "Lockheed Martin", "symbol": "LMT"},
            "GOOGL": {"name": "Alphabet (Google)", "symbol": "GOOGL"},
            "AAPL": {"name": "Apple", "symbol": "AAPL"},
            "MSFT": {"name": "Microsoft", "symbol": "MSFT"},
            "AMZN": {"name": "Amazon", "symbol": "AMZN"},
            "TSLA": {"name": "Tesla", "symbol": "TSLA"},
            "FB": {"name": "Meta (Facebook)", "symbol": "FB"},
            "NVDA": {"name": "NVIDIA", "symbol": "NVDA"},
            "NFLX": {"name": "Netflix", "symbol": "NFLX"},
            "DIS": {"name": "Disney", "symbol": "DIS"},
            "ADBE": {"name": "Adobe", "symbol": "ADBE"},
            "PYPL": {"name": "PayPal", "symbol": "PYPL"},
            "INTC": {"name": "Intel", "symbol": "INTC"}
        }
        self.previous_prices = {symbol: 0 for symbol in self.stocks}

    async def fetch_stock_price(self, symbol):
        # Respect API call limits (5 calls per minute, 500 per day for free tier)
        now = datetime.now()
        if symbol in self.last_api_call and now - self.last_api_call[symbol] < timedelta(seconds=12):
            await asyncio.sleep(12 - (now - self.last_api_call[symbol]).seconds)

        self.last_api_call[symbol] = datetime.now()

        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={self.stocks[symbol]['symbol']}&apikey={self.api_key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                if "Global Quote" in data and "05. price" in data["Global Quote"]:
                    return float(data["Global Quote"]["05. price"])
                else:
                    print(f"Error fetching price for {symbol}: {data}")
                    return None

    @tasks.loop(minutes=5)
    async def update_stocks(self):
        for symbol in self.stocks:
            self.previous_prices[symbol] = self.stocks[symbol].get('current_price', 0)
            price = await self.fetch_stock_price(symbol)
            if price:
                self.stocks[symbol]['current_price'] = round(price, 2)

    @commands.command()
    async def stocks(self, ctx):
        # Create the main embed
        main_embed = discord.Embed(
            title="📊 Marché Boursier",
            description="Vue d'ensemble des actions disponibles",
            color=discord.Color.gold()
        )
        main_embed.set_footer(text="Mise à jour toutes les 5 minutes | Données fournies par Alpha Vantage")

        # Add a timestamp
        main_embed.timestamp = datetime.utcnow()

        # Create fields for different sectors
        tech_field = ""
        finance_field = ""
        other_field = ""

        # Sort stocks by current price, descending
        sorted_stocks = sorted(self.stocks.items(), key=lambda x: x[1].get('current_price', 0), reverse=True)

        for symbol, stock in sorted_stocks:
            current_price = stock.get('current_price', 0)
            previous_price = self.previous_prices.get(symbol, current_price)
            
            if current_price > previous_price:
                arrow = "🟢"
            elif current_price < previous_price:
                arrow = "🔴"
            else:
                arrow = "⚪"
            
            change_percent = ((current_price - previous_price) / previous_price) * 100 if previous_price else 0
            
            stock_line = f"{arrow} **{symbol}**: {current_price:.2f}€ ({change_percent:+.2f}%)\n"
            
            # Categorize stocks (you can expand this categorization)
            if symbol in ['GOOGL', 'AAPL', 'MSFT', 'AMZN', 'TSLA', 'FB', 'NVDA', 'NFLX', 'ADBE', 'INTC']:
                tech_field += stock_line
            elif symbol in ['PYPL']:
                finance_field += stock_line
            else:
                other_field += stock_line

        # Add fields to the embed
        if tech_field:
            main_embed.add_field(name="🖥️ Technologie", value=tech_field, inline=False)
        if finance_field:
            main_embed.add_field(name="💰 Finance", value=finance_field, inline=False)
        if other_field:
            main_embed.add_field(name="🏢 Autres", value=other_field, inline=False)

        # Add some market insights
        top_gainer = max(self.stocks.items(), key=lambda x: ((x[1].get('current_price', 0) - self.previous_prices.get(x[0], x[1].get('current_price', 0))) / self.previous_prices.get(x[0], x[1].get('current_price', 0))) if self.previous_prices.get(x[0], 0) != 0 else 0)
        top_loser = min(self.stocks.items(), key=lambda x: ((x[1].get('current_price', 0) - self.previous_prices.get(x[0], x[1].get('current_price', 0))) / self.previous_prices.get(x[0], x[1].get('current_price', 0))) if self.previous_prices.get(x[0], 0) != 0 else 0)

        insights = (f"📈 Top gagnant: **{top_gainer[0]}** (+{((top_gainer[1].get('current_price', 0) - self.previous_prices.get(top_gainer[0], top_gainer[1].get('current_price', 0))) / self.previous_prices.get(top_gainer[0], top_gainer[1].get('current_price', 0)) * 100):.2f}%)\n"
                    f"📉 Top perdant: **{top_loser[0]}** ({((top_loser[1].get('current_price', 0) - self.previous_prices.get(top_loser[0], top_loser[1].get('current_price', 0))) / self.previous_prices.get(top_loser[0], top_loser[1].get('current_price', 0)) * 100):.2f}%)")

        main_embed.add_field(name="📊 Aperçu du Marché", value=insights, inline=False)

        # Send the embed
        await ctx.send(embed=main_embed)

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