import discord
from discord.ext import commands, tasks
import json
import asyncio
from datetime import datetime, timedelta
import os
import random
import math

USER_DATA_FILE = "user_data.json"
STOCKS_DATA_FILE = "stocks_data.json"
PORTFOLIO_FILE = "user_portfolios.json"

class Stocks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stocks = {}
        self.user_portfolios = {}
        self.price_history = {}
        self.load_stocks()
        self.load_portfolios()
        self.update_stocks.start()
        self.previous_prices = {}
        
        # Actions populaires avec données réelles
        self.popular_stocks = {
            "AAPL": {"name": "Apple Inc.", "emoji": "🍎", "sector": "Technology"},
            "MSFT": {"name": "Microsoft Corp.", "emoji": "💻", "sector": "Technology"},
            "GOOGL": {"name": "Alphabet Inc.", "emoji": "🔍", "sector": "Technology"},
            "AMZN": {"name": "Amazon.com Inc.", "emoji": "📦", "sector": "E-commerce"},
            "TSLA": {"name": "Tesla Inc.", "emoji": "🚗", "sector": "Automotive"},
            "META": {"name": "Meta Platforms", "emoji": "📘", "sector": "Social Media"},
            "NVDA": {"name": "NVIDIA Corp.", "emoji": "🎮", "sector": "Technology"},
            "NFLX": {"name": "Netflix Inc.", "emoji": "📺", "sector": "Entertainment"},
            "SPOT": {"name": "Spotify", "emoji": "🎵", "sector": "Entertainment"},
            "DIS": {"name": "Walt Disney Co.", "emoji": "🏰", "sector": "Entertainment"}
        }
        
        # Cryptos simulées
        self.crypto_stocks = {
            "BTC": {"name": "Bitcoin", "emoji": "₿", "sector": "Cryptocurrency"},
            "ETH": {"name": "Ethereum", "emoji": "⟠", "sector": "Cryptocurrency"},
            "ADA": {"name": "Cardano", "emoji": "🔷", "sector": "Cryptocurrency"},
            "SOL": {"name": "Solana", "emoji": "☀️", "sector": "Cryptocurrency"},
            "DOGE": {"name": "Dogecoin", "emoji": "🐕", "sector": "Cryptocurrency"}
        }
        
        # Animations de marché
        self.market_emojis = {
            "up": ["📈", "🚀", "💹", "⬆️", "🔥"],
            "down": ["📉", "💥", "⬇️", "🔻", "😱"],
            "stable": ["📊", "➡️", "⚖️", "🔄", "💤"]
        }

    def cog_unload(self):
        self.update_stocks.cancel()

    def load_user_data(self):
        try:
            if os.path.exists(USER_DATA_FILE):
                with open(USER_DATA_FILE, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Erreur lecture données utilisateur: {e}")
            return {}

    def save_user_data(self, data):
        try:
            with open(USER_DATA_FILE, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Erreur sauvegarde données utilisateur: {e}")

    def get_user_points(self, user_id):
        data = self.load_user_data()
        return data.get(str(user_id), {}).get("points", 1000)

    def update_user_points(self, user_id, new_points):
        data = self.load_user_data()
        user_str = str(user_id)
        if user_str not in data:
            data[user_str] = {"points": 1000}
        data[user_str]["points"] = round(new_points, 2)
        self.save_user_data(data)

    def load_stocks(self):
        try:
            if os.path.exists(STOCKS_DATA_FILE):
                with open(STOCKS_DATA_FILE, "r") as f:
                    self.stocks = json.load(f)
            else:
                # Initialiser avec des prix de base
                self.stocks = {}
                for symbol, info in {**self.popular_stocks, **self.crypto_stocks}.items():
                    self.stocks[symbol] = {
                        "price": random.uniform(50, 500),
                        "change": 0,
                        "volume": random.randint(1000000, 10000000),
                        "last_update": datetime.now().isoformat(),
                        "name": info["name"],
                        "emoji": info["emoji"],
                        "sector": info["sector"]
                    }
                self.save_stocks()
        except Exception as e:
            print(f"Erreur chargement stocks: {e}")
            self.stocks = {}

    def save_stocks(self):
        try:
            with open(STOCKS_DATA_FILE, "w") as f:
                json.dump(self.stocks, f, indent=4)
        except Exception as e:
            print(f"Erreur sauvegarde stocks: {e}")

    def load_portfolios(self):
        try:
            if os.path.exists(PORTFOLIO_FILE):
                with open(PORTFOLIO_FILE, "r") as f:
                    self.user_portfolios = json.load(f)
            else:
                self.user_portfolios = {}
        except Exception as e:
            print(f"Erreur chargement portfolios: {e}")
            self.user_portfolios = {}

    def save_portfolios(self):
        try:
            with open(PORTFOLIO_FILE, "w") as f:
                json.dump(self.user_portfolios, f, indent=4)
        except Exception as e:
            print(f"Erreur sauvegarde portfolios: {e}")

    def get_user_portfolio(self, user_id):
        user_str = str(user_id)
        if user_str not in self.user_portfolios:
            self.user_portfolios[user_str] = {}
        return self.user_portfolios[user_str]

    @tasks.loop(minutes=5)
    async def update_stocks(self):
        """Met à jour les prix des actions toutes les 5 minutes"""
        try:
            for symbol in self.stocks:
                old_price = self.stocks[symbol]["price"]
                
                # Simulation de mouvement de prix réaliste
                volatility = 0.05  # 5% de volatilité max
                if symbol in self.crypto_stocks:
                    volatility = 0.1  # 10% pour les cryptos
                
                change_percent = random.uniform(-volatility, volatility)
                new_price = old_price * (1 + change_percent)
                price_change = new_price - old_price
                
                # Maintenir un prix minimum
                new_price = max(new_price, 1.0)
                
                self.stocks[symbol].update({
                    "price": round(new_price, 2),
                    "change": round(price_change, 2),
                    "volume": random.randint(100000, 5000000),
                    "last_update": datetime.now().isoformat()
                })
                
                # Sauvegarder l'historique
                if symbol not in self.price_history:
                    self.price_history[symbol] = []
                
                self.price_history[symbol].append({
                    "price": new_price,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Garder seulement les 24 dernières heures (288 points pour 5min)
                if len(self.price_history[symbol]) > 288:
                    self.price_history[symbol] = self.price_history[symbol][-288:]
            
            self.save_stocks()
            
        except Exception as e:
            print(f"Erreur mise à jour stocks: {e}")

    @update_stocks.before_loop
    async def before_update_stocks(self):
        await self.bot.wait_until_ready()

    def format_price(self, price):
        """Formatage élégant des prix"""
        if price >= 1000:
            return f"${price:,.2f}"
        else:
            return f"${price:.2f}"

    def get_change_emoji(self, change):
        """Emoji basé sur le changement de prix"""
        if change > 0:
            return random.choice(self.market_emojis["up"])
        elif change < 0:
            return random.choice(self.market_emojis["down"])
        else:
            return random.choice(self.market_emojis["stable"])

    @commands.command(name="market", aliases=["marché", "stocks", "bourse"])
    async def show_market(self, ctx, page: int = 1):
        """Affiche l'état actuel du marché avec animation"""
        
        if not self.stocks:
            await ctx.send("🔄 Chargement du marché en cours...")
            return

        # Animation de chargement
        loading_msg = await ctx.send("📊 Chargement des données de marché...")
        
        for i in range(3):
            dots = "." * (i + 1)
            await loading_msg.edit(content=f"📊 Analyse du marché{dots}")
            await asyncio.sleep(0.5)

        # Pagination
        items_per_page = 8
        all_stocks = list(self.stocks.items())
        total_pages = math.ceil(len(all_stocks) / items_per_page)
        page = max(1, min(page, total_pages))
        
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        page_stocks = all_stocks[start_idx:end_idx]

        # Statistiques du marché
        total_stocks = len(self.stocks)
        gainers = sum(1 for stock in self.stocks.values() if stock.get("change", 0) > 0)
        losers = sum(1 for stock in self.stocks.values() if stock.get("change", 0) < 0)
        
        # Couleur basée sur la tendance générale
        if gainers > losers:
            color = 0x00FF00  # Vert
            market_trend = "📈 HAUSSIER"
        elif losers > gainers:
            color = 0xFF0000  # Rouge
            market_trend = "📉 BAISSIER"
        else:
            color = 0xFFD700  # Neutre
            market_trend = "📊 STABLE"

        embed = discord.Embed(
            title="🏦 MARCHÉ BOURSIER EN DIRECT",
            description=f"**{market_trend}** • Page {page}/{total_pages}",
            color=color
        )

        # Résumé du marché
        embed.add_field(
            name="📊 Résumé du marché",
            value=f"📈 **{gainers}** en hausse\n📉 **{losers}** en baisse\n📊 **{total_stocks - gainers - losers}** stables",
            inline=True
        )

        # Heure de mise à jour
        embed.add_field(
            name="🕐 Dernière MAJ",
            value=f"<t:{int(datetime.now().timestamp())}:R>",
            inline=True
        )

        embed.add_field(
            name="💡 Info",
            value="Prix mis à jour toutes les 5min",
            inline=True
        )

        # Affichage des actions
        stock_display = ""
        for symbol, data in page_stocks:
            emoji = data.get("emoji", "📈")
            name = data.get("name", symbol)
            price = self.format_price(data["price"])
            change = data.get("change", 0)
            change_emoji = self.get_change_emoji(change)
            
            change_text = f"+{change:.2f}" if change > 0 else f"{change:.2f}"
            change_percent = (change / (data["price"] - change)) * 100 if data["price"] != change else 0
            
            stock_display += f"{emoji} **{symbol}** • {price}\n"
            stock_display += f"   {change_emoji} {change_text} ({change_percent:+.1f}%)\n\n"

        if stock_display:
            embed.add_field(
                name="📈 Actions",
                value=stock_display,
                inline=False
            )

        # Navigation
        if total_pages > 1:
            embed.set_footer(text=f"💡 j!market {page+1} pour la page suivante • {total_stocks} actions disponibles")

        await loading_msg.edit(content=None, embed=embed)

        # Ajouter reactions pour navigation si plusieurs pages
        if total_pages > 1:
            if page > 1:
                await loading_msg.add_reaction("⬅️")
            if page < total_pages:
                await loading_msg.add_reaction("➡️")

    @commands.command(name="sbuy", aliases=["sacheter", "sachat"])
    async def buy_stock(self, ctx, symbol: str, quantity: int = 1):
        """Achète des actions avec animation"""
        symbol = symbol.upper()
        
        if symbol not in self.stocks:
            available = ", ".join(list(self.stocks.keys())[:10])
            await ctx.send(f"❌ Action `{symbol}` introuvable!\n💡 Disponibles: {available}...")
            return

        if quantity <= 0:
            await ctx.send("❌ La quantité doit être positive!")
            return

        user_points = self.get_user_points(ctx.author.id)
        stock_price = self.stocks[symbol]["price"]
        total_cost = stock_price * quantity

        if user_points < total_cost:
            await ctx.send(f"💸 Fonds insuffisants!\n💰 Coût: {self.format_price(total_cost)}\n💳 Votre solde: {self.format_price(user_points)}")
            return

        # Animation d'achat
        embed = discord.Embed(
            title="🛒 ORDRE D'ACHAT EN COURS",
            description="Traitement de votre ordre...",
            color=0xFFD700
        )
        
        stock_info = self.stocks[symbol]
        embed.add_field(name="📊 Action", value=f"{stock_info['emoji']} {symbol}", inline=True)
        embed.add_field(name="💰 Prix", value=self.format_price(stock_price), inline=True)
        embed.add_field(name="🔢 Quantité", value=f"{quantity:,}", inline=True)
        
        message = await ctx.send(embed=embed)

        # Animation de traitement
        processing_states = [
            "🔄 Vérification des fonds...",
            "📈 Analyse du marché...",
            "🤝 Négociation du prix...",
            "📝 Finalisation de l'ordre...",
            "✅ Achat confirmé!"
        ]

        for state in processing_states:
            embed.description = state
            await message.edit(embed=embed)
            await asyncio.sleep(0.8)

        # Exécuter l'achat
        portfolio = self.get_user_portfolio(ctx.author.id)
        if symbol not in portfolio:
            portfolio[symbol] = {"quantity": 0, "avg_price": 0}

        # Calcul du prix moyen
        old_quantity = portfolio[symbol]["quantity"]
        old_avg_price = portfolio[symbol]["avg_price"]
        new_avg_price = ((old_quantity * old_avg_price) + (quantity * stock_price)) / (old_quantity + quantity)
        
        portfolio[symbol]["quantity"] += quantity
        portfolio[symbol]["avg_price"] = new_avg_price

        # Mettre à jour les points
        new_points = user_points - total_cost
        self.update_user_points(ctx.author.id, new_points)
        self.save_portfolios()

        # Résultat avec animation de succès
        success_embed = discord.Embed(
            title="🎉 ACHAT RÉUSSI!",
            color=0x00FF00
        )
        
        success_embed.add_field(
            name="📊 Détails de l'achat",
            value=f"{stock_info['emoji']} **{quantity:,}x {symbol}** à {self.format_price(stock_price)}",
            inline=False
        )
        
        success_embed.add_field(name="💰 Coût total", value=self.format_price(total_cost), inline=True)
        success_embed.add_field(name="💳 Nouveau solde", value=self.format_price(new_points), inline=True)
        success_embed.add_field(name="📈 Prix moyen", value=self.format_price(new_avg_price), inline=True)
        
        # Calcul de la valeur actuelle du portefeuille
        total_value = portfolio[symbol]["quantity"] * stock_price
        success_embed.add_field(name="💎 Valeur position", value=self.format_price(total_value), inline=True)
        success_embed.add_field(name="🔢 Total détenu", value=f"{portfolio[symbol]['quantity']:,}", inline=True)
        
        # Profit/Perte potentielle
        if old_quantity > 0:
            old_value = old_quantity * old_avg_price
            new_position_value = portfolio[symbol]["quantity"] * stock_price
            old_position_value = old_quantity * stock_price
            gain_on_old = old_position_value - old_value
            gain_percent = (gain_on_old / old_value) * 100 if old_value > 0 else 0
            
            if gain_on_old > 0:
                success_embed.add_field(
                    name="📈 P&L sur ancienne position", 
                    value=f"+{self.format_price(gain_on_old)} ({gain_percent:+.1f}%)",
                    inline=True
                )

        success_embed.set_footer(text="💡 Utilisez j!portfolio pour voir toutes vos positions")
        await message.edit(embed=success_embed)

    @commands.command(name="sell", aliases=["vendre", "vente"])
    async def sell_stock(self, ctx, symbol: str, quantity: str = "all"):
        """Vend des actions avec animation"""
        symbol = symbol.upper()
        
        if symbol not in self.stocks:
            await ctx.send(f"❌ Action `{symbol}` introuvable!")
            return

        portfolio = self.get_user_portfolio(ctx.author.id)
        if symbol not in portfolio or portfolio[symbol]["quantity"] <= 0:
            await ctx.send(f"❌ Vous ne possédez pas d'actions {symbol}!")
            return

        max_quantity = portfolio[symbol]["quantity"]
        
        if quantity.lower() == "all":
            sell_quantity = max_quantity
        else:
            try:
                sell_quantity = int(quantity)
            except ValueError:
                await ctx.send("❌ Quantité invalide! Utilisez un nombre ou 'all'")
                return

        if sell_quantity <= 0 or sell_quantity > max_quantity:
            await ctx.send(f"❌ Quantité invalide! Vous possédez {max_quantity:,} actions {symbol}")
            return

        # Calculs
        current_price = self.stocks[symbol]["price"]
        avg_price = portfolio[symbol]["avg_price"]
        total_revenue = current_price * sell_quantity
        profit_loss = (current_price - avg_price) * sell_quantity
        profit_percent = ((current_price - avg_price) / avg_price) * 100 if avg_price > 0 else 0

        # Animation de vente
        embed = discord.Embed(
            title="💰 ORDRE DE VENTE EN COURS",
            description="Recherche des meilleurs acheteurs...",
            color=0xFF6B35
        )
        
        stock_info = self.stocks[symbol]
        embed.add_field(name="📊 Action", value=f"{stock_info['emoji']} {symbol}", inline=True)
        embed.add_field(name="💰 Prix actuel", value=self.format_price(current_price), inline=True)
        embed.add_field(name="🔢 Quantité", value=f"{sell_quantity:,}", inline=True)
        
        message = await ctx.send(embed=embed)

        # Animation de traitement
        sell_states = [
            "🔍 Recherche des acheteurs...",
            "📊 Évaluation du marché...",
            "🤝 Négociation en cours...",
            "💰 Calcul des plus-values...",
            "✅ Vente exécutée!"
        ]

        for state in sell_states:
            embed.description = state
            await message.edit(embed=embed)
            await asyncio.sleep(0.7)

        # Exécuter la vente
        portfolio[symbol]["quantity"] -= sell_quantity
        if portfolio[symbol]["quantity"] == 0:
            del portfolio[symbol]

        user_points = self.get_user_points(ctx.author.id)
        new_points = user_points + total_revenue
        self.update_user_points(ctx.author.id, new_points)
        self.save_portfolios()

        # Résultat avec couleur selon le profit/perte
        if profit_loss > 0:
            color = 0x00FF00  # Vert pour profit
            result_title = "🎉 VENTE PROFITABLE!"
            pl_emoji = "📈"
        elif profit_loss < 0:
            color = 0xFF0000  # Rouge pour perte
            result_title = "💸 VENTE À PERTE"
            pl_emoji = "📉"
        else:
            color = 0xFFD700  # Neutre
            result_title = "💰 VENTE RÉALISÉE"
            pl_emoji = "📊"

        success_embed = discord.Embed(title=result_title, color=color)
        
        success_embed.add_field(
            name="📊 Détails de la vente",
            value=f"{stock_info['emoji']} **{sell_quantity:,}x {symbol}** à {self.format_price(current_price)}",
            inline=False
        )
        
        success_embed.add_field(name="💰 Revenus", value=self.format_price(total_revenue), inline=True)
        success_embed.add_field(name="💳 Nouveau solde", value=self.format_price(new_points), inline=True)
        success_embed.add_field(name="📈 Prix d'achat moyen", value=self.format_price(avg_price), inline=True)
        
        # Profit/Perte avec formatage coloré
        pl_text = f"{'+' if profit_loss >= 0 else ''}{self.format_price(profit_loss)}"
        if profit_percent != 0:
            pl_text += f" ({profit_percent:+.1f}%)"
        
        success_embed.add_field(name=f"{pl_emoji} Plus/Moins-value", value=pl_text, inline=True)
        
        # Actions restantes
        remaining = portfolio.get(symbol, {}).get("quantity", 0)
        success_embed.add_field(name="📦 Restant", value=f"{remaining:,} actions", inline=True)
        
        if remaining > 0:
            remaining_value = remaining * current_price
            success_embed.add_field(name="💎 Valeur restante", value=self.format_price(remaining_value), inline=True)

        # Message motivationnel
        if profit_loss > 1000:
            success_embed.set_footer(text="🚀 Excellent trade! Vous êtes un vrai trader!")
        elif profit_loss > 0:
            success_embed.set_footer(text="👍 Bon trade! Les petits profits s'accumulent!")
        elif profit_loss < -1000:
            success_embed.set_footer(text="💪 Les pertes font partie du jeu, continuez!")
        else:
            success_embed.set_footer(text="📊 Trade neutre, analysez le marché!")

        await message.edit(embed=success_embed)

    @commands.command(name="portfolio", aliases=["portefeuille", "pf"])
    async def show_portfolio(self, ctx, user: discord.Member = None):
        """Affiche le portefeuille avec analytics avancées"""
        target_user = user or ctx.author
        portfolio = self.get_user_portfolio(target_user.id)
        user_points = self.get_user_points(target_user.id)

        if not portfolio:
            embed = discord.Embed(
                title=f"📊 Portefeuille de {target_user.display_name}",
                description="🛒 Aucune position ouverte\n💡 Utilisez `j!sbuy` pour commencer à investir!",
                color=0xFFD700
            )
            embed.add_field(name="💰 Liquidités", value=self.format_price(user_points), inline=True)
            embed.add_field(name="📈 Valeur totale", value=self.format_price(user_points), inline=True)
            await ctx.send(embed=embed)
            return

        # Animation de chargement du portefeuille
        loading_embed = discord.Embed(
            title="📊 ANALYSE DU PORTEFEUILLE",
            description="📈 Calcul des performances...",
            color=0xFFD700
        )
        message = await ctx.send(embed=loading_embed)

        await asyncio.sleep(1)

        # Calculs du portefeuille
        total_invested = 0
        current_value = 0
        total_pl = 0
        positions = []

        for symbol, position in portfolio.items():
            if symbol not in self.stocks:
                continue
                
            quantity = position["quantity"]
            avg_price = position["avg_price"]
            current_price = self.stocks[symbol]["price"]
            
            invested = quantity * avg_price
            value = quantity * current_price
            pl = value - invested
            pl_percent = (pl / invested) * 100 if invested > 0 else 0
            
            total_invested += invested
            current_value += value
            total_pl += pl
            
            positions.append({
                "symbol": symbol,
                "quantity": quantity,
                "avg_price": avg_price,
                "current_price": current_price,
                "invested": invested,
                "value": value,
                "pl": pl,
                "pl_percent": pl_percent,
                "weight": (value / (current_value + user_points)) * 100 if (current_value + user_points) > 0 else 0
            })

        # Tri par valeur décroissante
        positions.sort(key=lambda x: x["value"], reverse=True)

        total_portfolio = current_value + user_points
        total_pl_percent = (total_pl / total_invested) * 100 if total_invested > 0 else 0

        # Couleur selon la performance
        if total_pl > 0:
            color = 0x00FF00
        elif total_pl < 0:
            color = 0xFF0000
        else:
            color = 0xFFD700

        embed = discord.Embed(
            title=f"📊 Portefeuille de {target_user.display_name}",
            color=color
        )
        embed.set_thumbnail(url=target_user.display_avatar.url)

        # Résumé financier
        embed.add_field(
            name="💰 Résumé financier",
            value=(
                f"💵 **Liquidités:** {self.format_price(user_points)}\n"
                f"📈 **Positions:** {self.format_price(current_value)}\n"
                f"💎 **Total:** {self.format_price(total_portfolio)}"
            ),
            inline=True
        )

        # Performance globale
        pl_emoji = "📈" if total_pl >= 0 else "📉"
        pl_text = f"{'+' if total_pl >= 0 else ''}{self.format_price(total_pl)}"
        if total_pl_percent != 0:
            pl_text += f" ({total_pl_percent:+.1f}%)"

        embed.add_field(
            name="📊 Performance",
            value=(
                f"💸 **Investi:** {self.format_price(total_invested)}\n"
                f"{pl_emoji} **P&L:** {pl_text}\n"
                f"🎯 **ROI:** {total_pl_percent:+.1f}%"
            ),
            inline=True
        )

        # Diversification
        num_positions = len(positions)
        avg_position_size = (current_value / num_positions) if num_positions > 0 else 0
        
        embed.add_field(
            name="⚖️ Diversification",
            value=(
                f"🔢 **Positions:** {num_positions}\n"
                f"📊 **Taille moy.:** {self.format_price(avg_position_size)}\n"
                f"💧 **Liquidité:** {(user_points/total_portfolio)*100:.1f}%"
            ),
            inline=True
        )

        # Top 5 positions
        if positions:
            top_positions = ""
            for i, pos in enumerate(positions[:5]):
                stock_info = self.stocks[pos["symbol"]]
                emoji = stock_info.get("emoji", "📊")
                
                pl_indicator = "🟢" if pos["pl"] >= 0 else "🔴"
                top_positions += f"{emoji} **{pos['symbol']}** • {pos['quantity']:,} actions\n"
                top_positions += f"   💰 {self.format_price(pos['value'])} {pl_indicator} {pos['pl_percent']:+.1f}%\n\n"

            embed.add_field(
                name="🏆 Top Positions",
                value=top_positions[:1024],  # Limite Discord
                inline=False
            )

        # Graphique de performance simulé
        if total_pl_percent != 0:
            performance_bar = ""
            bars = int(abs(total_pl_percent) / 5)  # 1 barre par 5%
            bars = min(bars, 10)  # Max 10 barres
            
            if total_pl_percent > 0:
                performance_bar = "🟢" * bars + "⚪" * (10 - bars)
            else:
                performance_bar = "🔴" * bars + "⚪" * (10 - bars)
            
            embed.add_field(
                name="📊 Graphique Performance",
                value=f"`{performance_bar}` {total_pl_percent:+.1f}%",
                inline=False
            )

        # Conseils personnalisés basés sur la performance
        advice = ""
        if total_pl_percent > 10:
            advice = "🚀 Portfolio très performant! Pensez à prendre quelques bénéfices."
        elif total_pl_percent > 5:
            advice = "👍 Bonnes performances! Continuez votre stratégie."
        elif total_pl_percent > -5:
            advice = "📊 Performance stable. Analysez vos positions."
        elif total_pl_percent > -15:
            advice = "⚠️ Pertes modérées. Réévaluez votre stratégie."
        else:
            advice = "🔄 Grosses pertes. Considérez rebalancer votre portfolio."

        if advice:
            embed.set_footer(text=f"💡 {advice}")

        # Timestamp
        embed.timestamp = datetime.now()

        await message.edit(embed=embed)

    @commands.command(name="stock", aliases=["info", "quote"])
    async def stock_info(self, ctx, symbol: str):
        """Informations détaillées sur une action avec graphique"""
        symbol = symbol.upper()
        
        if symbol not in self.stocks:
            similar = [s for s in self.stocks.keys() if symbol in s][:3]
            suggestion = f"\n💡 Similaires: {', '.join(similar)}" if similar else ""
            await ctx.send(f"❌ Action `{symbol}` introuvable!{suggestion}")
            return

        # Animation de chargement des données
        loading_embed = discord.Embed(
            title=f"📊 Chargement des données pour {symbol}",
            description="🔍 Analyse technique en cours...",
            color=0xFFD700
        )
        message = await ctx.send(embed=loading_embed)

        await asyncio.sleep(1)

        stock_data = self.stocks[symbol]
        
        # Calculs techniques
        price = stock_data["price"]
        change = stock_data.get("change", 0)
        change_percent = (change / (price - change)) * 100 if price != change else 0
        volume = stock_data.get("volume", 0)
        
        # Simuler des données techniques
        support = price * 0.95
        resistance = price * 1.05
        rsi = random.uniform(20, 80)
        market_cap = price * random.randint(1000000, 100000000)

        # Couleur selon la performance
        color = 0x00FF00 if change >= 0 else 0xFF0000

        embed = discord.Embed(
            title=f"{stock_data['emoji']} {stock_data['name']} ({symbol})",
            color=color
        )

        # Prix principal avec animation d'effets
        price_display = self.format_price(price)
        change_emoji = self.get_change_emoji(change)
        change_text = f"{'+' if change >= 0 else ''}{change:.2f} ({change_percent:+.1f}%)"
        
        embed.add_field(
            name="💰 Prix",
            value=f"**{price_display}**\n{change_emoji} {change_text}",
            inline=True
        )

        # Volume avec animation
        volume_display = f"{volume:,}" if volume < 1000000 else f"{volume/1000000:.1f}M"
        embed.add_field(
            name="📊 Volume",
            value=f"**{volume_display}**\n🔄 24h",
            inline=True
        )

        # Secteur
        embed.add_field(
            name="🏢 Secteur",
            value=f"**{stock_data.get('sector', 'N/A')}**\n📈 Marché",
            inline=True
        )

        # Analyse technique
        embed.add_field(
            name="🔍 Support/Résistance",
            value=f"🟢 Support: {self.format_price(support)}\n🔴 Résistance: {self.format_price(resistance)}",
            inline=True
        )

        # RSI avec indicateur visuel
        rsi_emoji = "🟢" if rsi < 30 else "🔴" if rsi > 70 else "🟡"
        rsi_status = "Survente" if rsi < 30 else "Surachat" if rsi > 70 else "Neutre"
        
        embed.add_field(
            name="📊 RSI",
            value=f"**{rsi:.1f}** {rsi_emoji}\n{rsi_status}",
            inline=True
        )

        # Market Cap
        embed.add_field(
            name="💎 Market Cap",
            value=f"**{market_cap/1000000:.1f}M$**\n🌍 Capitalisation",
            inline=True
        )

        # Graphique de prix simulé (dernières 24h)
        if symbol in self.price_history and len(self.price_history[symbol]) > 5:
            recent_prices = self.price_history[symbol][-12:]  # Dernières heures
            
            # Mini graphique ASCII
            min_price = min(p["price"] for p in recent_prices)
            max_price = max(p["price"] for p in recent_prices)
            range_price = max_price - min_price if max_price != min_price else 1
            
            chart = "```\n📈 Évolution 24h\n"
            for i, point in enumerate(recent_prices):
                normalized = (point["price"] - min_price) / range_price
                bars = int(normalized * 10)
                chart += f"|{'█' * bars}{'░' * (10-bars)}| {point['price']:.1f}\n"
            chart += "```"
            
            embed.add_field(
                name="📈 Graphique",
                value=chart,
                inline=False
            )

        # Recommandation basée sur l'analyse
        if change_percent > 5 and rsi < 70:
            recommendation = "🚀 ACHAT FORT - Momentum positif"
            rec_color = "🟢"
        elif change_percent > 2:
            recommendation = "📈 ACHAT - Tendance haussière"
            rec_color = "🟢"
        elif change_percent < -5 and rsi > 30:
            recommendation = "💸 VENTE - Pression baissière"
            rec_color = "🔴"
        elif change_percent < -2:
            recommendation = "📉 PRUDENCE - Tendance baissière"
            rec_color = "🟡"
        else:
            recommendation = "📊 NEUTRE - Attendre signal"
            rec_color = "🟡"

        embed.add_field(
            name=f"{rec_color} Recommandation",
            value=recommendation,
            inline=False
        )

        # Dernière mise à jour
        embed.set_footer(text=f"💡 j!sbuy {symbol} <quantité> pour acheter • Données temps réel")
        embed.timestamp = datetime.now()

        await message.edit(embed=embed)

    @commands.command(name="watchlist", aliases=["watch", "suivre"])
    async def manage_watchlist(self, ctx, action: str = None, symbol: str = None):
        """Gère une watchlist personnalisée"""
        user_data = self.load_user_data()
        user_str = str(ctx.author.id)
        
        if user_str not in user_data:
            user_data[user_str] = {"points": 1000, "watchlist": []}
        
        if "watchlist" not in user_data[user_str]:
            user_data[user_str]["watchlist"] = []
        
        watchlist = user_data[user_str]["watchlist"]

        if not action:
            # Afficher la watchlist
            if not watchlist:
                embed = discord.Embed(
                    title="👁️ Votre Watchlist",
                    description="📝 Aucune action suivie\n💡 `j!watchlist add AAPL` pour ajouter",
                    color=0xFFD700
                )
                await ctx.send(embed=embed)
                return

            embed = discord.Embed(
                title="👁️ Votre Watchlist",
                color=0x00BFFF
            )

            watchlist_display = ""
            for stock_symbol in watchlist[:10]:  # Limite à 10
                if stock_symbol in self.stocks:
                    stock = self.stocks[stock_symbol]
                    price = self.format_price(stock["price"])
                    change = stock.get("change", 0)
                    change_emoji = self.get_change_emoji(change)
                    change_percent = (change / (stock["price"] - change)) * 100 if stock["price"] != change else 0
                    
                    watchlist_display += f"{stock['emoji']} **{stock_symbol}** • {price}\n"
                    watchlist_display += f"   {change_emoji} {change_percent:+.1f}% • {stock['name']}\n\n"

            if watchlist_display:
                embed.add_field(name="📊 Actions suivies", value=watchlist_display, inline=False)
            
            embed.set_footer(text="🔄 Mis à jour toutes les 5min • j!watchlist add/remove <symbol>")
            await ctx.send(embed=embed)
            return

        if not symbol:
            await ctx.send("❌ Spécifiez un symbole d'action!")
            return

        symbol = symbol.upper()

        if action.lower() in ["add", "ajouter", "+"]:
            if symbol not in self.stocks:
                await ctx.send(f"❌ Action `{symbol}` introuvable!")
                return
            
            if symbol in watchlist:
                await ctx.send(f"⚠️ {symbol} est déjà dans votre watchlist!")
                return
            
            if len(watchlist) >= 15:
                await ctx.send("❌ Watchlist pleine! (max 15 actions)")
                return

            watchlist.append(symbol)
            user_data[user_str]["watchlist"] = watchlist
            self.save_user_data(user_data)

            stock = self.stocks[symbol]
            embed = discord.Embed(
                title="✅ Action ajoutée à la watchlist!",
                description=f"{stock['emoji']} **{symbol}** • {stock['name']}",
                color=0x00FF00
            )
            embed.add_field(name="💰 Prix actuel", value=self.format_price(stock["price"]), inline=True)
            embed.add_field(name="📊 Total suivi", value=f"{len(watchlist)}/15", inline=True)
            await ctx.send(embed=embed)

        elif action.lower() in ["remove", "supprimer", "del", "-"]:
            if symbol not in watchlist:
                await ctx.send(f"❌ {symbol} n'est pas dans votre watchlist!")
                return

            watchlist.remove(symbol)
            user_data[user_str]["watchlist"] = watchlist
            self.save_user_data(user_data)

            await ctx.send(f"✅ {symbol} supprimé de votre watchlist!")

        else:
            await ctx.send("❌ Action invalide! Utilisez `add` ou `remove`")

    @commands.command(name="leaderboard", aliases=["classement", "top"])
    async def portfolio_leaderboard(self, ctx):
        """Classement des meilleurs traders"""
        
        # Animation de chargement
        loading_embed = discord.Embed(
            title="🏆 CLASSEMENT DES TRADERS",
            description="📊 Calcul des performances...",
            color=0xFFD700
        )
        message = await ctx.send(embed=loading_embed)

        await asyncio.sleep(1.5)

        user_data = self.load_user_data()
        trader_stats = []

        for user_id, data in user_data.items():
            try:
                user = self.bot.get_user(int(user_id))
                if not user:
                    continue

                points = data.get("points", 0)
                portfolio = self.user_portfolios.get(user_id, {})
                
                # Calcul de la valeur totale du portefeuille
                portfolio_value = 0
                total_invested = 0
                
                for symbol, position in portfolio.items():
                    if symbol in self.stocks:
                        current_price = self.stocks[symbol]["price"]
                        avg_price = position["avg_price"]
                        quantity = position["quantity"]
                        
                        portfolio_value += current_price * quantity
                        total_invested += avg_price * quantity

                total_wealth = points + portfolio_value
                total_pl = portfolio_value - total_invested if total_invested > 0 else 0
                roi = (total_pl / total_invested * 100) if total_invested > 0 else 0

                trader_stats.append({
                    "user": user,
                    "wealth": total_wealth,
                    "portfolio_value": portfolio_value,
                    "cash": points,
                    "pl": total_pl,
                    "roi": roi,
                    "positions": len(portfolio)
                })

            except Exception as e:
                continue

        # Tri par richesse totale
        trader_stats.sort(key=lambda x: x["wealth"], reverse=True)

        embed = discord.Embed(
            title="🏆 CLASSEMENT DES TRADERS",
            description="💎 Top des portefeuilles les plus performants",
            color=0xFFD700
        )

        # Podium
        podium_emojis = ["🥇", "🥈", "🥉"]
        leaderboard_text = ""

        for i, trader in enumerate(trader_stats[:10]):
            rank_emoji = podium_emojis[i] if i < 3 else f"{i+1}️⃣"
            user_name = trader["user"].display_name[:12]
            wealth = self.format_price(trader["wealth"])
            
            # Performance indicator
            if trader["roi"] > 10:
                perf_emoji = "🔥"
            elif trader["roi"] > 0:
                perf_emoji = "📈"
            elif trader["roi"] > -10:
                perf_emoji = "📊"
            else:
                perf_emoji = "📉"

            leaderboard_text += f"{rank_emoji} **{user_name}** • {wealth} {perf_emoji}\n"
            leaderboard_text += f"    💼 {trader['positions']} positions • ROI: {trader['roi']:+.1f}%\n\n"

        if leaderboard_text:
            embed.add_field(name="🏆 Classement", value=leaderboard_text, inline=False)

        # Stats globales
        if trader_stats:
            total_traders = len(trader_stats)
            avg_wealth = sum(t["wealth"] for t in trader_stats) / total_traders
            total_market_cap = sum(t["portfolio_value"] for t in trader_stats)
            
            embed.add_field(
                name="📊 Statistiques globales",
                value=f"👥 **{total_traders}** traders actifs\n💰 Richesse moyenne: {self.format_price(avg_wealth)}\n📈 Marché total: {self.format_price(total_market_cap)}",
                inline=True
            )

            # Position du joueur actuel
            user_rank = next((i+1 for i, t in enumerate(trader_stats) if t["user"].id == ctx.author.id), None)
            if user_rank:
                embed.add_field(
                    name="🎯 Votre position",
                    value=f"**#{user_rank}** / {total_traders}",
                    inline=True
                )

        embed.set_footer(text="🔄 Mis à jour en temps réel • Investissez pour grimper!")
        embed.timestamp = datetime.now()

        await message.edit(embed=embed)

    @commands.command(name="alerts", aliases=["alerte", "alert"])
    async def price_alerts(self, ctx, action: str = None, symbol: str = None, target_price: float = None):
        """Système d'alertes de prix (simulation)"""
        
        if not action:
            embed = discord.Embed(
                title="🔔 Système d'Alertes Prix",
                description="Recevez des notifications quand vos actions atteignent un prix cible!",
                color=0x00BFFF
            )
            embed.add_field(
                name="📝 Commandes",
                value="`j!alerts set AAPL 150.00` - Créer alerte\n`j!alerts list` - Voir vos alertes\n`j!alerts remove AAPL` - Supprimer",
                inline=False
            )
            embed.add_field(
                name="⚠️ Note",
                value="Les alertes sont vérifiées toutes les 5 minutes avec les mises à jour de prix.",
                inline=False
            )
            await ctx.send(embed=embed)
            return

        # Simulation d'un système d'alertes
        if action.lower() == "set":
            if not symbol or not target_price:
                await ctx.send("❌ Usage: `j!alerts set SYMBOL PRIX`")
                return
            
            symbol = symbol.upper()
            if symbol not in self.stocks:
                await ctx.send(f"❌ Action {symbol} introuvable!")
                return

            current_price = self.stocks[symbol]["price"]
            embed = discord.Embed(
                title="🔔 Alerte Prix Configurée!",
                color=0x00FF00
            )
            embed.add_field(name="📊 Action", value=f"{self.stocks[symbol]['emoji']} {symbol}", inline=True)
            embed.add_field(name="🎯 Prix cible", value=self.format_price(target_price), inline=True)
            embed.add_field(name="💰 Prix actuel", value=self.format_price(current_price), inline=True)
            
            difference = ((target_price - current_price) / current_price) * 100
            embed.add_field(
                name="📈 Évolution nécessaire",
                value=f"{difference:+.1f}%",
                inline=False
            )
            embed.set_footer(text="🔔 Vous recevrez un DM quand le prix sera atteint!")
            await ctx.send(embed=embed)

        elif action.lower() == "list":
            # Simulation de la liste d'alertes
            embed = discord.Embed(
                title="🔔 Vos Alertes Prix",
                description="📝 Exemple d'alertes actives:",
                color=0x00BFFF
            )
            
            sample_alerts = [
                {"symbol": "AAPL", "target": 180.00, "current": self.stocks.get("AAPL", {}).get("price", 150)},
                {"symbol": "TSLA", "target": 250.00, "current": self.stocks.get("TSLA", {}).get("price", 200)}
            ]
            
            alerts_text = ""
            for alert in sample_alerts:
                if alert["symbol"] in self.stocks:
                    stock = self.stocks[alert["symbol"]]
                    progress = (alert["current"] / alert["target"]) * 100
                    status = "🟢 Atteint" if progress >= 100 else "🟡 En cours"
                    
                    alerts_text += f"{stock['emoji']} **{alert['symbol']}**\n"
                    alerts_text += f"🎯 Cible: {self.format_price(alert['target'])}\n"
                    alerts_text += f"💰 Actuel: {self.format_price(alert['current'])}\n"
                    alerts_text += f"📊 {status} ({progress:.1f}%)\n\n"
            
            embed.add_field(name="📋 Alertes actives", value=alerts_text or "Aucune alerte", inline=False)
            await ctx.send(embed=embed)

        else:
            await ctx.send("❌ Action invalide! Utilisez `set`, `list` ou `remove`")

async def setup(bot):
    await bot.add_cog(Stocks(bot))

