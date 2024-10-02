# I literally can't be asked to finish this
import json
import time
import hashlib
import spotipy
import requests
import urllib.parse
from spotipy.oauth2 import SpotifyOAuth

def main() -> None:
    
    # Loading secret variables ->
    
    secretsDictionary: dict = loadJson("secrets.json")
    
    SPOTIFYCLIENTID: str = secretsDictionary["Spotify"]["clientID"].strip()
    SPOTIFYCLIENTSECRET: str = secretsDictionary["Spotify"]["clientSecret"].strip()
    
    LASTFMAPIKEY: str = secretsDictionary["lastfm"]["apiKey"].strip()
    LASTFMSHAREDSECRET: str = secretsDictionary["lastfm"]["sharedSecret"].strip()
    LASTFMUSERNAME: str = secretsDictionary["lastfm"]["username"].strip()
    LASTFMPASSWORD = hashlib.md5(secretsDictionary["lastfm"]["password"].strip().encode("utf-8")).hexdigest()
    # Making these empty strings for later ->
    
    trackName: str = ""
    trackArtist: str = ""
    trackAlbum: str = ""
    
    lastTrackID: str = ""
    scrobbledTracks: set = set()
    
    numberOfTimesRan: int = 0

    # Loading automatic edits ->
    
    automaticEdits: dict = loadJson("automaticEdits.json")

    # Getting the Spotify token ->

    token = getToken(SPOTIFYCLIENTID, SPOTIFYCLIENTSECRET)
    
    # Getting the Lastfm

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
                    scrobbleTrack(trackName, trackArtist, trackAlbum, LASTFMAPIKEY, automaticEdits, LASTFMSHAREDSECRET)
                scrobbledTracks.add(trackID)
                
            if lastTrackID != trackID or trackProgressMS < 15000:  # Reset if the track ID changes or restarts
                lastTrackID = trackID
                scrobbledTracks.clear()
        else:
            print("No track playing!")
        time.sleep(10)

def scrobbleTrack(track, artist, album, apiKey, edits, secret):
    newTags = tagFixer(track, artist, album, edits)
    url = 'http://ws.audioscrobbler.com/2.0/'

    # Prepare the data
    data = {
        'method': 'track.scrobble',
        'api_key': apiKey,
        'sk': getSessionKey(apiKey, secret),
        'artist': newTags[0],
        'track': newTags[1],
        'album': newTags[2],
        'timestamp': time.time(),
        'format': 'json'
    }

    signature = generateSignature(data, secret)
    data['api_sig'] = signature
    
    response = requests.post(url, data=data)

def generateSignature(params, apiSecret):
    # Sort parameters and concatenate them
    keys = sorted(params.keys())
    signature = ''.join(f'{key}{params[key]}' for key in keys)
    signature += apiSecret
    return hashlib.md5(signature.encode('utf-8')).hexdigest()

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

def getLastFMToken(apiKey):
    authUrl = f'http://last.fm/api/auth/?api_key={apiKey}&cb={urllib.parse.quote("https://github.com/jakewdr/middlefm/")}'
    print(f'Visit this URL to authenticate: {authUrl}')
    token = input("Paste the text after in the address bar after 'github.com/jakewdr/middlefm?token='")

    return token

def getSessionKey(apiKey, apiSecret):
    url = 'http://ws.audioscrobbler.com/2.0/'
    tokenValue = getLastFMToken(apiKey)
    params = {
        'method': 'auth.getSession',
        'api_key': apiKey,
        'token': tokenValue,
        'format': 'json'
    }
    params["api_sig"] = f"api_key{params['api_key']}methodauth.getSessiontoken{tokenValue}{apiSecret}"
    params["api_sig"] = hashlib.md5(params["api_sig"].encode('utf-8')).hexdigest()
    # Make the request
    response = requests.post(url, data=params)
    sessionData = response.json()
    print(sessionData)
    sessionKey = sessionData['session']['key']

    return sessionKey

def tagFixer(title: str, artist: str, album: str, edits: dict) -> list:
    if album in edits["albums"]:
        currentAlbum = edits["albums"][album]
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
    elif title in edits["songs"]:
        currentSong = edits["songs"][title]
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
