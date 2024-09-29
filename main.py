import json
import spotipy
import time
from spotipy.oauth2 import SpotifyOAuth

def main() -> None:
    
    # Loading secret variables ->
    
    secretsDictionary: dict = loadJson("secrets.json")
    
    SPOTIFYCLIENTID: str = secretsDictionary["Spotify"]["clientID"].strip()
    SPOTIFYCLIENTSECRET: str = secretsDictionary["Spotify"]["clientSecret"].strip()
    
    LASTFMAPIKEY: str = secretsDictionary["lastfm"]["apiKey"].strip()
    LASTFMSHAREDSECRET: str = secretsDictionary["lastfm"]["sharedSecret"].strip()

    # Getting the token ->

    token = getToken(SPOTIFYCLIENTID, SPOTIFYCLIENTSECRET)
    
    # Get currently Playing Track ->
    
    while True:
        currentTrack = token.current_user_playing_track()
        
        trackName = currentTrack["item"]["name"]
        trackArtist = currentTrack["item"]["artists"][0]["name"]
        trackAlbum = currentTrack["item"]["album"]["name"]
        print(f"Name: {trackName}\nArtist: {trackArtist}\nAlbum: {trackAlbum}\n")

        time.sleep(30)

def getToken(clientID: str, clientSecret: str):
    token = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=clientID,
            client_secret=clientSecret,
            redirect_uri="https://github.com/jakewdr/middlefm/",
            scope="user-read-playback-state"
        )
    )
    return token

def loadJson(jsonFileName: str) -> dict:
    with open(jsonFileName, 'r') as file:
        return dict(json.load(file))

if __name__ == "__main__":
    main()
