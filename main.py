import datetime
import math

import spotipy

from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

SONGS_SENT_PER_REQUEST = 95  # Must be less than 100
MAX_SONGS_DIRECTLY_REQUESTED = 300

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
    artist = None
    while artist is None:
        artist = get_artist(sp)
    duration_unit = input("Would you prefer to specify an amount of time or number of songs? (1/2) ")
    if duration_unit == '1':
        tracks_to_insert = get_time_length_songs(sp, artist)
    else:
        successful_number_of_tracks = False
        num_tracks = 25
        while not successful_number_of_tracks:
            try:
                num_tracks = int(input("How many songs would you like in your playlist? (Max out at 250) Enter whole number of songs: "))
                successful_number_of_tracks = True
            except ValueError:
                pass
        recommended = sp.recommendations(seed_artists=[artist['uri']], limit=min(num_tracks, MAX_SONGS_DIRECTLY_REQUESTED))
        tracks_to_insert = tracks_to_uris(recommended)

    playlist = sp.user_playlist_create(
        sp.current_user()['id'],
        "Jams - " + artist['name'],
        public=True,
        collaborative=False,
        description="Auto generated on " + datetime.datetime.now().strftime('%m/%d/%Y, %I:%M:%S %p')
    )
    for i in range(math.ceil(len(tracks_to_insert) / SONGS_SENT_PER_REQUEST)):
        sp.playlist_add_items(
            playlist_id=playlist['id'],
            items=tracks_to_insert[(i * SONGS_SENT_PER_REQUEST):((i + 1) * SONGS_SENT_PER_REQUEST)]
        )

    start_response = input('Would you like to listen to your newly created playlist? (y/n) ')
    if start_response.lower() == 'n':
        return
    shuffle_response = input('Would you like to shuffle the music? (y/n) ')
    successful_playback = False
    wait_for_active_device(sp)
    while not successful_playback:
        sp.shuffle(shuffle_response.lower() == 'y')
        sp.start_playback(context_uri=playlist['uri'])
        successful_playback = True


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
            response = input("Were you looking for " + artist['name'] + "? (y/n/q) ")
            if response.lower() == 'y' or response.lower() == '1':
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
            amount_of_time = int(input("How long would you like your playlist to be? Enter in whole minutes: "))
            successful_time_input = True
        except ValueError:
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


def is_device_available(sp):
    for device in sp.devices()['devices']:
        print(device)
        if device['is_active']:
            return True
    return False


def wait_for_active_device(sp):
    while not is_device_available(sp):
        print("Please launch Spotify on an app and initiate playback on that device")
        retry_response = input("Press any key to attempt playing playist or \"q\" to quit")
        if retry_response.lower() == 'q':
            exit(0)


if __name__ == '__main__':
    main()
