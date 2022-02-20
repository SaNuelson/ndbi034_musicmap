import json
import os
import sys
import sqlite3 as sl
from classes import *

data_path = 'data/playlists.db'
con = sl.connect(data_path)


def setup():
    con.execute('''CREATE TABLE playlist (
        id TEXT CONSTRAINT playlist_id_pk PRIMARY KEY,
        name TEXT
    )''')

    con.execute('''CREATE TABLE artist (
        id TEXT CONSTRAINT artist_id_pk PRIMARY KEY,
        name TEXT
    )''')

    con.execute('''CREATE TABLE track (
        id TEXT CONSTRAINT track_id_pk PRIMARY KEY,
        name TEXT,
        spotify_features TEXT,
        mnn_features TEXT,
        album_id TEXT,
        path TEXT,
        CONSTRAINT track_in_fk
            FOREIGN KEY (album_id)
            REFERENCES album(id)
    )''')

    con.execute('''CREATE TABLE album (
        id TEXT CONSTRAIN album_id_pk PRIMARY KEY,
        name TEXT,
        cover_url TEXT
    )''')

    con.execute('''CREATE TABLE authorship (
        artist_id TEXT,
        album_id TEXT,
    CONSTRAINT album_authored_fk 
        FOREIGN KEY (album_id)
        REFERENCES album(id),
    CONSTRAINT album_author_fk
        FOREIGN KEY (artist_id)
        REFERENCES artist(id)
    )''')

    con.execute('''CREATE TABLE inclusion (
        playlist_id TEXT,
        track_id TEXT,
    CONSTRAINT track_included_fk
        FOREIGN KEY (track_id)
        REFERENCES track(id),
    CONSTRAINT playlist_content_fk
        FOREIGN KEY (playlist_id)
        REFERENCES playlist(id)
    )''')

    con.commit()


def get(id: PlaylistID):
    cur = con.cursor()

    # Playlist
    cur.execute('SELECT * FROM playlist WHERE id=:id', {'id': id})
    playlist_data = cur.fetchone()

    if playlist_data is None:
        return None

    playlist = Playlist(*playlist_data)

    # TrackIDs
    cur.execute('SELECT track_id FROM inclusion WHERE playlist_id=:playlist_id', {'playlist_id': playlist.id})
    track_ids = cur.fetchall()
    track_ids = list(map(lambda x: x[0], track_ids))

    # Tracks
    cur.execute(f"SELECT * FROM track WHERE id IN ({','.join(['?']*len(track_ids))})", track_ids)
    tracks_data = cur.fetchall()
    tracks = [Track(*data, playlist_ids=[playlist.id]) for data in tracks_data]

    # AlbumIDs
    album_ids = list(set([track.album_id for track in tracks]))

    # Albums
    cur.execute(f"SELECT * FROM album WHERE id IN ({','.join(['?']*len(album_ids))})", album_ids)
    album_data = cur.fetchall()

    # ArtistIDs
    cur.execute(f"SELECT * FROM authorship WHERE album_id IN ({','.join(['?']*len(album_ids))})", album_ids)
    authorship_data = cur.fetchall()
    artist_ids = list(map(lambda x: x[0], authorship_data))
    albums = [Album(*data, artist_ids=[authorship[1] for authorship in authorship_data if authorship[0] == data[0]]) for data in album_data]

    # Artists
    cur.execute(f"SELECT * FROM artist WHERE id IN ({','.join(['?']*len(artist_ids))})", artist_ids)
    artists_data = cur.fetchall()
    artists = [Artist(*data) for data in artists_data]

    return Memory([playlist], albums, artists, tracks)


def getall():
    cur = con.cursor()

    cur.execute("SELECT * FROM playlist")
    playlists_data = cur.fetchall()
    playlists = [Playlist(*data) for data in playlists_data]

    cur.execute("SELECT * FROM inclusion")
    inclusions_data = cur.fetchall() # (playlist_id, track_id)

    cur.execute("SELECT * FROM track")
    tracks_data = cur.fetchall()
    tracks = [Track(*data, playlist_ids=[incl[0] for incl in inclusions_data if incl[1] == data[0]]) for data in tracks_data]

    cur.execute("SELECT * FROM album")
    albums_data = cur.fetchall()

    cur.execute("SELECT * FROM authorship")
    authorship_data = cur.fetchall() # (artist_id, album_id)

    albums = [Album(*data, artist_ids=[authorship[0] for authorship in authorship_data if authorship[1] == data[0]]) for data in albums_data]

    cur.execute("SELECT * FROM artist")
    artists_data = cur.fetchall()
    artists = [Artist(*data) for data in artists_data]

    return Memory(playlists, albums, artists, tracks)


def add(info: Memory):
    for artist in info.artists:
        con.execute('INSERT OR IGNORE INTO artist(id, name) VALUES (:id, :name)', artist.to_dict())
    for album in info.albums:
        con.execute('INSERT OR IGNORE INTO album(id, name, cover_url) VALUES (:id, :name, :cover_url)', album.to_dict())
        # authorship (artist - album)
        for artist_id in album.artist_ids:
            con.execute('''INSERT OR IGNORE INTO authorship(artist_id, album_id) VALUES (:artist_id, :album_id)''',
                        {'artist_id': artist_id, 'album_id': album.id})
    for playlist in info.playlists:
        con.execute('INSERT OR IGNORE INTO playlist(id, name) VALUES (:id, :name)', playlist.to_dict())
    for track in info.tracks:
        # TODO: tweak to store json features, should be changed somehow
        track_dict = track.to_dict()
        track_dict['spotify_features'] = json.dumps(track_dict['spotify_features'])
        track_dict['mnn_features'] = json.dumps(track_dict['mnn_features'])
        con.execute('''INSERT OR IGNORE INTO track(id, name, spotify_features, mnn_features, album_id, path)
            VALUES(:id, :name, :spotify_features, :mnn_features, :album_id, :path)''', track_dict)
        # inclusion (playlist - track)
        for playlist_id in track.playlist_ids:
            con.execute('''INSERT OR IGNORE INTO inclusion(playlist_id, track_id) VALUES (:playlist_id, :track_id)''',
                        {'playlist_id': playlist_id, 'track_id': track.id})
    con.commit()

# UTILS


def select_equals(items, table, attribute, value):
    return f"SELECT {items} FROM {table} WHERE {attribute}={value}"


def select_contains(items, table, attribute, n):
    return f"SELECT {items} FROM {table} WHERE {attribute} IN ({','.join(['?'] * n)})"


if __name__ == "__main__":
    args = sys.argv
    if len(args) > 1 and args[1] == "-r":
        con.close()
        os.remove(data_path)
        con = sl.connect(data_path)
        setup()
