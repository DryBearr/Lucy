# Import the required modules
from sqlalchemy.ext.declarative import declarative_base
from repository.lucy_repository import MusicLibrary
import os
import configparser
import logging.config
import json
import asyncio

# Define the base for ORM mapping
Base = declarative_base()

# Get the current working directory and the path to the virtual environment
path = os.getcwd() + '\\venv'

# Read the configuration from the config file
config = configparser.ConfigParser()
config.read(path +  '\\config.cfg')
DATABASE_FOLDER = config.get('config_section_lucy', 'database_folder')

# Load the logging configuration from JSON file
with open(path + '\\logger_config.json', 'r') as f:
    config = json.load(f)

# Configure the logger
logging.config.dictConfig(config)

# Create an instance of the MusicLibrary
music_library = MusicLibrary(DATABASE_FOLDER, Base, logging.getLogger(__name__))

# Run the create_tables method asynchronously
asyncio.run(music_library.create_tables())
