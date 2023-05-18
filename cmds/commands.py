import discord
from discord.ext import commands
import random
import trading as td

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Clear messages
    @commands.guild_only()
    @commands.command(name='clear')
    async def clear(self, ctx, amount=0):
        """ Clear [number] messages not including this message. (Admin only, Use at your own risk) """
        if ctx.author.permissions_in(ctx.channel).administrator:
            await ctx.channel.purge(limit=amount + 1)
        else:
            await ctx.send("You don't have permissions to do that")

    @commands.command(name='hello')
    async def hello(self, ctx):
        """ Howdy """
        await ctx.send('Rise and shine Barbie, its gona be a good day!')
    
    @commands.command(name='roll')
    async def roll(self, ctx): 
        """ Roll a Dice """
        await ctx.send(str(random.randint(1,6)))

    @commands.command(name='random')
    async def random(self, ctx, min, max):
        """ Get a random number [min] [max]] """
        try:
            await ctx.send(str(random.randint(int(min), int(max))))
        except Exception as e:
            print(e)
            await ctx.send('Error getting random number')
    
    @commands.command(name='quote')
    async def quote(self, ctx, stock):
        """ Get [stock] quote: """
        try:
            await ctx.send(td.get_quote(stock.upper()))
        except Exception as e:
            print(e)
            await ctx.send('Error getting quote or quote does not exist')

    @commands.command(name='ping')
    async def ping(self, ctx: commands.context.Context):
        await ctx.channel.send("pong")

def setup(bot):
    bot.add_cog(Commands(bot))