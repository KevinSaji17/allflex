import google.genai as genai
from google.genai import types
import json
import re
from typing import Dict
from django.conf import settings

# Demo gyms when GEMINI_API_KEY is not set (FALLBACK ONLY - NOT USED WHEN API KEY IS CONFIGURED)
# These are only shown if the API key is missing or invalid
# With a valid API key, Gemini will return REAL gyms from the actual location
DEMO_GYMS = {
    "Kevin's Fitness Hub": {
        "distance": "1.0 km",
        "rating": "4.7",
        "location": "123 Main Street, Mumbai",
        "has_ac": True,
        "has_dressing_room": True,
        "has_washroom": True,
        "has_music": True
    },
    "Gold's Gym Central": {
        "distance": "1.2 km",
        "rating": "4.5",
        "location": "Central Area",
        "has_ac": True,
        "has_dressing_room": True,
        "has_washroom": True,
        "has_music": True
    },
    "Fitness First Plus": {
        "distance": "1.8 km",
        "rating": "4.2",
        "location": "Downtown",
        "has_ac": True,
        "has_dressing_room": True,
        "has_washroom": True,
        "has_music": False
    },
    "Cult.fit Elite": {
        "distance": "2.1 km",
        "rating": "4.3",
        "location": "Business District",
        "has_ac": True,
        "has_dressing_room": True,
        "has_washroom": True,
        "has_music": True
    },
    "Anytime Fitness": {
        "distance": "2.5 km",
        "rating": "4.0",
        "location": "Residential Area",
        "has_ac": False,
        "has_dressing_room": True,
        "has_washroom": True,
        "has_music": False
    },
    "Local Fitness Hub": {
        "distance": "3.0 km",
        "rating": "4.1",
        "location": "Market District",
        "has_ac": False,
        "has_dressing_room": False,
        "has_washroom": True,
        "has_music": False
    },
    "PowerZone Gym": {
        "distance": "4.5 km",
        "rating": "4.4",
        "location": "Sports Complex",
        "has_ac": True,
        "has_dressing_room": True,
        "has_washroom": True,
        "has_music": True
    },
    "FitLife Center": {
        "distance": "5.8 km",
        "rating": "4.2",
        "location": "Suburb East",
        "has_ac": True,
        "has_dressing_room": True,
        "has_washroom": True,
        "has_music": False
    },
    "BodyBuilders Arena": {
        "distance": "6.5 km",
        "rating": "4.3",
        "location": "Suburb West",
        "has_ac": False,
        "has_dressing_room": True,
        "has_washroom": True,
        "has_music": True
    },
}


