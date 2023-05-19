import os, discord, responses, asyncio
from discord.ext import commands
from dotenv import load_dotenv

# Other modules imports
import trading as td
import datetime as dt

# Load environment variables
load_dotenv()

def get_prefix(client, message):
    # Public triggers
    prefixes = ['!', '?', '.', '$']
    
    # Private triggers
    if not message.guild:
        return '!'

    # If in guild allow for users to mention bot
    return commands.when_mentioned_or(*prefixes)(client, message)

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
    intents = discord.Intents.default()
    intents.message_content = True
    help_command = commands.DefaultHelpCommand(no_category='Help')
    bot = commands.Bot(command_prefix=get_prefix, help_command=help_command , intents=intents)

    # On ready
    @bot.event
    async def on_ready():
        # Load extensions
        for filename in os.listdir('./cmds'):
            if filename.endswith('.py'):
                await bot.load_extension(f'cmds.{filename[:-3]}')
        
        # Bot Running
        print(f'{bot.user} is now running!')

        # Get quote
        await get_quote(bot.get_channel(int(os.getenv('CHANNEL_ID'))))

    # On message
    @bot.listen()
    async def on_message(message: discord.Message):
        # Get User infos
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)
        
        # Debug data
        print(f"{username} said: '{user_message}' ({channel})")

    # Run bot
    bot.run(os.getenv('DISCORD_TOKEN'), reconnect=True)
    

    
def main():
    run_discord_bot()
    
if __name__ == '__main__':
    main()