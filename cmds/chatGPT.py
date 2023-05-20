import discord, os
from discord.ext import commands
import FreshBot as fb

import openai

# Enable or Disable chatbot features
ENABLED = True

# ChatGPT parameters
ENGINE = "text-davinci-003"
TEMPERATURE = 0.9
MAX_TOKENS = 150
PRESENCE_PENALTY = 0.6

class ChatGPT(commands.Cog):
    def __init__(self, bot):
        # Load variables
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.bot = bot
    
    # Command Error handling
    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        print(fb.get_time_format(12))
        print("ChatGPT Cog Error: \n", error)
    
    # Send message to channel depending on if chatbot is enabled
    async def send_message(self, ctx, message):
        """ Send message to channel depending on if chatbot is enabled """
        if ENABLED:
            await ctx.send(message)
        else:
            await ctx.send("This feature is currently in works.")

    # Get response from GPT API
    async def get_response(self, message):
        """ Get response from GPT API"""
        try:
            response = openai.Completion.create(
                engine=ENGINE,
                prompt=message,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                presence_penalty=PRESENCE_PENALTY,
            )
            return response.choices[0].text
        except Exception as e:
            print("chatGPT Error: ", e)
            return "Error getting response"

    # Ask something (guild only)
    # @commands.guild_only()
    @commands.command(name='ask')
    async def ask(self, ctx, *, message):
        """ Ask the bot something """
        await self.send_message(ctx, await self.get_response(message))
        
    # @commands.dm_only()
    # @commands.command(name='query')
    # async def ask(self, ctx, *, message):
    #     """ Ask the bot something """
    #     await self.send_message(ctx, await self.get_response(message))

async def setup(bot):
    await bot.add_cog(ChatGPT(bot))