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
async def get_quote(channels):
    while True:
        # Variables
        delay = 15 # seconds
        date = "Date: " + str(dt.date.today().strftime("%m/%d/%Y"))
        spacer = "**" + ''.join(["\*"] * (len(date) + 6)) + "**"
        def marketStatus(): return dt.time(9, 30) <= dt.datetime.now().time() <= dt.time(16, 00)
        # def marketStatus(): return True

        # Print and send todays date
        if marketStatus():
            print(date)
            response = spacer + "\n**\* " + date + " \*** \n" + spacer
            for channel in channels:
                await channel.send(response)

        # Get quote while time is between 9:30 and 4:00
        while marketStatus():
            try:
                response = "------------------\n"
                response += "**Time: " + str(dt.datetime.now().time().strftime("%H:%M")) + "**\n"
                response += td.get_stock_quotes()
                response += "------------------\n"
                for channel in channels:
                    # Get Quote timestamp to terminal
                    print("\nGetting quote for: " + channel.guild.name)
                    print(dt.datetime.now().time(), "\n")

                    # Send quote to channel
                    await channel.send(response)
                
                # 1 * delay minutes between quotes
                await asyncio.sleep(60 * delay) 

            except Exception as e:
                print("Error getting quote: ")
                print(e)
                await asyncio.sleep(1)
            
        # Stop quote
        # print("Stock Market Closed")
        # print(dt.datetime.now().time())
        # print("\n")
        # # await channel.send("Stock Market Closed")
        await asyncio.sleep(delay)
        
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

        # Update playing status
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing , name="!help"))
        
        # Bot Running
        print(f'{bot.user} is now running!')
        print(str(dt.datetime.now().time().strftime("%H:%M")), "\n")

        # Get all 'stock-trading' channels
        channels = []
        for channel in bot.get_all_channels():
            if channel.name == 'stock-trading':
                channels.append(bot.get_channel(channel.id))
        
        # Get quotes for all channels
        await get_quote(channels)

    # On message
    @bot.listen()
    async def on_message(message: discord.Message):
        # Get User infos
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)
        
        # Debug data
        # Ignore bot messages
        if message.author == bot.user:
            return
        print(f"\n{username} said: \n'{user_message}' ({channel})")

    # Run bot
    bot.run(os.getenv('DISCORD_TOKEN'), reconnect=True)
    

    
def main():
    run_discord_bot()
    
if __name__ == '__main__':
    main()