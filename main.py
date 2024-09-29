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

    # Initial post request ->
    print(SPOTIFYCLIENTID, SPOTIFYCLIENTSECRET)
    token = getToken(SPOTIFYCLIENTID, SPOTIFYCLIENTSECRET)
    
    # Get currently Playing Track ->
    
    while True:
        time.sleep(30)
        currentTrack = token.current_user_playing_track()
        print(currentTrack)

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
