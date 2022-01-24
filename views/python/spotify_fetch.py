# Credits to: https://github.com/JayChen35/spotify-to-mp3-python
# Downloads a Spotify playlist into a folder of MP3 tracks
# Jason Chen, 21 June 2020

import os
import spotipy
import spotipy.oauth2 as oauth2
import yt_dlp
import argparse
from youtube_search import YoutubeSearch

parser = argparse.ArgumentParser()
parser.add_argument("--client_id", type=str, default=None, help="Spotify client ID")
parser.add_argument("--client_secret", type=str, default=None, help="Spotify client secret")
parser.add_argument("--playlist_id", type=str, default=None, help="Spotify playlist ID to download")

client_id = None
client_secret = None

def write_tracks(text_file: str, tracks: dict):
    # Writes the information of all tracks in the playlist to a text file.
    # This includes the name, artist, and spotify URL. Each is delimited by a comma.
    with open(text_file, 'w+', encoding='utf-8') as file_out:
        while True:
            for item in tracks['items']:
                if 'track' in item:
                    track = item['track']
                else:
                    track = item
                try:
                    track_url = track['external_urls']['spotify']
                    track_name = track['name']
                    track_artist = track['artists'][0]['name']
                    csv_line = track_name + "," + track_artist + "," + track_url + "\n"
                    try:
                        file_out.write(csv_line)
                    except UnicodeEncodeError:  # Most likely caused by non-English song names
                        print("Track named {} failed due to an encoding error. This is \
                            most likely due to this song having a non-English name.".format(track_name))
                except KeyError:
                    print(u'Skipping track {0} by {1} (local only?)'.format(
                            track['name'], track['artists'][0]['name']))
            # 1 page = 50 results, check if there are more pages
            if tracks['next']:
                tracks = spotify.next(tracks)
            else:
                break


def write_playlist(playlist_id: str):
    results = spotify.playlist(playlist_id, fields='tracks,next,name')
    playlist_name = results['name']
    text_file = u'{0}.txt'.format(playlist_name, ok='-_()[]{}')
    print(u'Writing {0} tracks to {1}.'.format(results['tracks']['total'], text_file))
    tracks = results['tracks']

    '''
    for track in tracks['items']:
        track_results = spotify.audio_features(track['track']['id'])
        print(track_results)
    '''

    write_tracks(text_file, tracks)
    return playlist_name


def find_and_download_songs(reference_file: str):
    TOTAL_ATTEMPTS = 10
    with open(reference_file, "r", encoding='utf-8') as file:
        for line in file:
            temp = line.split(",")
            name, artist = temp[0], temp[1]
            text_to_search = artist + " - " + name
            best_url = None
            attempts_left = TOTAL_ATTEMPTS
            while attempts_left > 0:
                try:
                    results_list = YoutubeSearch(text_to_search, max_results=1).to_dict()
                    best_url = "https://www.youtube.com{}".format(results_list[0]['url_suffix'])
                    break
                except IndexError:
                    attempts_left -= 1
                    print("No valid URLs found for {}, trying again ({} attempts left).".format(
                        text_to_search, attempts_left))
            if best_url is None:
                print("No valid URLs found for {}, skipping track.".format(text_to_search))
                continue
            # Run you-get to fetch and download the link's audio
            print("Initiating download for {}.".format(text_to_search))
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([best_url])


if __name__ == "__main__":
    args = parser.parse_args()

    client_id = args.client_id
    client_secret = args.client_secret
    playlist_uri = args.playlist_id

    if client_id is None or client_secret is None or playlist_uri is None:
        print("Error: Client ID, client secret and playlist URI are required parameters")
        exit(1)

    auth_manager = oauth2.SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    playlist_name = write_playlist(playlist_uri)

    reference_file = "{}.txt".format(playlist_name)

    # Create the playlist folder
    if not os.path.exists(playlist_name):
        os.makedirs(playlist_name)
    os.rename(reference_file, playlist_name + "/" + reference_file)
    os.chdir(playlist_name)

    find_and_download_songs(reference_file)

    print("Operation complete.")