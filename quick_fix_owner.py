#!/usr/bin/env python
"""Quick fix: Transfer gym from kevin123 to kevin."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from accounts.db_utils import get_user_model, get_gym_model

User = get_user_model()
Gym = get_gym_model()

print("\n[QUICK FIX]")

# Find users
kevin = User.objects(username='kevin').first()
kevin123 = User.objects(username='kevin123').first()

if not kevin:
    print("❌ User 'kevin' not found!")
    exit(1)

if not kevin123:
    print("❌ User 'kevin123' not found!")
    exit(1)

print(f"✓ Found kevin: {kevin.email}")
print(f"✓ Found kevin123: {kevin123.email}")

# Transfer gyms
kevin123_gyms = list(Gym.objects(owner=kevin123))
print(f"✓ kevin123 has {len(kevin123_gyms)} gym(s)")

if kevin123_gyms:
    for gym in kevin123_gyms:
        gym.owner = kevin
        gym.save()
        print(f"  ✓ Transferred: {gym.name}")
    
    # Update kevin's role
    kevin.role = 'gym_owner'
    kevin.save()
    print(f"✓ Updated kevin role to: gym_owner")
    
    print(f"\n✅ DONE!")
    print(f"📝 Login as: kevin / kevin123")
    print(f"🌐 Dashboard: http://127.0.0.1:8000/gym-dashboard/")
else:
    print("✓ No gyms to transfer")
    kevin_gyms = list(Gym.objects(owner=kevin))
    print(f"✓ kevin already has {len(kevin_gyms)} gym(s)")
