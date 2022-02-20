from typing import NewType, List, Dict

SpotifyID = NewType("SpotifyID", str)
PlaylistID = NewType("PlaylistID", SpotifyID)
ArtistID = NewType("ArtistID", SpotifyID)
AlbumID = NewType("AlbumID", SpotifyID)
TrackID = NewType("TrackID", SpotifyID)


class SpotifyInfoObject:
    id: SpotifyID
    name: str

    def to_dict(self) -> Dict:
        return vars(self)


class Playlist(SpotifyInfoObject):
    id: PlaylistID

    def __init__(self, playlist_id: PlaylistID, name: str):
        self.id = playlist_id
        self.name = name


class Artist(SpotifyInfoObject):
    id: ArtistID

    def __init__(self, artist_id: ArtistID, name: str):
        self.id = artist_id
        self.name = name

class Album(SpotifyInfoObject):
    id: AlbumID
    cover_url: str
    artist_ids: List[ArtistID]

    def __init__(self, album_id: AlbumID, name: str, cover_url: str, artist_ids: List[ArtistID]):
        self.id = album_id
        self.name = name
        self.cover_url = cover_url
        self.artist_ids = artist_ids


class Track(SpotifyInfoObject):
    id: TrackID
    spotify_features: Dict
    mnn_features: List[float]
    album_id: AlbumID
    path: str
    playlist_ids: List[PlaylistID]

    def __init__(self, track_id: TrackID, name: str, spotify_features: Dict, mnn_features: List[float],
                 album_id: AlbumID, path: str, playlist_ids: List[PlaylistID]):
        self.id = track_id
        self.name = name
        self.spotify_features = spotify_features
        self.mnn_features = mnn_features
        self.album_id = album_id
        self.path = path
        self.playlist_ids = playlist_ids


class Memory:
    playlists: List[Playlist]
    albums: List[Album]
    artists: List[Artist]
    tracks: List[Track]

    def __init__(self, playlists, albums, artists, tracks):
        self.playlists = playlists
        self.albums = albums
        self.artists = artists
        self.tracks = tracks

    def validate(self) -> bool:
        for album in self.albums:
            for aid in album.artist_ids:
                if self.get_artist(aid) is None:
                    return False
        for track in self.tracks:
            for pid in track.playlist_ids:
                if self.get_playlist(pid) is None:
                    return False
            if self.get_album(track.album_id) is None:
                return False

        for ls in [self.tracks, self.albums, self.tracks, self.playlists]:
            if len(ls) != len(_map_ids(ls)):
                return False
        return True

    def get_playlist(self, item_id: PlaylistID) -> Playlist:
        return _get_by_id(self, 'playlists', item_id)

    def get_album(self, item_id: AlbumID) -> Album:
        return _get_by_id(self, 'albums', item_id)

    def get_track(self, item_id: TrackID) -> Track:
        return _get_by_id(self, 'tracks', item_id)

    def get_artist(self, item_id: ArtistID) -> Artist:
        return _get_by_id(self, 'artists', item_id)

    def __sub__(self, other: __qualname__) -> __qualname__:
        tracks = []
        for track in self.tracks:
            if not other.get_track(track.id):
                tracks.append(track)
        return Memory(self.playlists, self.albums, self.artists, tracks)

    def to_dict(self) -> Dict:
        return {
            'playlists': [playlist.to_dict() for playlist in self.playlists],
            'albums': [album.to_dict() for album in self.albums],
            'artists': [artist.to_dict() for artist in self.artists],
            'tracks': [track.to_dict() for track in self.tracks]
        }


def _get_by_id(mem, mem_type, item_id):
    for obj in getattr(mem, mem_type):
        if obj.id == item_id:
            return obj
    return None


def _map_ids(ls):
    return list(map(lambda x: x.id, ls))


def from_playlist(playlist_id, playlist_name, playlist_info) -> Memory:
    """
    A disgusting function that just had to be, sorry
    :param playlist_id: id of the playlist
    :param playlist_name: name of the playlist
    :param playlist_info: object returned by spotipy's .playlist(id) method
    :return:
    """
    playlists = [Playlist(playlist_id, playlist_name)]
    albums = []
    album_ids = []
    artists = []
    artist_ids = []
    tracks = []

    for track_info in playlist_info:
        track_info = track_info['track']

        album_info = track_info['album']
        album_id = album_info['id']
        if album_id in album_ids:
            continue

        album_artist_ids = []
        for artist_info in album_info['artists']:
            artist_id = artist_info['id']
            album_artist_ids.append(artist_id)
            if artist_id in artist_ids:
                continue

            artist_name = artist_info['name']
            artist_ids.append(artist_id)
            artists.append(Artist(artist_id, artist_name))

        album_ids.append(album_id)
        album_name = album_info['name']
        album_cover = album_info['images'][0]['url']
        albums.append(Album(album_id, album_name, album_cover, album_artist_ids))

        tracks.append(Track(track_info['id'], track_info['name'], {}, [], album_id, "", [playlist_id]))

    mem = Memory(playlists, albums, artists, tracks)
    if not mem.validate():
        print("WARNING: Invalid memory created, code is wrong")
    return mem
