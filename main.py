import datetime
import math

import spotipy

from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

SONGS_SENT_PER_REQUEST = 95  # Must be less than 100
MAX_SONGS_DIRECTLY_REQUESTED = 300
SCOPE = "user-library-read, " \
        "streaming, " \
        "user-follow-read, " \
        "playlist-modify-public, " \
        "playlist-modify-private, " \
        "playlist-read-private, " \
        "playlist-read-collaborative, " \
        "user-read-playback-state, " \
        "user-read-currently-playing"


def create_new_playlist():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=SCOPE))
    artists = get_artists(sp)
    artist_names = get_list_properties(artists, 'name')
    artist_uris = get_list_properties(artists, 'uri')
    duration_unit = input("Would you prefer to specify an amount of time or number of songs? (1/2) ")
    if duration_unit == '1':
        tracks_to_insert = get_time_length_songs(sp, artist_uris)
    else:
        successful_number_of_tracks = False
        num_tracks = 25
        while not successful_number_of_tracks:
            try:
                num_tracks = int(
                    input(
                        "How many songs would you like in your playlist? (Max out at " +
                        str(MAX_SONGS_DIRECTLY_REQUESTED) + ") Enter whole number of songs: "
                    )
                )
                successful_number_of_tracks = True
            except ValueError:
                pass
        recommended = sp.recommendations(
            seed_artists=artist_uris,
            limit=min(num_tracks, MAX_SONGS_DIRECTLY_REQUESTED)
        )
        tracks_to_insert = get_list_properties(recommended['tracks'], 'uri')

    playlist = sp.user_playlist_create(
        sp.current_user()['id'],
        ("Jams - " + ", ".join(artist_names))[:99],
        public=True,
        collaborative=False,
        description="Auto generated on " + datetime.datetime.now().strftime('%m/%d/%Y, %I:%M:%S %p')
    )
    for i in range(math.ceil(len(tracks_to_insert) / SONGS_SENT_PER_REQUEST)):
        sp.playlist_add_items(
            playlist_id=playlist['id'],
            items=tracks_to_insert[(i * SONGS_SENT_PER_REQUEST):((i + 1) * SONGS_SENT_PER_REQUEST)]
        )

    playlist_items = sp.playlist_items(playlist_id=playlist['id'])['items']
    playlist_duration = sum([x['track']['duration_ms'] for x in playlist_items]) // 60000
    duration_text = '' if playlist_duration // 3600 == 0 else str(playlist_duration / 3600) + ' hours, '
    duration_text += str(playlist_duration % 3600) + ' minutes'
    print('>> Playlist is ' + duration_text + '(' + str(len(playlist_items)) + ' songs) long')
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


def get_artists(sp):
    all_artists = []
    while len(all_artists) == 0:
        artist = get_artist(sp)
        if artist:
            all_artists.append(artist)

    finished_adding_artists = False
    while not finished_adding_artists:
        done_adding_response = input("Would you like to add more artists to base your playlist off? (y/n) ")
        if done_adding_response.lower() == 'y':
            artist = get_artist(sp)
            if artist and artist not in all_artists:
                all_artists.append(artist)
        else:
            finished_adding_artists = True

    print(
        ">> Playlist will be based on the following artist(s): " + ", ".join(get_list_properties(all_artists, 'name'))
    )
    return all_artists


def get_time_length_songs(sp, artists: list):
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
        recommended = sp.recommendations(seed_artists=artists)
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
        retry_response = input("Press any key to attempt playing playlist or \"q\" to quit")
        if retry_response.lower() == 'q':
            exit(0)


def get_list_properties(collection: list, key: str):
    return [x[key] for x in collection]


if __name__ == '__main__':
    load_dotenv()
    create_new_playlist()
