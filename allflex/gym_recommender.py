import google.genai as genai
import json
import re
from typing import Dict
from django.conf import settings

# Demo gyms when GEMINI_API_KEY is not set (so MVP works without an API key)
DEMO_GYMS = {
    "Gold's Gym Central": {"distance": "1.2 km", "rating": "4.5"},
    "Fitness First Plus": {"distance": "1.8 km", "rating": "4.2"},
    "Cult.fit Elite": {"distance": "2.1 km", "rating": "4.3"},
    "Anytime Fitness": {"distance": "2.5 km", "rating": "4.0"},
    "Local Fitness Hub": {"distance": "3.0 km", "rating": "4.1"},
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
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
        
        # Enhanced system prompt for better gym recommendations
        self.system_prompt = """
        You are a gym location assistant for the ALLFLEX platform. The user will provide you with a pincode (postal code).
        Your task is to find the 10 closest and most popular gyms to that pincode location and return the information
        in a specific JSON format.
        
        Requirements:
        1. Only accept pincode inputs (6-digit numbers for Indian pincodes, or valid postal codes for other countries)
        2. Find the 10 closest and most reputable gyms to that pincode
        3. Include a mix of chain gyms (Gold's Gym, Fitness First, Anytime Fitness, Cult.fit, etc.) and local gyms
        4. Return ONLY a JSON object with gym names as keys and an object with distance and rating as values
        5. Distance should be in kilometers with one decimal place (e.g., "2.5 km")
        6. Rating should be out of 5 stars (e.g., "4.2")
        7. Do not include any additional text, explanations, or formatting
        8. If the pincode is invalid, return: {"error": "Invalid pincode"}
        9. If no gyms found, return: {"error": "No gyms found in this area"}
        
        Example output format:
        {
            "Gold's Gym Bandra": {"distance": "1.2 km", "rating": "4.5"},
            "Fitness First Andheri": {"distance": "1.8 km", "rating": "4.2"},
            "Cult.fit Powai": {"distance": "2.1 km", "rating": "4.3"},
            "Local Fitness Center": {"distance": "2.5 km", "rating": "4.0"}
        }
        """
    
    def validate_pincode(self, pincode: str) -> bool:
        """
        Validate if the input is a proper pincode
        
        Args:
            pincode (str): The pincode to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Remove any spaces or special characters
        pincode = re.sub(r'[^\d]', '', pincode)
        
        # Check if it's a 6-digit Indian pincode or other valid postal code formats
        if len(pincode) == 6 and pincode.isdigit():
            return True
        elif len(pincode) == 5 and pincode.isdigit():  # US ZIP codes
            return True
        elif len(pincode) in [4, 5, 6] and pincode.isdigit():  # Other countries
            return True
        
        return False
    
    def find_gyms(self, pincode: str) -> Dict:
        """
        Find gyms near the given pincode using Gemini API, or return demo gyms if no API key.
        """
        if not self.validate_pincode(pincode):
            return {"error": "Invalid pincode format. Please enter a valid 6-digit pincode."}

        # No API key: return demo gyms so the app works without Gemini
        if not self.model:
            return dict(DEMO_GYMS)

        try:
            # Create the full prompt
            full_prompt = f"{self.system_prompt}\n\nPincode: {pincode}\n\nPlease find gyms near this pincode and return the data in the exact JSON format specified."
            
            # Generate response from Gemini
            response = self.model.generate_content(full_prompt)
            
            # Extract the response text
            response_text = response.text.strip()
            
            # Try to parse as JSON
            try:
                gym_data = json.loads(response_text)
                return gym_data
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from the response
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        gym_data = json.loads(json_match.group())
                        return gym_data
                    except json.JSONDecodeError:
                        return {"error": "Unable to parse gym data from response"}
                else:
                    return {"error": "No valid JSON found in response"}
                    
        except Exception as e:
            return {"error": f"API request failed: {str(e)}"}

# Django utility function
def get_gyms_by_pincode(pincode: str) -> Dict:
    """
    Get gyms by pincode. Uses Gemini when GEMINI_API_KEY is set; otherwise returns demo gyms.
    """
    try:
        gym_finder = GymFinder()
        return gym_finder.find_gyms(pincode)
    except Exception as e:
        return {"error": f"Service unavailable: {str(e)}"}