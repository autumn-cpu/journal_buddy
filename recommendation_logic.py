import logging
import random
import requests
from requests.exceptions import RequestException, HTTPError

# Mood to genre mapping
MOOD_GENRES = {
    "happy": ["pop", "dance", "electronic"],
    "sad": ["indie", "alternative", "folk"],
    "stressed": ["ambient", "chillout", "new age"],
    "relaxed": ["jazz", "classical", "acoustic"]
}

# Offline/Fallback Music Database 
FALLBACK_SONGS = {
    "happy": [("Happy", "Pharrell Williams"), ("Good as Hell", "Lizzo"), ("Uptown Funk", "Bruno Mars")],
    "sad": [("Someone Like You", "Adele"), ("Hurt", "Johnny Cash"), ("Mad World", "Gary Jules")],
    "stressed": [("Weightless", "Marconi Union"), ("Clair de Lune", "Debussy"), ("Aqueous Transmission", "Incubus")],
    "relaxed": [("Take Five", "Dave Brubeck"), ("Blue in Green", "Miles Davis"), ("River", "Joni Mitchell")]
}

# python
def get_recommendation_logic(mood_input: str, api_key: str) -> dict:
    if not isinstance(mood_input, str) or not mood_input:
        return {'status': 'Invalid Mood', 'recommendations': random.sample(FALLBACK_SONGS['happy'], 3)}

    normalized_mood = mood_input.lower()
    if normalized_mood not in MOOD_GENRES:
        return {'status': 'Invalid Mood', 'recommendations': random.sample(FALLBACK_SONGS['happy'], 3)}

    songs = FALLBACK_SONGS[normalized_mood]
    genre = random.choice(MOOD_GENRES[normalized_mood])

    if not api_key:
        return {
            'status': f'API Key Missing. Using Fallback ({genre}).',
            'recommendations': random.sample(songs, min(3, len(songs)))
        }
    

    genre = random.choice(MOOD_GENRES[normalized_mood])
    url = "https://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "tag.gettoptracks",
        "tag": genre,
        "api_key": api_key,
        "format": "json",
        "limit": 10
    }

    try:
        response = requests.get(url, params=params, timeout=5)

        # Force HTTP errors so tests can catch Status 500
        if response.status_code != 200:
            raise HTTPError(response=response)

        data = response.json()
    # Check for tracks found (Decision Table Row 1)
    if "tracks" in data and "track" in data["tracks"]:
        tracks = data["tracks"]["track"]
        if tracks:
            selected = random.sample(tracks, min(3, len(tracks)))
            formatted_tracks = [(t['name'], t['artist']['name']) for t in selected]
            return {
                'status': f'API Success ({genre}).',
                'recommendations': formatted_tracks
            }

    # API returned valid JSON but no tracks (Decision Table Row 2)
    raise ValueError("API returned no usable track data.")


    # ------------------ 1. CATCH HTTP STATUS ERRORS FIRST ------------------
    except requests.exceptions.HTTPError as e:
        code = getattr(e.response, "status_code", "unknown")
        status = f"API Failed (Status {code}) Using Fallback ({genre})."
        return {
            'status': status,
            'recommendations': random.sample(songs, min(3, len(songs)))
        }

# 2. CATCH ALL OTHER EXCEPTIONS (RequestException, Value Error, Key Error)
    except (requests.exceptions.RequestException, ValueError, KeyError) as e:
        songs = FALLBACK_SONGS[normalized_mood]
        status = f'API Failed ({type(e).__name__}). Using Fallback ({genre}).'
        logging.warning(f"Connection or parsing failure: {e}") 
        
        return {
            'status': status,
            'recommendations': random.sample(songs, min(3, len(songs)))
        }