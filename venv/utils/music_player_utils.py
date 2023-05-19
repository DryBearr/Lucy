import os
import logging
import asyncio
import discord
import threading
import traceback
from utils.yt_dlp_downloader_utils import YtDlpDownloader
from discord.ext import commands, tasks
from repository.lucy_repository import MusicLibrary

class MusicPlayer:
    """
    Class for managing a music player that handles a queue of songs to play.
    """

    def __init__(self, music_library: MusicLibrary, downloader: YtDlpDownloader, logger: logging.Logger):
        """
        Initialize the MusicPlayer object.

        Args:
            logger (logging.Logger): Logger object for logging messages.
        """
        self._queue = []  # List to store the music queue
        self.current_song = None  # Currently playing song
        self._music_library = music_library
        self._logger = logger
        self._downloader = downloader

    async def add(self, ids: list[str], voice_client):
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

    async def play_queue(self):
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
            source = discord.FFmpegPCMAudio(song_path, executable='C:/ProgramData/chocolatey/bin/ffmpeg.exe')
            voice_client.play(source)  # Play the song
            song_name = song_path.split('/')[-1]  # Get the song name from the path

            while voice_client.is_playing():  # Wait for the song to finish playing
                await asyncio.sleep(1)

        else:  # If the music doesn't exist, add it back to the end of the queue
            self._queue.append((song_path, voice_client))

    def _download_song(self, song_ids:list[str], voice_client):
        for song_id in song_ids:
            song_info = self._downloader.download('https://youtu.be/' + song_id, option='AUDIO').pop(0)
            asyncio.run(self._music_library.add_music(id=song_id, title=song_info['title'], path=song_info['requested_downloads'][0]['filepath']))
            self._queue.append((song_info['requested_downloads'][0]['filepath'], voice_client,))

    async def skip(self):
        """
        Skip the currently playing song.
        """
        if self.current_song is not None:  # If a song is currently playing
            self.current_song.stop()  # Stop the current song
            self.current_song = None  # Set the current song to None

    async def clear(self):
        """
        Clear the music queue.
        """
        self._queue.clear()  # Clear the queue
        self._logger.info(f'Now Queue is empty')
