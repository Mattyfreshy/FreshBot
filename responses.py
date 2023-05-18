import discord
import random, trading
from enum import Enum

# Enum to store information about every command
class Inputs(Enum):
    help = "List of commands"
    roll = "Roll a Dice"
    random = "Get a random number [min] [max]]"
    hello = "Howdy"
    quote = "Get [stock] quote: "
    purge = "Purge [number] messages. (Admin only)"
    
    
# Function to handle responses
async def handle_responses(message: discord.Message, trigger) -> str:
    args = message.split(' ')[1:]
    command = message.split(' ')[0].lower()

    if command == "help":
        # generate list of commands w/ corresponding information.
        help_lst = ['Below is a list of commands called with public/private trigger ' + trigger + ': \n']
        for i in Inputs:
            help_lst.append(i.name.capitalize() + ': ' + i.value)
            
        return '\n'.join(help_lst)

    elif command == 'purge':
        try:
            if message.author.guild_permissions.administrator:
                await message.channel.purge(limit=int(args[0]) + 1)
                return 'Purged ' + str(args[0]) + ' messages' if int(args[0]) <= 100 else 'Max purge is 100 messages'
            else:
                return 'Purge failed: user does not have admin permissions'
        except Exception as e:
            print(e)
            return 'Error purging messages'
    
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
    
    return 'Message not handled'
