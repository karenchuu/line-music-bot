import datetime as dt
from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
from bs4 import BeautifulSoup

load_dotenv()

BILLBOARD_URL = "https://www.billboard.com/charts/hot-100/"

# the scope required by the Spotify API, to allow the creation and modification of playlists
SPOTIFY_CLIENT_ID = os.environ['SPOTIFY_CLIENT_ID']
SPOTIFY_SECRET = os.environ['SPOTIFY_SECRET']
SCOPE = "playlist-modify-private"
REDIRECT_URL = "http://example.com"

# number of years to go back, make sure there was a Billboard chart published
# while True:
#     YEARS_AGO = int(input("你想建立幾年前的 Billboard Hot 100 進 Spotify Album？(ex.20) "))
#     if YEARS_AGO > 0:
#         break
#
# # calculate the date in the past
# today = dt.datetime.now().strftime("%Y-%m-%d").split("-")
# past_year = int(today[0]) - YEARS_AGO
# past_date = f"{past_year}-{today[1]}-{today[2]}"

def add_hot100_in_spotify_playlists(date):

    # Scraping Billboard 100
    page_url = BILLBOARD_URL + date
    response = requests.get(url=page_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    all_songs = soup.find_all("span", class_="chart-element__information__song")
    all_artists = soup.find_all("span", class_="chart-element__information__artist")

    # get lists of songs and artists for that year
    song_list = [song.get_text() for song in all_songs]
    artist_list = [artist.get_text() for artist in all_artists]

    # Spotify Authentication
    # at the first run this will open the web browser for confirmation and generate [token.txt]
    oauth = SpotifyOAuth(scope=SCOPE, redirect_uri=REDIRECT_URL,
                         client_id=SPOTIFY_CLIENT_ID,
                         client_secret=SPOTIFY_SECRET,
                         show_dialog=True, cache_path="token.txt")
    sp = spotipy.Spotify(auth_manager=oauth)
    user_id = sp.current_user()["id"]

    if song_list:
        song_uris = []
        for i in range(100):
            # print(f"#{i + 1}: {song_list[i]} by {artist_list[i]}")
            result = sp.search(q=f"track:{song_list[i]} year:{date[:4]}", type="track")
            try:
                uri = result["tracks"]["items"][0]["uri"]
            except IndexError:
                print(f"{song_list[i]} by {artist_list[i]} doesn't exist in Spotify. Skipped.")
            else:
                song_uris.append(uri)

        # if song_list exist, create the playlist
        playlist = sp.user_playlist_create(user=user_id, name=f"Week of {date} Billboard 100", public=False)
        # add the songs
        sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)
        return 0
    else:
        return None
