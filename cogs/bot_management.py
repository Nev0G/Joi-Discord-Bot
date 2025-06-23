import discord
from discord.ext import commands, tasks
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
import os
import logging
import subprocess
import sys

class BotManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.temp_changes_file = 'temp_bot_changes.json'
        self.user_data_file = 'user_data.json'
        self.original_avatar = None
        self.original_name = None
        self.original_status = None
        self.temp_changes = self.load_temp_changes()
        self.cleanup_task.start()
      
    @commands.command(name="updatebot")
    @commands.is_owner()
    async def update_bot(self, ctx):
        await ctx.send("🔄 Mise à jour du bot depuis le dépôt Git en cours...")

        try:
            result = subprocess.run(["git", "pull"], capture_output=True, text=True)
            if result.returncode == 0:
                await ctx.send(f"✅ Mise à jour terminée :\n```{result.stdout.strip()}```")
            else:
                await ctx.send(f"❌ Erreur lors du git pull :\n```{result.stderr.strip()}```")
                return
            
            await ctx.send("♻️ Redémarrage du bot en cours...")

            await self.bot.close()
            os.execl(sys.executable, sys.executable, *sys.argv)

        except Exception as e:
            await ctx.send(f"❌ Une erreur est survenue : `{e}`")

  
    def load_temp_changes(self):
        try:
            if os.path.exists(self.temp_changes_file):
                with open(self.temp_changes_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if "status" not in data:
                        data["status"] = None
                    return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.warning(f"Erreur lors du chargement de {self.temp_changes_file}: {e}")
        return {"avatar": None, "name": None, "status": None}

    def save_temp_changes(self):
        try:
            with open(self.temp_changes_file, 'w', encoding='utf-8') as f:
                json.dump(self.temp_changes, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde de {self.temp_changes_file}: {e}")

    def load_user_data(self):
        try:
            if os.path.exists(self.user_data_file):
                with open(self.user_data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.warning(f"Erreur lors du chargement de {self.user_data_file}: {e}")
        return {}

    def save_user_data(self, data):
        try:
            with open(self.user_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde de {self.user_data_file}: {e}")

    def deduct_user_points(self, user_id, points):
        user_data = self.load_user_data()
        user_id = str(user_id)
        if user_id not in user_data or user_data[user_id].get('points', 0) < points:
            return False
        user_data[user_id]['points'] -= points
        self.save_user_data(user_data)
        return True

    def refund_user_points(self, user_id, points):
        user_data = self.load_user_data()
        user_id = str(user_id)
        if user_id not in user_data:
            user_data[user_id] = {'points': 0}
        user_data[user_id]['points'] += points
        self.save_user_data(user_data)

    async def save_original_values(self):
        try:
            if self.original_avatar is None and self.bot.user.avatar:
                self.original_avatar = await self.bot.user.avatar.read()
            if self.original_name is None:
                self.original_name = self.bot.user.display_name or self.bot.user.name
            if self.original_status is None:
                self.original_status = {'activity': self.bot.activity, 'status': self.bot.status}
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde des valeurs originales: {e}")

    @tasks.loop(minutes=30)
    async def cleanup_task(self):
        try:
            current_time = datetime.now()
            changes_made = False
            avatar_data = self.temp_changes.get("avatar")
            if avatar_data and datetime.fromisoformat(avatar_data["expires_at"]) <= current_time:
                if self.original_avatar:
                    try:
                        await self.bot.user.edit(avatar=self.original_avatar)
                        print("✅ Avatar restauré")
                    except discord.HTTPException as e:
                        print(f"❌ Erreur avatar: {e}")
                self.temp_changes["avatar"] = None
                changes_made = True

            name_data = self.temp_changes.get("name")
            if name_data and datetime.fromisoformat(name_data["expires_at"]) <= current_time:
                if self.original_name:
                    try:
                        await self.bot.user.edit(username=self.original_name)
                        print("✅ Nom restauré")
                    except discord.HTTPException as e:
                        print(f"❌ Erreur nom: {e}")
                self.temp_changes["name"] = None
                changes_made = True

            status_data = self.temp_changes.get("status")
            if status_data and datetime.fromisoformat(status_data["expires_at"]) <= current_time:
                if self.original_status:
                    try:
                        await self.bot.change_presence(activity=self.original_status['activity'], status=self.original_status['status'])
                        print("✅ Statut restauré")
                    except Exception as e:
                        print(f"❌ Erreur statut: {e}")
                self.temp_changes["status"] = None
                changes_made = True

            if changes_made:
                self.save_temp_changes()
        except Exception as e:
            logging.error(f"❌ Erreur dans cleanup_task: {e}")

    @cleanup_task.before_loop
    async def before_cleanup_task(self):
        await self.bot.wait_until_ready()

    @commands.command(name="botstatus", aliases=["status_info"])
    async def show_bot_status_info(self, ctx):
        embed = discord.Embed(title="🤖 État du Bot", description="Modifications actives", color=0x3498db, timestamp=datetime.now())
        activity_text = "Aucune"
        if self.bot.activity:
            activity_text = f"{self.bot.activity.type.name.title()}: {self.bot.activity.name}"
        embed.add_field(name="📊 Informations Actuelles", value=f"**Nom :** {self.bot.user.display_name or self.bot.user.name}\n**Statut :** {self.bot.status.name.title()}\n**Activité :** {activity_text}", inline=False)

        active_changes = []

        avatar_data = self.temp_changes.get("avatar")
        if avatar_data:
            try:
                expires = datetime.fromisoformat(avatar_data["expires_at"])
                user_id = avatar_data["user_id"]
                user = self.bot.get_user(user_id)
                user_mention = user.mention if user else f"<@{user_id}>"
                active_changes.append(f"🖼️ **Avatar** - Par {user_mention}\nExpire <t:{int(expires.timestamp())}:R>")
            except (ValueError, KeyError):
                self.temp_changes["avatar"] = None

        name_data = self.temp_changes.get("name")
        if name_data:
            try:
                expires = datetime.fromisoformat(name_data["expires_at"])
                user_id = name_data["user_id"]
                user = self.bot.get_user(user_id)
                user_mention = user.mention if user else f"<@{user_id}>"
                active_changes.append(f"📝 **Nom** - Par {user_mention}\nExpire <t:{int(expires.timestamp())}:R>")
            except (ValueError, KeyError):
                self.temp_changes["name"] = None

        status_data = self.temp_changes.get("status")
        if status_data:
            try:
                expires = datetime.fromisoformat(status_data["expires_at"])
                user_id = status_data["user_id"]
                user = self.bot.get_user(user_id)
                user_mention = user.mention if user else f"<@{user_id}>"
                status_type = status_data["activity_type"]
                status_text = status_data["text"]
                active_changes.append(f"🎮 **Statut** - Par {user_mention}\n{status_type.title()}: {status_text}\nExpire <t:{int(expires.timestamp())}:R>")
            except (ValueError, KeyError):
                self.temp_changes["status"] = None

        if active_changes:
            embed.add_field(name="🔄 Modifications Actives", value="\n\n".join(active_changes), inline=False)
        else:
            embed.add_field(name="✅ État Normal", value="Aucune modification temporaire active", inline=False)

        if self.original_name or self.original_avatar or self.original_status:
            original_info = []
            if self.original_name:
                original_info.append(f"**Nom original :** {self.original_name}")
            if self.original_avatar:
                original_info.append("**Avatar original :** Sauvegardé")
            if self.original_status:
                original_info.append("**Statut original :** Sauvegardé")
            embed.add_field(name="💾 Valeurs de Sauvegarde", value="\n".join(original_info), inline=False)

        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BotManagement(bot))