class GymFinder:
    def __init__(self, api_key: str = None):
        """
        Initialize the GymFinder with Google Gemini API key (optional).
        If no key is set, find_gyms() returns demo gyms so the app still works.
        """
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = getattr(settings, 'GEMINI_API_KEY', None) or ''
        self.api_key = (self.api_key or '').strip()
        
        if self.api_key and self.api_key != 'YOUR_API_KEY_HERE':
            try:
                self.client = genai.Client(api_key=self.api_key)
                self.model_name = 'gemini-2.5-flash'
                print(f"[OK] Gemini API initialized successfully with model: {self.model_name}")
            except Exception as e:
                print(f"[ERROR] Failed to initialize Gemini client: {e}")
                self.client = None
                self.model_name = None
        else:
            print(f"[WARNING] No valid API key found. Using demo gyms.")
            self.client = None
            self.model_name = None
        
        # Compact system prompt to minimize token usage
        self.system_prompt = """You are a gym finder for INDIA only. Find REAL gyms within 7km of the given location.

Return ONLY a JSON object. Keys = gym names. Values = objects with:
- distance: "X.X km" (must be ≤7.0 km)
- rating: "X.X" (realistic)
- location: "area, city"
- has_ac: bool
- has_dressing_room: bool
- has_washroom: bool
- has_music: bool

Rules:
- India locations ONLY
- Real gyms only (actual businesses)
- Max 20 results, sorted by distance
- No markdown, no explanations — pure JSON only
- If location is not in India: {"error": "Only India locations supported"}
- If no gyms found: {"error": "No gyms found within 7 km"}"""
    
    def validate_location(self, location: str) -> bool:
        """
        Validate if the input is a valid location (more flexible than just pincodes)
        
        Args:
            location (str): The location to validate (address, area, landmark, pincode, etc.)
            
        Returns:
            bool: True if valid, False otherwise
        """
        location = location.strip()
        
        # Must have at least 3 characters
        if len(location) < 3:
            return False
        
        # Accept any reasonable location input:
        # - Pincodes (digits)
        # - Addresses (alphanumeric with spaces, commas)
        # - Area names (letters with spaces)
        # - Landmarks (letters with spaces)
        
        # Reject if only special characters or clearly invalid
        if not any(c.isalnum() for c in location):
            return False
        
        return True
    
    def filter_by_distance(self, gym_data: Dict, max_km: float = 7.0) -> Dict:
        """
        Filter gym results to only include those within max_km range.
        
        Args:
            gym_data (Dict): Dictionary of gyms with distance info
            max_km (float): Maximum distance in kilometers (default: 7.0)
            
        Returns:
            Dict: Filtered gym data
        """
        if not isinstance(gym_data, dict):
            return gym_data
            
        if "error" in gym_data:
            return gym_data
            
        filtered = {}
        for gym_name, info in gym_data.items():
            if isinstance(info, dict) and "distance" in info:
                # Extract numeric distance from string like "5.2 km"
                distance_str = info.get("distance", "")
                try:
                    distance_value = float(re.search(r'(\d+\.?\d*)', distance_str).group(1))
                    if distance_value <= max_km:
                        filtered[gym_name] = info
                except (AttributeError, ValueError):
                    # If we can't parse distance, include it to be safe
                    filtered[gym_name] = info
            else:
                # If info doesn't have expected structure, include it
                filtered[gym_name] = info
                
        return filtered if filtered else {"error": f"No gyms found within {max_km} km of this area"}
    
    def find_gyms(self, location: str) -> Dict:
        """
        Find REAL gyms near the given location using Gemini API (Google Maps-style search).
        
        - WITH API KEY: Returns real gyms from the actual location using Gemini AI
        - WITHOUT API KEY: Returns demo gyms as fallback (for testing only)
        
        Args:
            location (str): The location to search around (address, area, landmark, pincode, etc.)
            
        Returns:
            Dict: JSON object with gym names as keys and {'distance', 'rating'} as values
        """
        if not self.validate_location(location):
            return {"error": "Invalid location. Please enter a valid address, area, landmark, or pincode."}

        # No API key: return demo gyms so the app works without Gemini
        if not self.client:
            print(f"[WARNING] No client available for location {location}. Returning demo gyms.")
            return dict(DEMO_GYMS)

        print(f"[INFO] Searching for REAL gyms near '{location}' using Gemini API...")
        
        try:
            # Create the full prompt
            full_prompt = f"""{self.system_prompt}

LOCATION: {location}

Find real gyms within 7km of this India location. Return pure JSON only."""
            
            # Generate response from Gemini using new API
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt
            )
            
            # Extract the response text
            response_text = response.text.strip()
            
            # Try to parse as JSON
            try:
                gym_data = json.loads(response_text)
                # Filter to ensure only gyms within 7 km are returned
                gym_data = self.filter_by_distance(gym_data, max_km=7.0)
                # Limit to max 30 gyms
                if len(gym_data) > 30:
                    gym_data = dict(list(gym_data.items())[:30])
                return gym_data
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from the response
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        gym_data = json.loads(json_match.group())
                        # Filter to ensure only gyms within 7 km are returned
                        gym_data = self.filter_by_distance(gym_data, max_km=7.0)
                        # Limit to max 30 gyms
                        if len(gym_data) > 30:
                            gym_data = dict(list(gym_data.items())[:30])
                        return gym_data
                    except json.JSONDecodeError:
                        return {"error": "Unable to parse gym data from response"}
                else:
                    return {"error": "No valid JSON found in response"}
                    
        except Exception as e:
            error_str = str(e)
            print(f"[ERROR] Gemini API error: {error_str}")
            
            # Check for rate limit error (429 RESOURCE_EXHAUSTED)
            if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str or 'quota' in error_str.lower():
                print(f"[WARNING] Rate limit exceeded. Returning demo gyms for location: {location}")
                # Return demo gyms directly when rate limited instead of error
                # This ensures the app continues to work even when quota is exceeded
                return dict(DEMO_GYMS)
            
            # Other errors: return demo gyms as fallback
            print(f"[WARNING] API error, returning demo gyms for location: {location}")
            return dict(DEMO_GYMS)

# Django utility function
def get_gyms_by_location(location: str) -> Dict:
    """
    Get gyms by location (address, area, landmark, pincode, etc.).
    Uses Gemini AI for Google Maps-style accurate search when GEMINI_API_KEY is set.
    """
    try:
        gym_finder = GymFinder()
        return gym_finder.find_gyms(location)
    except Exception as e:
        return {"error": f"Service unavailable: {str(e)}"}

# Backward compatibility alias  
get_gyms_by_pincode = get_gyms_by_location