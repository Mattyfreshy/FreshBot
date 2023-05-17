import os, discord, responses, asyncio
from dotenv import load_dotenv

# Other modules imports
import trading as td
import datetime as dt

# Sends message from responses.py based on user message
async def send_message(message, user_message, is_private, trigger):
    try:
        response = responses.handle_responses(user_message, trigger)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

# Sends stock quote every minute
async def get_quote(channel):
    # Start quote
    print("Getting quote...")
    print(dt.datetime.now().time())
    await asyncio.sleep(1)

    # Get quote while time is between 9:30 and 4:00
    while dt.time(9, 30) <= dt.datetime.now().time() <= dt.time(16, 00):
        try:
            await channel.send(td.get_stock_quotes())
            await asyncio.sleep(60) # 1 minute
        except Exception as e:
            print("Error getting quote: ")
            print(e)
            await asyncio.sleep(1)
        
    # Stop quote
    print("Quote stopped")
    print(dt.datetime.now().time())
    await asyncio.sleep(1)
        
# Run discord bot
def run_discord_bot():
    # Init discord client
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    # Init/load variables
    load_dotenv()     
    trigger = '!'

    # On ready
    @client.event
    async def on_ready():
        # Client Running
        print(f'{client.user} is now running!')

        # Get quote
        await get_quote(client.get_channel(int(os.getenv('CHANNEL_ID'))))

    # On message
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
        if user_message[0] == trigger:
            user_message = user_message[1:]
            await send_message(message, user_message, False, trigger)
        elif isinstance(message.channel, discord.channel.DMChannel):
            await message.channel.send("ChatGPT support in progress..." )
          
        # use ! to send private messages to user  
        # if user_message[0] == '!':
        #     user_message = user_message[1:]
        #     await send_message(message, user_message, is_private=True)
        # else:
        #     await send_message(message, user_message, is_private=False)

    # Run bot
    client.run(os.getenv('DISCORD_TOKEN'))
    
    
def main():
    run_discord_bot()
    
if __name__ == '__main__':
    main()