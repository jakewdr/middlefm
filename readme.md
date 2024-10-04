    docker build -t python-middlefm .
    https://docs.render.com/deploy-an-image

# How to set this up

## Getting the project downloaded

First thing you need to do is to get the code on your local machine, there are a few requirements though

1) Python 3 (tested on python 3.11.9)
2) Git (if you git clone the repository)
3) Docker (for building the image)

You can either run the command:

    git clone https://github.com/jakewdr/middlefm/

or use the button 'Code' -> 'Download Zip' on the GitHub page

## Getting API keys

Next you are going to need to acquire [last.fm](https://www.last.fm/api/account/create) and [Spotify](https://developer.spotify.com/dashboard) api keys

### LastFM

Navigate to the API account creation page and input these in the following boxes

*Application name* = middlefm

*Application description* = Middle Layer between spotify and LastFM allowing for automatic track edits

*Callback URL* = "https://github.com/jakewdr/middlefm

*Application Homepage* = "https://github.com/jakewdr/middlefm/

After doing this you will get a secret and a API key **DO NOT SHARE** them with anyone else, all you need to do then is place them in the secrets.json file in the *apiKey* and *sharedSecret*