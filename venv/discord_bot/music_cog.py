import asyncio
import threading
from utils.threading_utils import ThreadManager
from discord.ext import commands
from repository.lucy_repository import MusicLibrary
from utils.data_scrapper_utils import find_urls, get_video_id_from_url, get_videIds_from_title, get_video_ids_from_playlist
from utils.music_player_utils import MusicPlayer

class MusicCog(commands.Cog):
    def __init__(self, bot:commands.Bot, thread_manager:ThreadManager, music_player:MusicPlayer):
        self._bot = bot
        self._thread_manager = thread_manager
        self._music_player = music_player

    @commands.Cog.listener()
    async def on_ready(self):
        print('Lucy successfully connected to the server! :3')
        music_player_loop = self._thread_manager.add_event_loop()
        self._thread_manager.start_threads()
        asyncio.run_coroutine_threadsafe(self._music_player.play_queue(), music_player_loop)

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
                if 'list' in url:
                    song_ids.expend(get_video_ids_from_playlist(url))
                else:
                    song_ids.append(get_video_id_from_url(url))

        await self._music_player.add(song_ids, voice_client)

    @commands.command()
    async def skip(self, ctx: commands.Context):
        await self._music_player.skip()
        await ctx.send("SKIPPED!")