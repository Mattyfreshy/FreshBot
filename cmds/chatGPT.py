import discord, os
from discord.ext import commands
import openai

# Enable or Disable chatbot features
ENABLED = True

class ChatGPT(commands.Cog):
    def __init__(self, bot):
        # Load variables
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.bot = bot
    
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
                engine="text-davinci-003",
                prompt=message,
                temperature=0.9,
                max_tokens=150,
                presence_penalty=0.6,
            )
            return response.choices[0].text
        except Exception as e:
            print(e)
            return "Error getting response"

    # Ask something
    @commands.guild_only()
    @commands.command(name='ask')
    async def ask(self, ctx, *, message):
        """ Ask the bot something """
        await self.send_message(ctx, await self.get_response(message))
        

async def setup(bot):
    await bot.add_cog(ChatGPT(bot))