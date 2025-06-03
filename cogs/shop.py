import discord
from discord.ext import commands
import json
import asyncio
import random
from datetime import datetime, timedelta

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_buffs = {}  # {user_id: {buff_type: expiry_time}}
        
    def load_user_data(self):
        try:
            with open('user_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_user_data(self, data):
        with open('user_data.json', 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_shop_items(self):
        try:
            with open('shop_items.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"items": []}
    
    def get_user_points(self, user_id):
        data = self.load_user_data()
        return data.get(str(user_id), {}).get("points", 0)
    
    def update_user_points(self, user_id, points):
        data = self.load_user_data()
        if str(user_id) not in data:
            data[str(user_id)] = {"points": 0}
        data[str(user_id)]["points"] = round(data[str(user_id)]["points"] + points, 2)
        self.save_user_data(data)
    
    def has_active_buff(self, user_id, buff_type):
        if user_id in self.active_buffs and buff_type in self.active_buffs[user_id]:
            if datetime.now() < self.active_buffs[user_id][buff_type]:
                return True
            else:
                del self.active_buffs[user_id][buff_type]
        return False
    
    def add_buff(self, user_id, buff_type, duration_hours):
        if user_id not in self.active_buffs:
            self.active_buffs[user_id] = {}
        self.active_buffs[user_id][buff_type] = datetime.now() + timedelta(hours=duration_hours)

    @commands.command(name="shop", aliases=["boutique"])
    async def shop(self, ctx):
        """Affiche la boutique"""
        shop_data = self.load_shop_items()
        user_points = self.get_user_points(ctx.author.id)
        
        embed = discord.Embed(title="🛒 Boutique", color=0x00ff00)
        embed.add_field(name="💰 Tes points", value=f"{user_points}", inline=False)
        
        for i, item in enumerate(shop_data["items"], 1):
            embed.add_field(
                name=f"{i}. {item['name']} - {item['price']} points",
                value=item['description'],
                inline=False
            )
        
        embed.set_footer(text="Utilise j!buy <numéro> pour acheter un item")
        await ctx.send(embed=embed)

    @commands.command(name="buy", aliases=["acheter"])
    async def buy_item(self, ctx, item_number: int):
        """Achète un item de la boutique"""
        shop_data = self.load_shop_items()
        user_points = self.get_user_points(ctx.author.id)
        
        if item_number < 1 or item_number > len(shop_data["items"]):
            await ctx.send("❌ Numéro d'item invalide!")
            return
        
        item = shop_data["items"][item_number - 1]
        
        if user_points < item["price"]:
            await ctx.send(f"❌ Tu n'as pas assez de points! Il te manque {item['price'] - user_points} points.")
            return
        
        # Débiter les points
        self.update_user_points(ctx.author.id, -item["price"])
        
        # Traiter l'achat selon le type
        await self.process_purchase(ctx, item)

    async def process_purchase(self, ctx, item):
        """Traite l'achat selon le type d'item"""
        item_name = item["name"]
        
        if item_name == "BombDM":
            await self.handle_bomb_dm(ctx)
        elif item_name == "Spam Master":
            await self.handle_spam_master(ctx)
        elif item_name == "Voleur de Points":
            await self.handle_point_thief(ctx)
        elif item_name == "Multiplicateur x2":
            await self.handle_multiplier(ctx)
        elif item_name == "Message Fantôme":
            await self.handle_ghost_message(ctx)
        elif item_name == "Changeur de Pseudo":
            await self.handle_nickname_change(ctx)
        elif item_name == "Notification Troll":
            await self.handle_troll_notification(ctx)
        elif item_name == "Doubleur de Mise":
            await self.handle_bet_doubler(ctx)
        elif item_name == "Bouclier Anti-Vol":
            await self.handle_theft_shield(ctx)
        elif item_name == "Resurrection":
            await self.handle_resurrection(ctx)
        elif item_name == "Message Doré":
            await self.handle_golden_message(ctx)
        elif item_name == "Roulette Russe":
            await self.handle_russian_roulette(ctx)
        elif item_name == "Banquier Temporaire":
            await self.handle_temporary_banker(ctx)
        elif item_name == "Custom Status":
            await self.handle_custom_status(ctx)
        elif item["type"] == "role":
            await self.handle_role_purchase(ctx, item)

    async def handle_bomb_dm(self, ctx):
        await ctx.send ("💣 BombDM acheté! Écris ton message:")
        try:
            msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=60)
            await ctx.send("À qui veux-tu l'envoyer? (mentionne la personne)")
            target_msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=60)
            
            if target_msg.mentions:
                target = target_msg.mentions[0]
                try:
                    await target.send(f"💣 Message anonyme: {msg.content}")
                    await ctx.send("✅ Message envoyé!")
                except:
                    await ctx.send("❌ Impossible d'envoyer le message (DM fermés?)")
            else:
                await ctx.send("❌ Personne mentionnée!")
        except asyncio.TimeoutError:
            await ctx.send("❌ Temps écoulé!")

    async def handle_spam_master(self, ctx):
        await ctx.send("🚀 Spam Master activé! Tu peux envoyer 10 messages sans cooldown maintenant!")
        # Logique à implémenter selon ton système de cooldown

    async def handle_point_thief(self, ctx):
        data = self.load_user_data()
        users_with_points = [(uid, udata) for uid, udata in data.items() 
                           if udata.get("points", 0) > 0 and int(uid) != ctx.author.id]
        
        if not users_with_points:
            await ctx.send("❌ Aucun utilisateur à voler!")
            return
        
        target_id, target_data = random.choice(users_with_points)
        stolen_points = round(target_data["points"] * 0.1, 2)
        
        self.update_user_points(int(target_id), -stolen_points)
        self.update_user_points(ctx.author.id, stolen_points)
        
        target_user = self.bot.get_user(int(target_id))
        await ctx.send(f"🕵️ Tu as volé {stolen_points} points à {target_user.mention if target_user else 'quelqu\'un'}!")

    async def handle_multiplier(self, ctx):
        self.add_buff(ctx.author.id, "multiplier", 24)
        await ctx.send("✨ Multiplicateur x2 activé pendant 24h! Tes gains de points sont doublés!")

    async def handle_ghost_message(self, ctx):
        await ctx.send("👻 Dans quel salon veux-tu envoyer un message anonyme?")
        try:
            channel_msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author, timeout=60)
            if channel_msg.channel_mentions:
                target_channel = channel_msg.channel_mentions[0]
                await ctx.send("Quel message veux-tu envoyer?")
                content_msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author, timeout=60)
                await target_channel.send(f"👻 Message anonyme: {content_msg.content}")
                await ctx.send("✅ Message fantôme envoyé!")
        except asyncio.TimeoutError:
            await ctx.send("❌ Temps écoulé!")

    async def handle_nickname_change(self, ctx):
        await ctx.send("🏷️ Mentionne la personne dont tu veux changer le pseudo:")
        try:
            target_msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author, timeout=60)
            if target_msg.mentions:
                target = target_msg.mentions[0]
                await ctx.send("Quel nouveau pseudo?")
                nick_msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author, timeout=60)
                
                old_nick = target.display_name
                await target.edit(nick=nick_msg.content)
                await ctx.send(f"✅ Pseudo changé! Il redeviendra normal dans 1h.")
                
                # Programmer le retour du pseudo original
                await asyncio.sleep(3600)  # 1 heure
                try:
                    await target.edit(nick=old_nick if old_nick != target.name else None)
                except:
                    pass
        except asyncio.TimeoutError:
            await ctx.send("❌ Temps écoulé!")
        except discord.Forbidden:
            await ctx.send("❌ Je n'ai pas les permissions pour changer ce pseudo!")

    async def handle_troll_notification(self, ctx):
        await ctx.send("😈 Mentionne ta victime:")
        try:
            target_msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author, timeout=60)
            if target_msg.mentions:
                target = target_msg.mentions[0]
                troll_messages = [
                    "🔔 Ding dong!",
                    "📢 ATTENTION!",
                    "🚨 ALERTE!",
                    "⚡ NOTIFICATION IMPORTANTE!",
                    "🎉 SURPRISE!"
                ]
                
                for msg in troll_messages:
                    await ctx.send(f"{target.mention} {msg}")
                    await asyncio.sleep(1)
                
                await ctx.send("😈 Troll réussi!")
        except asyncio.TimeoutError:
            await ctx.send("❌ Temps écoulé!")

    async def handle_bet_doubler(self, ctx):
        self.add_buff(ctx.author.id, "bet_doubler", 1)
        await ctx.send("🎰 Doubleur de mise activé! Ta prochaine commande casino doublera automatiquement ta mise!")

    async def handle_theft_shield(self, ctx):
        self.add_buff(ctx.author.id, "theft_shield", 48)
        await ctx.send("🛡️ Bouclier anti-vol activé pendant 48h! Tes points sont protégés!")

    async def handle_resurrection(self, ctx):
        # Logique à adapter selon ton système de tracking des pertes
        recovered_points = 1000  # Exemple
        self.update_user_points(ctx.author.id, recovered_points)
        await ctx.send(f"🔄 Résurrection! Tu as récupéré {recovered_points} points!")

    async def handle_golden_message(self, ctx):
        self.add_buff(ctx.author.id, "golden_message", 1)
        await ctx.send("✨ Message doré prêt! Ton prochain message sera mis en évidence!")

    async def handle_russian_roulette(self, ctx):
        user_points = self.get_user_points(ctx.author.id)
        if random.choice([True, False]):
            self.update_user_points(ctx.author.id, user_points)
            await ctx.send(f"🎰 JACKPOT! Tu as doublé tes points! Nouveau total: {user_points * 2}")
        else:
            self.update_user_points(ctx.author.id, -user_points)
            await ctx.send("💀 BANG! Tu as perdu tous tes points... Mes condoléances.")

    async def handle_temporary_banker(self, ctx):
        self.add_buff(ctx.author.id, "banker", 12)
        await ctx.send("🏦 Tu es maintenant banquier temporaire! Tu reçois 1% des achats pendant 12h!")

    async def handle_custom_status(self, ctx):
        await ctx.send("🎭 Quel statut veux-tu que j'affiche?")
        try:
            status_msg = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author, timeout=60)
            await self.bot.change_presence(activity=discord.Game(name=status_msg.content))
            await ctx.send("✅ Statut personnalisé activé pour 6h!")
            
            # Retour au statut normal après 6h
            await asyncio.sleep(21600)  # 6 heures
            await self.bot.change_presence(activity=None)
        except asyncio.TimeoutError:
            await ctx.send("❌ Temps écoulé!")

    async def handle_role_purchase(self, ctx, item):
        try:
            role = ctx.guild.get_role(int(item["role_id"]))
            if role:
                await ctx.author.add_roles(role)
                await ctx.send(f"✅ Rôle {role.name} ajouté!")
            else:
                await ctx.send("❌ Rôle introuvable!")
        except Exception as e:
            await ctx.send(f"❌ Erreur: {e}")

    @commands.command(name="buffs")
    async def check_buffs(self, ctx):
        """Vérifie tes buffs actifs"""
        if ctx.author.id not in self.active_buffs:
            await ctx.send("❌ Aucun buff actif!")
            return
        
        embed = discord.Embed(title="✨ Tes buffs actifs", color=0xffff00)
        for buff_type, expiry in self.active_buffs[ctx.author.id].items():
            if datetime.now() < expiry:
                time_left = expiry - datetime.now()
                hours = int(time_left.total_seconds() // 3600)
                minutes = int((time_left.total_seconds() % 3600) // 60)
                embed.add_field(
                    name=buff_type.replace("_", " ").title(),
                    value=f"Expire dans {hours}h {minutes}m",
                    inline=False
                )
        
        await ctx.send(embed=embed)

    # Hook pour le multiplicateur de points
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.content.startswith("j!"):
            return
        
        # Vérifier les buffs
        points_to_add = 0.1
        
        if self.has_active_buff(message.author.id, "multiplier"):
            points_to_add *= 2
            
        if self.has_active_buff(message.author.id, "golden_message"):
            # Mettre en évidence le message
            embed = discord.Embed(description=f"✨ **MESSAGE DORÉ** ✨\n{message.content}", color=0xffd700)
            embed.set_author(name=message.author.display_name, icon_url=message.author.avatar.url)
            await message.channel.send(embed=embed)
            # Retirer le buff
            del self.active_buffs[message.author.id]["golden_message"]

async def setup(bot):
    await bot.add_cog(Shop(bot))