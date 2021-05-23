import datetime
import random

import spotipy

from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

scope = "user-library-read, " \
        "streaming, " \
        "user-follow-read, " \
        "playlist-modify-public, " \
        "playlist-modify-private, " \
        "playlist-read-private, " \
        "playlist-read-collaborative"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
results = sp.current_user_saved_tracks(limit=15)
len_songs = len(results['items'])
random_song = random.randrange(0, len_songs - 1)
for idx, item in enumerate(results['items']):
    track = item['track']
    print(idx, track['artists'][0]['name'], "–", track['name'])
    if idx == random_song:
        try:
            sp.start_playback(uris=[track['uri']])
        except:
            sp.pause_playback()

print('~~~~~~~~~~~~~~~~~~~~~~')

requested_artist = input('What artist would you like to listen to: ')
search_result = sp.search('artist:' + requested_artist, type='artist')
search_items = search_result['artists']['items']
artist = None
if len(search_items) > 0:
    artist = search_items[0]
    top_tracks = sp.artist_top_tracks(artist['uri'])
    top_track_uris = [x['uri'] for x in top_tracks['tracks']]
    input('Press Enter To Listen To Your Favorite Artist')
    try:
        sp.start_playback(uris=top_track_uris)
    except:
        sp.pause_playback()

print('~~~~~~~~~~~~~~~~~~~~~~')

print(len(sp.recommendation_genre_seeds()['genres']))
if artist:
    recommended = sp.recommendations(seed_artists=[artist['uri']])
    # print(recommended)
    sp.user_playlist_create(
        sp.current_user()['id'],
        "Jams",
        public=True,
        collaborative=False,
        description="Auto generated on " + datetime.datetime.now().strftime('%m/%d/%Y, %I:%M:%S %p')
    )
