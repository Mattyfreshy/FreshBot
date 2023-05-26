import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import FreshBot as fb
import random
import trading as td

class Commands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self): 
        print('Commands Cog is ready.')

    # Command Error handling
    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        print(fb.get_time_format(12))
        print("Commands Cog Error: \n", error, "\n")
        await ctx.reply(error, ephemeral=True)

    # Clear num messages
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator = True, manage_messages=True)
    @app_commands.command(name='delete')
    async def purge(self, interaction: discord.Interaction, amount: int=0):
        """ Delete [number] messages. (Admin only, Use at your own risk) """
        try:
            await interaction.response.defer(ephemeral=True)
            await interaction.channel.purge(limit=amount)
            await interaction.followup.send(f'Deleted {amount} messages')
        except Exception as e:
            print(e)
            await interaction.response.send_message('Missing permissions or invalid number of messages', ephemeral=True)

    # Clear all messages
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator = True, manage_messages=True)
    @app_commands.command(name='purge')
    async def purge_all(self, interaction: discord.Interaction):
        """ Purge all messages. (Admin only, Use at your own risk) """
        try:
            await interaction.response.defer(ephemeral=True)
            limit = 0
            async for _ in interaction.channel.history(limit=None):
                limit += 1
            await interaction.channel.purge(limit=limit)
            await interaction.followup.send(f'Purged {limit} messages', ephemeral=True)
        except Exception as e:
            print(e)
            await interaction.response.send_message('Missing permissions', ephemeral=True)

    @app_commands.command(name='hello')
    async def hello(self, interaction: discord.Interaction):
        """ Howdy """
        await interaction.response.send_message('Rise and shine Barbie, its gona be a good day!')
    
    @app_commands.command(name='roll')
    async def roll(self, interaction: discord.Interaction): 
        """ Roll a Dice """
        await interaction.response.send_message(str(random.randint(1,6)))

    @app_commands.command(name='random')
    async def random(self, interaction: discord.Interaction, lower: int, upper: int):
        """ Get a random number [min] [max] """
        try:
            await interaction.response.send_message(str(random.randint(int(lower), int(upper))))
        except Exception as e:
            print(e)
            await interaction.response.send_message('Error getting random number', ephemeral=True)
    
    @app_commands.command(name='quote')
    async def quote(self, interaction: discord.Interaction , stock: str):
        """ Get [stock] quote """
        try:
            await interaction.response.send_message(td.get_quote(stock.upper()))
        except Exception as e:
            print(e)
            await interaction.response.send_message('Error getting quote or quote does not exist', ephemeral=True)

async def setup(bot):
    await bot.add_cog(Commands(bot))