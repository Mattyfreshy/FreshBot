import discord
from discord.ext import commands
import random
import trading as td

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Clear num messages
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.command(name='purge')
    async def purge(self, ctx, amount=0):
        """ Purge [number] messages. (Admin only, Use at your own risk) """
        try:
            await ctx.channel.purge(limit=amount + 1)
        except Exception as e:
            print(e)
            await ctx.send('Missing permissions or invalid number of messages')

    # Clear all messages
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.command(name='purgeAll')
    async def purge_all(self, ctx):
        """ Purge all messages. (Admin only, Use at your own risk) """
        try:
            limit = 0
            async for _ in ctx.channel.history(limit=None):
                limit += 1
            await ctx.channel.purge(limit=limit)
        except Exception as e:
            print(e)
            await ctx.send('Missing permissions')

    @commands.command(name='hello')
    async def hello(self, ctx):
        """ Howdy """
        await ctx.send('Rise and shine Barbie, its gona be a good day!')
    
    @commands.command(name='roll')
    async def roll(self, ctx): 
        """ Roll a Dice """
        await ctx.send(str(random.randint(1,6)))

    @commands.command(name='random')
    async def random(self, ctx, lower, upper):
        """ Get a random number [min] [max] """
        try:
            await ctx.send(str(random.randint(int(lower), int(upper))))
        except Exception as e:
            print(e)
            await ctx.send('Error getting random number')
    
    @commands.command(name='quote')
    async def quote(self, ctx, stock):
        """ Get [stock] quote """
        try:
            await ctx.send(round(float(td.get_quote(stock.upper())), 2))
        except Exception as e:
            print(e)
            await ctx.send('Error getting quote or quote does not exist')

async def setup(bot):
    await bot.add_cog(Commands(bot))