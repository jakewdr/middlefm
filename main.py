import json
import time
import calendar
import datetime
import hashlib
import spotipy
import requests
from spotipy.oauth2 import SpotifyOAuth


def main() -> None:
    secretsDictionary = loadJson("secrets.json")

    SPOTIFYCLIENTID = secretsDictionary["Spotify"]["clientID"].strip()
    SPOTIFYCLIENTSECRET = secretsDictionary["Spotify"]["clientSecret"].strip()

    LASTFMAPIKEY = secretsDictionary["lastfm"]["apiKey"].strip()
    LASTFMSHAREDSECRET = secretsDictionary["lastfm"]["sharedSecret"].strip()
    LASTFMSESSIONKEY = secretsDictionary["lastfm"]["sessionKey"].strip()

    lastTrackID = ""
    scrobbledTracks = set()

    automaticEdits = loadJson("automaticEdits.json")

    token = getToken(SPOTIFYCLIENTID, SPOTIFYCLIENTSECRET)

    while True:
        try:
            currentTrack = token.current_user_playing_track()
            if currentTrack and currentTrack["is_playing"]:
                trackName = currentTrack["item"]["name"]
                trackArtist = currentTrack["item"]["artists"][0]["name"]
                trackAlbum = currentTrack["item"]["album"]["name"]
                trackID = currentTrack["item"]["id"]
                trackProgressMS = currentTrack["progress_ms"]
                trackProgressSeconds = trackProgressMS / 1000
                trackDurationSeconds = currentTrack["item"]["duration_ms"] / 1000
                currentlyPlayingTrack(
                    trackName,
                    trackArtist,
                    trackAlbum,
                    automaticEdits,
                    LASTFMAPIKEY,
                    LASTFMSHAREDSECRET,
                    LASTFMSESSIONKEY,
                )

                print(
                    f"Name: {trackName}\nArtist: {trackArtist}\nAlbum: {trackAlbum}\nCurrent Progress: {trackProgressSeconds:.2f}\n"
                )

                if trackID not in scrobbledTracks and (
                    trackProgressSeconds >= 240
                    or trackProgressSeconds >= trackDurationSeconds / 2
                ):
                    scrobbleTrack(
                        trackName,
                        trackArtist,
                        trackAlbum,
                        LASTFMAPIKEY,
                        automaticEdits,
                        LASTFMSHAREDSECRET,
                        LASTFMSESSIONKEY,
                        trackProgressSeconds,
                    )
                    scrobbledTracks.add(trackID)

                if (
                    lastTrackID != trackID or trackProgressMS < 15000
                ):  # Reset if the track ID changes or restarts
                    lastTrackID = trackID
                    scrobbledTracks.clear()
            else:
                print("No track playing!")
        except Exception as error:
            print(f"Error: {error}")

        time.sleep(10)


def scrobbleTrack(
    track, artist, album, apiKey, edits, secret, sessionKey, trackProgress
):
    newTags = tagFixer(track, artist, album, edits)
    url = "http://ws.audioscrobbler.com/2.0/"
    data = {
        "method": "track.scrobble",
        "api_key": apiKey,
        "sk": sessionKey,
        "artist": newTags[1],
        "track": newTags[0],
        "album": newTags[2],
        "timestamp": int(calendar.timegm(datetime.datetime.utcnow().utctimetuple()))
        - int(trackProgress),
        "format": "json",
    }

    signature = generateSignature(data, secret)
    data["api_sig"] = signature

    try:
        response = requests.post(url, data=data)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        print("Track scrobbled successfully.")
    except requests.RequestException as error:
        print(f"Failed to scrobble track: {error}")
        print(f"Response content: {response.text}")


def currentlyPlayingTrack(track, artist, album, edits, apiKey, secret, sessionKey):
    newTags = tagFixer(track, artist, album, edits)
    url = "http://ws.audioscrobbler.com/2.0/"
    data = {
        "method": "track.updateNowPlaying",
        "api_key": apiKey,
        "sk": sessionKey,
        "artist": newTags[1],
        "track": newTags[0],
        "album": newTags[2],
        "format": "json",
    }
    signature = generateSignature(data, secret)
    data["api_sig"] = signature

    try:
        response = requests.post(url, data=data)
        response.raise_for_status()  # Raises an HTTPError for bad responses
    except requests.RequestException as error:
        print(f"Failed to set track as currently playing: {error}")
        print(f"Response content: {response.text}")


def generateSignature(params, apiSecret):
    del params["format"]
    keys = sorted(params.keys())
    signature = "".join(f"{key}{params[key]}" for key in keys) + apiSecret
    return hashlib.md5(signature.encode("utf-8")).hexdigest()


def getToken(clientID: str, clientSecret: str) -> dict:
    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=clientID,
            client_secret=clientSecret,
            redirect_uri="https://github.com/jakewdr/middlefm/",
            scope="user-read-playback-state",
        )
    )


def tagFixer(title: str, artist: str, album: str, edits: dict) -> list:
    if album in edits["albums"] and artist in edits["albums"]["originalArtist"]:
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
    if title in edits["songs"]:
        currentSong = edits["songs"][title]
        if (
            currentSong["originalArtist"] == artist
            and currentSong["originalAlbum"] == album
        ):
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
        with open(jsonFileName, "r") as file:
            return json.load(file)
    except Exception as error:
        print(f"Failed to load JSON file {jsonFileName}: {error}")
        return {}


if __name__ == "__main__":
    main()
