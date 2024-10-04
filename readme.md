# How to set this up

## Getting the project downloaded

First thing you need to do is to get the code on your local machine, there are a few requirements though

1) Python 3 (tested on python 3.11.9)
2) Git (if you git clone the repository)
3) Docker (for building the image)

You can either run the command:

    git clone https://github.com/jakewdr/middlefm/

or use the button 'Code' -> 'Download Zip' on the GitHub page

Then just run:

    pip install -r requirements.txt

## Getting API keys

Firstly rename templateSecrets.json to secrets.json

Next you are going to need to acquire [last.fm](https://www.last.fm/api/account/create) and [Spotify](https://developer.spotify.com/dashboard) api keys

### LastFM

Navigate to the API account creation page and input these in the boxes:

- *Application name* = middlefm

- *Application description* = Middle Layer between spotify and LastFM allowing for automatic track edits

- *Callback URL* = "https://github.com/jakewdr/middlefm

- *Application Homepage* = "https://github.com/jakewdr/middlefm/

After doing this you will get a secret and a API key **DO NOT SHARE** them with anyone else, all you need to do then is place them in the secrets.json file in the *apiKey* and *sharedSecret*

### Spotify

Spotify can be a bit more difficult but the steps are largely the same. First log into the spotify dashboard for developers and click create new app, then input these details into the boxes:

- *App Name* = middlefm
- *App description* = Middle Layer between spotify and LastFM allowing for automatic track edits
- *Redirect URIs* = https://github.com/jakewdr/middlefm/ **(PLEASE MAKE SURE IT HAS THE SLASH AT THE END)**
- Select Web API

Then as with lastfm you copy the client ID and client secret into the relevant json fields

## LastFM session key

Next up is authentication, run the getSessionKey.py file and follow the steps making sure to paste the information after ?token= only

In the command line you should get the session key, which you can copy and paste into the relevant field of the json file

## Spotify token

For the spotify token run the main.py file and follow the details in the command prompt, if done correctly you will have a .cache file in your directory which is needed for the final steps

## Docker image

To generate a docker image run:

    docker build -t python-middlefm .

This allows you to host the project anywhere you like
