import sys, os, discord, asyncio
from discord.ext import commands
from dotenv import load_dotenv
import trading as td
import datetime as dt


load_dotenv()

def get_prefix(client, message):
    # Public triggers
    prefixes = ['!', '?', '.', '$']
    
    # Private triggers
    if not message.guild:
        return '!'

    # If in guild allow for users to mention bot
    return commands.when_mentioned_or(*prefixes)(client, message)

def get_time_format(format):
    """ 
    Return time format depending on user preference
    - 12 hour (default) 
    - 24 hour 
    """
    if format == '12':
        return dt.datetime.now().strftime("%m-%d-%Y %I:%M %p")
    elif format == '24':
        return dt.datetime.now().strftime("%H:%M")
    else:
        return dt.datetime.now().strftime("%m-%d-%Y %I:%M %p")

async def get_quote(channels, enabled):
    """ Send stock quote every minute """

    while enabled:
        # Variables
        delay = 15 # seconds
        date = "Date: " + str(dt.date.today().strftime("%m/%d/%Y"))
        spacer = "**" + ''.join(["\*"] * (len(date) + 6)) + "**"
        def marketStatus(): 
            weekday = dt.date.today().weekday() <= 4
            time = dt.time(9, 30) <= dt.datetime.now().time() <= dt.time(16, 00)
            return weekday and time
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
                response += "**Time: " + get_time_format(12) + "**\n"
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
        
def run_discord_bot():
    """ Run discord bot """

    intents = discord.Intents.default()
    intents.message_content = True
    intents.voice_states = True
    help_command = commands.DefaultHelpCommand(no_category='Help')
    bot = commands.Bot(command_prefix=get_prefix, help_command=help_command , intents=intents)

    # Ignore List
    ignore = ['music_hybrid.py']

    # load extensions/cogs
    async def load():
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py') and not filename in ignore:
                await bot.load_extension(f'cogs.{filename[:-3]}')

    # On ready
    @bot.event
    async def on_ready():
        # Clear terminal screen
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Load extensions
        await load()

        # Load slash commands. Global sync.
        try:
            synced = await bot.tree.sync()
            print(f"Synced {len(synced)} commands/n")
        except Exception as e:
            print(e)

        # Update playing status
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing , name="Your Mom!"))
        
        # Bot Running
        print(get_time_format(12))
        print(f'{bot.user} is now running!')
        print('Python ', sys.version)
        print('Discord.py ', discord.__version__)
        print('------------------\n')

        # Get all 'stock-trading' channels
        channels = []
        for channel in bot.get_all_channels():
            if channel.name == 'stock-trading':
                channels.append(bot.get_channel(channel.id))
        
        # Get quotes for all channels
        await get_quote(channels, False)

    # On message
    @bot.listen()
    async def on_message(message: discord.Message):
        # Get User infos
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)
        
        # Debug data
        # Ignore bot messages
        if message.author == bot.user and not isinstance(message.channel, discord.channel.DMChannel):
            return
        print(get_time_format(12))
        print(f"{username} said: \n'{user_message}' ({channel})\n")

    # Run bot
    bot.run(os.getenv('DISCORD_TOKEN'), reconnect=True)
    

    
def main():
    run_discord_bot()
    
if __name__ == '__main__':
    main()