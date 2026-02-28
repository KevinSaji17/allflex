import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from accounts.db_utils import get_gym_model
import json

Gym = get_gym_model()

print("\n" + "="*70)
print("TESTING GYM BADGE DISPLAY")
print("="*70)

# Get all approved gyms
approved_gyms = Gym.objects.filter(status='approved', is_active=True)
print(f"\n✅ Approved Gyms in Database: {approved_gyms.count()}")

for gym in approved_gyms:
    print(f"\n  📍 {gym.name}")
    print(f"     Location: {gym.location}")
    print(f"     ID: {gym.id}")
    print(f"     is_verified_partner: {gym.is_verified_partner}")
    print(f"     Badge will show: {'✅ YES' if gym.is_verified_partner else '❌ NO'}")

# Simulate enrichment logic
print("\n" + "="*70)
print("SIMULATING GYM SEARCH ENRICHMENT")
print("="*70)

# Simulate Gemini returning these gyms
simulated_gemini_response = {
    "FitZone Premium Gym": {
        "distance": "1.2 km",
        "rating": "4.5",
        "location": "MG Road, Bangalore"
    },
    "PowerHouse Fitness": "2.3 km",  # String format
    "Random Non-DB Gym": {
        "distance": "3.4 km",
        "rating": "4.0"
    }
}

# Enrichment logic (same as in views.py)
by_name = {g.name.strip().lower(): g for g in approved_gyms}
enriched = {}

for gym_name, info in simulated_gemini_response.items():
    gym_obj = by_name.get((gym_name or '').strip().lower())
    if isinstance(info, dict):
        enriched_info = dict(info)
        if gym_obj:
            enriched_info['id'] = str(gym_obj.id)
            enriched_info['is_verified_partner'] = gym_obj.is_verified_partner
        else:
            enriched_info['is_verified_partner'] = False
        enriched[gym_name] = enriched_info
    else:
        if gym_obj:
            enriched[gym_name] = {
                'distance': info, 
                'id': str(gym_obj.id),
                'is_verified_partner': gym_obj.is_verified_partner
            }
        else:
            enriched[gym_name] = {
                'distance': info,
                'is_verified_partner': False
            }

print("\nEnriched Response (what frontend receives):")
print(json.dumps(enriched, indent=2))

print("\n" + "="*70)
print("BADGE DISPLAY SUMMARY")
print("="*70)

for gym_name, data in enriched.items():
    if isinstance(data, dict):
        has_badge = data.get('is_verified_partner', False)
        badge_emoji = "🔵" if has_badge else "⚪"
        print(f"{badge_emoji} {gym_name}: is_verified_partner = {has_badge}")

print("\n" + "="*70)
