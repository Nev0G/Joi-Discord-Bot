import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timedelta
import asyncio

USER_DATA_FILE = "user_data.json"
SHOP_ITEMS_FILE = "shop_items.json"
PURCHASES_FILE = "user_purchases.json"

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shop_items = self.load_shop_items()
        self.user_purchases = self.load_user_purchases()

    def load_shop_items(self):
        """Charge les articles de la boutique"""
        try:
            if os.path.exists(SHOP_ITEMS_FILE):
                with open(SHOP_ITEMS_FILE, "r", encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Créer le fichier avec les articles par défaut
                default_items = {
                    "items": [
                        {
                            "id": "bombdm",
                            "name": "BombDM",
                            "description": "Envoi un message choisi en DM via le bot",
                            "price": 300,
                            "type": "command",
                            "category": "⚡ Commandes",
                            "emoji": "💣",
                            "uses": 1
                        },
                        {
                            "id": "casino_addict",
                            "name": "Casino Addict",
                            "description": "Accès à un rôle Discord exclusif de maxi bogoss",
                            "price": 10000,
                            "type": "role",
                            "category": "🎭 Rôles",
                            "emoji": "🎰",
                            "role_id": "1259251354967478324"
                        },
                        {
                            "id": "roi_juifs",
                            "name": "Roi des Juifs",
                            "description": "Il ne faut pas avoir peur",
                            "price": 25000,
                            "type": "role",
                            "category": "🎭 Rôles",
                            "emoji": "👑",
                            "role_id": "1286715796520697887"
                        },
                        {
                            "id": "voleur_points",
                            "name": "Voleur de Points",
                            "description": "Vole 10% des points d'un utilisateur au hasard",
                            "price": 10000,
                            "type": "command",
                            "category": "⚡ Commandes",
                            "emoji": "🦹",
                            "uses": 1
                        },
                        {
                            "id": "multiplicateur_x2",
                            "name": "Multiplicateur x2",
                            "description": "Double tes gains de points pendant 12h",
                            "price": 10000,
                            "type": "buff",
                            "category": "💪 Buffs",
                            "emoji": "⚡",
                            "duration": 43200
                        },
                        {
                            "id": "message_fantome",
                            "name": "Message Fantôme",
                            "description": "Envoie un message anonyme dans un salon de ton choix",
                            "price": 750,
                            "type": "command",
                            "category": "⚡ Commandes",
                            "emoji": "👻",
                            "uses": 1
                        },
                        {
                            "id": "vip_premium",
                            "name": "VIP Premium",
                            "description": "Statut VIP avec privilèges exclusifs",
                            "price": 5000,
                            "type": "role",
                            "category": "🎭 Rôles",
                            "emoji": "💎",
                            "role_id": "1380935037901471784"
                        },
                        {
                            "id": "chance_boost",
                            "name": "Boost de Chance",
                            "description": "Augmente tes chances de gagner au casino pendant 12h",
                            "price": 5000,
                            "type": "buff",
                            "category": "💪 Buffs",
                            "emoji": "🍀",
                            "duration": 43200
                        },
                        {
                            "id": "daily_double",
                            "name": "Daily Double",
                            "description": "Double ton prochain bonus quotidien",
                            "price": 1000,
                            "type": "buff",
                            "category": "💪 Buffs",
                            "emoji": "💰",
                            "uses": 1
                        },
                        {
                            "name": "Avatar Changer",
                            "description": "Change l'avatar du bot avec ton image personnalisée (6h)",
                            "price": 20000,
                            "type": "command",
                            "duration": 21600
                        },
                        {
                            "name": "Name Changer", 
                            "description": "Change le nom du bot temporairement (6h)",
                            "price": 10000,
                            "type": "command",
                            "duration": 21600
                        },
                        {
                            "name": "Reset Avatar",
                            "description": "Remet l'avatar du bot par défaut",
                            "price": 10000,
                            "type": "command"
                        },
                        {
                            "name": "Custom Status",
                            "description": "Le bot affiche un statut personnalisé de ton choix pendant 6h",
                            "price": 3500,
                            "type": "command",
                            "duration": 21600
                        },
                        {
                            "name": "Premium Status",
                            "description": "Statut avec activité personnalisée et type au choix (12h)",
                            "price": 6000,
                            "type": "command",
                            "duration": 43200
                        },
                        {
                            "name": "Reset Status",
                            "description": "Remet le statut du bot par défaut",
                            "price": 500,
                            "type": "command"
                        }

                    ]
                }
                self.save_shop_items(default_items)
                return default_items
        except Exception as e:
            print(f"Erreur lors du chargement des articles: {e}")
            return {"items": []}

    def save_shop_items(self, items):
        """Sauvegarde les articles de la boutique"""
        try:
            with open(SHOP_ITEMS_FILE, "w", encoding='utf-8') as f:
                json.dump(items, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des articles: {e}")

    def load_user_purchases(self):
        """Charge les achats des utilisateurs"""
        try:
            if os.path.exists(PURCHASES_FILE):
                with open(PURCHASES_FILE, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Erreur lors du chargement des achats: {e}")
            return {}

    def save_user_purchases(self):
        """Sauvegarde les achats des utilisateurs"""
        try:
            with open(PURCHASES_FILE, "w") as f:
                json.dump(self.user_purchases, f, indent=4)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des achats: {e}")

    def load_user_data(self):
        """Charge les données des utilisateurs (points)"""
        try:
            if os.path.exists(USER_DATA_FILE):
                with open(USER_DATA_FILE, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Erreur lors de la lecture des données: {e}")
            return {}

    def save_user_data(self, data):
        """Sauvegarde les données des utilisateurs"""
        try:
            with open(USER_DATA_FILE, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")

    def get_user_points(self, user_id):
        """Récupère les points d'un utilisateur"""
        data = self.load_user_data()
        return data.get(str(user_id), {}).get("points", 1000)

    def update_user_points(self, user_id, new_points):
        """Met à jour les points d'un utilisateur"""
        data = self.load_user_data()
        user_str = str(user_id)
        if user_str not in data:
            data[user_str] = {"points": 1000}
        data[user_str]["points"] = new_points
        self.save_user_data(data)

    def get_item_by_id(self, item_id):
        """Récupère un article par son ID"""
        for item in self.shop_items["items"]:
            if item["id"].lower() == item_id.lower():
                return item
        return None

    def get_user_purchase(self, user_id, item_id):
        """Récupère l'achat d'un utilisateur pour un article"""
        user_str = str(user_id)
        if user_str not in self.user_purchases:
            return None
        
        for purchase in self.user_purchases[user_str]:
            if purchase["item_id"] == item_id:
                return purchase
        return None

    def add_user_purchase(self, user_id, item):
        """Ajoute un achat pour un utilisateur"""
        user_str = str(user_id)
        if user_str not in self.user_purchases:
            self.user_purchases[user_str] = []
        
        purchase = {
            "item_id": item["id"],
            "item_name": item["name"],
            "purchase_date": datetime.now().isoformat(),
            "price_paid": item["price"],
            "uses_remaining": item.get("uses", 0),
            "expires_at": None
        }
        
        # Pour les buffs temporaires
        if item["type"] == "buff" and "duration" in item:
            expires_at = datetime.now() + timedelta(seconds=item["duration"])
            purchase["expires_at"] = expires_at.isoformat()
        
        self.user_purchases[user_str].append(purchase)
        self.save_user_purchases()

    @commands.command(name="shop", aliases=["boutique"])
    async def show_shop(self, ctx, category: str = None):
        """Affiche la boutique"""
        if not self.shop_items["items"]:
            await ctx.send("❌ La boutique est vide pour le moment !")
            return

        if category is None:
            # Afficher les catégories
            categories = {}
            for item in self.shop_items["items"]:
                cat = item.get("category", "🛍️ Divers")
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(item)

            embed = discord.Embed(
                title="🛒 Boutique Premium",
                description="Dépensez vos points dans notre boutique exclusive !",
                color=0xFF1493
            )

            for cat_name, items in categories.items():
                items_text = ""
                for item in items[:3]:  # Limite à 3 items par catégorie dans l'aperçu
                    items_text += f"{item.get('emoji', '🛍️')} **{item['name']}** - {item['price']:,} pts\n"
                
                if len(items) > 3:
                    items_text += f"... et {len(items) - 3} autres articles"
                
                embed.add_field(name=cat_name, value=items_text, inline=True)

            embed.add_field(
                name="💡 Comment acheter ?",
                value="`j!buy <nom_article>` - Acheter un article\n`j!inventory` - Voir vos achats",
                inline=False
            )
            embed.set_footer(text="Utilisez j!shop <catégorie> pour voir une catégorie spécifique")
        else:
            # Afficher une catégorie spécifique
            filtered_items = []
            for item in self.shop_items["items"]:
                if category.lower() in item.get("category", "").lower():
                    filtered_items.append(item)

            if not filtered_items:
                await ctx.send("❌ Aucun article trouvé dans cette catégorie !")
                return

            embed = discord.Embed(
                title=f"🛒 Boutique - {category.title()}",
                color=0xFF1493
            )

            for item in filtered_items:
                embed.add_field(
                    name=f"{item.get('emoji', '🛍️')} {item['name']} - {item['price']:,} pts",
                    value=f"{item['description']}\nType: {item['type'].title()}",
                    inline=False
                )

        user_points = self.get_user_points(ctx.author.id)
        embed.add_field(name="💰 Votre solde", value=f"{user_points:,} points", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command(name="buy", aliases=["acheter"])
    async def buy_item(self, ctx, *, item_name: str = None):
        """Acheter un article"""
        if item_name is None:
            await ctx.send("❌ Usage: `j!buy <nom_article>`\nVoir `j!shop` pour la liste des articles.")
            return

        # Recherche de l'article
        item = None
        for shop_item in self.shop_items["items"]:
            if shop_item["name"].lower() == item_name.lower() or shop_item["id"].lower() == item_name.lower():
                item = shop_item
                break

        if not item:
            await ctx.send("❌ Article introuvable ! Vérifiez le nom avec `j!shop`.")
            return

        user_points = self.get_user_points(ctx.author.id)
        
        if user_points < item["price"]:
            embed = discord.Embed(
                title="💸 Fonds insuffisants",
                description=f"Il vous manque **{item['price'] - user_points:,}** points pour acheter cet article !",
                color=0xFF0000
            )
            embed.add_field(name="💰 Votre solde", value=f"{user_points:,} points", inline=True)
            embed.add_field(name="💳 Prix", value=f"{item['price']:,} points", inline=True)
            await ctx.send(embed=embed)
            return

        # Vérifications spéciales selon le type
        if item["type"] == "role":
            try:
                role = ctx.guild.get_role(int(item["role_id"]))
                if not role:
                    await ctx.send("❌ Rôle introuvable ! Contactez un administrateur.")
                    return
                
                if role in ctx.author.roles:
                    await ctx.send("❌ Vous possédez déjà ce rôle !")
                    return
            except:
                await ctx.send("❌ Erreur avec le rôle ! Contactez un administrateur.")
                return

        # Confirmation d'achat
        embed = discord.Embed(
            title="🛒 Confirmation d'achat",
            description=f"Êtes-vous sûr de vouloir acheter **{item['name']}** ?",
            color=0xFFD700
        )
        embed.add_field(name="📦 Article", value=item["description"], inline=False)
        embed.add_field(name="💳 Prix", value=f"{item['price']:,} points", inline=True)
        embed.add_field(name="💰 Solde après", value=f"{user_points - item['price']:,} points", inline=True)
        
        message = await ctx.send(embed=embed)
        await message.add_reaction("✅")
        await message.add_reaction("❌")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == message.id

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=30.0, check=check)
            
            if str(reaction.emoji) == "❌":
                await message.edit(embed=discord.Embed(title="❌ Achat annulé", color=0xFF0000))
                return
            
            # Procéder à l'achat
            new_points = user_points - item["price"]
            self.update_user_points(ctx.author.id, new_points)
            
            # Traitement selon le type d'article
            if item["type"] == "role":
                try:
                    role = ctx.guild.get_role(int(item["role_id"]))
                    await ctx.author.add_roles(role)
                    success_msg = f"Rôle **{role.name}** ajouté !"
                except Exception as e:
                    # Rembourser si erreur
                    self.update_user_points(ctx.author.id, user_points)
                    await ctx.send("❌ Erreur lors de l'attribution du rôle ! Achat annulé.")
                    return
            else:
                success_msg = "Article ajouté à votre inventaire !"
            
            # Enregistrer l'achat
            self.add_user_purchase(ctx.author.id, item)
            
            # Message de succès
            embed = discord.Embed(
                title="✅ Achat réussi !",
                description=f"Vous avez acheté **{item['name']}** !",
                color=0x00FF00
            )
            embed.add_field(name="🎉 Résultat", value=success_msg, inline=False)
            embed.add_field(name="💰 Nouveau solde", value=f"{new_points:,} points", inline=False)
            
            if item["type"] == "command":
                embed.add_field(
                    name="ℹ️ Utilisation", 
                    value=f"Utilisez `j!use {item['id']}` pour utiliser cet article",
                    inline=False
                )
            
            await message.edit(embed=embed)

        except asyncio.TimeoutError:
            await message.edit(embed=discord.Embed(title="⏰ Temps écoulé - Achat annulé", color=0xFF0000))

    @commands.command(name="inventory", aliases=["inv", "inventaire"])
    async def show_inventory(self, ctx):
        """Affiche l'inventaire de l'utilisateur"""
        user_str = str(ctx.author.id)
        
        if user_str not in self.user_purchases or not self.user_purchases[user_str]:
            embed = discord.Embed(
                title="📦 Inventaire vide",
                description="Vous n'avez aucun achat ! Visitez `j!shop` pour découvrir nos articles.",
                color=0x808080
            )
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title=f"📦 Inventaire de {ctx.author.display_name}",
            color=0x7289DA
        )

        current_time = datetime.now()
        active_items = []
        expired_items = []

        for purchase in self.user_purchases[user_str]:
            # Vérifier si l'article a expiré
            if purchase.get("expires_at"):
                expires_at = datetime.fromisoformat(purchase["expires_at"])
                if current_time > expires_at:
                    expired_items.append(purchase)
                    continue
            
            # Vérifier si l'article a encore des utilisations
            if purchase.get("uses_remaining", 1) <= 0:
                continue
                
            active_items.append(purchase)

        if not active_items:
            embed.description = "Tous vos articles ont expiré ou ont été utilisés !"
        else:
            for purchase in active_items:
                item_info = f"Acheté le: {purchase['purchase_date'][:10]}\n"
                item_info += f"Prix payé: {purchase['price_paid']:,} points\n"
                
                if purchase.get("uses_remaining"):
                    item_info += f"Utilisations restantes: {purchase['uses_remaining']}\n"
                
                if purchase.get("expires_at"):
                    expires_at = datetime.fromisoformat(purchase["expires_at"])
                    time_left = expires_at - current_time
                    hours_left = int(time_left.total_seconds() // 3600)
                    item_info += f"⏰ Expire dans: {hours_left}h"
                
                embed.add_field(
                    name=f"📦 {purchase['item_name']}",
                    value=item_info,
                    inline=True
                )

        # Nettoyage des articles expirés
        if expired_items:
            for expired in expired_items:
                self.user_purchases[user_str].remove(expired)
            self.save_user_purchases()
            
            if expired_items:
                embed.add_field(
                    name="🗑️ Articles expirés nettoyés",
                    value=f"{len(expired_items)} article(s) expiré(s) supprimé(s)",
                    inline=False
                )

        embed.set_footer(text="Utilisez j!use <item_id> pour utiliser vos articles")
        await ctx.send(embed=embed)

    @commands.command(name="use", aliases=["utiliser"])
    async def use_item(self, ctx, item_id: str = None):
        """Utiliser un article acheté"""
        if item_id is None:
            await ctx.send("❌ Usage: `j!use <item_id>`\nVoir `j!inventory` pour vos articles.")
            return

        user_str = str(ctx.author.id)
        if user_str not in self.user_purchases:
            await ctx.send("❌ Vous n'avez aucun achat !")
            return

        # Trouver l'achat
        purchase = None
        for p in self.user_purchases[user_str]:
            if p["item_id"].lower() == item_id.lower():
                purchase = p
                break

        if not purchase:
            await ctx.send("❌ Article non trouvé dans votre inventaire !")
            return

        # Vérifier les utilisations restantes
        if purchase.get("uses_remaining", 1) <= 0:
            await ctx.send("❌ Cet article n'a plus d'utilisations restantes !")
            return

        # Vérifier l'expiration
        if purchase.get("expires_at"):
            expires_at = datetime.fromisoformat(purchase["expires_at"])
            if datetime.now() > expires_at:
                await ctx.send("❌ Cet article a expiré !")
                return

        # Exécuter l'action selon le type d'article
        item = self.get_item_by_id(item_id)
        if not item:
            await ctx.send("❌ Article introuvable dans la boutique !")
            return

        try:
            success = await self.execute_item_action(ctx, item, purchase)
            if success:
                # Décrémenter les utilisations
                if "uses_remaining" in purchase:
                    purchase["uses_remaining"] -= 1
                    if purchase["uses_remaining"] <= 0:
                        self.user_purchases[user_str].remove(purchase)
                    self.save_user_purchases()
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de l'utilisation de l'article: {e}")

    async def execute_item_action(self, ctx, item, purchase):
        """Exécute l'action d'un article"""
        if item["id"] == "bombdm":
            await ctx.send("💣 **BombDM activé !** Tapez votre message à envoyer en DM:")
            
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            
            try:
                message = await self.bot.wait_for('message', timeout=60.0, check=check)
                # Ici vous pouvez ajouter la logique pour envoyer le DM
                await ctx.send(f"✅ Message prêt à être envoyé: `{message.content}`")
                return True
            except asyncio.TimeoutError:
                await ctx.send("⏰ Temps écoulé ! Utilisation annulée.")
                return False
                
        elif item["id"] == "voleur_points":
            # Logique pour voler des points
            guild_members = [m for m in ctx.guild.members if not m.bot and m.id != ctx.author.id]
            if not guild_members:
                await ctx.send("❌ Aucun membre à voler !")
                return False
                
            target = random.choice(guild_members)
            target_points = self.get_user_points(target.id)
            stolen_amount = int(target_points * 0.1)
            
            if stolen_amount <= 0:
                await ctx.send(f"❌ {target.display_name} n'a pas assez de points à voler !")
                return False
            
            # Effectuer le vol
            new_target_points = target_points - stolen_amount
            user_points = self.get_user_points(ctx.author.id)
            new_user_points = user_points + stolen_amount
            
            self.update_user_points(target.id, new_target_points)
            self.update_user_points(ctx.author.id, new_user_points)
            
            embed = discord.Embed(
                title="🦹 Vol réussi !",
                description=f"Vous avez volé **{stolen_amount:,} points** à {target.display_name} !",
                color=0x8B0000
            )
            embed.add_field(name="💰 Votre nouveau solde", value=f"{new_user_points:,} points", inline=False)
            await ctx.send(embed=embed)
            return True
            
        elif item["id"] == "message_fantome":
            await ctx.send("👻 **Message Fantôme activé !** Mentionnez le salon puis tapez votre message:")
            await ctx.send("Format: `#salon Votre message anonyme`")
            
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            
            try:
                message = await self.bot.wait_for('message', timeout=60.0, check=check)
                if message.channel_mentions:
                    target_channel = message.channel_mentions[0]
                    anonymous_msg = message.content.split(' ', 1)[1] if len(message.content.split(' ', 1)) > 1 else "Message anonyme"
                    
                    embed = discord.Embed(
                        title="👻 Message Anonyme",
                        description=anonymous_msg,
                        color=0x36393F
                    )
                    embed.set_footer(text="Message envoyé par un utilisateur anonyme")
                    
                    await target_channel.send(embed=embed)
                    await ctx.send("✅ Message anonyme envoyé !")
                    return True
                else:
                    await ctx.send("❌ Veuillez mentionner un salon !")
                    return False
            except asyncio.TimeoutError:
                await ctx.send("⏰ Temps écoulé ! Utilisation annulée.")
                return False
        
        # Actions par défaut selon le type
        elif item["type"] == "command":
            await ctx.send(f"✅ {item['name']} utilisé avec succès !")
            return True
        elif item["type"] == "buff":
            await ctx.send(f"✅ {item['name']} activé !")
            return True
        
        return False

async def setup(bot):
    await bot.add_cog(Shop(bot))
