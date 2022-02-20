# Credits to: https://github.com/JayChen35/spotify-to-mp3-python

import os

import spotipy
import spotipy.oauth2 as oauth2

from classes import *
from file_manager import add as add_playlist_to_db, get as load_playlist_from_db
from download_manager import download_song, download_cover_art
from mnn_extractor import process as mnn_process

client_id = None
client_secret = None
spotify: spotipy.Spotify = None
save_path: str = os.path.join(__file__, "..\\res\\")
credentials_path: str = os.path.join(__file__, "..\\spotify_credentials.txt")
print("Save path: ", save_path)
connected = False


def init(store_path=None, load_credentials=True):
    """
    Initialize downloader by connecting to Spotify API. Is called automatically upon querying DL operation.
    :param store_path: Path to use as root for downloaded playlists
    :param load_credentials: Whether to load client ID and secret from a local file "./spotify_credentials.txt"
    """

    if load_credentials:
        with open(credentials_path, "r") as f:
            data = f.readlines()
            client_id = data[0].strip()
            client_secret = data[1].strip()

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


def save_playlist(playlist_id: PlaylistID, progress_listener) -> Memory:
    """
        Save playlist of songs.
        :param str playlist_id: Spotify internal playlist ID to download
        :returns bool: If operation was successful
        - Fetch playlist info from Spotify API using provided client credentials
    """
    global save_path

    if not connected:
        init()

    if progress_listener is not None:
        progress_listener.start()

    playlist_name, playlist_tracks = get_playlist_info(playlist_id)
    memory = from_playlist(playlist_id, playlist_name, playlist_tracks)

    saved_memory = load_playlist_from_db(playlist_id)
    if saved_memory is not None:
        memory -= saved_memory

    track_index = 0
    track_count = len(memory.tracks)

    for track in memory.tracks:
        if not track.mnn_features:
            if not track.path:
                download_song(memory, track.id)
            mnn_process(track)

        if progress_listener is not None:
            progress_listener.set_progress(100 * track_index / track_count)
        track_index += 1

    add_playlist_to_db(memory)

    if progress_listener is not None:
        progress_listener.end()

    return memory


def get_playlist_info(playlist_id):
    global spotify

    if not connected:
        init()

    results = spotify.playlist(playlist_id, fields='next,name,tracks.items(track(album(artists(id,name),id,images,name),id,name))')


    playlist_name = results['name']
    playlist_tracks = results['tracks']['items']

    next_results = results['tracks']
    while 'next' in next_results:
        next_results = spotify.next(next_results)
        playlist_tracks += next_results['items']

    return playlist_name, playlist_tracks


def get_track_features(track: Track):
    global spotify
    return spotify.audio_features(track.id)


if __name__ == "__main__":
    test_playlist_1 = "1m6lKVbvLLwbW0tGDzX62y"
    test_playlist_2 = "1nSeTWPOi62KRvCb5sW9WD"
    test_playlist_3 = "0pHKFQFymRBdDOk5NVKXh0"

    for playlist in [test_playlist_1, test_playlist_2, test_playlist_3]:
        save_playlist(playlist)

# TODO: Probably get rid of this at some point
init()
