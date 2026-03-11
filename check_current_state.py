#!/usr/bin/env python
"""Verify current state of kevin users and gyms."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from accounts.db_utils import get_user_model, get_gym_model

User = get_user_model()
Gym = get_gym_model()

print("\n" + "="*60)
print("CURRENT STATE CHECK")
print("="*60)

# Check kevin
kevin = User.objects(username='kevin').first()
if kevin:
    print(f"\n✓ User: kevin")
    print(f"  Email: {kevin.email}")
    print(f"  Role: {kevin.role}")
    kevin_gyms = list(Gym.objects(owner=kevin))
    print(f"  Owned gyms: {len(kevin_gyms)}")
    for g in kevin_gyms:
        print(f"    • {g.name}")
else:
    print(f"\n❌ User 'kevin' NOT FOUND")

# Check kevin123
kevin123 = User.objects(username='kevin123').first()
if kevin123:
    print(f"\n✓ User: kevin123")
    print(f"  Email: {kevin123.email}")
    print(f"  Role: {kevin123.role}")
    kevin123_gyms = list(Gym.objects(owner=kevin123))
    print(f"  Owned gyms: {len(kevin123_gyms)}")
    for g in kevin123_gyms:
        print(f"    • {g.name}")
else:
    print(f"\n❌ User 'kevin123' NOT FOUND")

print("\n" + "="*60)
if kevin and kevin.role == 'gym_owner' and kevin_gyms:
    print("✅ READY TO USE!")
    print("="*60)
    print(f"\n📝 Login as: kevin / kevin123")
    print(f"🌐 Dashboard: http://127.0.0.1:8000/gym-dashboard/")
    print(f"   (Look for '🏢 My Dashboard' link in navbar)")
elif kevin123 and kevin123.role == 'gym_owner' and kevin123_gyms:
    print("⚠️  NEEDS FIX")
    print("="*60)
    print(f"\nGym is owned by kevin123 but should be owned by kevin")
    print(f"Run: .venv\\Scripts\\python.exe quick_fix_owner.py")
else:
    print("❌ ISSUE DETECTED")
    print("="*60)
    print(f"\nNo gym owner found or no gyms exist")
