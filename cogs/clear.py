from discord.ext import commands
import discord

class Clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Cette méthode sera appelée chaque fois qu'un message est envoyé
        if message.author == self.bot.user:
            # Ignorer les messages du bot lui-même
            return 

    @commands.command(name="clear")
    @commands.has_permissions(manage_messages=True, manage_channels=True)
    async def clear(self, ctx, option=None, num_messages: int = None):
        if option == "purge":
            await self.purge_channel(ctx)
        elif option is None and num_messages is None:
            await ctx.send(f"{ctx.author.mention}, veuillez spécifier une option valide (ex: `purge`) ou un nombre de messages à supprimer.")
        elif num_messages is not None:
            await self.delete_messages(ctx, num_messages)
        else:
            await ctx.send(f"{ctx.author.mention}, l'option `{option}` n'est pas valide pour cette commande.")

    async def purge_channel(self, ctx):
        try:
            # Récupérer les informations du channel à recréer
            channel_name = ctx.channel.name
            channel_position = ctx.channel.position
            channel_topic = ctx.channel.topic
            channel_category = ctx.channel.category
            overwrites = ctx.channel.overwrites  # Récupérer les permissions du channel actuel

            # Supprimer le channel actuel
            await ctx.channel.delete()

            # Créer un nouveau channel avec les mêmes paramètres et les mêmes permissions
            new_channel = await ctx.guild.create_text_channel(
                name=channel_name,
                position=channel_position,
                topic=channel_topic,
                category=channel_category,
                overwrites=overwrites  # Appliquer les mêmes permissions
            )

            # Envoyer un message de confirmation
            await new_channel.send(f"Channel `{channel_name}` purgé avec succès et recréé avec les mêmes permissions.")
        except discord.Forbidden:
            await ctx.send(f"{ctx.author.mention}, je n'ai pas les permissions nécessaires pour purger ce channel.")
        except discord.HTTPException as e:
            await ctx.send(f"{ctx.author.mention}, une erreur est survenue lors de la tentative de purge et recréation du channel : {e}")

    async def delete_messages(self, ctx, num_messages: int):
        try:
            # Supprimer le message de commande
            await ctx.message.delete()
            # Supprimer les messages spécifiés
            deleted = await ctx.channel.purge(limit=num_messages)
            await ctx.send(f"{len(deleted)} messages ont été supprimés.", delete_after=5)
        except discord.Forbidden:
            await ctx.send(f"{ctx.author.mention}, je n'ai pas les permissions nécessaires pour supprimer les messages.")
        except discord.HTTPException as e:
            await ctx.send(f"{ctx.author.mention}, une erreur est survenue lors de la suppression des messages : {e}")

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"{ctx.author.mention}, vous n'avez pas les permissions nécessaires pour utiliser cette commande.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{ctx.author.mention}, veuillez spécifier une option valide (ex: `purge`) ou un nombre de messages à supprimer.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"{ctx.author.mention}, argument invalide. Utilisez `j!clear purge` pour purger le canal ou `j!clear <nombre>` pour supprimer un nombre spécifique de messages.")
        else:
            await ctx.send(f"{ctx.author.mention}, une erreur est survenue lors de l'exécution de la commande.")
            raise error  # Relever l'erreur si ce n'est pas un problème de permission

async def setup(bot):
    await bot.add_cog(Clear(bot))