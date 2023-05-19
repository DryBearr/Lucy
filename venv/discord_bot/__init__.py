import os
import configparser

path = os.getcwd() + '\\venv'
config = configparser.ConfigParser()
config.read(path + '\\config.cfg')

DISCORD_TOKEN = config.get('config_section_lucy', 'discord_token')

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())


import asyncio
from discord_bot.music_cog import MusicCog
from utils import thread_manager
from utils import music_player

asyncio.run(bot.add_cog(MusicCog(bot, thread_manager, music_player)))