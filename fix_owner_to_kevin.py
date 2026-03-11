#!/usr/bin/env python
"""Check and fix gym owner - should be 'kevin' not 'kevin123'."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from accounts.db_utils import get_user_model, get_gym_model, is_mongodb

User = get_user_model()
Gym = get_gym_model()

print("\n" + "="*60)
print("CHECKING USERNAME AND GYM OWNER")
print("="*60)

# Check both usernames
kevin = User.objects(username='kevin').first()
kevin123 = User.objects(username='kevin123').first()

print("\n✓ Users found:")
if kevin:
    print(f"  - kevin: email={kevin.email}, role={kevin.role}")
    kevin_gyms = list(Gym.objects(owner=kevin))
    print(f"    Owned gyms: {len(kevin_gyms)}")
    for g in kevin_gyms:
        print(f"      • {g.name}")
else:
    print(f"  - kevin: NOT FOUND")

if kevin123:
    print(f"  - kevin123: email={kevin123.email}, role={kevin123.role}")
    kevin123_gyms = list(Gym.objects(owner=kevin123))
    print(f"    Owned gyms: {len(kevin123_gyms)}")
    for g in kevin123_gyms:
        print(f"      • {g.name}")
else:
    print(f"  - kevin123: NOT FOUND")

# Fix: Transfer gym from kevin123 to kevin
if kevin and kevin123_gyms:
    print(f"\n🔧 FIXING: Transferring gyms from kevin123 to kevin...")
    for gym in kevin123_gyms:
        gym.owner = kevin
        gym.save()
        print(f"  ✓ Transferred: {gym.name}")
    
    # Update kevin's role
    if kevin.role != 'gym_owner':
        kevin.role = 'gym_owner'
        kevin.save()
        print(f"  ✓ Updated kevin role to: gym_owner")
    
    print("\n✅ FIXED!")
    
elif kevin and not kevin123_gyms:
    print("\n✓ Kevin already owns gyms or no gyms to transfer")
    kevin_gyms_check = list(Gym.objects(owner=kevin))
    print(f"  Kevin's gyms: {len(kevin_gyms_check)}")

print("\n" + "="*60)
print("FINAL STATE")
print("="*60)

if kevin:
    final_gyms = list(Gym.objects(owner=kevin))
    print(f"\n✓ User: kevin")
    print(f"  Role: {kevin.role}")
    print(f"  Owned gyms: {len(final_gyms)}")
    for g in final_gyms:
        print(f"    • {g.name}")
    
    print(f"\n📝 LOGIN AS:")
    print(f"   Username: kevin")
    print(f"   Password: kevin123")
    print(f"\n🌐 Dashboard: http://127.0.0.1:8000/gym-dashboard/")
else:
    print("\n❌ User 'kevin' not found!")
