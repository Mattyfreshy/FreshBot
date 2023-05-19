import discord
from discord.ext import commands

class ChatGPT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Say something
    @commands.command(name='say')
    async def say(self, ctx, *, message):
        """ Say something """
        await ctx.send(message)

async def setup(bot):
    await bot.add_cog(ChatGPT(bot))