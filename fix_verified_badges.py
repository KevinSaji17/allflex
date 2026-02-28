#!/usr/bin/env python
"""
Test and fix verified partner badges for approved gyms
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from accounts.db_utils import get_gym_model, is_mongodb

def check_and_fix_badges():
    print("=" * 70)
    print("Checking ALLFLEX Badge Status for Approved Gyms")
    print("=" * 70)
    print()
    
    Gym = get_gym_model()
    
    # Get all approved gyms
    if is_mongodb():
        approved_gyms = list(Gym.objects(status='approved'))
    else:
        approved_gyms = list(Gym.objects.filter(status='approved'))
    
    total_approved = len(approved_gyms)
    print(f"Total Approved Gyms: {total_approved}")
    print()
    
    if total_approved == 0:
        print("No approved gyms found. Nothing to check.")
        return
    
    # Check for gyms missing the verified badge
    missing_badge = []
    has_badge = []
    
    for gym in approved_gyms:
        if gym.is_verified_partner:
            has_badge.append(gym)
        else:
            missing_badge.append(gym)
    
    print(f"✓ Gyms WITH ALLFLEX Badge: {len(has_badge)}")
    for gym in has_badge:
        print(f"   • {gym.name} - {gym.location}")
    print()
    
    print(f"✗ Gyms MISSING ALLFLEX Badge: {len(missing_badge)}")
    for gym in missing_badge:
        print(f"   • {gym.name} - {gym.location}")
    print()
    
    # Fix gyms missing badge
    if missing_badge:
        print("Fixing gyms missing badge...")
        for gym in missing_badge:
            gym.is_verified_partner = True
            gym.save()
            print(f"   ✓ Fixed: {gym.name}")
        print()
        print(f"✓ Updated {len(missing_badge)} gym(s) to have ALLFLEX verified partner badge!")
    else:
        print("✓ All approved gyms already have the ALLFLEX badge!")
    
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Total Approved Gyms: {total_approved}")
    print(f"Gyms with Badge: {total_approved}")
    print(f"Status: ✓ All set!")
    print()
    print("The ALLFLEX Partner badge will now appear next to these gyms in:")
    print("  • Browse Gyms page (/gyms/)")
    print("  • User Dashboard gym search results")
    print("  • All gym listings")
    print()

if __name__ == "__main__":
    check_and_fix_badges()
