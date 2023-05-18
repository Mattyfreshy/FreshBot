import os, discord, responses, asyncio, setup
from discord.ext import commands
from dotenv import load_dotenv

# Other modules imports
import trading as td
import datetime as dt

# Load environment variables
load_dotenv()     
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=setup.get_prefix, intents=intents)
EXTENSIONS = ['cogs.trading', 'cogs.commands', 'cogs.chatGPT']

# Sends message from responses.py based on user message
async def send_message(message, user_message, is_private, trigger):
    try:
        response = await responses.handle_responses(user_message, trigger)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)

# Sends stock quote every minute
async def get_quote(channel):
    # Variables
    date = "Date: " + str(dt.date.today().strftime("%m/%d/%Y"))
    spacer = "**" + ''.join(["\*"] * (len(date) + 6)) + "**"
    def marketStatus(): return dt.time(9, 30) <= dt.datetime.now().time() <= dt.time(16, 00)

    # Print and send todays date
    if marketStatus():
        print(date)
        await channel.send(spacer)
        await channel.send("**\* " + date + " \*** ")
        await channel.send(spacer)

    # Get quote while time is between 9:30 and 4:00
    while marketStatus():
        try:
            # Get Quote to terminal
            print("\nGetting quote...")
            print(dt.datetime.now().time(), "\n")
            await asyncio.sleep(1)

            # Send quote to channel + sleep before next quote
            await channel.send("------------------")
            await channel.send("**Time: " + str(dt.datetime.now().time().strftime("%H:%M")) + "**")
            await channel.send(td.get_stock_quotes())
            await channel.send("------------------")
            await asyncio.sleep(60 * 15) # 1 * n minutes

        except Exception as e:
            print("Error getting quote: ")
            print(e)
            await asyncio.sleep(1)
        
    # Stop quote
    print("Stock Market Closed")
    print(dt.datetime.now().time())
    await channel.send("Stock Market Closed")
    await asyncio.sleep(1)
        
# Run discord bot
def run_discord_bot():
    # On ready
    @bot.event
    async def on_ready():
        # Bot Running
        print(f'{bot.user} is now running!')

        # Get quote
        await get_quote(bot.get_channel(int(os.getenv('CHANNEL_ID'))))

    # On message
    @bot.listen()
    async def on_message(message: discord.Message):
        # prevent bot from responding to itself
        # if message.author == client.user:
        #     return
        
        # Get User infos
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)
        
        # Debug data
        print(f"{username} said: '{user_message}' ({channel})")
        
        # If publicTrigger/privateTrigger used, trigger bot response
        # if user_message[0] == publicTrigger:
        #     user_message = user_message[1:]
        #     await send_message(message, user_message, False, publicTrigger)
        # elif user_message[0] == privateTrigger:
        #     user_message = user_message[1:]
        #     await send_message(message, user_message, True, privateTrigger)
        # elif isinstance(message.channel, discord.channel.DMChannel):
        #     await message.channel.send("ChatGPT support in progress..." )

    # Run bot
    bot.run(os.getenv('DISCORD_TOKEN'), bot=True, reconnect=True)
    

    
def main():
    for extension in EXTENSIONS:
        bot.load_extension(extension)

    run_discord_bot()
    
if __name__ == '__main__':
    main()