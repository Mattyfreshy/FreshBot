import discord, responses
import os
from dotenv import load_dotenv

# Sends message from responses.py based on user message
async def send_message(message, user_message, is_private, trigger):
    try:
        response = responses.handle_responses(user_message, trigger)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

# Run discord bot
def run_discord_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')
        
    @client.event
    async def on_message(message):
        # prevent bot from responding to itself
        if message.author == client.user:
            return
        
        # Get User infos
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)
        
        # Debug data
        print(f"{username} said: '{user_message}' ({channel})")
        
        # If special character used, trigger bot response
        trigger = '!'
        if user_message[0] == trigger:
            user_message = user_message[1:]
            await send_message(message, user_message, False, trigger)
        elif user_message == "help":
            await message.channel.send("Trigger is '" + trigger + "'" )
          
        # use ! to send private messages to user  
        # if user_message[0] == '!':
        #     user_message = user_message[1:]
        #     await send_message(message, user_message, is_private=True)
        # else:
        #     await send_message(message, user_message, is_private=False)
    
    load_dotenv()     
    client.run(os.getenv('DISCORD_TOKEN'))
    
    
def main():
    run_discord_bot()
    
if __name__ == '__main__':
    main()