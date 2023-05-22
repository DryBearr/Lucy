import os
import configparser

path = os.getcwd() + '\\venv'
config = configparser.ConfigParser()
config.read(path + '\\config.cfg')

DISCORD_TOKEN = config.get('config_section_lucy', 'discord_token')
FFMPEG_EXECUTE_FOLDER = config.get("config_section_lucy", "ffmpeg_execute_folder")
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())


import json
import asyncio
import logging
from utils import downloader
from utils import thread_manager
from repository import music_library
from discord_bot.music_cog import MusicCog

# Load the logging configuration from JSON file
with open(path + '\\logger_config.json', 'r') as f:
    config = json.load(f)

# Configure the logger
logging.config.dictConfig(config)

asyncio.run(bot.add_cog(MusicCog(bot, thread_manager, music_library, downloader, logging.getLogger(__name__))))