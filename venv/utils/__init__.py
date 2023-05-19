import configparser
import os
import re
import json
import logging.config


# Read the configuration file
path = os.getcwd() +  '\\venv'
config = configparser.ConfigParser()
config.read(path + '\\config.cfg')

# Get configuration values
FFMPEG_EXECUTE_FOLDER = config.get('config_section_lucy', 'ffmpeg_execute_folder')
MUSIC_DOWNLOAD_FOLDER = config.get('config_section_lucy', 'music_download_folder')
CHROME_DRIVER_PATH = config.get('config_section_lucy', 'chrome_driver_path')

# Regular expressions
URL_REGEX = re.compile(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))")
VIDEO_ID_HTML_REGEX = re.compile(r'{"videoRenderer":{"videoId":"([^"]+)')
PLAYLIST_ID_URL_REGEX = re.compile(r'list=([a-zA-Z0-9_-]+)')
VIDEO_ID_URL_REGEX = re.compile(r'v=([a-zA-Z0-9_-]+)')

# Load download options from JSON file
with open(path + '\\utils' + '\\download_options.json', 'r') as f:
    options = json.load(f)

# Replace placeholders with actual values in download options
for temp in ['AUDIO', 'VIDEO']:
    options[temp]['outtmpl'] = options[temp]['outtmpl'].replace('${project_directory}', MUSIC_DOWNLOAD_FOLDER)
    options[temp]['ffmpeg_location'] = FFMPEG_EXECUTE_FOLDER

# Load the logging configuration from JSON file
with open(path + '\\logger_config.json', 'r') as f:
    config = json.load(f)

# Configure the logger
logging.config.dictConfig(config)

# Create the YtDlpDownloader object
from utils.yt_dlp_downloader_utils import YtDlpDownloader
downloader = YtDlpDownloader(options, logging.getLogger(__name__))

# Create the MusicPlayer object
from utils.music_player_utils import MusicPlayer
from repository import music_library
music_player = MusicPlayer(music_library, downloader, logging.getLogger(__name__))

# Create the ThreadManager object
from utils.threading_utils import  ThreadManager
thread_manager = ThreadManager(logging.getLogger(__name__))