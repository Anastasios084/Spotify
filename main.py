

import spotipy
import requests
import math
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd


columns = ['Track', 'Artist', 'Album', 'Duration']
df = pd.DataFrame(columns=columns)

# Set up your credentials
SPOTIPY_CLIENT_ID = '9c51a2c92c3347c6b1186ca74757adb5'
SPOTIPY_CLIENT_SECRET = '6f9350ce9af34fcfbd7eeb25a704b0de'
SPOTIPY_REDIRECT_URI = 'http://localhost:8000/'  # This can be any valid URI, for example, 'http://localhost/' (the port was added to specify)

# Authenticate with Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope='playlist-read-private'))

# Replace with your playlist ID
playlist_id = 'https://open.spotify.com/playlist/5a6SLrpoo6TKmrEbUAgAg4'

# Get playlist items
results = sp.playlist_items(playlist_id)

# Extract and print information for each track
for item in results['items']:
    track = item['track']
    track_name = track['name']
    track_duration_ms = track['duration_ms']
    artist_name = track['artists'][0]['name']
    album_name = track['album']['name']
    album_image = track['album']['images'][0]['url']
    
    # Convert duration from milliseconds to minutes and seconds
    duration_min = track_duration_ms // 60000
    duration_sec = track_duration_ms // 1000

    # Get audio features (including BPM)
    audio_features = sp.audio_features(track['id'])[0]
    bpm = round(audio_features['tempo'])
    
    img_data = requests.get(album_image).content
    with open('./track_photos/'+str(track_name)+'.jpg', 'wb') as handler:
        handler.write(img_data)

    print(f"Track: {track_name}")
    print(f"Artist: {artist_name}")
    print(f"Album: {album_name}")
    print(f"Album Image: {album_image}")
    print(f"Duration: {duration_min}:{duration_sec%60}")
    print(f"Duration in s: {duration_sec}")
    print(f"Duration in ms: {track_duration_ms}")

    print(f"BPM: {bpm}")

    print()
    ######################### DONE WITH PRINTING, LET'S SAVE THIS THING

    row = pd.DataFrame([{'Track': track_name, 'Artist': artist_name, 'Album': album_name, 'Duration': track_duration_ms}])

    df = pd.concat([df, row], ignore_index=True)

print(df)

df.to_csv("./playlist.csv", index=False)


