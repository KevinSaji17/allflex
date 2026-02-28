#!/usr/bin/env python
"""
Check gym status counts in admin
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from accounts.db_utils import get_gym_model, is_mongodb

def check_gym_admin():
    print("=" * 70)
    print("Checking Gym Admin Panel Data")
    print("=" * 70)
    print()
    
    Gym = get_gym_model()
    
    # Get all gyms
    if is_mongodb():
        all_gyms = list(Gym.objects)
    else:
        all_gyms = list(Gym.objects.all())
    
    print(f"Total Gyms in Database: {len(all_gyms)}")
    print()
    
    # Count by status
    print("Gyms by Status:")
    for status_key, status_label in [('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')]:
        gyms_in_status = [g for g in all_gyms if g.status == status_key]
        print(f"  {status_label}: {len(gyms_in_status)}")
        for gym in gyms_in_status:
            verified = "✓ Verified" if gym.is_verified_partner else "✗ Not Verified"
            active = "Active" if gym.is_active else "Inactive"
            print(f"    - {gym.name} ({active}, {verified})")
    
    print()
    print("=" * 70)
    print("Admin Panel Info:")
    print("=" * 70)
    print("✓ All gyms (pending, approved, rejected) should show in admin panel")
    print("✓ You can filter by status using the right sidebar")
    print("✓ Approved gyms should have:")
    print("  - Status: Approved (green badge)")
    print("  - is_active: ✓")
    print("  - is_verified_partner: ✓")
    print()
    print("To view approved gyms in admin:")
    print("  1. Go to /admin/gyms/gym/")
    print("  2. Use filter on right: Status → Approved")
    print()

if __name__ == "__main__":
    check_gym_admin()
