import re
import requests
from bs4 import BeautifulSoup
from utils import URL_REGEX, VIDEO_ID_HTML_REGEX, PLAYLIST_ID_URL_REGEX, VIDEO_ID_URL_REGEX

def get_videIds_from_title(title: str) -> list[str]:
    """
    Retrieves video IDs from YouTube search results based on a given title.

    Args:
        title: The title to search for.

    Returns:
        A list of video IDs.
    """
    search_query = '+'.join(title.split())
    url = f'https://www.youtube.com/results?search_query={search_query}'

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')

    content = soup.select_one('script:-soup-contains("var ytInitialData = ")')
    temp = str(content.contents[0])

    ids = [match.group(1) for match in VIDEO_ID_HTML_REGEX.finditer(temp)][:5]

    return ids[0]

def find_urls(string: str) -> list[str]:
    """
    Finds URLs in a given string.

    Args:
        string: The string to search for URLs.

    Returns:
        A list of URLs.
    """
    return URL_REGEX.findall(string)

def get_video_ids_from_playlist(url: str) -> list[str]:
    """
    Retrieves video IDs from a YouTube playlist based on the given playlist URL.

    Args:
        url: The URL of the YouTube playlist.

    Returns:
        A list of video IDs.
    """
    playlist_id = None
    try:
        playlist_id = next(PLAYLIST_ID_URL_REGEX.finditer(url))  # Find the first playlist ID in the URL
    except StopIteration:
        return []  # Return an empty list if no playlist ID is found

    new_url = f'https://www.youtube.com/playlist?list={playlist_id}'
    playlist_html = requests.get(new_url).text
    video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]+)"', playlist_html)

    return video_ids

def get_video_id_from_url(url:str) -> str:
    """
    Retrieves the video ID from a YouTube video URL.

    Args:
        url: The URL of the YouTube video.

    Returns:
        The video ID.
    """
    return VIDEO_ID_URL_REGEX.findall(url)
