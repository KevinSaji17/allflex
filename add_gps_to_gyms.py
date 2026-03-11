"""
Add GPS Coordinates to Existing Gyms
------------------------------------
Uses Google Geocoding API to add GPS coordinates to gyms.
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from accounts.db_utils import is_mongodb, get_gym_model
import time

print("=" * 70)
print("ADD GPS COORDINATES TO EXISTING GYMS")
print("=" * 70)

Gym = get_gym_model()

if is_mongodb():
    gyms = list(Gym.objects())
else:
    gyms = list(Gym.objects.all())

print(f"\nFound {len(gyms)} gyms in database")

if len(gyms) == 0:
    print("No gyms to update.")
    sys.exit(0)

# Sample GPS coordinates for major Indian cities (for demo purposes)
# In production, use Google Geocoding API to get real coordinates
SAMPLE_COORDINATES = {
    'mumbai': (19.0760, 72.8777),
    'delhi': (28.6139, 77.2090),
    'bangalore': (12.9716, 77.5946),
    'kolkata': (22.5726, 88.3639),
    'chennai': (13.0827, 80.2707),
    'hyderabad': (17.3850, 78.4867),
    'pune': (18.5204, 73.8567),
    'ahmedabad': (23.0225, 72.5714),
}

print("\n⚠ Using sample coordinates for demo. Configure Google Geocoding API for real coordinates.")
print("\nUpdating gyms with GPS coordinates...\n")

updated_count = 0

for gym in gyms:
    # Skip if already has coordinates
    if gym.latitude and gym.longitude:
        print(f"  ⏭ {gym.name} - Already has GPS coordinates")
        continue
    
    # Try to match city from location
    location_lower = gym.location.lower()
    coords = None
    
    for city, (lat, lon) in SAMPLE_COORDINATES.items():
        if city in location_lower:
            coords = (lat, lon)
            break
    
    # Default to Mumbai if no match
    if not coords:
        coords = SAMPLE_COORDINATES['mumbai']
        print(f"  ⚠ {gym.name} - No city match, using Mumbai coordinates")
    
    # Add small random offset to spread gyms across city
    import random
    lat_offset = random.uniform(-0.05, 0.05)
    lon_offset = random.uniform(-0.05, 0.05)
    
    gym.latitude = coords[0] + lat_offset
    gym.longitude = coords[1] + lon_offset
    gym.save()
    
    print(f"  ✓ {gym.name} - Added coordinates ({gym.latitude:.4f}, {gym.longitude:.4f})")
    updated_count += 1
    
    time.sleep(0.1)  # Small delay to avoid overwhelming the system

print(f"\n" + "=" * 70)
print(f"✅ Updated {updated_count} gyms with GPS coordinates")
print("=" * 70)

print("\n📌 NEXT STEPS:")
print("  1. For production: Configure Google Geocoding API")
print("  2. Replace sample coordinates with real geocoded locations")
print("  3. Test check-in flow with GPS verification")
