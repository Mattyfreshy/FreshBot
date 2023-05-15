import random
from enum import Enum

# Enum to store information about every command
class Inputs(Enum):
    help = "List of commands"
    roll = "Roll a Dice"
    hello = "Howdy"
    
    
# Function to handle responses
def handle_responses(message, trigger) -> str:
    p_message = message.lower()
    
    if p_message == 'hello':
        return 'Howdy!'
    
    if p_message == 'roll':
        return str(random.randint(1,6))   
    
    if p_message == "help":
        # generate list of commands w/ corrosponding information.
        help_lst = ['Below is a list of commands called with trigger ' + trigger + ': \n']
        for i in Inputs:
            help_lst.append(i.name.capitalize() + ': ' + i.value)
            
        return '\n'.join(help_lst)
    
    return 'Message not handled'
