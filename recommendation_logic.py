import random
import requests
from requests.exceptions import RequestException

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

def get_recommendation_logic(mood_input: str, api_key: str) -> dict:
    """
    Pure function to determine music recommendations based on mood and API availability.
    Implements normalization and guard clauses.
    """
    # 1. Normalization & Guard Clause for Mood (Decision Table Row 4)
    normalized_mood = mood_input.lower()
    if normalized_mood not in MOOD_GENRES:
        # Fallback for invalid mood input
        return {
            'status': 'Invalid Mood',
            'recommendations': random.sample(FALLBACK_SONGS['happy'], 3)
        }

    # 2. Guard Clause for API Key
    if not api_key:
        # Fallback if API key is missing
        genre = random.choice(MOOD_GENRES[normalized_mood])
        songs = FALLBACK_SONGS[normalized_mood]
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
        response.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)
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

    except (RequestException, ValueError, KeyError) as e:
        # API Failure or data failure (Decision Table Row 3)
        songs = FALLBACK_SONGS[normalized_mood]
        return {
            'status': f'API Failed ({type(e).__name__}). Using Fallback ({genre}).',
            'recommendations': random.sample(songs, min(3, len(songs)))
        }