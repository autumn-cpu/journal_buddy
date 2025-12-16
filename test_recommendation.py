import unittest
from unittest.mock import patch, MagicMock
# Imports the pure function and data from your logic file
from recommendation_logic import get_recommendation_logic, FALLBACK_SONGS 
from requests.exceptions import RequestException

# A sample API key for testing purposes (it won't actually be used to call the API)
TEST_API_KEY = "dummy_key_123"

# --- Mock Data to Simulate API Responses ---

# Mock data for a successful Last.fm response (Decision Table Row 1)
MOCK_API_SUCCESS = {
    "tracks": {
        "track": [
            {"name": "Track 1 - Success", "artist": {"name": "Artist A"}},
            {"name": "Track 2 - Success", "artist": {"name": "Artist B"}},
            {"name": "Track 3 - Success", "artist": {"name": "Artist C"}},
            {"name": "Track 4 - Success", "artist": {"name": "Artist D"}},
        ]
    }
}

# Mock data for a Last.fm response that is successful but returns NO tracks (Decision Table Row 2)
MOCK_API_EMPTY = {
    "tracks": {
        "track": []
    }
}


class TestRecommendationLogic(unittest.TestCase):
    
    # 1. Test API Success (Decision Table Row 1)
    @patch('recommendation_logic.requests.get')
    def test_api_success(self, mock_get):
        """Tests R1: A valid mood results in 3 tracks from the mocked API."""
        # Setup: Configure the mock response for success
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_API_SUCCESS
        mock_get.return_value = mock_response

        result = get_recommendation_logic("Happy", TEST_API_KEY)
        
        # Assertions
        self.assertTrue('API Success' in result['status'])
        self.assertEqual(len(result['recommendations']), 3)
        mock_get.assert_called_once()
        
    # 2. Test API Failure (Decision Table Row 3)
    @patch('recommendation_logic.requests.get')
    def test_api_failure_fallback(self, mock_get):
        """Tests R3: API connection errors cause a fallback to internal songs."""
        # Setup: Configure the mock to raise a connection error
        mock_get.side_effect = RequestException("Simulated connection error")
        
        result = get_recommendation_logic("Sad", TEST_API_KEY)
        
        # Assertions
        self.assertTrue('API Failed (RequestException)' in result['status'])
        self.assertLessEqual(len(result['recommendations']), len(FALLBACK_SONGS['sad']))


    # 3. Test Invalid Input (Decision Table Row 4 - Normalization/Guard)
    @patch('recommendation_logic.requests.get')
    def test_invalid_mood_guard_clause(self, mock_get):
        """Tests R4: An invalid mood ('Angry') defaults to the Happy fallback."""
        
        result = get_recommendation_logic("Angry", TEST_API_KEY)
        
        # Assertions
        self.assertEqual(result['status'], 'Invalid Mood')
        self.assertLessEqual(len(result['recommendations']), len(FALLBACK_SONGS['happy']))
        
        # Crucially: Test that the API request was NOT made because the guard clause prevented it
        mock_get.assert_not_called()

    # 4. Test API Success but No Tracks (Decision Table Row 2)
    @patch('recommendation_logic.requests.get')
    def test_api_empty_tracks_fallback(self, mock_get):
        """Tests R2: API returns 200 but the JSON is empty/missing tracks."""
        # Setup: Configure the mock for 200 OK but empty track list
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = MOCK_API_EMPTY 
        mock_get.return_value = mock_response

        result = get_recommendation_logic("Stressed", TEST_API_KEY)
        
        # Assertions: Should fail internally and fall back to the internal list
        self.assertTrue('API Failed (ValueError)' in result['status'])
        self.assertLessEqual(len(result['recommendations']), len(FALLBACK_SONGS['stressed']))
        mock_get.assert_called_once()


    # 5. Test Missing API Key (Guard Clause)
    @patch('recommendation_logic.requests.get')
    def test_missing_api_key_guard_clause(self, mock_get):
        """Tests the guard clause when the API key is passed as None/empty string."""
        
        result = get_recommendation_logic("Relaxed", None)
        
        # Assertions
        self.assertTrue('API Key Missing' in result['status'])
        self.assertLessEqual(len(result['recommendations']), len(FALLBACK_SONGS['relaxed']))
        
        # Crucially: Test that the API request was NOT made
        mock_get.assert_not_called()



    # 6. Test Unhandled HTTP 500 Error (The Failing Test) <--- **PASTE IT HERE**
    @patch('recommendation_logic.requests.get')
    def test_unhandled_http_error_bug(self, mock_get):
        """
        Tests the bug where the function fails to fall back 
        gracefully on an unhandled HTTP 500 status code.
        """
        # Setup: Configure the mock response for an unhandled 500 error
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        # We assert that the function should still successfully return a fallback list
        result = get_recommendation_logic("Happy", TEST_API_KEY)
        
        # Assertion: If the code is buggy, it might crash or return None/empty list.
        self.assertLessEqual(len(result['recommendations']), len(FALLBACK_SONGS['happy']))
        self.assertTrue('API Failed (Status 500)' in result['status'])
        
# Final block to ensure tests run and display output
if __name__ == '__main__':
    print("Attempting to run tests...")
    # This line tells unittest to find and run all tests in the current module
    unittest.main(module=__name__, argv=['ignored'], exit=False, verbosity=2)
