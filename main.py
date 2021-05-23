import random

import spotipy

from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

scope = "user-library-read, streaming"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
results = sp.current_user_saved_tracks()
len_songs = len(results['items'])
random_song = random.randrange(0, len_songs - 1)
for idx, item in enumerate(results['items']):
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    track = item['track']
    print(track)
    print(idx, track['artists'][0]['name'], " – ", track['name'])
    if idx == random_song:
        try:
            sp.start_playback(uris=[track['uri']])
        except:
            sp.pause_playback()
