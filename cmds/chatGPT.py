import discord, os
from discord.ext import commands
import openai
from flask import Flask, redirect, render_template, request, url_for


# Load environment variables
ENABLED = False

class ChatGPT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_message(self, ctx, message):
        if ENABLED:
            await ctx.send(message)
        else:
            await ctx.send("This feature is currently disabled.")

    # Say something
    @commands.command(name='say')
    async def say(self, ctx, *, message):
        """ Say something """
        await self.send_message(ctx, message)
        

async def setup(bot):
    await bot.add_cog(ChatGPT(bot))