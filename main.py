import datetime
import random

import spotipy

from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth


def main():
    load_dotenv()

    scope = "user-library-read, " \
            "streaming, " \
            "user-follow-read, " \
            "playlist-modify-public, " \
            "playlist-modify-private, " \
            "playlist-read-private, " \
            "playlist-read-collaborative, " \
            "user-read-playback-state, " \
            "user-read-currently-playing"

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    # results = sp.current_user_saved_tracks(limit=15)
    # len_songs = len(results['items'])
    # random_song = random.randrange(0, len_songs - 1)
    # for idx, item in enumerate(results['items']):
    #     track = item['track']
    #     # print(idx, track['artists'][0]['name'], "–", track['name'])
    #     if idx == random_song:
    #         try:
    #             sp.start_playback(uris=[track['uri']])
    #         except:
    #             sp.pause_playback()

    # print('~~~~~~~~~~~~~~~~~~~~~~')
    artist = None
    while artist is None:
        artist = get_artist(sp)
    tracks_to_insert = []
    duration_unit = input("Would you prefer to specify an amount of time or number of songs? (1/2)")
    if duration_unit == '1':
        tracks_to_insert = get_time_length_songs(sp, artist)
    else:
        recommended = sp.recommendations(seed_artists=[artist['uri']])
        tracks_to_insert = tracks_to_uris(recommended)

    playlist = sp.user_playlist_create(
        sp.current_user()['id'],
        "Jams - " + artist['name'],
        public=True,
        collaborative=False,
        description="Auto generated on " + datetime.datetime.now().strftime('%m/%d/%Y, %I:%M:%S %p')
    )
    sp.playlist_add_items(playlist['id'], tracks_to_insert)

    start_response = input('Would you like to listen to your newly created playlist? (y/n)')
    if start_response.lower() == 'n':
        return
    shuffle_response = input('Would you like to shuffle the music? (y/n)')
    successful_playback = False
    # for device in sp.devices()['devices']:

    while not successful_playback:
        try:
            sp.shuffle(shuffle_response.lower() == 'y')
            sp.start_playback(context_uri=playlist['uri'])
            successful_playback = True
        except:
            print("Please launch Spotify on an app and initiate playback on that device")
            retry_response = input("Press any key to attempt playing playist or \"q\" to quit")
            if retry_response.lower() == 'q':
                exit(0)


def tracks_to_uris(tracks):
    return [x['uri'] for x in tracks['tracks']]


def get_artist(sp):
    search_items = []
    while len(search_items) == 0:
        requested_artist = input('What artist would you like to make a playlist for: ')
        search_result = sp.search('artist:' + requested_artist, type='artist')
        search_items = search_result['artists']['items']
        if len(search_items) == 0:
            print("**  Unable to find desired artist in the given search **")
    if len(search_items) > 1:
        for artist in search_items:
            response = input("Were you looking for " + artist['name'] + "? (y/n/q)")
            if response.lower() == 'y':
                return artist
            if response.lower() == 'q':
                print("Quiting Program..")
                exit(0)
        print("**  Unable to find desired artist in the given search **")
        return None
    else:
        return search_items[0]


def get_time_length_songs(sp, artist):
    successful_time_input = False
    amount_of_time = 90
    while not successful_time_input:
        try:
            amount_of_time = int(input("How long would you like your playlist? Enter in whole minutes"))
            successful_time_input = True
        except TypeError:
            pass
    amount_of_time *= 60000
    song_time_so_far = 0
    tracks = []
    while song_time_so_far < amount_of_time:
        recommended = sp.recommendations(seed_artists=[artist['uri']])
        for track in recommended['tracks']:
            if song_time_so_far >= amount_of_time:
                break
            if track['uri'] not in tracks:
                tracks.append(track['uri'])
                song_time_so_far += track['duration_ms']
    return tracks


if __name__ == '__main__':
    main()
