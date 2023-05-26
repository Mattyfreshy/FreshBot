import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View, button
import FreshBot as fb

import asyncio
import itertools
import sys
import traceback
from async_timeout import timeout
from functools import partial
from yt_dlp import YoutubeDL

ytdlopts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
}

ffmpegopts = {
    # Optimized for streaming
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -filter:a "volume=.75"'
}

ytdl = YoutubeDL(ytdlopts)


class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""


class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid Voice Channels."""


class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester

        self.title = data.get('title')
        self.web_url = data.get('webpage_url')

    def __getitem__(self, item: str):
        """Allows us to access attributes similar to a dict.
        This is only useful when you are NOT downloading.
        """
        return self.__getattribute__(item)
    
    def create_embed(url, info):
        title = info.get('title', None)
        thumbnail = info.get('thumbnail', None)
        duration = info.get('duration', None)

        duration_minutes = int(duration / 60)
        duration_seconds = int(duration % 60)
        duration_formatted = "{:d}:{:02d}".format(duration_minutes, duration_seconds)
        
        embed = discord.Embed(description="", color=1412061)
        embed.set_thumbnail(url=thumbnail)
        embed.add_field(name="Song:", value=f"[{title}]({url})", inline=False)
        embed.add_field(name="Song length:", value=duration_formatted, inline=False)

        return embed

    @classmethod
    async def create_source(cls, ctx, search: str, *, download=False):
        loop = asyncio.get_event_loop()

        url = search
        if not "http" in search: #Checks whether the user provided a link or a name
            search_results = ytdl.extract_info(url=f"ytsearch:{search}", download=download)
            url = search_results['entries'][0]['webpage_url']

        to_run = partial(ytdl.extract_info, url=url, download=download)
        data = await loop.run_in_executor(None, to_run)
        # data = to_run

        embed = cls.create_embed(url=url, info=data)
        await ctx.send(embed=embed)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        await ctx.send(f'```ini\n[Added {data["title"]} to the Queue.]\n```')
    
        if download:
            source = ytdl.prepare_filename(data)
        else:
            # source = data['formats'][0]['url']
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}

        return cls(discord.FFmpegPCMAudio(source, **ffmpegopts), data=data, requester=ctx.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        """Used for preparing a stream, instead of downloading.
        Since Youtube Streaming links expire."""
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)
        # data = ytdl.extract_info(url=data['webpage_url'], download=False)

        return cls(discord.FFmpegPCMAudio(data['url'], **ffmpegopts), data=data, requester=requester)


class MusicPlayer():
    """A class which is assigned to each guild using the bot for Music.
    This class implements a queue and loop, which allows for different guilds to listen to different playlists
    simultaneously.
    When the bot disconnects from the Voice it's instance will be destroyed.
    """

    __slots__ = ('bot', '_guild', '_channel', '_cog', 'queue', 'next', 'current', 'np', 'volume')

    def __init__(self, ctx: discord.Interaction):
        self.bot = ctx.client
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None  # Now playing message
        self.volume = .5
        self.current = None

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Our main player loop."""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(60 * 10):  # 10 minutes...
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self._guild)

            if not isinstance(source, YTDLSource):
                # Source was probably a stream (not downloaded)
                # So we should regather to prevent stream expiration
                try:
                    source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
                except Exception as e:
                    await self._channel.send(f'There was an error processing your song.\n'
                                             f'```css\n[{e}]\n```')
                    continue

            source.volume = self.volume
            self.current = source

            self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            self.np = await self._channel.send(f'**Now Playing:** `{source.title}` requested by '
                                               f'`{source.requester}`')
            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            # source.cleanup()  # Can cause I/O operation on closed file Error
            self.current = None

            try:
                # We are no longer playing this song...
                await self.np.delete()
            except discord.HTTPException:
                pass

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class Music(commands.Cog):
    """Music related commands."""

    __slots__ = ('bot', 'players')

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    # @commands.Cog.listener()
    async def on_ready(self): 
        print('Music Cog is ready.')

    # Command Error handling
    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        print(fb.get_time_format(12))
        print("Music Cog Error: \n", error, "\n")
        await ctx.reply(error, ephemeral=True)

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    async def __local_check(self, ctx):
        """A local check which applies to all commands in this cog."""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def __error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send('This command can not be used in Private Messages.')
            except discord.HTTPException:
                pass
        elif isinstance(error, InvalidVoiceChannel):
            await ctx.send('Error connecting to Voice Channel. '
                           'Please make sure you are in a valid channel or provide me with one')

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def get_player(self, ctx: discord.Interaction):
        """Retrieve the guild player, or generate one."""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player
    
    async def defer_response(self, interaction: discord.Interaction, coroutine: asyncio.coroutines, command: str, response: str):
        """ Defers responses to get around 3 second response time limit """
        try:
            print(f'Deferring {command} command')
            await interaction.response.defer(ephemeral=True)
            await coroutine
            await interaction.followup.send(response)
        except Exception as e:
            print(e)
            await interaction.response.send_message('Error deferring', ephemeral=True)

    async def connect_(self, interaction: discord.Interaction, *, channel: discord.VoiceChannel=None):
        """Connect to voice. """
        """
        Parameters
        ------------
        channel: discord.VoiceChannel [Optional]
            The channel to connect to. If a channel is not specified, an attempt to join the voice channel you are in
            will be made.
        This command also handles moving the bot to different channels.
        """
        if not channel:
            try:
                channel = interaction.user.voice.channel
            except AttributeError:
                await interaction.response.send_message('No channel to join. Please either specify a valid channel or join one.')
                return
                # raise InvalidVoiceChannel('No channel to join. Please either specify a valid channel or join one.')

        vc = interaction.guild.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Moving to channel: <{channel}> timed out.')
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Connecting to channel: <{channel}> timed out.')

        await interaction.response.send_message(f'Connected to: **{channel}**', delete_after=20)

    @app_commands.command(name='join')
    async def join_(self, interaction: discord.Interaction, *, channel: discord.VoiceChannel=None):
        """Connect to voice. """
        await self.connect_(interaction, channel=channel)

    @app_commands.command(name='leave')
    async def leave_(self, interaction: discord.Interaction):
        """Disconnect from voice.
            This command also stops the music if it's playing.
        """
        vc = interaction.guild.voice_client

        if not vc:
            return await interaction.response.send_message('I am not currently connected to voice!')

        await self.cleanup(interaction.guild)

    @app_commands.command(name='play')
    async def play_(self, interaction: discord.Interaction, *, search: str):
        """Request a song and add it to the queue. """
        """
        This command attempts to join a valid voice channel if the bot is not already in one.
        Uses YTDL to automatically search and retrieve a song.
        Parameters
        ------------
        search: str [Required]
            The song to search and retrieve using YTDL. This could be a simple search, an ID or URL.
        """
        vc = interaction.guild.voice_client

        if not vc:
            await self.connect_(interaction)

        player = self.get_player(interaction)

        # If download is False, source will be a dict which will be used later to regather the stream.
        # If download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
        source = await YTDLSource.create_source(interaction, search, download=False)
        
        await player.queue.put(source)

    @commands.command(name='pause')
    async def pause_(self, ctx):
        """Pause the currently playing song."""
        vc = ctx.voice_client
        await ctx.trigger_typing()


        if not vc or not vc.is_playing():
            return await ctx.send('I am not currently playing anything!', delete_after=20)
        elif vc.is_paused():
            return

        vc.pause()
        await ctx.send(f'**`{ctx.author}`**: Paused the song!')

    @commands.command(name='resume')
    async def resume_(self, ctx):
        """Resume the currently paused song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently playing anything!', delete_after=20)
        elif not vc.is_paused():
            return

        vc.resume()
        await ctx.send(f'**`{ctx.author}`**: Resumed the song!')

    @commands.command(name='skip')
    async def skip_(self, ctx):
        """Skip the song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am currently not in a channel!', delete_after=20)

        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return await ctx.send('I am not currently playing anything!', delete_after=20)

        vc.stop()
        queue = self.get_player(ctx).queue
        if not queue.empty(): #Checks if there is a track in the queue
            await ctx.send(f'**`{ctx.author}`**: Skipped the song!')
            next_song = await queue.get()
            await self.play_(ctx, next_song)
        else:
            await ctx.send('There is no next song on the waiting list.')

    @commands.command(name='clear')
    async def clear_(self, ctx):
        """Clears the queue."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am currently not in a channel!', delete_after=20)

        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return await ctx.send('I am not currently playing anything!', delete_after=20)

        vc.stop()
        self.get_player(ctx).queue = asyncio.Queue()
        await ctx.send(f'**`{ctx.author}`**: Cleared the queue!')

    @commands.command(name='queue')
    async def queue_info(self, ctx):
        """Retrieve a basic queue of upcoming songs."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently connected to voice!', delete_after=20)

        player = self.get_player(ctx)
        if player.queue.empty():
            return await ctx.send('There are currently no queued songs.')

        # Grab up to 5 entries from the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, 5))

        fmt = '\n'.join(f'**`{_["title"]}`**' for _ in upcoming)
        embed = discord.Embed(title=f'Upcoming - Next {len(upcoming)}', description=fmt)

        await ctx.send(embed=embed)

    @commands.command(name='now_playing')
    async def now_playing_(self, ctx):
        """Display information about the currently playing song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently connected to voice!', delete_after=20)

        player = self.get_player(ctx)
        if not player.current:
            return await ctx.send('I am not currently playing anything!')

        try:
            # Remove our previous now_playing message.
            await player.np.delete()
        except discord.HTTPException:
            pass

        player.np = await ctx.send(f'**Now Playing:** `{vc.source.title}` '
                                   f'requested by `{vc.source.requester}`')

    @commands.command(name='volume')
    async def change_volume(self, ctx, *, vol: float):
        """Change the player volume.
        Parameters
        ------------
        volume: float or int [Required]
            The volume to set the player to in percentage. This must be between 1 and 100.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently connected to voice!', delete_after=20)

        if not 0 < vol < 101:
            return await ctx.send('Please enter a value between 1 and 100.')

        player = self.get_player(ctx)

        if vc.source:
            vc.source.volume = vol / 100

        player.volume = vol / 100
        await ctx.send(f'**`{ctx.author}`**: Set the volume to **{vol}%**')

    @commands.command(name='stop')
    async def stop_(self, ctx):
        """Stop the currently playing song and destroy the player.
        !Warning!
            This will destroy the player assigned to your guild, also deleting any queued songs and settings.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently playing anything!', delete_after=20)

        await self.cleanup(ctx.guild)

# class buttons(View):
#     def __init__(self):
#         super().__init__(timeout=None)
#         self.value = None

#     @button(label='Play', style=discord.ButtonStyle.green)
#     async def play(self, button: Button, interaction: Interaction):
#         self.value = True

#         await interaction.response.edit_message(view=self)


async def setup(bot):
    await bot.add_cog(Music(bot))