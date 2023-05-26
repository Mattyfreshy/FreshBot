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

    # Defers response
    async def defer_response(self, interaction: discord.Interaction, coroutine: asyncio.coroutines, response: str):
        try:
            print("Deferring '/' commands")
            await interaction.response.defer(ephemeral=True)
            await coroutine
            await interaction.followup.send(response)
        except Exception as e:
            print(e)
            await interaction.response.send_message('Error executing, invalid parameters, or Missing permissions', ephemeral=True)

    # Clear num messages
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator = True, manage_messages=True)
    @app_commands.command(name='delete')
    async def delete(self, interaction: discord.Interaction, amount: int=0):
        """ Delete [number] messages. (Admin only, Use at your own risk) """
        await self.defer_response(interaction, interaction.channel.purge(limit=amount), f'Deleted {amount} messages')

    # Clear all messages
    @app_commands.guild_only()
    @app_commands.default_permissions(administrator = True, manage_messages=True)
    @app_commands.command(name='purge')
    async def purge(self, interaction: discord.Interaction):
        """ Purge all messages. (Admin only, Use at your own risk) """
        limit = 0
        async for _ in interaction.channel.history(limit=None):
            limit += 1
        await self.defer_response(interaction, interaction.channel.purge(limit=limit), f'Purged {limit} messages')
    
    @commands.hybrid_command(name='hello')
    async def hello(self, ctx: commands.Context):
        """ Howdy """
        await ctx.send('Rise and shine Barbie, its gona be a good day!')
    
    @commands.hybrid_command(name='roll')
    async def roll(self, ctx: commands.Context): 
        """ Roll a Dice """
        await ctx.send(str(random.randint(1,6)))

    @commands.hybrid_command(name='random')
    async def random(self, ctx: commands.Context, lower: int, upper: int):
        """ Get a random number [min] [max] """
        try:
            await ctx.send(str(random.randint(int(lower), int(upper))))
        except Exception as e:
            print(e)
            await ctx.send('Error getting random number', ephemeral=True)
    
    @commands.hybrid_command(name='quote')
    async def quote(self, ctx: commands.Context, stock: str):
        """ Get [stock] quote """
        try:
            await ctx.send(td.get_quote(stock.upper()))
        except Exception as e:
            print(e)
            await ctx.send('Error getting quote or quote does not exist', ephemeral=True)

async def setup(bot):
    await bot.add_cog(Commands(bot))