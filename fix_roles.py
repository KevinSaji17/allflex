#!/usr/bin/env python
"""Fix roles: kevin = gym_owner, kevin123 = regular user."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from accounts.db_utils import get_user_model, get_gym_model

User = get_user_model()
Gym = get_gym_model()

print("\n" + "="*60)
print("FIXING USER ROLES")
print("="*60)

# Get users
kevin = User.objects(username='kevin').first()
kevin123 = User.objects(username='kevin123').first()

if not kevin:
    print("\n❌ User 'kevin' not found!")
    exit(1)

if not kevin123:
    print("\n❌ User 'kevin123' not found!")
    exit(1)

print(f"\nBEFORE:")
print(f"  kevin: role={kevin.role}")
print(f"  kevin123: role={kevin123.role}")

# Fix: kevin = gym owner, kevin123 = regular user
kevin.role = 'gym_owner'
kevin.save()
print(f"\n✓ Set kevin role to: gym_owner")

kevin123.role = 'user'
kevin123.save()
print(f"✓ Set kevin123 role to: user")

# Transfer all gyms to kevin
kevin123_gyms = list(Gym.objects(owner=kevin123))
if kevin123_gyms:
    print(f"\n✓ Transferring {len(kevin123_gyms)} gym(s) from kevin123 to kevin...")
    for gym in kevin123_gyms:
        gym.owner = kevin
        gym.save()
        print(f"  ✓ Transferred: {gym.name}")

print(f"\nAFTER:")
print(f"  kevin: role={kevin.role}")
print(f"  kevin123: role={kevin123.role}")

# Verify final state
kevin_gyms = list(Gym.objects(owner=kevin))
kevin123_gyms_final = list(Gym.objects(owner=kevin123))

print(f"\n" + "="*60)
print("FINAL STATE")
print("="*60)
print(f"\n✓ kevin (gym owner):")
print(f"    Email: {kevin.email}")
print(f"    Role: {kevin.role}")
print(f"    Owns: {len(kevin_gyms)} gym(s)")
for g in kevin_gyms:
    print(f"      • {g.name}")
print(f"    Will see: '🏢 My Dashboard' link")

print(f"\n✓ kevin123 (regular user):")
print(f"    Email: {kevin123.email}")
print(f"    Role: {kevin123.role}")
print(f"    Owns: {len(kevin123_gyms_final)} gym(s)")
print(f"    Will NOT see dashboard link")

print(f"\n" + "="*60)
print("✅ FIXED!")
print("="*60)
print(f"\n📝 Login as gym owner:")
print(f"   Username: kevin")
print(f"   Password: kevin123")
print(f"   Will see: '🏢 My Dashboard' in navbar")

print(f"\n📝 Login as regular user:")
print(f"   Username: kevin123")
print(f"   Password: kevin123")
print(f"   Will NOT see dashboard link")

print(f"\n🌐 Test now: http://127.0.0.1:8000/login/\n")
