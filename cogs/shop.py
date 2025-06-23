import discord
from discord.ext import commands
import json
import os
import asyncio
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

class ShopManager:
    def __init__(self):
        self.user_data_file = "user_data.json"
        self.shop_items_file = "shop_items.json"
        self.purchases_file = "user_purchases.json"
        self.shop_data = self.load_shop_data()
        self.user_purchases = self.load_user_purchases()

    def load_shop_data(self) -> Dict[str, Any]:
        """Charge les données de la boutique avec des items par défaut"""
        try:
            if os.path.exists(self.shop_items_file):
                with open(self.shop_items_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement de la boutique: {e}")
        
        # Items par défaut avec structure standardisée
        default_shop = {
            "items": [
                {
                    "id": "bombdm",
                    "name": "BombDM",
                    "description": "Envoi un message choisi en DM via le bot",
                    "price": 300,
                    "type": "command",
                    "category": "⚡ Commandes",
                    "emoji": "💣",
                    "uses": 1,
                    "cooldown": 0
                },
                {
                    "id": "casino_addict",
                    "name": "Casino Addict",
                    "description": "Accès à un rôle Discord exclusif",
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
                    "price": 5000,
                    "type": "command",
                    "category": "⚡ Commandes",
                    "emoji": "🦹",
                    "uses": 1,
                    "cooldown": 3600
                },
                {
                    "id": "multiplicateur_x2",
                    "name": "Multiplicateur x2",
                    "description": "Double tes gains de points pendant 12h",
                    "price": 8000,
                    "type": "buff",
                    "category": "💪 Buffs",
                    "emoji": "⚡",
                    "duration": 43200
                },
                {
                    "id": "message_fantome",
                    "name": "Message Fantôme",
                    "description": "Envoie un message anonyme dans un salon",
                    "price": 750,
                    "type": "command",
                    "category": "⚡ Commandes",
                    "emoji": "👻",
                    "uses": 1,
                    "cooldown": 1800
                },
                {
                    "id": "vip_premium",
                    "name": "VIP Premium",
                    "description": "Statut VIP avec privilèges exclusifs",
                    "price": 15000,
                    "type": "role",
                    "category": "🎭 Rôles",
                    "emoji": "💎",
                    "role_id": "1380935037901471784"
                },
                {
                    "id": "chance_boost",
                    "name": "Boost de Chance",
                    "description": "Augmente tes chances au casino pendant 12h",
                    "price": 6000,
                    "type": "buff",
                    "category": "💪 Buffs",
                    "emoji": "🍀",
                    "duration": 43200
                },
                {
                    "id": "avatar_changer",
                    "name": "Avatar Changer",
                    "description": "Change l'avatar du bot (6h)",
                    "price": 20000,
                    "type": "command",
                    "category": "🤖 Bot",
                    "emoji": "🖼️",
                    "uses": 1,
                    "duration": 21600
                },
                {
                    "id": "name_changer",
                    "name": "Name Changer",
                    "description": "Change le nom du bot (6h)",
                    "price": 15000,
                    "type": "command",
                    "category": "🤖 Bot",
                    "emoji": "📝",
                    "uses": 1,
                    "duration": 21600
                },
                {
                    "id": "custom_status",
                    "name": "Custom Status",
                    "description": "Statut personnalisé pour le bot (6h)",
                    "price": 5000,
                    "type": "command",
                    "category": "🤖 Bot",
                    "emoji": "📊",
                    "uses": 1,
                    "duration": 21600
                }
            ]
        }
        
        self.save_shop_data(default_shop)
        return default_shop

    def save_shop_data(self, data: Dict[str, Any]) -> None:
        """Sauvegarde les données de la boutique"""
        try:
            with open(self.shop_items_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la boutique: {e}")

    def load_user_purchases(self) -> Dict[str, List[Dict]]:
        """Charge les achats des utilisateurs"""
        try:
            if os.path.exists(self.purchases_file):
                with open(self.purchases_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement des achats: {e}")
        return {}

    def save_user_purchases(self) -> None:
        """Sauvegarde les achats des utilisateurs"""
        try:
            with open(self.purchases_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_purchases, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des achats: {e}")

    def load_user_data(self) -> Dict[str, Dict]:
        """Charge les données utilisateur"""
        try:
            if os.path.exists(self.user_data_file):
                with open(self.user_data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement des données utilisateur: {e}")
        return {}

    def save_user_data(self, data: Dict[str, Dict]) -> None:
        """Sauvegarde les données utilisateur"""
        try:
            with open(self.user_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des données utilisateur: {e}")

    def get_user_points(self, user_id: int) -> float:
        """Récupère les points d'un utilisateur"""
        data = self.load_user_data()
        return data.get(str(user_id), {}).get("points", 0)

    def update_user_points(self, user_id: int, points: float) -> None:
        """Met à jour les points d'un utilisateur"""
        data = self.load_user_data()
        user_str = str(user_id)
        if user_str not in data:
            data[user_str] = {}
        data[user_str]["points"] = round(points, 2)
        self.save_user_data(data)

    def get_item_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un item par son ID"""
        for item in self.shop_data.get("items", []):
            if item.get("id", "").lower() == item_id.lower():
                return item
        return None

    def get_item_by_name(self, item_name: str) -> Optional[Dict[str, Any]]:
        """Récupère un item par son nom"""
        for item in self.shop_data.get("items", []):
            if item.get("name", "").lower() == item_name.lower():
                return item
        return None

    def add_purchase(self, user_id: int, item: Dict[str, Any]) -> Dict[str, Any]:
        """Ajoute un achat pour un utilisateur"""
        user_str = str(user_id)
        if user_str not in self.user_purchases:
            self.user_purchases[user_str] = []

        purchase = {
            "item_id": item["id"],
            "item_name": item["name"],
            "item_type": item["type"],
            "purchase_date": datetime.now().isoformat(),
            "price_paid": item["price"],
            "uses_remaining": item.get("uses", 0),
            "active": True,
            "expires_at": None
        }

        # Gestion des buffs temporaires
        if item["type"] == "buff" and "duration" in item:
            expires_at = datetime.now() + timedelta(seconds=item["duration"])
            purchase["expires_at"] = expires_at.isoformat()

        # Gestion des commandes temporaires
        if item["type"] == "command" and "duration" in item:
            expires_at = datetime.now() + timedelta(seconds=item["duration"])
            purchase["expires_at"] = expires_at.isoformat()

        self.user_purchases[user_str].append(purchase)
        self.save_user_purchases()
        return purchase

    def get_user_purchases(self, user_id: int) -> List[Dict[str, Any]]:
        """Récupère les achats actifs d'un utilisateur"""
        user_str = str(user_id)
        if user_str not in self.user_purchases:
            return []

        current_time = datetime.now()
        active_purchases = []

        for purchase in self.user_purchases[user_str]:
            # Vérifier l'expiration
            if purchase.get("expires_at"):
                expires_at = datetime.fromisoformat(purchase["expires_at"])
                if current_time > expires_at:
                    purchase["active"] = False
                    continue

            # Vérifier les utilisations
            if purchase.get("uses_remaining", 1) <= 0 and purchase["item_type"] == "command":
                purchase["active"] = False
                continue

            if purchase.get("active", True):
                active_purchases.append(purchase)

        return active_purchases

    def use_item(self, user_id: int, item_id: str) -> Optional[Dict[str, Any]]:
        """Utilise un item et met à jour les données"""
        user_str = str(user_id)
        if user_str not in self.user_purchases:
            return None

        for purchase in self.user_purchases[user_str]:
            if purchase["item_id"] == item_id and purchase.get("active", True):
                # Vérifier si l'item peut être utilisé
                if purchase.get("uses_remaining", 1) > 0:
                    purchase["uses_remaining"] -= 1
                    if purchase["uses_remaining"] <= 0:
                        purchase["active"] = False
                    self.save_user_purchases()
                    return purchase
                break

        return None

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shop_manager = ShopManager()

    @commands.group(name="shop", aliases=["boutique"], invoke_without_command=True)
    async def shop(self, ctx, *, category: str = ""):
        """Affiche la boutique"""
        items = self.shop_manager.shop_data.get("items", [])
        
        if not items:
            embed = discord.Embed(
                title="🛒 Boutique",
                description="❌ La boutique est actuellement vide !",
                color=0xFF0000
            )
            await ctx.send(embed=embed)
            return

        # Grouper par catégorie
        categories = {}
        for item in items:
            cat = item.get("category", "🛍️ Divers")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(item)

        if category:
            # Afficher une catégorie spécifique
            found_category = None
            for cat_name in categories.keys():
                if category.lower() in cat_name.lower():
                    found_category = cat_name
                    break
            
            if not found_category:
                await ctx.send("❌ Catégorie introuvable !")
                return

            embed = discord.Embed(
                title=f"🛒 Boutique - {found_category}",
                color=0x7289DA
            )

            for item in categories[found_category][:10]:  # Limite à 10 items
                value = f"{item['description']}\n"
                value += f"💰 **{item['price']:,}** points"
                if item.get("uses"):
                    value += f" • {item['uses']} utilisation(s)"
                if item.get("duration"):
                    hours = item["duration"] // 3600
                    value += f" • Durée: {hours}h"

                embed.add_field(
                    name=f"{item.get('emoji', '🛍️')} {item['name']}",
                    value=value,
                    inline=False
                )
        else:
            # Afficher l'aperçu des catégories
            embed = discord.Embed(
                title="🛒 Boutique Premium",
                description="Dépensez vos points dans notre boutique exclusive !\n\n",
                color=0x7289DA
            )

            for cat_name, cat_items in categories.items():
                items_preview = []
                for item in cat_items[:3]:  # 3 premiers items
                    items_preview.append(f"{item.get('emoji', '🛍️')} **{item['name']}** - {item['price']:,}pts")
                
                if len(cat_items) > 3:
                    items_preview.append(f"... et {len(cat_items) - 3} autres")

                embed.add_field(
                    name=cat_name,
                    value="\n".join(items_preview),
                    inline=True
                )

            embed.add_field(
                name="📖 Commandes",
                value="`j!buy <item>` - Acheter un article\n`j!inventory` - Voir vos achats\n`j!use <item>` - Utiliser un article",
                inline=False
            )

        # Afficher le solde de l'utilisateur
        user_points = self.shop_manager.get_user_points(ctx.author.id)
        embed.set_footer(text=f"💰 Votre solde: {user_points:,} points")
        
        await ctx.send(embed=embed)

    @commands.command(name="buy", aliases=["acheter"])
    async def buy_item(self, ctx, *, item_name: str = ""):
        """Acheter un article de la boutique"""
        if not item_name:
            await ctx.send("❌ Veuillez spécifier un article à acheter !\nUtilisation: `j!buy <nom_article>`")
            return

        # Rechercher l'article
        item = self.shop_manager.get_item_by_name(item_name)
        if not item:
            item = self.shop_manager.get_item_by_id(item_name)
        
        if not item:
            await ctx.send("❌ Article introuvable ! Vérifiez le nom avec `j!shop`")
            return

        user_points = self.shop_manager.get_user_points(ctx.author.id)
        
        # Vérifier si l'utilisateur a assez de points
        if user_points < item["price"]:
            deficit = item["price"] - user_points
            embed = discord.Embed(
                title="💸 Fonds insuffisants",
                description=f"Il vous manque **{deficit:,}** points !",
                color=0xFF0000
            )
            embed.add_field(name="💰 Votre solde", value=f"{user_points:,} points", inline=True)
            embed.add_field(name="💳 Prix de l'article", value=f"{item['price']:,} points", inline=True)
            await ctx.send(embed=embed)
            return

        # Vérifications spéciales pour les rôles
        if item["type"] == "role":
            if not ctx.guild:
                await ctx.send("❌ Cette commande doit être utilisée dans un serveur !")
                return
            
            role_id = item.get("role_id")
            if not role_id:
                await ctx.send("❌ Rôle mal configuré ! Contactez un administrateur.")
                return
            
            try:
                role = ctx.guild.get_role(int(role_id))
                if not role:
                    await ctx.send("❌ Rôle introuvable ! Contactez un administrateur.")
                    return
                
                if role in ctx.author.roles:
                    await ctx.send("❌ Vous possédez déjà ce rôle !")
                    return
            except ValueError:
                await ctx.send("❌ ID de rôle invalide ! Contactez un administrateur.")
                return

        # Confirmation d'achat
        embed = discord.Embed(
            title="🛒 Confirmation d'achat",
            description=f"Voulez-vous acheter **{item['name']}** ?",
            color=0xFFD700
        )
        embed.add_field(name="📦 Description", value=item["description"], inline=False)
        embed.add_field(name="💰 Prix", value=f"{item['price']:,} points", inline=True)
        embed.add_field(name="💳 Solde après achat", value=f"{user_points - item['price']:,} points", inline=True)
        
        if item.get("uses"):
            embed.add_field(name="🔄 Utilisations", value=f"{item['uses']}", inline=True)
        if item.get("duration"):
            hours = item["duration"] // 3600
            embed.add_field(name="⏱️ Durée", value=f"{hours}h", inline=True)

        embed.set_footer(text="Réagissez avec ✅ pour confirmer ou ❌ pour annuler")

        message = await ctx.send(embed=embed)
        await message.add_reaction("✅")
        await message.add_reaction("❌")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == message.id

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=30.0, check=check)
            
            if str(reaction.emoji) == "❌":
                embed = discord.Embed(title="❌ Achat annulé", color=0xFF0000)
                await message.edit(embed=embed)
                return

            # Procéder à l'achat
            success_message = await self.process_purchase(ctx, item, user_points)
            
            if success_message:
                embed = discord.Embed(
                    title="✅ Achat réussi !",
                    description=f"Vous avez acheté **{item['name']}** !",
                    color=0x00FF00
                )
                embed.add_field(name="🎉 Résultat", value=success_message, inline=False)
                embed.add_field(name="💰 Nouveau solde", value=f"{user_points - item['price']:,} points", inline=False)
                
                if item["type"] in ["command", "buff"]:
                    embed.add_field(name="📋 Utilisation", value=f"Utilisez `j!use {item['id']}` pour activer cet article", inline=False)
                
                await message.edit(embed=embed)
            else:
                embed = discord.Embed(title="❌ Erreur lors de l'achat", color=0xFF0000)
                await message.edit(embed=embed)

        except asyncio.TimeoutError:
            embed = discord.Embed(title="⏰ Temps écoulé - Achat annulé", color=0xFF0000)
            await message.edit(embed=embed)

    async def process_purchase(self, ctx, item: Dict[str, Any], user_points: float) -> Optional[str]:
        """Traite l'achat d'un article"""
        try:
            # Déduire les points
            new_points = user_points - item["price"]
            self.shop_manager.update_user_points(ctx.author.id, new_points)
            
            # Traitement selon le type
            if item["type"] == "role":
                role = ctx.guild.get_role(int(item["role_id"]))
                await ctx.author.add_roles(role)
                return f"Rôle **{role.name}** attribué avec succès !"
            
            elif item["type"] in ["command", "buff"]:
                self.shop_manager.add_purchase(ctx.author.id, item)
                return "Article ajouté à votre inventaire !"
            
            else:
                self.shop_manager.add_purchase(ctx.author.id, item)
                return "Article acheté avec succès !"
                
        except Exception as e:
            # Rembourser en cas d'erreur
            self.shop_manager.update_user_points(ctx.author.id, user_points)
            print(f"Erreur lors du traitement de l'achat: {e}")
            return None

    @commands.command(name="inventory", aliases=["inv", "inventaire"])
    async def inventory(self, ctx):
        """Affiche l'inventaire de l'utilisateur"""
        purchases = self.shop_manager.get_user_purchases(ctx.author.id)
        
        if not purchases:
            embed = discord.Embed(
                title="📦 Inventaire vide",
                description="Vous n'avez aucun article ! Visitez `j!shop` pour découvrir nos articles.",
                color=0x808080
            )
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title=f"📦 Inventaire de {ctx.author.display_name}",
            color=0x7289DA
        )

        current_time = datetime.now()
        
        for purchase in purchases[:10]:  # Limite à 10 articles
            item_info = f"**Acheté:** {purchase['purchase_date'][:10]}\n"
            item_info += f"**Prix payé:** {purchase['price_paid']:,} points\n"
            
            if purchase.get("uses_remaining", 0) > 0:
                item_info += f"**Utilisations restantes:** {purchase['uses_remaining']}\n"
            
            if purchase.get("expires_at"):
                expires_at = datetime.fromisoformat(purchase["expires_at"])
                time_left = expires_at - current_time
                if time_left.total_seconds() > 0:
                    hours_left = int(time_left.total_seconds() // 3600)
                    minutes_left = int((time_left.total_seconds() % 3600) // 60)
                    item_info += f"**⏰ Expire dans:** {hours_left}h {minutes_left}m"
                else:
                    item_info += "**⏰ Expiré**"

            embed.add_field(
                name=f"📦 {purchase['item_name']}",
                value=item_info,
                inline=True
            )

        embed.set_footer(text="Utilisez j!use <item_id> pour utiliser vos articles")
        await ctx.send(embed=embed)

    @commands.command(name="use", aliases=["utiliser"])
    async def use_item(self, ctx, *, item_identifier: str = ""):
        """Utiliser un article de l'inventaire"""
        if not item_identifier:
            await ctx.send("❌ Veuillez spécifier l'article à utiliser !\nUtilisation: `j!use <nom_ou_id_article>`")
            return

        # Rechercher l'article dans l'inventaire
        purchases = self.shop_manager.get_user_purchases(ctx.author.id)
        
        target_purchase = None
        for purchase in purchases:
            if (purchase["item_id"].lower() == item_identifier.lower() or 
                purchase["item_name"].lower() == item_identifier.lower()):
                target_purchase = purchase
                break

        if not target_purchase:
            await ctx.send("❌ Article introuvable dans votre inventaire !")
            return

        # Vérifier si l'article peut être utilisé
        if target_purchase.get("uses_remaining", 1) <= 0:
            await ctx.send("❌ Cet article n'a plus d'utilisations restantes !")
            return

        # Vérifier l'expiration
        if target_purchase.get("expires_at"):
            expires_at = datetime.fromisoformat(target_purchase["expires_at"])
            if datetime.now() > expires_at:
                await ctx.send("❌ Cet article a expiré !")
                return

        # Récupérer les données de l'article
        item = self.shop_manager.get_item_by_id(target_purchase["item_id"])
        if not item:
            await ctx.send("❌ Données de l'article introuvables !")
            return

        # Exécuter l'action
        try:
            success = await self.execute_item_action(ctx, item, target_purchase)
            if success:
                # Décrémenter les utilisations
                used_purchase = self.shop_manager.use_item(ctx.author.id, item["id"])
                if used_purchase:
                    await ctx.send(f"✅ **{item['name']}** utilisé avec succès !")
            else:
                await ctx.send("❌ Échec de l'utilisation de l'article.")
        except Exception as e:
            await ctx.send(f"❌ Erreur lors de l'utilisation: {e}")
            print(f"Erreur use_item: {e}")

    async def execute_item_action(self, ctx, item: Dict[str, Any], purchase: Dict[str, Any]) -> bool:
        """Exécute l'action spécifique d'un article"""
        item_id = item["id"]
        
        try:
            if item_id == "bombdm":
                return await self.action_bombdm(ctx)
            elif item_id == "voleur_points":
                return await self.action_voleur_points(ctx)
            elif item_id == "message_fantome":
                return await self.action_message_fantome(ctx)
            elif item_id == "multiplicateur_x2":
                return await self.action_multiplicateur(ctx, purchase)
            elif item_id == "chance_boost":
                return await self.action_chance_boost(ctx, purchase)
            elif item_id == "avatar_changer":
                return await self.action_avatar_changer(ctx)
            elif item_id == "name_changer":
                return await self.action_name_changer(ctx)
            elif item_id == "custom_status":
                return await self.action_custom_status(ctx)
            else:
                # Action générique
                embed = discord.Embed(
                    title="✅ Article utilisé",
                    description=f"**{item['name']}** a été activé !",
                    color=0x00FF00
                )
                await ctx.send(embed=embed)
                return True
                
        except Exception as e:
            print(f"Erreur dans execute_item_action: {e}")
            return False

    async def action_bombdm(self, ctx) -> bool:
        """Action pour BombDM"""
        await ctx.send("💣 **BombDM activé !** Écrivez le message à envoyer en DM :")
        
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        try:
            message = await self.bot.wait_for('message', timeout=60.0, check=check)
            
            # Ici vous pouvez ajouter la logique pour envoyer le DM
            # Par exemple, demander à qui l'envoyer
            await ctx.send(f"✅ Message préparé : `{message.content[:100]}...`")
            await ctx.send("💣 BombDM sera bientôt implémenté complètement !")
            return True
            
        except asyncio.TimeoutError:
            await ctx.send("⏰ Temps écoulé ! BombDM annulé.")
            return False

    async def action_voleur_points(self, ctx) -> bool:
        """Action pour voler des points"""
        if not ctx.guild:
            await ctx.send("❌ Cette commande doit être utilisée dans un serveur !")
            return False
        
        # Récupérer les membres éligibles
        eligible_members = []
        for member in ctx.guild.members:
            if (not member.bot and 
                member.id != ctx.author.id and 
                self.shop_manager.get_user_points(member.id) > 0):
                eligible_members.append(member)
        
        if not eligible_members:
            await ctx.send("❌ Aucun membre éligible pour le vol de points !")
            return False
        
        # Sélectionner une victime au hasard
        victim = random.choice(eligible_members)
        victim_points = self.shop_manager.get_user_points(victim.id)
        
        if victim_points <= 0:
            await ctx.send("❌ La victime sélectionnée n'a pas de points à voler !")
            return False
        
        # Calculer les points volés (10%)
        stolen_points = round(victim_points * 0.1, 2)
        
        # Effectuer le transfert
        new_victim_points = victim_points - stolen_points
        thief_points = self.shop_manager.get_user_points(ctx.author.id)
        new_thief_points = thief_points + stolen_points
        
        self.shop_manager.update_user_points(victim.id, new_victim_points)
        self.shop_manager.update_user_points(ctx.author.id, new_thief_points)
        
        # Message de confirmation
        embed = discord.Embed(
            title="🦹 Vol réussi !",
            description=f"Vous avez volé **{stolen_points:,}** points à {victim.mention} !",
            color=0x800080
        )
        embed.add_field(name="💰 Votre nouveau solde", value=f"{new_thief_points:,} points", inline=True)
        embed.add_field(name="😭 Victime", value=f"{victim.display_name}", inline=True)
        await ctx.send(embed=embed)
        
        # Notifier la victime (optionnel)
        try:
            victim_embed = discord.Embed(
                title="😱 Vous avez été victime d'un vol !",
                description=f"{ctx.author.display_name} vous a volé **{stolen_points:,}** points !",
                color=0xFF0000
            )
            await victim.send(embed=victim_embed)
        except (discord.Forbidden, discord.HTTPException):
            pass  # Si les DM sont fermés ou autres erreurs
        
        return True

    async def action_message_fantome(self, ctx) -> bool:
        """Action pour envoyer un message fantôme"""
        if not ctx.guild:
            await ctx.send("❌ Cette commande doit être utilisée dans un serveur !")
            return False

        await ctx.send("👻 **Message Fantôme activé !**\nÉcrivez le message à envoyer anonymement :")
        
        def check_message(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        try:
            message = await self.bot.wait_for('message', timeout=60.0, check=check_message)
            
            await ctx.send("📝 Dans quel salon voulez-vous envoyer ce message ?\nMentionnez le salon (ex: #général) :")
            
            channel_msg = await self.bot.wait_for('message', timeout=30.0, check=check_message)
            
            # Trouver le salon
            target_channel = None
            if channel_msg.channel_mentions:
                target_channel = channel_msg.channel_mentions[0]
            else:
                # Recherche par nom
                for channel in ctx.guild.text_channels:
                    if channel_msg.content.lower() in channel.name.lower():
                        target_channel = channel
                        break
            
            if not target_channel:
                await ctx.send("❌ Salon introuvable !")
                return False
            
            # Vérifier les permissions
            if not target_channel.permissions_for(ctx.guild.me).send_messages:
                await ctx.send("❌ Je n'ai pas la permission d'écrire dans ce salon !")
                return False
            
            # Envoyer le message fantôme
            ghost_embed = discord.Embed(
                description=message.content,
                color=0x2F3136
            )
            ghost_embed.set_author(name="👻 Message Fantôme", icon_url=ctx.guild.me.avatar.url if ctx.guild.me.avatar else "")
            ghost_embed.set_footer(text="Un membre anonyme a utilisé un Message Fantôme")
            
            await target_channel.send(embed=ghost_embed)
            await ctx.send(f"✅ Message fantôme envoyé dans {target_channel.mention} !")
            
            return True
            
        except asyncio.TimeoutError:
            await ctx.send("⏰ Temps écoulé ! Message fantôme annulé.")
            return False

    async def action_multiplicateur(self, ctx, purchase: Dict[str, Any]) -> bool:
        """Action pour le multiplicateur x2"""
        embed = discord.Embed(
            title="⚡ Multiplicateur x2 Activé !",
            description="Vos gains de points sont maintenant **doublés** pendant 12h !",
            color=0xFFD700
        )
        
        if purchase.get("expires_at"):
            expires_at = datetime.fromisoformat(purchase["expires_at"])
            embed.add_field(
                name="⏰ Expire le",
                value=f"<t:{int(expires_at.timestamp())}:F>",
                inline=False
            )
        
        await ctx.send(embed=embed)
        return True

    async def action_chance_boost(self, ctx, purchase: Dict[str, Any]) -> bool:
        """Action pour le boost de chance"""
        embed = discord.Embed(
            title="🍀 Boost de Chance Activé !",
            description="Vos chances au casino sont maintenant **améliorées** pendant 12h !",
            color=0x00FF00
        )
        
        if purchase.get("expires_at"):
            expires_at = datetime.fromisoformat(purchase["expires_at"])
            embed.add_field(
                name="⏰ Expire le",
                value=f"<t:{int(expires_at.timestamp())}:F>",
                inline=False
            )
        
        await ctx.send(embed=embed)
        return True

    async def action_avatar_changer(self, ctx) -> bool:
        """Action pour changer l'avatar du bot"""
        await ctx.send("🖼️ **Avatar Changer activé !**\nEnvoyez l'image que vous voulez définir comme avatar :")
        
        def check_message(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        try:
            message = await self.bot.wait_for('message', timeout=60.0, check=check_message)
            
            if not message.attachments:
                await ctx.send("❌ Aucune image détectée ! Veuillez envoyer une image.")
                return False
            
            attachment = message.attachments[0]
            
            # Vérifier que c'est une image
            if not any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                await ctx.send("❌ Format d'image non supporté ! Utilisez PNG, JPG, JPEG, GIF ou WEBP.")
                return False
            
            # Télécharger et changer l'avatar
            avatar_data = await attachment.read()
            await self.bot.user.edit(avatar=avatar_data)
            
            embed = discord.Embed(
                title="✅ Avatar changé !",
                description="L'avatar du bot a été mis à jour avec succès !",
                color=0x00FF00
            )
            embed.add_field(name="⏰ Durée", value="6 heures", inline=True)
            embed.set_thumbnail(url=attachment.url)
            await ctx.send(embed=embed)
            
            # Programmer le retour à l'avatar original (optionnel)
            # Vous pouvez stocker l'avatar original et le restaurer après 6h
            
            return True
            
        except discord.HTTPException as e:
            await ctx.send(f"❌ Erreur lors du changement d'avatar : {e}")
            return False
        except asyncio.TimeoutError:
            await ctx.send("⏰ Temps écoulé ! Changement d'avatar annulé.")
            return False

    async def action_name_changer(self, ctx) -> bool:
        """Action pour changer le nom du bot"""
        await ctx.send("📝 **Name Changer activé !**\nÉcrivez le nouveau nom pour le bot :")
        
        def check_message(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        try:
            message = await self.bot.wait_for('message', timeout=60.0, check=check_message)
            new_name = message.content.strip()
            
            if len(new_name) < 2 or len(new_name) > 32:
                await ctx.send("❌ Le nom doit faire entre 2 et 32 caractères !")
                return False
            
            old_name = self.bot.user.display_name
            await self.bot.user.edit(username=new_name)
            
            embed = discord.Embed(
                title="✅ Nom changé !",
                description=f"Le nom du bot a été changé de **{old_name}** à **{new_name}** !",
                color=0x00FF00
            )
            embed.add_field(name="⏰ Durée", value="6 heures", inline=True)
            await ctx.send(embed=embed)
            
            return True
            
        except discord.HTTPException as e:
            await ctx.send(f"❌ Erreur lors du changement de nom : {e}")
            return False
        except asyncio.TimeoutError:
            await ctx.send("⏰ Temps écoulé ! Changement de nom annulé.")
            return False

    async def action_custom_status(self, ctx) -> bool:
        """Action pour changer le statut du bot"""
        await ctx.send("📊 **Custom Status activé !**\nÉcrivez le nouveau statut pour le bot :")
        
        def check_message(m):
            return m.author == ctx.author and m.channel == ctx.channel
        
        try:
            message = await self.bot.wait_for('message', timeout=60.0, check=check_message)
            new_status = message.content.strip()
            
            if len(new_status) > 128:
                await ctx.send("❌ Le statut ne peut pas dépasser 128 caractères !")
                return False
            
            # Changer l'activité du bot
            activity = discord.Game(name=new_status)
            await self.bot.change_presence(activity=activity, status=discord.Status.online)
            
            embed = discord.Embed(
                title="✅ Statut changé !",
                description=f"Le statut du bot a été changé à : **{new_status}**",
                color=0x00FF00
            )
            embed.add_field(name="⏰ Durée", value="6 heures", inline=True)
            await ctx.send(embed=embed)
            
            return True
            
        except asyncio.TimeoutError:
            await ctx.send("⏰ Temps écoulé ! Changement de statut annulé.")
            return False

    # Commandes administrateur pour gérer la boutique
    @commands.group(name="shopadmin", aliases=["sa"], invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def shop_admin(self, ctx):
        """Commandes d'administration de la boutique"""
        embed = discord.Embed(
            title="🛠️ Administration de la Boutique",
            description="Commandes disponibles :",
            color=0xFF6B6B
        )
        embed.add_field(
            name="📦 Gestion des articles",
            value="`j!sa add` - Ajouter un article\n`j!sa remove <id>` - Supprimer un article\n`j!sa edit <id>` - Modifier un article",
            inline=False
        )
        embed.add_field(
            name="👥 Gestion des utilisateurs",
            value="`j!sa give <user> <points>` - Donner des points\n`j!sa take <user> <points>` - Retirer des points\n`j!sa reset <user>` - Reset un utilisateur",
            inline=False
        )
        embed.add_field(
            name="📊 Statistiques",
            value="`j!sa stats` - Statistiques de la boutique\n`j!sa sales` - Historique des ventes",
            inline=False
        )
        await ctx.send(embed=embed)

    @shop_admin.command(name="give")
    @commands.has_permissions(administrator=True)
    async def give_points(self, ctx, user: discord.Member, points: float):
        """Donner des points à un utilisateur"""
        if points <= 0:
            await ctx.send("❌ Le nombre de points doit être positif !")
            return
        
        current_points = self.shop_manager.get_user_points(user.id)
        new_points = current_points + points
        self.shop_manager.update_user_points(user.id, new_points)
        
        embed = discord.Embed(
            title="✅ Points accordés",
            description=f"**{points:,}** points ont été accordés à {user.mention}",
            color=0x00FF00
        )
        embed.add_field(name="💰 Nouveau solde", value=f"{new_points:,} points", inline=True)
        await ctx.send(embed=embed)

    @shop_admin.command(name="take")
    @commands.has_permissions(administrator=True)
    async def take_points(self, ctx, user: discord.Member, points: float):
        """Retirer des points à un utilisateur"""
        if points <= 0:
            await ctx.send("❌ Le nombre de points doit être positif !")
            return
        
        current_points = self.shop_manager.get_user_points(user.id)
        new_points = max(0, current_points - points)
        self.shop_manager.update_user_points(user.id, new_points)
        
        embed = discord.Embed(
            title="✅ Points retirés",
            description=f"**{points:,}** points ont été retirés à {user.mention}",
            color=0xFF6B6B
        )
        embed.add_field(name="💰 Nouveau solde", value=f"{new_points:,} points", inline=True)
        await ctx.send(embed=embed)

    @shop_admin.command(name="stats")
    @commands.has_permissions(administrator=True)
    async def shop_stats(self, ctx):
        """Affiche les statistiques de la boutique"""
        user_data = self.shop_manager.load_user_data()
        
        total_users = len(user_data)
        total_points = sum(user.get("points", 0) for user in user_data.values())
        
        # Top 5 des plus riches
        top_users = sorted(user_data.items(), key=lambda x: x[1].get("points", 0), reverse=True)[:5]
        
        embed = discord.Embed(
            title="📊 Statistiques de la Boutique",
            color=0x7289DA
        )
        embed.add_field(name="👥 Utilisateurs totaux", value=f"{total_users:,}", inline=True)
        embed.add_field(name="💰 Points en circulation", value=f"{total_points:,}", inline=True)
        embed.add_field(name="🛍️ Articles disponibles", value=f"{len(self.shop_manager.shop_data.get('items', []))}", inline=True)
        
        if top_users:
            top_list = []
            for i, (user_id, data) in enumerate(top_users, 1):
                try:
                    user = self.bot.get_user(int(user_id))
                    name = user.display_name if user else f"User {user_id}"
                    points = data.get("points", 0)
                    top_list.append(f"{i}. {name}: {points:,} points")
                except (ValueError, AttributeError):
                    continue
            
            if top_list:
                embed.add_field(
                    name="🏆 Top Utilisateurs",
                    value="\n".join(top_list),
                    inline=False
                )
        
        await ctx.send(embed=embed)

# Fonction pour ajouter le cog au bot
async def setup(bot):
    await bot.add_cog(Shop(bot))