import os, discord, responses, asyncio
from discord.ext import commands
from dotenv import load_dotenv

# Other modules imports
import trading as td
import datetime as dt

def get_prefix(client, message):
    # Public triggers
    prefixes = ['!', '?', '.']
    
    # Private triggers
    if not message.guild:
        return '$'

    # If in guild allow for users to mention bot
    return commands.when_mentioned_or(*prefixes)(client, message)
