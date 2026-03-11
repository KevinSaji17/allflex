#!/usr/bin/env python
"""Quick role check and fix."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from accounts.db_utils import get_user_model, get_gym_model

User = get_user_model()
Gym = get_gym_model()

print("\n[CHECKING ROLES]")

# Get users
kevin = User.objects(username='kevin').first()
kevin123 = User.objects(username='kevin123').first()

if kevin:
    print(f"kevin: role = {kevin.role}")
else:
    print("kevin: NOT FOUND")

if kevin123:
    print(f"kevin123: role = {kevin123.role}")
    
    if kevin123.role == 'gym_owner':
        print("\n[FIXING] kevin123 should NOT be gym owner!")
        kevin123.role = 'user'
        kevin123.save()
        print("✅ Updated kevin123.role to 'user'")
    else:
        print("✅ kevin123 role is already correct")
else:
    print("kevin123: NOT FOUND")

if kevin:
    if kevin.role != 'gym_owner':
        print("\n[FIXING] kevin should BE gym owner!")
        kevin.role = 'gym_owner'
        kevin.save()
        print("✅ Updated kevin.role to 'gym_owner'")
        
        # Transfer gyms
        kevin123_gyms = list(Gym.objects(owner=kevin123)) if kevin123 else []
        if kevin123_gyms:
            print(f"\n[TRANSFERRING] {len(kevin123_gyms)} gym(s) to kevin...")
            for gym in kevin123_gyms:
                gym.owner = kevin
                gym.save()
                print(f"✅ Transferred: {gym.name}")
    else:
        print("✅ kevin role is already correct")

print("\n[FINAL RESULT]")
kevin = User.objects(username='kevin').first()
kevin123 = User.objects(username='kevin123').first()

if kevin:
    print(f"kevin: role = {kevin.role}")
if kevin123:
    print(f"kevin123: role = {kevin123.role}")

print("\n✅ DONE! Logout and login again to see changes.\n")
