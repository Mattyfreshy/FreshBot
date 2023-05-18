import random, trading
from enum import Enum

# Enum to store information about every command
class Inputs(Enum):
    help = "List of commands"
    roll = "Roll a Dice"
    random = "Get a random number [min] [max]]"
    hello = "Howdy"
    quote = "Get [stock] quote: "
    
    
# Function to handle responses
def handle_responses(message, trigger) -> str:
    args = message.split(' ')[1:]
    command = message.split(' ')[0].lower()

    if command == "help":
        # generate list of commands w/ corrosponding information.
        help_lst = ['Below is a list of commands called with trigger ' + trigger + ': \n']
        for i in Inputs:
            help_lst.append(i.name.capitalize() + ': ' + i.value)
            
        return '\n'.join(help_lst)
    
    if command == 'hello':
        return 'Rise and shine Barbie, its gona be a good day!'
    
    if command == 'roll':
        return str(random.randint(1,6))   
    
    if command == 'random':
        try:
            return str(random.randint(int(args[0]), int(args[1])))
        except Exception as e:
            print(e)
            return 'Error getting random number'
    
    if command == 'quote':
        try:
            return trading.get_quote(args[0].upper())
        except Exception as e:
            print(e)
            return 'Error getting quote or quote does not exist'
    
    return 'Message not handled'
