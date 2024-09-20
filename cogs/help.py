import discord
from discord.ext import commands

class CustomHelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help_command(self, ctx, specific_command: str = None):
        if specific_command:
            # Afficher l'aide pour une commande spécifique
            command = self.bot.get_command(specific_command)
            if command:
                embed = discord.Embed(title=f"Aide pour la commande : {command.name}", color=discord.Color.blue())
                embed.add_field(name="Description", value=command.help or "Aucune description disponible.", inline=False)
                embed.add_field(name="Utilisation", value=f"`{ctx.prefix}{command.name} {command.signature}`", inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"La commande '{specific_command}' n'existe pas.")
        else:
            # Afficher toutes les commandes par cog
            embed = discord.Embed(title="Liste des commandes", description="Voici toutes les commandes disponibles:", color=discord.Color.blue())
            
            for cog_name, cog in self.bot.cogs.items():
                cog_commands = cog.get_commands()
                if cog_commands:
                    command_list = [f"`{ctx.prefix}{cmd.name}`" for cmd in cog_commands]
                    embed.add_field(name=cog_name, value=", ".join(command_list), inline=False)
            
            embed.set_footer(text=f"Utilisez {ctx.prefix}help <commande> pour plus de détails sur une commande spécifique.")
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(CustomHelpCommand(bot))