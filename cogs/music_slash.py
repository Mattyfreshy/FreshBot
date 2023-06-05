import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View, button
import json

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
    'source_address': '0.0.0.0',  # ipv6 addresses cause issues sometimes
    'extract_flat': 'in_playlist',
    'skip_download': True
}

ffmpegopts = {
    # Optimized for streaming
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -filter:a "volume=0.25"'
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
        self.data = data

    def __getitem__(self, item: str):
        """Allows us to access attributes similar to a dict.
        This is only useful when you are NOT downloading.
        """
        return self.__getattribute__(item)
    
    def discord_requester(interaction: discord.Interaction):
        """Returns the discord user who requested the song"""
        name = interaction.user.name
        discriminator = interaction.user.discriminator
        mention = interaction.user.mention
        return f'{mention}'

    async def create_embed(interaction: discord.Interaction, url, info, header, vol):
        """Creates an embed for the current song"""
        is_playlist = 'playlist?list=' in url
        title = info.get('title', None)
        thumbnail = info.get('thumbnails' if is_playlist else 'thumbnail', None)

        # If the thumbnail is a list, get the first element 'url' from it
        if isinstance(thumbnail, list) and 'url' in thumbnail[0]:
            thumbnail = thumbnail[0]['url']
        
        embed = discord.Embed(description=header, color=1412061)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)
        embed.set_thumbnail(url=thumbnail)
        embed.add_field(name='', value=f"[{title}]({url})", inline=False)

        if not is_playlist:
            duration = info.get('duration', None)
            duration_minutes = int(duration / 60)
            duration_seconds = int(duration % 60)
            duration_formatted = "{:d}:{:02d}".format(duration_minutes, duration_seconds)
            embed.add_field(name="Song length: ", value=duration_formatted, inline=True)
        
        embed.add_field(name="Volume: ", value=f"{vol * 100}%", inline=True)

        return embed

    @classmethod
    async def create_source(cls, interaction: discord.Interaction, player, search: str, *, loop, download=False):
        loop = loop or asyncio.get_event_loop()

        url = search
        if not "http" in search: #Checks whether the user provided a link or a name
            search_results = ytdl.extract_info(url=f"ytsearch:{search}", download=download)
            url = search_results['entries'][0]['url']

        try:
            to_run = partial(ytdl.extract_info, url=url, download=download)
            data = await loop.run_in_executor(None, to_run)
            # data = ytdl.extract_info(url=url, download=download)
        except Exception as e:
            print(e)
            return

        is_playlist = 'playlist?list=' in url
        header = f"**{'Playlist' if 'playlist?list=' in url else 'Song'} Queued - **{cls.discord_requester(interaction=interaction)}"
        vol = player.volume
        embed = await cls.create_embed(interaction=interaction, url=url, info=data, header=header, vol=vol)
        await interaction.response.send_message(embed=embed)

        # Due to dict formatting, we need get entries from playlist
        is_playlist = 'playlist?list=' in url
        if is_playlist:
            data = data['entries']
        else:
            data = [data]
        
        source_entries = []
        if download:
            for entries in data:
                source_entries.append(ytdl.prepare_filename(entries))

            audio_sources = []
            for song, source in zip(data, source_entries):
                audio_sources.append(cls(discord.FFmpegPCMAudio(source, **ffmpegopts), data=song, requester=cls.discord_requester(interaction=interaction)))
            return audio_sources
        else:
            for song in data:
                source_entries.append(song | {'webpage_url': song['url' if is_playlist else 'webpage_url'], 'requester': cls.discord_requester(interaction=interaction)})
        return source_entries

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

    def __init__(self, interaction: discord.Interaction):
        self.bot = interaction.client
        self._guild = interaction.guild
        self._channel = interaction.channel
        self._cog = interaction.client.get_cog('Music')
        # self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None  # Now playing message
        self.volume = 0.75
        self.current = None

        interaction.client.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Our main player loop."""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(60 * 3):  # 3 minutes...
                    try: # bypass the Task exception was never retrieved error
                        source = await self.queue.get()
                    except:
                        pass
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

            try:
                self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
                # self.np = await self._channel.send(f'**Now Playing:** `{source.title}` requested by {source.requester}')
                await self.next.wait()
            except:
                pass

            # Make sure the FFmpeg process is cleaned up.
            try:
                """Cleanup seems to cause ffmpeg process not terminated error"""
                source.cleanup()  # Can cause I/O operation on closed file Error
            except Exception as e:
                print(e)
                pass
                
            self.current = None

            # try:
            #     # We are no longer playing this song...
            #     await self.np.delete()
            # except discord.HTTPException:
            #     pass

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        # return self.bot.loop.create_task(guild.voice_client.disconnect())
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class Music(commands.Cog):
    """Music related commands."""

    __slots__ = ('bot', 'players')

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self, interaction: discord.Interaction):
        try:
            """Temp solution to mass ffmpeg process not terminated error"""
            player = self.get_player(interaction=interaction)
            player.queue = asyncio.Queue()
            interaction.guild.voice_client.stop()
            await interaction.guild.voice_client.disconnect(force=True)
        except AttributeError:
            pass

        try:
            del self.players[interaction.guild.id]
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

    def get_player(self, interaction: discord.Interaction):
        """Retrieve the guild player, or generate one."""
        try:
            player = self.players[interaction.guild.id]
        except KeyError:
            player = MusicPlayer(interaction)
            self.players[interaction.guild.id] = player

        return player
    
    async def defer_response(self, interaction: discord.Interaction, coroutine: asyncio.coroutines, command: str, response: str):
        """ Defers responses to get around 3 second response time limit."""
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
                return False
                # raise InvalidVoiceChannel('No channel to join. Please either specify a valid channel or join one.')

        vc = interaction.guild.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return True
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                await interaction.response.send_message(f'Moving to channel: <{channel}> timed out.')
                return False
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                await interaction.response.send_message(f'Connecting to channel: <{channel}> timed out.')
                return False
        return True

    @app_commands.command(name='join')
    async def join_(self, interaction: discord.Interaction, *, channel: discord.VoiceChannel=None):
        """Connect to voice. """
        await self.connect_(interaction, channel=channel)
        try:
            if not channel:
                channel = interaction.user.voice.channel
            await interaction.response.send_message(f'Connected to: **{channel}**')
        except:
            pass

    @app_commands.command(name='leave')
    async def leave_(self, interaction: discord.Interaction):
        """Disconnect from voice.
            This command also stops the music if it's playing.
        """
        vc = interaction.guild.voice_client

        if not vc:
            return await interaction.response.send_message('I am not currently connected to voice!')

        await self.cleanup(interaction=interaction)
        await interaction.response.send_message('Disconnected!')

    @app_commands.command(name='play')
    async def play_(self, interaction: discord.Interaction, *, search: str):
        """Request a song and add it to the queue."""
        """
        This command attempts to join a valid voice channel if the bot is not already in one.
        Uses YTDL to automatically search and retrieve a song.
        Parameters
        ------------
        search: str [Required]
            The song to search and retrieve using YTDL. This could be a simple search, an ID or URL.
        """
        # Connect to voice if not already connected
        vc = interaction.guild.voice_client
        if not vc:
            if not await self.connect_(interaction=interaction):
                return
        
        # Get player
        player = self.get_player(interaction=interaction)
        # If download is False, source will be a dict which will be used later to regather the stream.
        # If download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
        try:
            source = await YTDLSource.create_source(interaction, player, search, loop=self.bot.loop, download=False)
            for entry in source:
                await player.queue.put(entry)
        except Exception as e:
            try:
                await interaction.response.send_message(f'Error processing request: {search}')
            except:
                await interaction.followup.send(f'Error processing request: {search}')
            print(f'Error processing request: {search}')
            print(e)
        
    @app_commands.command(name='pause')
    async def pause_(self, interaction: discord.Interaction):
        """Pause the currently playing song."""
        vc = interaction.guild.voice_client
        if not vc or not vc.is_playing():
            return await interaction.response.send_message('I am not currently playing anything!', delete_after=20)
        elif vc.is_paused():
            return

        vc.pause()
        await interaction.response.send_message(f'**{vc.source.requester}**: Paused the song!')

    @app_commands.command(name='resume')
    async def resume_(self, interaction: discord.Interaction):
        """Resume the currently paused song."""
        vc = interaction.guild.voice_client

        if not vc or not vc.is_connected():
            return await interaction.response.send_message('I am not currently playing anything!', delete_after=20)
        elif not vc.is_paused():
            return await interaction.response.send_message('I am not paused!', delete_after=20)

        vc.resume()
        await interaction.response.send_message(f'**{vc.source.requester}**: Resumed the song!')

    @app_commands.command(name='skip')
    async def skip_(self, interaction: discord.Interaction, *, count: int=1):
        """Skip the song. If a number is specified, skip that many songs."""

        vc = interaction.guild.voice_client

        if not vc or not vc.is_connected():
            return await interaction.response.send_message('I am currently not in a channel!', delete_after=20)

        if not vc.is_playing():
            return await interaction.response.send_message('I am not currently playing anything!', delete_after=20)
        
        # for _ in range(count):
        vc.stop()
        queue = self.get_player(interaction=interaction).queue
        if not queue.empty():
            requester = YTDLSource.discord_requester(interaction=interaction)
            await interaction.response.send_message(f'**{requester}**: Skipped {count} song(s)!')
            queue.task_done()
        else:
            await interaction.response.send_message('There is no next song on the waiting list.')

    @app_commands.command(name='clear')
    async def clear_(self, interaction: discord.Interaction):
        """Clears the queue."""
        vc = interaction.guild.voice_client

        if not vc or not vc.is_connected():
            return await interaction.response.send_message('I am currently not in a channel!', delete_after=20)

        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return await interaction.response.send_message('I am not currently playing anything!', delete_after=20)

        self.get_player(interaction=interaction).queue = asyncio.Queue()
        await interaction.response.send_message(f'**{vc.source.requester}**: Cleared the queue!')

    @app_commands.command(name='queue')
    async def queue_info(self, interaction: discord.Interaction):
        """Retrieve currently playing and a basic queue of upcoming songs."""
        vc = interaction.guild.voice_client

        if not vc or not vc.is_connected():
            return await interaction.response.send_message('I am not currently connected to voice!', delete_after=20)

        player = self.get_player(interaction=interaction)
        if player.queue.empty():
            return await interaction.response.send_message('There are currently no queued songs.')

        # Grab up to 5 entries from the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, 5))
        
        # Embed
        header = '**__Now Playing__**'
        embed = await YTDLSource.create_embed(interaction=interaction, url=vc.source.web_url, info=vc.source.data, header=header, vol=player.volume)
        # Upcoming field
        fmt = '\n'.join(f'- {_["title"]}' for _ in upcoming)
        embed.add_field(name=f'__Upcoming - Next {len(upcoming)}__', value=fmt, inline=False)
        # Set author
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='now_playing')
    async def now_playing_(self, interaction: discord.Interaction):
        """Display information about the currently playing song."""
        vc = interaction.guild.voice_client

        if not vc or not vc.is_connected():
            return await interaction.response.send_message('I am not currently connected to voice!', delete_after=20)

        player = self.get_player(interaction=interaction)
        if not player.current:
            return await interaction.response.send_message('I am not currently playing anything!')

        header = f'**Now Playing** - {vc.source.requester}'
        vol = player.volume
        embed = await YTDLSource.create_embed(interaction=interaction, url=vc.source.web_url, info=vc.source.data, header=header, vol=vol)
        player.np = await interaction.response.send_message(embed=embed)

    @app_commands.command(name='volume')
    async def change_volume(self, interaction: discord.Interaction, *, vol: float):
        """Change the player volume."""
        """
        Parameters
        ------------
        volume: float or int [Required]
            The volume to set the player to in percentage. This must be between 1 and 100.
        """
        vc = interaction.guild.voice_client

        if not vc or not vc.is_connected():
            return await interaction.response.send_message('I am not currently connected to voice!', delete_after=20)

        if not 0 < vol < 101:
            return await interaction.response.send_message('Please enter a value between 1 and 100.')

        player = self.get_player(interaction=interaction)

        if vc.source:
            vc.source.volume = vol / 100

        player.volume = vol / 100
        await interaction.response.send_message(f'**{vc.source.requester}**: Set the volume to **{vol}%**')

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