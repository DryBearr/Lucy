import os
import discord
import asyncio
import logging
import threading
import traceback
from discord.ext import commands
from discord_bot import FFMPEG_EXECUTE_FOLDER
from utils.threading_utils import ThreadManager
from repository.lucy_repository import MusicLibrary
from repository.lucy_repository import  MusicLibrary
from utils.yt_dlp_downloader_utils import YtDlpDownloader
from utils.data_scrapper_utils import find_urls, get_video_id_from_url, get_videIds_from_title, get_video_ids_from_playlist

class MusicCog(commands.Cog):
    def __init__(self,
                 bot:commands.Bot,
                 thread_manager:ThreadManager,
                 music_library:MusicLibrary,
                 downloader: YtDlpDownloader,
                 logger:logging.Logger):
        self._bot = bot
        self._thread_manager = thread_manager
        self._music_library = music_library
        self._downloader = downloader
        self._logger = logging
        self._queue = []
        self.current_song = None

#--------- bot commands ---------
    @commands.Cog.listener()
    async def on_ready(self):
        print('Lucy successfully connected to the server! :3')
        music_player_loop = self._thread_manager.add_event_loop()
        self._thread_manager.start_threads()
        asyncio.run_coroutine_threadsafe(self._play_queue(), music_player_loop)

    @commands.command()
    async def say_hi(self, ctx: commands.Context):
        await ctx.send('HI MOTHER FUCKERS!')

    @commands.command()
    async def disconnect(self, ctx: commands.Context):
        voice_client = ctx.guild.voice_client

        if voice_client.is_connected():
            await voice_client.disconnect()
            await ctx.send("Disconnected from the voice channel")
        else:
            await ctx.send("I'm not currently connected to a voice channel")

    @commands.command()
    async def stop(self, ctx: commands.Context):
        voice_client = ctx.guild.voice_client
        if voice_client.is_connected():
            voice_client.stop()
            await ctx.send("Stop!")
        else:
            await ctx.send("I'm not currently connected to a voice channel")

    @commands.command()
    async def pause(self, ctx: commands.Context):
        voice_client = ctx.guild.voice_client

        if voice_client.is_connected():
            voice_client.pause()
            await ctx.send("Pause!")
        else:
            await ctx.send("I'm not currently connected to a voice channel")

    @commands.command()
    async def resume(self, ctx: commands.Context):
        voice_client = ctx.guild.voice_client

        if voice_client.is_connected():
            voice_client.resume()
            await ctx.send("Resume!")
        else:
            await ctx.send("I'm not currently connected to a voice channel")

    @commands.command()
    async def play(self, ctx: commands.Context, *args):
        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            await ctx.send('You need to be in a voice channel to use this command')
            return

        voice_client = ctx.voice_client

        if ctx.voice_client is None:
            voice_client = await voice_channel.connect()

        string = ' '.join(args)
        urls = find_urls(string)
        song_ids = []
        if urls == []:
            song_ids = [get_videIds_from_title(string)]
        else:
            for url in urls:
                if 'list' in url[0]:
                    song_ids.extend(get_video_ids_from_playlist(url[0]))
                else:
                    song_ids.append(get_video_id_from_url(url[0]))

        await self._add(song_ids, voice_client)

    @commands.command()
    async def skip(self, ctx: commands.Context):
        await self._skip()
        await ctx.send("SKIPPED!")

#--------- functions ---------
    async def _add(self, ids: list[str], voice_client):
            """
            Add a song to the music queue.

            Args:
                ids list[str]: ids of songs.
                voice_client (discord.VoiceClient): Voice client to play the song.
            """
            song_ids_to_download = []
            for i in ids:
                song = await self._music_library.get_music_by_id(i)
                if song is None:
                    song_ids_to_download.append(i)
                    continue
                self._queue.append((song.path, voice_client,))
                self._logger.info(f'------ Music:{song.title} added to queue! ------')
            threading.Thread(target=self._download_song, args=(song_ids_to_download, voice_client), daemon=True).start() # background download

    async def _play_queue(self):
        """
        Continuously play songs from the music queue.
        """
        while True:
            try:
                if len(self._queue) != 0:  # If the queue is not empty
                    song_path, voice_client = self._queue.pop(0)  # Get the first song path and voice client to play
                    await self._play(song_path, voice_client)  # Play the song
                else:
                    await asyncio.sleep(1)  # Sleep for a second if the queue is empty
            except Exception as e:
                self._logger.error(f'ERROR: {e}\n{traceback.format_exc()}')
                continue

    async def _play(self, song_path: str, voice_client):
        """
        Play a song using the provided voice client.

        Args:
            song_path (str): Path to the song file.
            voice_client (discord.VoiceClient): Voice client to play the song.
        """
        if os.path.exists(song_path):  # Check if the song exists
            self.current_song = voice_client  # Set the currently playing song

            # Create a discord.FFmpegPCMAudio source from the song path
            source = discord.FFmpegPCMAudio(song_path, executable=FFMPEG_EXECUTE_FOLDER)
            voice_client.play(source)  # Play the song
            song_name = song_path.split('/')[-1]  # Get the song name from the path

            while voice_client.is_playing():  # Wait for the song to finish playing
                await asyncio.sleep(1)

        else:  # If the music doesn't exist, add it back to the end of the queue
            self._queue.append((song_path, voice_client))

    async def _skip(self):
        """
        Skip the currently playing song.
        """
        if self.current_song is not None:  # If a song is currently playing
            self.current_song.stop()  # Stop the current song
            self.current_song = None  # Set the current song to None

    def _download_song(self, song_ids:list[str], voice_client):
            for song_id in song_ids:
                song_info = self._downloader.download('https://youtu.be/' + song_id, option='AUDIO').pop(0)
                asyncio.run(self._music_library.add_music(id=song_id[0], title=song_info['title'], path=song_info['requested_downloads'][0]['filepath']))
                self._queue.append((song_info['requested_downloads'][0]['filepath'], voice_client,))

    async def _clear(self):
        """
        Clear the music queue.
        """
        self._queue.clear()  # Clear the queue
        self._logger.info(f'Now Queue is empty')
