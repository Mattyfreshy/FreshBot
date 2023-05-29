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

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        """ Command Error handling """
        print(fb.get_time_format(12))
        print("Commands Cog Error: \n", error, "\n")
        await ctx.reply(error, ephemeral=True)

    async def defer_response(self, interaction: discord.Interaction, coroutine: asyncio.coroutines, command: str, response: str):
        """ Defers responses to get around 3 second response time limit """
        try:
            print(f'Deferring {command} command')
            await interaction.response.defer(ephemeral=True, thinking=True)
            await coroutine
            await interaction.followup.send(response)
        except Exception as e:
            print(e)
            await interaction.response.send_message('Error deferring', ephemeral=True, delete_after=10)

    @app_commands.guild_only()
    @app_commands.default_permissions(administrator = True, manage_messages=True)
    @app_commands.command(name='delete')
    async def delete(self, interaction: discord.Interaction, amount: int=0):
        """ Delete [number] messages. (Use at your own risk) """
        coroutine = interaction.channel.purge(limit=amount)
        await self.defer_response(interaction, coroutine=coroutine, command='delete', response=f'Deleted {amount} messages')

    @app_commands.guild_only()
    @app_commands.default_permissions(administrator = True, manage_messages=True)
    @app_commands.command(name='purge')
    async def purge(self, interaction: discord.Interaction):
        """ Purge all messages. (Use at your own risk) """
        limit = 0
        async for _ in interaction.channel.history(limit=None):
            limit += 1
        coroutine = interaction.channel.purge(limit=limit)
        await self.defer_response(interaction, coroutine=coroutine, command='purge', response=f'Purged {limit} messages')
    
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
            await ctx.send('Error getting random number', ephemeral=True, delete_after=5)
    
    @commands.hybrid_command(name='quote')
    async def quote(self, ctx: commands.Context, stock: str):
        """ Get [stock] quote """
        try:
            await ctx.send(td.get_quote(stock.upper()))
        except Exception as e:
            print(e)
            await ctx.send('Error getting quote or quote does not exist', ephemeral=True, delete_after=5)

async def setup(bot):
    await bot.add_cog(Commands(bot))