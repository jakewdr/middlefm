import json
import time
import hashlib
import spotipy
import requests
import urllib.parse
from spotipy.oauth2 import SpotifyOAuth

def main() -> None:
    secretsDictionary = loadJson("secrets.json")

    SPOTIFYCLIENTID = secretsDictionary["Spotify"]["clientID"].strip()
    SPOTIFYCLIENTSECRET = secretsDictionary["Spotify"]["clientSecret"].strip()
    
    LASTFMAPIKEY = secretsDictionary["lastfm"]["apiKey"].strip()
    LASTFMSHAREDSECRET = secretsDictionary["lastfm"]["sharedSecret"].strip()

    lastTrackID = ""
    scrobbledTracks = set()

    automaticEdits = loadJson("automaticEdits.json")

    token = getToken(SPOTIFYCLIENTID, SPOTIFYCLIENTSECRET)
    lastFMToken = getLastFMToken(LASTFMAPIKEY)
    lastFMsessionKey = getSessionKey(LASTFMAPIKEY, LASTFMSHAREDSECRET, lastFMToken)

    while True:
        try:
            currentTrack = token.current_user_playing_track()
            if currentTrack and currentTrack["is_playing"]:       
                trackName = currentTrack["item"]["name"]
                trackArtist = currentTrack["item"]["artists"][0]["name"]
                trackAlbum = currentTrack["item"]["album"]["name"]
                trackID = currentTrack['item']['id']
                trackProgressMS = currentTrack["progress_ms"]
                trackProgressSeconds = trackProgressMS / 1000
                trackDurationSeconds = currentTrack["item"]["duration_ms"] / 1000
                
                print(f"Name: {trackName}\nArtist: {trackArtist}\nAlbum: {trackAlbum}\nCurrent Progress: {trackProgressSeconds:.2f}\n")

                if trackID not in scrobbledTracks and (trackProgressSeconds >= 240 or trackProgressSeconds >= trackDurationSeconds / 2):
                    scrobbleTrack(trackName, trackArtist, trackAlbum, LASTFMAPIKEY, automaticEdits, LASTFMSHAREDSECRET, lastFMToken, lastFMsessionKey)
                    scrobbledTracks.add(trackID)

                if lastTrackID != trackID or trackProgressMS < 15000:  # Reset if the track ID changes or restarts
                    lastTrackID = trackID
                    scrobbledTracks.clear()
            else:
                print("No track playing!")
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(10)

def scrobbleTrack(track, artist, album, apiKey, edits, secret, token, sessionKey):
    newTags = tagFixer(track, artist, album, edits)
    url = 'http://ws.audioscrobbler.com/2.0/'

    data = {
        'method': 'track.scrobble',
        'api_key': apiKey,
        'sk': sessionKey,
        'artist': newTags[0],
        'track': newTags[1],
        'album': newTags[2],
        'timestamp': int(time.time()),
        'format': 'json'
    }

    signature = generateSignature(data, secret)
    data['api_sig'] = signature
    
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        print("Track scrobbled successfully.")
    except requests.RequestException as e:
        print(f"Failed to scrobble track: {e}")

def generateSignature(params, apiSecret):
    keys = sorted(params.keys())
    signature = ''.join(f'{key}{params[key]}' for key in keys) + apiSecret
    return hashlib.md5(signature.encode('utf-8')).hexdigest()

def getToken(clientID: str, clientSecret: str) -> dict: 
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=clientID,
        client_secret=clientSecret,
        redirect_uri="https://github.com/jakewdr/middlefm/",
        scope="user-read-playback-state"
    ))

def getLastFMToken(apiKey):
    authUrl = f'http://last.fm/api/auth/?api_key={apiKey}&cb={urllib.parse.quote("https://github.com/jakewdr/middlefm/")}'
    print(f'Visit this URL to authenticate: {authUrl}')
    token = input("Paste the text after 'github.com/jakewdr/middlefm?token=': ")
    return token

def getSessionKey(apiKey, apiSecret, tokenValue):
    url = 'http://ws.audioscrobbler.com/2.0/'
    params = {
        'method': 'auth.getSession',
        'api_key': apiKey,
        'token': tokenValue,
        'format': 'json'
    }
    params["api_sig"] = generateSignature(params, apiSecret)
    
    try:
        response = requests.post(url, data=params)
        response.raise_for_status()
        sessionData = response.json()
        return sessionData['session']['key']
    except requests.RequestException as e:
        print(f"Failed to get session key: {e}")
        return None

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
    print([title, album, artist])
    return [title, artist, album]

def loadJson(jsonFileName: str) -> dict:
    try:
        with open(jsonFileName, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Failed to load JSON file {jsonFileName}: {e}")
        return {}

if __name__ == "__main__":
    main()
