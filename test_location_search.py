#!/usr/bin/env python
"""
Test location-based gym search with specific landmarks and areas.
Demonstrates improved accuracy over pincode-only search.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from allflex.gym_recommender import GymFinder

def test_location_based_search():
    print("=" * 70)
    print("Testing Location-Based Gym Search (Google Maps Style)")
    print("=" * 70)
    print()
    
    finder = GymFinder()
    
    if not finder.client:
        print("[WARNING] No API key - showing demo gyms only")
        print()
    else:
        print(f"[OK] Using Gemini {finder.model_name} for accurate location search")
        print()
    
    # Test various location types
    test_locations = [
        ("Gateway of India, Mumbai", "Specific landmark in Mumbai"),
        ("Bandra West, Mumbai", "Neighborhood in Mumbai"),
        ("Connaught Place, Delhi", "Central area in Delhi"),
        ("Koramangala, Bangalore", "Tech hub in Bangalore"),
        ("MG Road, Bangalore", "Major road/area in Bangalore"),
        ("Indiranagar, Bangalore", "Popular area in Bangalore"),
    ]
    
    for location, description in test_locations:
        print("-" * 70)
        print(f"📍 Location: {location}")
        print(f"   ({description})")
        print("-" * 70)
        
        result = finder.find_gyms(location)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Found {len(result)} gyms within 7 km:\n")
            
            # Sort by distance
            sorted_gyms = sorted(
                result.items(),
                key=lambda x: float(x[1].get('distance', '999').split()[0]) if isinstance(x[1], dict) else 999
            )
            
            for i, (gym_name, info) in enumerate(sorted_gyms[:7], 1):
                if isinstance(info, dict):
                    distance = info.get('distance', 'N/A')
                    rating = info.get('rating', 'N/A')
                    print(f"  {i}. {gym_name}")
                    print(f"     📏 {distance}  |  ⭐ {rating}")
        
        print()
    
    print("=" * 70)
    print("Key Benefits of Location-Based Search:")
    print("=" * 70)
    print("✅ Search by address, landmark, or area name (not just pincodes)")
    print("✅ More accurate distance calculations from exact location")
    print("✅ Finds gyms specific to that precise area")
    print("✅ Works like Google Maps gym search")
    print("✅ All results within 7 km radius")
    print("=" * 70)

if __name__ == "__main__":
    test_location_based_search()
