import argparse
import os
from dotenv import load_dotenv
# Import the pure function you successfully unit-tested!
from recommendation_logic import get_recommendation_logic 

# Load environment variables from .env file
load_dotenv()

def main():
    """
    Main function to handle the Command Line Interface (CLI) for music recommendation.
    """
    # Use argparse to define command-line arguments
    parser = argparse.ArgumentParser(description="Music Recommendation CLI Tool")
    parser.add_argument(
        '--recommend', 
        type=str, 
        metavar='MOOD', 
        help='Get music recommendations based on a specified MOOD (e.g., Happy, Sad, Stressed).'
    )
    
    args = parser.parse_args()
    
    # Check if the --recommend argument was provided
    if args.recommend:
        mood_input = args.recommend
        
        # Retrieve API Key (required for full functionality)
        api_key = os.getenv("LASTFM_API_KEY") 

        print(f"\n--- Searching for Music Recommendations for MOOD: {mood_input.upper()} ---")
        
        # CALL THE PURE FUNCTION
        result = get_recommendation_logic(mood_input, api_key)
        
        # Display Results
        print(f"\nStatus: {result['status']}")
        
        if result['recommendations']:
            print("\nRecommended Tracks:")
            for name, artist in result['recommendations']:
                print(f"- {name} by {artist}")
        else:
            print("No recommendations found.")
        
        print("-" * 50)
    else:
        # Default behavior if no arguments are provided
        parser.print_help()

if __name__ == "__main__":
    main()