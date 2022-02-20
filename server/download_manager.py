# Credits to: https://github.com/JayChen35/spotify-to-mp3-python
import json
import os

import requests
import spotipy
import yt_dlp
from youtube_search import YoutubeSearch

from classes import *

track_path = ".\\res\\tracks"
cover_path = ".\\res\\covers"

def download_cover_art(memory: Memory, track_id: TrackID):
    track = memory.get_track(track_id)
    album = memory.get_album(track.album_id)
    cover_url = album.cover_url
    album_name = album.name
    cover_art = requests.get(cover_url).content
    # TODO: Somehow read the file type from response header
    if not os.path.exists(album_name):
        with open(album_name + ".jpeg", "wb") as img:
            img.write(cover_art)


def download_song(memory: Memory, track_id: TrackID) -> bool:
    """
    Download specified song from YT
    :param memory: Memory object
    :param track_id: TrackID to download
    :return: path to saved file
    """
    TOTAL_ATTEMPTS = 10
    track = memory.get_track(track_id)
    album = memory.get_album(track.album_id)
    artists = [memory.get_artist(artist_id) for artist_id in album.artist_ids]
    artist_names = [artist.name for artist in artists]

    artist = ""
    if len(artist_names) == 1:
        artist = artist_names[0]
    elif len(artist_names) == 2:
        artist = artist_names[0] + " feat. " + artist_names[1]
    else:
        artist = ", ".join(artist_names)
    search_query = artist + " - " + track.name

    best_url = None
    attempts_left = TOTAL_ATTEMPTS
    while attempts_left > 0:
        try:
            results_list = YoutubeSearch(search_query, max_results=1).to_dict()
            best_url = "https://www.youtube.com{}".format(results_list[0]['url_suffix'])
            break
        except IndexError:
            attempts_left -= 1
            print("No valid URLs found for {}, trying again ({} attempts left).".format(
                search_query, attempts_left))
    if best_url is None:
        print("No valid URLs found for {}, skipping track.".format(search_query))
        return False

    ydl_opts = {
        'format': 'bestaudio/best',
        'paths': {'home': track_path},
        'outtmpl': search_query + ".%(ext)s",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([best_url])
        info = ydl.extract_info(best_url)
        track.path = os.path.relpath(info['requested_downloads'][0]['filepath'], os.getcwd())
        pass
    print("Song downloaded...")
    return True
