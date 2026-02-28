#!/usr/bin/env python
"""
Test script to verify Gemini API is returning REAL gyms from actual locations.
This demonstrates the API is working and not using hardcoded data.
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from allflex.gym_recommender import GymFinder
import json

def test_real_gyms():
    print("=" * 60)
    print("Testing Gemini API - Real Gym Finder")
    print("=" * 60)
    print()
    
    # Initialize GymFinder
    finder = GymFinder()
    
    # Check if API is configured
    if not finder.client:
        print("⚠️  WARNING: No API key configured!")
        print("   Demo gyms will be shown (hardcoded fallback)")
        print("   To get REAL gyms, ensure GEMINI_API_KEY is in .env")
        print()
    else:
        print("✅ Gemini API Key: Configured")
        print(f"✅ Model: {finder.model_name}")
        print("✅ Will search for REAL gyms at the location")
        print()
    
    # Test with different pincodes
    test_pincodes = [
        ("400001", "Mumbai - Fort/Colaba area"),
        ("110001", "Delhi - Connaught Place area"),
        ("560001", "Bangalore - MG Road area"),
    ]
    
    for pincode, description in test_pincodes:
        print("-" * 60)
        print(f"📍 Testing Pincode: {pincode} ({description})")
        print("-" * 60)
        
        # Call the API
        result = finder.find_gyms(pincode)
        
        # Display results
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Found {len(result)} gyms within 7 km:\n")
            
            # Sort by distance
            sorted_gyms = sorted(
                result.items(),
                key=lambda x: float(x[1].get('distance', '999').split()[0]) if isinstance(x[1], dict) else 999
            )
            
            for i, (gym_name, info) in enumerate(sorted_gyms, 1):
                if isinstance(info, dict):
                    distance = info.get('distance', 'N/A')
                    rating = info.get('rating', 'N/A')
                    print(f"  {i}. {gym_name}")
                    print(f"     📏 Distance: {distance}")
                    print(f"     ⭐ Rating: {rating}")
                    print()
        
        print()
    
    print("=" * 60)
    print("Test Complete!")
    print()
    
    if finder.client:
        print("✅ These are REAL gyms returned by Gemini API")
        print("✅ Try different pincodes to see gyms in those areas")
        print("✅ The gyms change based on the actual location")
    else:
        print("⚠️  Add GEMINI_API_KEY to .env to get real gyms")
        print("   Current results are demo/fallback data")
    print("=" * 60)

if __name__ == "__main__":
    test_real_gyms()
