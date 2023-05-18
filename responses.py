import discord
from discord.ext import commands
import FreshBot as fb
import random, trading
from enum import Enum

## NO LONGER SUPPORTED SINCE SWITCH TO BOT FROM CLIENT ##

# Enum to store information about every command
class Inputs(Enum):
    help = "List of commands"
    roll = "Roll a Dice"
    random = "Get a random number [min] [max]]"
    hello = "Howdy"
    quote = "Get [stock] quote: "
    clear = "Clear [number] messages not including this message. (Admin only, Use at your own risk)"
    
    
# Function to handle responses
async def handle_responses(message, trigger) -> str:
    args = message.split(' ')[1:]
    command = message.split(' ')[0].lower()

    if command == "help":
        # generate list of commands w/ corresponding information.
        help_lst = ['Below is a list of commands called with public/private trigger ' + trigger + ': \n']
        for i in Inputs:
            help_lst.append(i.name.capitalize() + ': ' + i.value)
            
        return '\n'.join(help_lst)
    
    elif command == 'clear':
        # Clear messages
        @fb.bot.command()
        async def clear(messages, amount=0):
            if messages.author.permissions_in(messages.channel).administrator:
                await messages.channel.purge(limit=amount)
            else:
                await messages.send("You don't have permissions to do that")
        
        clear()
    
    elif command == 'hello':
        return 'Rise and shine Barbie, its gona be a good day!'
    
    elif command == 'roll':
        return str(random.randint(1,6))   
    
    elif command == 'random':
        try:
            return str(random.randint(int(args[0]), int(args[1])))
        except Exception as e:
            print(e)
            return 'Error getting random number'
    
    elif command == 'quote':
        try:
            return trading.get_quote(args[0].upper())
        except Exception as e:
            print(e)
            return 'Error getting quote or quote does not exist'
    
    else:
        return 'Message not handled'

@fb.bot.command()
async def ping(ctx: commands.context.Context):
    await ctx.channel.send("pong")