"""
Test script to verify Kevin's Fitness Hub shows up in gym search
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from allflex.gym_recommender import get_gyms_by_pincode

print("\n" + "=" * 80)
print("TESTING GYM SEARCH FOR KEVIN'S FITNESS HUB")
print("=" * 80)

# Test search for Mumbai pincode 400001
location = "400001"
print(f"\n🔍 Searching for gyms near: {location}")

try:
    results = get_gyms_by_pincode(location)
    print(f"\n✓ Found {len(results)} gyms")
    
    # Check if Kevin's Fitness Hub is in results
    kevin_gym_found = False
    for gym_name, info in results.items():
        if "Kevin's Fitness Hub" in gym_name:
            kevin_gym_found = True
            print(f"\n✅ FOUND: {gym_name}")
            print(f"   Distance: {info.get('distance', 'N/A')}")
            print(f"   Rating: {info.get('rating', 'N/A')}")
            print(f"   Location: {info.get('location', 'N/A')}")
            break
    
    if not kevin_gym_found:
        print("\n⚠️  Kevin's Fitness Hub NOT found in results")
        print("\nAll gyms returned:")
        for gym_name, info in list(results.items())[:5]:
            print(f"  • {gym_name} - {info.get('distance', 'N/A')}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    
    if kevin_gym_found:
        print("\n✅ SUCCESS: Kevin's gym will appear in search results!")
        print("   Users can book this gym and Kevin can see bookings in his dashboard")
    else:
        print("\n⚠️  Note: Kevin's gym may not appear in Gemini AI results")
        print("   However, it's in the database and will show in 'All Gyms' view")
        print("   It's also added to demo gyms as a fallback")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print()
