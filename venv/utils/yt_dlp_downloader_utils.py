import asyncio
import yt_dlp
import logging
import traceback


class YtDlpDownloader:
    def __init__(self, options: dict, logger: logging.Logger) -> None:
        """
        Initialize the YtDlpDownloader object.

        Args:
            options (dict): Download options for yt_dlp.
            logger (logging.Logger): Logger object for logging.
        """
        self._options = options
        self._logger = logger

    def download(self, *urls: str, option: str = None) -> list[dict]:
        """
        Download videos from the given URLs.

        Args:
            urls (str): URLs of the videos to download.
            option (str): Download option ("AUDIO" or "VIDEO").

        Returns:
            list[dict]: List of dictionaries containing video metadata.

        Raises:
            Exception: If the option is not valid.
        """
        try:
            if option is not None and option.upper() in ["AUDIO", "VIDEO"]:
                with yt_dlp.YoutubeDL(self._options[option]) as ydl:
                    video_metadata_list = []
                    for url in urls:
                        info = ydl.extract_info(url, download=True)
                        video_metadata_list.append(info)

                    return video_metadata_list
            else:
                raise Exception(f'OPTION: {option} IS NOT VALID!')
        except Exception as e:
            self._logger.error(f"Error: {e} \n{traceback.format_exc()}")





