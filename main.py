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
    
    # Making these empty strings for later ->
    
    trackName: str = ""
    trackArtist: str = ""
    trackAlbum: str = ""
    
    lastTrackID: str = ""
    scrobbledTracks: set = set()
    
    numberOfTimesRan: int = 0

    # Loading automatic edits ->
    
    secretsDictionary: dict = loadJson("automaticEdits.json")

    # Getting the token ->

    token = getToken(SPOTIFYCLIENTID, SPOTIFYCLIENTSECRET)
    
    # Get currently Playing Track ->
    
    while True:
        currentTrack = token.current_user_playing_track()
        if (currentTrack and currentTrack["is_playing"]) == True:       
            trackName = currentTrack["item"]["name"]
            trackArtist = currentTrack["item"]["artists"][0]["name"]
            trackAlbum = currentTrack["item"]["album"]["name"]
            trackID = currentTrack['item']['id']
            
            trackProgressMS = currentTrack["progress_ms"]
            trackProgressSeconds = trackProgressMS / 1000
            trackDurationSeconds = currentTrack["item"]["duration_ms"] / 1000
            
            print(f"Name: {trackName}\nArtist: {trackArtist}\nAlbum: {trackAlbum}\nCurrent Progress: {str(trackProgressSeconds)}\n")

            if (trackProgressSeconds >= 240 or 
            trackProgressSeconds >= trackDurationSeconds / 2):
                if trackID  not in scrobbledTracks:
                    print("Scrobble")
                scrobbledTracks.add(trackID)
                
            if lastTrackID != trackID or trackProgressMS < 15000:  # Reset if the track ID changes or restarts
                lastTrackID = trackID
                scrobbledTracks.clear()
        else:
            print("No track playing!")
        time.sleep(10)

def getToken(clientID: str, clientSecret: str) -> dict: 
    token = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=clientID,
            client_secret=clientSecret,
            redirect_uri="https://github.com/jakewdr/middlefm/",
            scope="user-read-playback-state"
        )
    )
    return token

def tagFixer(title: str, artist: str, album: str, edits: dict) -> list:
    if album in edits["album"]:
        currentAlbum = edits["album"][album]
        if title not in currentAlbum["ignoredTracks"]:
            if currentAlbum["newAlbum"] != "":
                album = currentAlbum["newAlbum"]
            if currentAlbum["newArtist"] != "":
                artist = currentAlbum["newArtist"]
            if currentAlbum["removeString"] != "":
                title = title.replace(currentAlbum["removeString"], "")
            if currentAlbum["format"] != "":
                if currentAlbum["format"] == "capital":
                    title.title()
                elif currentAlbum["format"] == "capital1":
                    title.capitalize()
                elif currentAlbum["format"] == "lower":
                    title.lower()
                elif currentAlbum["format"] == "upper":
                    title.upper()
        elif title in currentAlbum["ignoredTracks"]:
            if currentAlbum["ignoredTracksNewAlbum"] != "":
                album = currentAlbum["ignoredTracksNewAlbum"]
            if currentAlbum["ignoredTracksRemoveString"] != "":
                title = title.replace(currentAlbum["removeString"], "")
    elif title in edits["song"]:
        currentSong = edits["song"][title]
        if currentSong["originalArtist"] == artist and currentSong["originalAlbum"] == album:
            if currentSong["newName"] != "":
                title = currentSong["newName"]
            if currentSong["newArtist"] != "":
                artist = currentSong["newArtist"]
            if currentSong["newAlbum"] != "":
                album = currentSong["newAlbum"]
    
    return [title, artist, album]    

def loadJson(jsonFileName: str) -> dict:
    with open(jsonFileName, 'r') as file:
        return dict(json.load(file))

if __name__ == "__main__":
    main()
