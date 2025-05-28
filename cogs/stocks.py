import discord
from discord.ext import commands, tasks
import json
import asyncio
import yfinance as yf
from datetime import datetime, timedelta
import os

class Stocks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stocks = {}
        self.load_stocks()
        self.update_stocks.start()
        self.previous_prices = {}
        self.stocks_data_file = 'stocks_data.json'

    def cog_unload(self):
        self.update_stocks.cancel()

    def load_stocks(self):
        """Définit les stocks disponibles avec leurs symboles Yahoo Finance"""
        self.stocks = {
            "BTC": {"name": "Bitcoin", "symbol": "BTC-USD"},
            "ETH": {"name": "Ethereum", "symbol": "ETH-USD"},
            "UBI": {"name": "Ubisoft", "symbol": "UBI.PA"},
            "LMT": {"name": "Lockheed Martin", "symbol": "LMT"},
            "GOOGL": {"name": "Alphabet (Google)", "symbol": "GOOGL"},
            "AAPL": {"name": "Apple", "symbol": "AAPL"},
            "MSFT": {"name": "Microsoft", "symbol": "MSFT"},
            "AMZN": {"name": "Amazon", "symbol": "AMZN"},
            "TSLA": {"name": "Tesla", "symbol": "TSLA"},
            "META": {"name": "Meta (Facebook)", "symbol": "META"},
            "NVDA": {"name": "NVIDIA", "symbol": "NVDA"},
            "NFLX": {"name": "Netflix", "symbol": "NFLX"},
            "DIS": {"name": "Disney", "symbol": "DIS"},
            "ADBE": {"name": "Adobe", "symbol": "ADBE"},
            "PYPL": {"name": "PayPal", "symbol": "PYPL"},
            "INTC": {"name": "Intel", "symbol": "INTC"},
            "AMD": {"name": "AMD", "symbol": "AMD"},
            "SONY": {"name": "Sony", "symbol": "SONY"},
            "EA": {"name": "Electronic Arts", "symbol": "EA"}
        }
        
        # Charger les prix précédents depuis le fichier
        self.load_previous_prices()

    def load_previous_prices(self):
        """Charge les prix précédents depuis un fichier JSON"""
        try:
            with open(self.stocks_data_file, 'r') as f:
                data = json.load(f)
                self.previous_prices = data.get('previous_prices', {symbol: 0 for symbol in self.stocks})
                # Charger les prix actuels s'ils existent
                for symbol in self.stocks:
                    if symbol in data.get('current_prices', {}):
                        self.stocks[symbol]['current_price'] = data['current_prices'][symbol]
        except FileNotFoundError:
            self.previous_prices = {symbol: 0 for symbol in self.stocks}

    def save_stocks_data(self):
        """Sauvegarde les données des stocks"""
        data = {
            'previous_prices': self.previous_prices,
            'current_prices': {symbol: stock.get('current_price', 0) for symbol, stock in self.stocks.items()},
            'last_update': datetime.now().isoformat()
        }
        with open(self.stocks_data_file, 'w') as f:
            json.dump(data, f, indent=2)

    async def fetch_stock_price(self, symbol):
        """Récupère le prix d'une action via yfinance"""
        try:
            ticker = yf.Ticker(self.stocks[symbol]['symbol'])
            hist = ticker.history(period="1d")
            if not hist.empty:
                return round(float(hist['Close'].iloc[-1]), 2)
            else:
                print(f"Aucune donnée trouvée pour {symbol}")
                return None
        except Exception as e:
            print(f"Erreur lors de la récupération du prix pour {symbol}: {e}")
            return None

    @tasks.loop(minutes=10)  # Mise à jour toutes les 10 minutes
    async def update_stocks(self):
        """Met à jour les prix des stocks"""
        print("Mise à jour des prix des stocks...")
        
        for symbol in self.stocks:
            # Sauvegarder le prix précédent
            self.previous_prices[symbol] = self.stocks[symbol].get('current_price', 0)
            
            # Récupérer le nouveau prix
            price = await self.fetch_stock_price(symbol)
            if price is not None:
                self.stocks[symbol]['current_price'] = price
                print(f"{symbol}: {price}€")
            else:
                print(f"Échec de mise à jour pour {symbol}")
        
        # Sauvegarder les données
        self.save_stocks_data()
        print("Mise à jour des stocks terminée")

    @update_stocks.before_loop
    async def before_update_stocks(self):
        """Attend que le bot soit prêt avant de commencer les mises à jour"""
        await self.bot.wait_until_ready()
        # Mise à jour initiale
        await self.update_stocks()

    def load_user_data(self):
        """Charge les données utilisateur"""
        try:
            with open('user_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_user_data(self, user_data):
        """Sauvegarde les données utilisateur"""
        with open('user_data.json', 'w') as f:
            json.dump(user_data, f, indent=2)

    @commands.command()
    async def stocks(self, ctx):
        """Affiche la liste des stocks disponibles avec leurs prix"""
        # Créer l'embed principal
        main_embed = discord.Embed(
            title="📊 Marché Boursier",
            description="Vue d'ensemble des actions disponibles",
            color=discord.Color.gold()
        )
        main_embed.set_footer(text="Mise à jour toutes les 10 minutes | Données fournies par Yahoo Finance")
        main_embed.timestamp = datetime.utcnow()

        # Trier les stocks par catégorie
        crypto_field = ""
        tech_field = ""
        gaming_field = ""
        other_field = ""

        # Trier les stocks par prix actuel, décroissant
        sorted_stocks = sorted(self.stocks.items(), 
                             key=lambda x: x[1].get('current_price', 0), 
                             reverse=True)

        for symbol, stock in sorted_stocks:
            current_price = stock.get('current_price', 0)
            previous_price = self.previous_prices.get(symbol, current_price)
            
            # Déterminer la direction du changement
            if current_price > previous_price:
                arrow = "🟢"
            elif current_price < previous_price:
                arrow = "🔴"
            else:
                arrow = "⚪"
            
            # Calculer le pourcentage de changement
            if previous_price > 0:
                change_percent = ((current_price - previous_price) / previous_price) * 100
            else:
                change_percent = 0
            
            stock_line = f"{arrow} **{symbol}**: {current_price:.2f}€ ({change_percent:+.2f}%)\n"
            
            # Catégoriser les stocks
            if symbol in ['BTC', 'ETH']:
                crypto_field += stock_line
            elif symbol in ['GOOGL', 'AAPL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'ADBE', 'INTC', 'AMD']:
                tech_field += stock_line
            elif symbol in ['UBI', 'EA', 'SONY']:
                gaming_field += stock_line
            else:
                other_field += stock_line

        # Ajouter les champs à l'embed
        if crypto_field:
            main_embed.add_field(name="₿ Cryptomonnaies", value=crypto_field, inline=False)
        if tech_field:
            main_embed.add_field(name="🖥️ Technologie", value=tech_field, inline=False)
        if gaming_field:
            main_embed.add_field(name="🎮 Gaming", value=gaming_field, inline=False)
        if other_field:
            main_embed.add_field(name="🏢 Autres", value=other_field, inline=False)

        # Ajouter des informations de marché
        def calculate_percent_change(current, previous):
            if previous == 0:
                return 0
            return ((current - previous) / previous) * 100

        # Trouver le top gagnant et perdant
        changes = []
        for symbol, stock in self.stocks.items():
            current_price = stock.get('current_price', 0)
            previous_price = self.previous_prices.get(symbol, current_price)
            change = calculate_percent_change(current_price, previous_price)
            changes.append((symbol, change))

        if changes:
            top_gainer = max(changes, key=lambda x: x[1])
            top_loser = min(changes, key=lambda x: x[1])

            insights = (f"📈 Top gagnant: **{top_gainer[0]}** ({top_gainer[1]:+.2f}%)\n"
                       f"📉 Top perdant: **{top_loser[0]}** ({top_loser[1]:+.2f}%)")

            main_embed.add_field(name="📊 Aperçu du Marché", value=insights, inline=False)

        await ctx.send(embed=main_embed)

    @commands.command(name="stocksbuy", aliases=["sb"])
    async def stocksbuy(self, ctx, symbol: str, amount: int):
        """Acheter des actions"""
        symbol = symbol.upper()
        
        if symbol not in self.stocks:
            available_stocks = ", ".join(self.stocks.keys())
            await ctx.send(f"❌ Cette action n'existe pas.\nActions disponibles: {available_stocks}")
            return

        if amount <= 0:
            await ctx.send("❌ La quantité doit être positive.")
            return

        # Vérifier si le prix existe
        current_price = self.stocks[symbol].get('current_price', 0)
        if current_price == 0:
            await ctx.send("❌ Prix non disponible pour cette action. Réessayez plus tard.")
            return

        user_data = self.load_user_data()
        user_id = str(ctx.author.id)

        # Initialiser l'utilisateur s'il n'existe pas
        if user_id not in user_data:
            user_data[user_id] = {"points": 0, "inventory": {}}

        total_cost = round(current_price * amount, 2)
        user_points = user_data[user_id].get('points', 0)

        if user_points < total_cost:
            await ctx.send(f"❌ Vous n'avez pas assez de points pour cet achat.\n"
                          f"Coût: {total_cost:.2f} points\nVos points: {user_points:.2f}")
            return

        # Effectuer l'achat
        user_data[user_id]['points'] = user_points - total_cost
        
        # Gérer l'inventaire
        if 'inventory' not in user_data[user_id]:
            user_data[user_id]['inventory'] = {}
        
        if symbol not in user_data[user_id]['inventory']:
            user_data[user_id]['inventory'][symbol] = {'amount': 0, 'avg_price': 0}
        
        current_amount = user_data[user_id]['inventory'][symbol]['amount']
        current_avg_price = user_data[user_id]['inventory'][symbol]['avg_price']
        
        # Calculer le nouveau prix moyen
        new_amount = current_amount + amount
        if current_amount == 0:
            new_avg_price = current_price
        else:
            new_avg_price = ((current_amount * current_avg_price) + (amount * current_price)) / new_amount
        
        user_data[user_id]['inventory'][symbol]['amount'] = new_amount
        user_data[user_id]['inventory'][symbol]['avg_price'] = round(new_avg_price, 2)

        self.save_user_data(user_data)
        
        embed = discord.Embed(
            title="✅ Achat réussi",
            description=f"Vous avez acheté **{amount}** actions de **{self.stocks[symbol]['name']}** ({symbol})",
            color=discord.Color.green()
        )
        embed.add_field(name="Prix unitaire", value=f"{current_price:.2f}€", inline=True)
        embed.add_field(name="Coût total", value=f"{total_cost:.2f} points", inline=True)
        embed.add_field(name="Points restants", value=f"{user_data[user_id]['points']:.2f}", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command(name="stockssell", aliases=["ss"])
    async def stockssell(self, ctx, symbol: str, amount: int):
        """Vendre des actions"""
        symbol = symbol.upper()
        
        if symbol not in self.stocks:
            await ctx.send("❌ Cette action n'existe pas.")
            return

        if amount <= 0:
            await ctx.send("❌ La quantité doit être positive.")
            return

        current_price = self.stocks[symbol].get('current_price', 0)
        if current_price == 0:
            await ctx.send("❌ Prix non disponible pour cette action. Réessayez plus tard.")
            return

        user_data = self.load_user_data()
        user_id = str(ctx.author.id)

        if (user_id not in user_data or 
            'inventory' not in user_data[user_id] or 
            symbol not in user_data[user_id]['inventory']):
            await ctx.send("❌ Vous n'avez pas d'actions de ce type à vendre.")
            return

        stock_data = user_data[user_id]['inventory'][symbol]
        current_amount = stock_data.get('amount', 0)

        if current_amount < amount:
            await ctx.send(f"❌ Vous n'avez que {current_amount} actions de {symbol} à vendre.")
            return

        # Effectuer la vente
        total_value = round(current_price * amount, 2)
        user_data[user_id]['points'] = user_data[user_id].get('points', 0) + total_value

        # Mettre à jour l'inventaire
        stock_data['amount'] -= amount
        if stock_data['amount'] == 0:
            del user_data[user_id]['inventory'][symbol]

        self.save_user_data(user_data)
        
        # Calculer le profit/perte
        avg_price = stock_data.get('avg_price', current_price)
        profit_loss = (current_price - avg_price) * amount
        
        embed = discord.Embed(
            title="✅ Vente réussie",
            description=f"Vous avez vendu **{amount}** actions de **{self.stocks[symbol]['name']}** ({symbol})",
            color=discord.Color.blue()
        )
        embed.add_field(name="Prix unitaire", value=f"{current_price:.2f}€", inline=True)
        embed.add_field(name="Valeur totale", value=f"{total_value:.2f} points", inline=True)
        embed.add_field(name="P/L", value=f"{profit_loss:+.2f} points", inline=True)
        embed.add_field(name="Points totaux", value=f"{user_data[user_id]['points']:.2f}", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command(name="portfolio", aliases=["pf"])
    async def portfolio(self, ctx):
        """Affiche le portefeuille de l'utilisateur"""
        user_data = self.load_user_data()
        user_id = str(ctx.author.id)

        if (user_id not in user_data or 
            'inventory' not in user_data[user_id] or 
            not user_data[user_id]['inventory']):
            await ctx.send("❌ Vous n'avez pas d'actions dans votre portefeuille.")
            return

        embed = discord.Embed(
            title="💼 Votre portefeuille",
            description=f"Portefeuille de {ctx.author.display_name}",
            color=discord.Color.purple()
        )
        
        total_value = 0
        total_cost = 0
        inventory = user_data[user_id]['inventory']
        
        for symbol, stock_data in inventory.items():
            if symbol in self.stocks:
                current_price = self.stocks[symbol].get('current_price', 0)
                amount = stock_data.get('amount', 0)
                avg_price = stock_data.get('avg_price', current_price)
                
                stock_value = current_price * amount
                stock_cost = avg_price * amount
                total_value += stock_value
                total_cost += stock_cost
                
                profit_loss = stock_value - stock_cost
                profit_loss_percent = (profit_loss / stock_cost) * 100 if stock_cost > 0 else 0
                
                # Icône selon le profit/perte
                if current_price > avg_price:
                    arrow = "🟢 ↗️"
                elif current_price < avg_price:
                    arrow = "🔴 ↘️"
                else:
                    arrow = "⚪ ➡️"
                
                value_text = (f"**Quantité:** {amount}\n"
                             f"**Prix moyen:** {avg_price:.2f}€\n"
                             f"**Prix actuel:** {current_price:.2f}€\n"
                             f"**Valeur totale:** {stock_value:.2f}€\n"
                             f"{arrow} **P/L:** {profit_loss:+.2f}€ ({profit_loss_percent:+.2f}%)")
                
                embed.add_field(
                    name=f"{self.stocks[symbol]['name']} ({symbol})",
                    value=value_text,
                    inline=False
                )

        # Résumé du portefeuille
        total_profit_loss = total_value - total_cost
        total_profit_loss_percent = (total_profit_loss / total_cost) * 100 if total_cost > 0 else 0

        summary_text = (f"**Valeur totale:** {total_value:.2f}€\n"
                       f"**Investissement:** {total_cost:.2f}€\n"
                       f"**P/L total:** {total_profit_loss:+.2f}€ ({total_profit_loss_percent:+.2f}%)")

        embed.add_field(name="📊 Résumé", value=summary_text, inline=False)
        embed.add_field(name="💰 Points disponibles", 
                       value=f"{user_data[user_id].get('points', 0):.2f}", inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="stockinfo", aliases=["si"])
    async def stockinfo(self, ctx, symbol: str):
        """Affiche des informations détaillées sur une action"""
        symbol = symbol.upper()
        
        if symbol not in self.stocks:
            await ctx.send("❌ Cette action n'existe pas.")
            return

        try:
            ticker = yf.Ticker(self.stocks[symbol]['symbol'])
            info = ticker.info
            hist = ticker.history(period="5d")
            
            current_price = self.stocks[symbol].get('current_price', 0)
            previous_price = self.previous_prices.get(symbol, current_price)
            
            change = current_price - previous_price
            change_percent = (change / previous_price) * 100 if previous_price > 0 else 0
            
            embed = discord.Embed(
                title=f"📈 {self.stocks[symbol]['name']} ({symbol})",
                color=discord.Color.gold()
            )
            
            embed.add_field(name="Prix actuel", value=f"{current_price:.2f}€", inline=True)
            embed.add_field(name="Changement", value=f"{change:+.2f}€ ({change_percent:+.2f}%)", inline=True)
            embed.add_field(name="Symbole", value=self.stocks[symbol]['symbol'], inline=True)
            
            # Informations supplémentaires si disponibles
            if 'marketCap' in info:
                market_cap = info['marketCap'] / 1_000_000_000  # En milliards
                embed.add_field(name="Capitalisation", value=f"{market_cap:.1f}B€", inline=True)
            
            if not hist.empty:
                week_high = hist['High'].max()
                week_low = hist['Low'].min()
                embed.add_field(name="Max 5j", value=f"{week_high:.2f}€", inline=True)
                embed.add_field(name="Min 5j", value=f"{week_low:.2f}€", inline=True)
            
            embed.set_footer(text="Données fournies par Yahoo Finance")
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de la récupération des informations: {e}")

async def setup(bot):
    await bot.add_cog(Stocks(bot))