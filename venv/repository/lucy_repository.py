import asyncio
import logging
import traceback
from repository.models import Music
from sqlalchemy.future import select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

class MusicLibrary:
    """
    Represents a music library that interacts with a database to manage music information.
    """

    def __init__(self, db_path:str = None, base:declarative_base = None, logger:logging.Logger = None):
        """
        Initializes the MusicLibrary object.

        Args:
            db_path (str): The path to the database file.
            base (declarative_base): The declarative base for ORM mapping.
            logger (logging.Logger): The logger object for logging messages.
        """
        self.engine = create_async_engine(f'sqlite+aiosqlite:///{db_path}', echo=True, future=True) # engine for low level
        self.async_session_maker = async_sessionmaker( # session is ORM for high-level interface
                                        self.engine,
                                        expire_on_commit=False,
                                        class_=AsyncSession
                                    )
        self.Base = base
        self.logger = logger

    async def create_tables(self) -> None:
        """
        Creates the necessary tables in the database based on the provided declarative base.
        """
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(self.Base.metadata.create_all, checkfirst=True)
                self.logger.info('All tables created successfully!')
        except Exception as e:
            self.logger.error(f'{e} \n {traceback.format_exc()}')

    async def add_music(self, **music_data) -> None:
        """
        Adds a music entry to the database.

        Args:
            **music_data: The data for the music entry.
        """
        try:
            async with self.async_session_maker() as session:
                if await session.get(Music, music_data['id']) is None:
                    session.add(Music(**music_data))
                    self.logger.info(f'Music:{music_data} added to the database')
                else:
                    self.logger.warning(f'Music:{music_data} already exists in the database!')
                await session.commit()
        except Exception as e:
            self.logger.error(f"Error occurred while adding music: {e} \n{traceback.format_exc()}")

    async def delete_musics_by_id(self, *ids: str) -> None:
        """
        Deletes music entries from the database based on their IDs.

        Args:
            *ids: The IDs of the music entries to delete.
        """
        try:
            async with self.async_session_maker() as session:
                for music_id in ids:
                    music = await session.get(Music, music_id)
                    if music is None:
                        self.logger.warning(f'Music with ID {music_id} does not exist in the database!')
                    else:
                        await session.delete(music)
                await session.commit()
                self.logger.info(f'Deletion of music entries completed successfully!')
        except Exception as e:
            self.logger.error(f"Error occurred while deleting music: {e}\n{traceback.format_exc()}")

    async def get_music_by_id(self, index:str) -> Music:
        """
        Retrieves a music entry from the database based on its ID.

        Args:
            index (str): The ID of the music entry to retrieve.

        Returns:
            Music: The retrieved music entry.
        """
        try:
            async with self.async_session_maker() as session:
                music = await session.get(Music, index)
                self.logger.info(f'Retrieval of music entry completed successfully!')
                return music
        except Exception as e:
            self.logger.error(f"Error occurred while getting music: {e} \n{traceback.format_exc()}")

    async def get_music_by_title_patterns(self, patterns:list) -> list[Music]:
        """
        Retrieves music entries from the database based on title patterns.

        Args:
            patterns (list): A list of title patterns to search for.

        Returns:
            list[Music]: The list of retrieved music entries.
        """
        try:
            async with self.async_session_maker() as session:
                return [
                    await session.query(Music).filter(Music.title.like(f'%{pattern}%')).all()
                    for pattern in patterns
                ]
        except Exception as e:
            self.logger.error(f"Error occurred while getting music: {e} \n{traceback.format_exc()}")

    async def get_all(self):
        """
        Retrieves all music entries from the database.

        Returns:
            A result set of all music entries.
        """
        try:
            async with self.async_session_maker() as session:
                music = await session.execute(select(Music))
                self.logger.info(f'Retrieval of all music entries completed successfully!')
                return music.scalars()
        except Exception as e:
            self.logger.error(f"Error occurred while retrieving music: {e} \n{traceback.format_exc()}")
