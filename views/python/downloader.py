# Credits to: https://github.com/JayChen35/spotify-to-mp3-python

import os
import spotipy
import spotipy.oauth2 as oauth2
import yt_dlp
import json
from youtube_search import YoutubeSearch

client_id = "eb9d9961d9ea426fba452ff3cc947ae0"
client_secret = "23297c90f6804bbfb1fefcd5d4565a65"
spotify : spotipy.Spotify = None
save_path : str = os.path.join(os.getcwd(), "hs\\res\\")


connected = False
def init(store_path = None):
    """
    Initialize downloader by connecting to Spotify API. Is called automatically upon querying DL operation.
    :param store_path: Path to use as root for downloaed playlists
    """
    global spotify, save_path, connected
    if store_path is not None:
        save_path = store_path

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    if client_id is None or client_secret is None:
        print("Warning: Downloader called with unset client credentials.")
        return False

    auth_manager = oauth2.SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    try:
        auth_manager.get_access_token(False)
    except spotipy.oauth2.SpotifyOauthError:
        print("Warning: Downloader contains invalid client credentials, it will NOT work.")
        return False
    print("Downloader successfully connected to Spotify API")
    connected = True
    return True


def save_playlist(playlist_id: str) -> bool:
    """
        Save playlist of songs.
        :param str playlist_id: Spotify internal playlist ID to download
        :returns bool: If operation was successful
        - Fetch playlist info from Spotify API using provided client credentials
    """
    global spotify, save_path

    if not connected:
        init()

    results = spotify.playlist(playlist_id, fields='tracks,next,name')
    playlist_name = results['name']
    playlist_tracks = results['tracks']['items']

    next_results = results['tracks']
    while next_results['next']:
        next_results = spotify.next(next_results)
        playlist_tracks += next_results['items']

    playlist_tracks = [extract_track_info(track) for track in playlist_tracks]

    playlist_path = os.path.join(save_path, playlist_name)
    if not os.path.exists(playlist_path):
        os.makedirs(playlist_path)
    os.chdir(playlist_path)

    save_log_file(playlist_path, playlist_tracks)
    for track in playlist_tracks:
        download_song(track)

def get_playlist_info(playlist_id):
    global spotify

    if not connected:
        init()

    results = spotify.playlist(playlist_id, fields='tracks,next,name')
    playlist_name = results['name']
    playlist_tracks = results['tracks']['items']

    next_results = results['tracks']
    while next_results['next']:
        next_results = spotify.next(next_results)
        playlist_tracks += next_results['items']

    playlist_tracks = [extract_track_info(track) for track in playlist_tracks]
    return {
        'name': playlist_name,
        'id': playlist_id,
        'tracks': playlist_tracks
    }

def save_log_file(path, tracks):
    os.chdir(path)
    with open("log.txt", "w") as f:
        json.dump(tracks, f)
    print("Log file written.")

def extract_track_info(track: dict) -> dict:
    """
    Extract only relevant info from track info object
    :param track: spotipy track data object
    :return: stipped track data object
    """
    info = track['track']
    return {
        'name': info['name'],
        'id': info['id'],
        'artists': [{
            'name': artist['name'],
            'id': artist['id']
            } for artist in info['artists']]
    }

def download_song(track_info):
    """
    Download song from YT if search is successful
    :param track_info: stripped track data object
    :returns bool: If operation was successful
    """
    TOTAL_ATTEMPTS = 10
    artist_names = [artist['name'] for artist in track_info['artists']]
    artist = ""
    if len(artist_names) == 1:
        artist = artist_names[0]
    elif len(artist_names) == 2:
        artist = artist_names[0] + " feat. " + artist_names[1]
    else:
        artist = ", ".join(artist_names)
    search_query = artist + " - " + track_info['name']

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
        'outtmpl': search_query + ".%(ext)s",
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([best_url])
    print("Song downloaded...")
    return


DEBUG_TEST_PLAYLIST = "1m6lKVbvLLwbW0tGDzX62y?si=256fdfc0b0164e96"
DEBUG_LONG_PLAYLIST = "3N7dK1j49MNZoGh64SjlXT?si=5ef58c470ac54151"
DEBUG_MEDIUM_PLAYLIST = "0CO8A3nZAiV2PkdYTnyQGr?si=6c07804003c84feb:"

save_playlist(DEBUG_MEDIUM_PLAYLIST)