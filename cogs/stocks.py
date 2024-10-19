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
        self.api_key = "YOUR_ALPHA_VANTAGE_API_KEY"  # Replace with your Alpha Vantage API key

    # ... (other methods remain the same)

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

    # ... (other methods remain the same)

async def setup(bot):
    await bot.add_cog(Stocks(bot))