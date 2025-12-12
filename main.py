import random
import datetime
import os
import requests
from dotenv import load_dotenv
# Load environment variables
load_dotenv()
# Mood to genre mapping for Last.fm API
mood_genres = {
    "happy": ["pop", "dance", "electronic"],
    "sad": ["indie", "alternative", "folk"],
    "stressed": ["ambient", "chillout", "new age"],
    "relaxed": ["jazz", "classical", "acoustic"]
}
def write_entry():
    """Write a new journal entry"""
    print("\n--- New Journal Entry ---")
    entry = input("Write your thoughts: ")
    mood = input("How are you feeling? (Happy/Sad/Stressed/Relaxed): ")
    # Create entry with timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry_text = f"[{timestamp}] Mood: {mood}\n{entry}\n{'-'*50}\n"
    # Save to file
    with open("journal.txt", "a") as f:
        f.write(entry_text)
    print("Entry saved!")
    # Always offer music recommendation
    recommend = input(f"Want music for your {mood.lower()} mood? (y/n): ")
    if recommend.lower() == 'y':
        get_music_recommendation(mood)
def view_entries():
    """View recent journal entries"""
    if not os.path.exists("journal.txt"):
        print("No entries yet. Write your first entry!")
        return
    with open("journal.txt", "r") as f:
        entries = f.read()
    print("\n--- Your Journal Entries ---")
    print(entries)
def get_music_recommendation(mood):
    """Get music recommendations from Last.fm API"""
    genres = mood_genres.get(mood.lower(), ["pop"])
    genre = random.choice(genres)
    print(f"Getting {genre} music for {mood.lower()} mood...")
    url = "https://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "tag.gettoptracks",
        "tag": genre,
        "api_key": os.getenv("LASTFM_API_KEY"),
        "format": "json",
        "limit": 10
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if "tracks" in data and "track" in data["tracks"]:
            tracks = data["tracks"]["track"]
            if tracks:
                selected = random.sample(tracks, min(3, len(tracks)))
                print(f"\n:musical_note: Music for your {mood.lower()} mood ({genre}):")
                for track in selected:
                    artist_name = track['artist']['name'] if isinstance(track['artist'], dict) else track['artist']
                    print(f"  • {track['name']} by {artist_name}")
            else:
                print(f"No tracks found for {genre}.")
        else:
            fallback_songs = {
                "happy": [("Happy", "Pharrell Williams"), ("Good as Hell", "Lizzo"), ("Uptown Funk", "Bruno Mars")],
                "sad": [("Someone Like You", "Adele"), ("Hurt", "Johnny Cash"), ("Mad World", "Gary Jules")],
                "stressed": [("Weightless", "Marconi Union"), ("Clair de Lune", "Debussy"), ("Aqueous Transmission", "Incubus")],
                "relaxed": [("Take Five", "Dave Brubeck"), ("Blue in Green", "Miles Davis"), ("River", "Joni Mitchell")]
            }
            songs = fallback_songs.get(mood.lower(), fallback_songs["happy"])
            selected = random.sample(songs, min(3, len(songs)))
            print(f"\n:musical_note: Music for your {mood.lower()} mood:")
            for title, artist in selected:
                print(f"  • {title} by {artist}")
    except Exception as e:
        print(f"API error. Using offline recommendations...")
        fallback_songs = {
            "happy": [("Happy", "Pharrell Williams"), ("Good as Hell", "Lizzo")],
            "sad": [("Someone Like You", "Adele"), ("Hurt", "Johnny Cash")],
            "stressed": [("Weightless", "Marconi Union"), ("Clair de Lune", "Debussy")],
            "relaxed": [("Take Five", "Dave Brubeck"), ("Blue in Green", "Miles Davis")]
        }
        songs = fallback_songs.get(mood.lower(), fallback_songs["happy"])
        print(f"\n:musical_note: Music for your {mood.lower()} mood:")
        for title, artist in songs:
            print(f"  • {title} by {artist}")
def show_menu():
    """Display the main menu"""
    print("\n=== Personal Journal ===")
    print("1. Write new entry")
    print("2. View recent entries")
    print("3. Get music recommendation")
    print("4. Exit")
def main():
    """Main program loop"""
    while True:
        show_menu()
        choice = input("\nChoose an option (1-4): ")
        if choice == "1":
            write_entry()
        elif choice == "2":
            view_entries()
        elif choice == "3":
            mood = input("What's your mood? (Happy/Sad/Stressed/Relaxed): ")
            get_music_recommendation(mood)
        elif choice == "4":
            print("Thanks for journaling! :memo:")
            break
        else:
            print("Please choose 1, 2, 3, or 4.")
if __name__ == "__main__":
    main()