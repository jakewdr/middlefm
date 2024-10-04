import requests
import hashlib
import urllib
import json

def getSessionKey(apiKey, apiSecret, tokenValue):
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        'method': 'auth.getSession',
        'api_key': apiKey,
        'token': tokenValue
    }
    params["api_sig"] = generateSignature(params, apiSecret)
    
    try:
        response = requests.post(url, data=params)
        response.raise_for_status()
        sessionData = response.json()
        return sessionData['session']['key']
    except requests.RequestException as error:
        print(f"Failed to get session key: {error}")
        print(f"Response content: {response.text}")
        return None

def getLastFMToken(apiKey):
    authUrl = f'http://last.fm/api/auth/?api_key={apiKey}&cb={urllib.parse.quote("https://github.com/jakewdr/middlefm/")}'
    print(f'Visit this URL to authenticate: {authUrl}')
    token = input("Paste the text after 'github.com/jakewdr/middlefm?token=': ")
    return token

def loadJson(jsonFileName: str) -> dict:
    try:
        with open(jsonFileName, 'r') as file:
            return json.load(file)
    except Exception as error:
        print(f"Failed to load JSON file {jsonFileName}: {error}")
        return {}
    
def generateSignature(params, apiSecret):
    keys = sorted(params.keys())
    signature = ''.join(f'{key}{params[key]}' for key in keys) + apiSecret
    return hashlib.md5(signature.encode('utf-8')).hexdigest()

if __name__ == "__main__":
    secretsDictionary = loadJson("secrets.json")
    print(secretsDictionary)
    LASTFMAPIKEY = secretsDictionary["lastfm"]["apiKey"].strip()
    LASTFMSHAREDSECRET = secretsDictionary["lastfm"]["sharedSecret"].strip()
    LASTFMTOKEN = getLastFMToken(LASTFMAPIKEY)
    print(getSessionKey(LASTFMAPIKEY, LASTFMSHAREDSECRET, LASTFMTOKEN))