#!/usr/bin/env python
"""
Test ALLFLEX badge display in user gym search
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from accounts.db_utils import get_gym_model, is_mongodb
from allflex.gym_recommender import get_gyms_by_pincode

def test_badge_in_search():
    print("=" * 70)
    print("Testing ALLFLEX Badge in User Gym Search")
    print("=" * 70)
    print()
    
    Gym = get_gym_model()
    
    # Get approved gyms
    if is_mongodb():
        approved_gyms = list(Gym.objects(status='approved', is_active=True))
    else:
        approved_gyms = list(Gym.objects.filter(status='approved', is_active=True))
    
    print(f"✓ Found {len(approved_gyms)} approved gym(s)")
    print()
    
    if not approved_gyms:
        print("No approved gyms to test. Please approve a gym first.")
        return
    
    # Show gym details
    for gym in approved_gyms:
        print(f"Gym: {gym.name}")
        print(f"  - Location: {gym.location}")
        print(f"  - Status: {gym.status}")
        print(f"  - Active: {gym.is_active}")
        print(f"  - Verified Partner: {gym.is_verified_partner}")
        print()
    
    # Simulate the enrichment process (what happens in find_gyms_by_pincode)
    print("=" * 70)
    print("Simulating Gym Search Enrichment Process")
    print("=" * 70)
    print()
    
    # Create a dummy gym data similar to what Gemini returns
    dummy_gym_data = {
        approved_gyms[0].name: {
            'distance': '2.5 km',
            'rating': '4.5',
            'location': 'Central Area',
            'has_ac': True,
            'has_dressing_room': True,
            'has_washroom': True,
            'has_music': True
        }
    }
    
    print("Before enrichment:")
    print(f"  Gym data: {dummy_gym_data}")
    print()
    
    # Enrich with DB data (same logic as in views.py)
    by_name = {g.name.strip().lower(): g for g in approved_gyms}
    enriched = {}
    
    for gym_name, info in dummy_gym_data.items():
        gym_obj = by_name.get((gym_name or '').strip().lower())
        if isinstance(info, dict):
            enriched_info = dict(info)
            if gym_obj:
                enriched_info.setdefault('id', str(gym_obj.id))
                enriched_info.setdefault('is_verified_partner', gym_obj.is_verified_partner)
            enriched[gym_name] = enriched_info
    
    print("After enrichment:")
    for name, data in enriched.items():
        print(f"  {name}:")
        print(f"    - id: {data.get('id', 'N/A')}")
        print(f"    - is_verified_partner: {data.get('is_verified_partner', 'N/A')}")
        print(f"    - distance: {data.get('distance', 'N/A')}")
        print(f"    - rating: {data.get('rating', 'N/A')}")
    print()
    
    # Check result
    print("=" * 70)
    print("Result Analysis")
    print("=" * 70)
    for name, data in enriched.items():
        has_badge_field = 'is_verified_partner' in data
        is_verified = data.get('is_verified_partner', False)
        
        if has_badge_field and is_verified:
            print(f"✓ PASS: '{name}' will show ALLFLEX badge in user search")
        elif has_badge_field and not is_verified:
            print(f"⚠ WARNING: '{name}' has badge field but is_verified_partner=False")
        else:
            print(f"✗ FAIL: '{name}' missing is_verified_partner field - badge won't show")
    
    print()
    print("When users search for gyms:")
    print("  1. Backend enriches gym data with is_verified_partner field")
    print("  2. Frontend checks: isVerified = gymInfo.is_verified_partner")
    print("  3. If true, shows: ✓ ALLFLEX Partner badge")
    print()

if __name__ == "__main__":
    test_badge_in_search()
