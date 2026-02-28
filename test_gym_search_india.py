#!/usr/bin/env python
"""
Test gym search with India-only restriction
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from allflex.gym_recommender import GymFinder

def test_india_only_search():
    print("=" * 70)
    print("Testing India-Only Gym Search")
    print("=" * 70)
    print()
    
    finder = GymFinder()
    
    if not finder.client:
        print("[WARNING] No API key - showing demo gyms only")
        print()
    else:
        print(f"[OK] Using Gemini {finder.model_name}")
        print()
    
    # Test Indian locations
    print("Testing VALID Indian Locations:")
    print("-" * 70)
    
    indian_locations = [
        "Indiranagar, Bangalore",
        "Gateway of India, Mumbai",
        "Connaught Place, Delhi",
    ]
    
    for location in indian_locations:
        print(f"\n📍 Location: {location}")
        result = finder.find_gyms(location)
        
        if "error" in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            gym_count = len(result)
            print(f"   ✅ Found {gym_count} gyms:")
            for gym_name, info in list(result.items())[:3]:  # Show first 3
                print(f"      • {gym_name}")
                print(f"        Distance: {info.get('distance', 'N/A')}, Rating: {info.get('rating', 'N/A')}")
                print(f"        Location: {info.get('location', 'N/A')}")
            if gym_count > 3:
                print(f"      ... and {gym_count - 3} more gyms")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    test_india_only_search()
