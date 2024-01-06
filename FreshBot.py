import sys, os, discord, asyncio
from discord.ext import commands
from dotenv import load_dotenv
import datetime as dt

# Speech processing for Speech to Text
import speech_recognition as sr
import pydub
from pydub.playback import play
from pydub.utils import make_chunks
from pydub import AudioSegment


# Load environment variables
load_dotenv()

# Speech Recognition
r = sr.Recognizer()

def get_prefix(client, message):
    '''Get prefix for bot'''
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
        
# def process_audio_chunk(chunk):
#     '''Process audio chunk'''
#     audio = sr.AudioData(chunk.raw_data, chunk.frame_rate, chunk.sample_width)
#     try:
#         text = r.recognize_google(audio)
#         print(f"You said: {text}")
#     except sr.UnknownValueError:
#         print("Speech recognition could not understand audio")
#     except sr.RequestError as e:
#         print(f"Could not request results from Google Speech Recognition service; {e}")        

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
        # Debug data
        print(get_time_format(12))
        print(f'{bot.user} is now running!')
        print('Python ', sys.version)
        print('Discord.py ', discord.__version__)
        print('------------------\n')

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
        
    # On Audio Events
    # @bot.event
    # async def on_voice_state_update(member, before, after):
    #     if after.channel is not None and after.channel != before.channel:
    #         if member == bot.user:
    #             voice_client = await after.channel.connect()
    #         else:
    #             voice_client = discord.utils.get(bot.voice_clients, guild=member.guild)

    #         if voice_client is not None and not voice_client.is_playing():
    #             audio_source = voice_client.listen()

    #             # Save audio to a file
    #             audio_file = "audio.wav"
    #             audio_source.save(audio_file)

    #             # Load audio file using pydub
    #             audio = AudioSegment.from_wav(audio_file)

    #             # Process audio using SpeechRecognition
    #             with sr.AudioFile(audio_file) as source:
    #                 audio = r.record(source)
    #                 try:
    #                     text = r.recognize_google(audio)
    #                     print(f"You said: {text}")
    #                 except sr.UnknownValueError:
    #                     print("Speech recognition could not understand audio")
    #                 except sr.RequestError as e:
    #                     print(f"Could not request results from Google Speech Recognition service; {e}")

    #             # Cleanup
    #             voice_client.stop()
    #             await voice_client.disconnect()
    #             audio.export(audio_file, format="wav")

    # Run bot
    bot.run(os.getenv('DISCORD_TOKEN'), reconnect=True)
    

    
def main():
    run_discord_bot()
    
if __name__ == '__main__':
    main()