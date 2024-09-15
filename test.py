import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Spotify API setup
SPOTIFY_CLIENT_ID = open('spotify_id.txt').read()
SPOTIFY_CLIENT_SECRET = open('spotify_secret.txt').read()
SPOTIFY_REDIRECT_URI = 'https://google.com/callback'

scope = "user-read-playback-state user-modify-playback-state"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID,
                                               client_secret=SPOTIFY_CLIENT_SECRET,
                                               redirect_uri=SPOTIFY_REDIRECT_URI,
                                               scope=scope))

def main():
    url = "https://open.spotify.com/album/7sGYAV0xv7ZfAMzIpMl8m1?si=ig9pg2bjQoSkLu45v8kIvg"
    album_id = url.split('/')[-1].split('?')[0]
    print(album_id)
    album_info = sp.album(album_id)
    tracks = album_info['tracks']['items']
    for track in tracks:
        print(track['name'])

if __name__ == '__main__':
    main()