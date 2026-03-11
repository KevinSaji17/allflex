#!/usr/bin/env python
"""Quick check of user roles."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from accounts.db_utils import get_user_model

User = get_user_model()

kevin = User.objects(username='kevin').first()
kevin123 = User.objects(username='kevin123').first()

print("\n" + "="*50)
print("USER ROLES CHECK")
print("="*50)

if kevin:
    print(f"\n✓ kevin:")
    print(f"    Role: {kevin.role}")
    if kevin.role == 'gym_owner':
        print(f"    ✅ WILL see '🏢 My Dashboard' link")
    else:
        print(f"    ❌ Will NOT see dashboard link")
else:
    print("\n❌ kevin not found")

if kevin123:
    print(f"\n✓ kevin123:")
    print(f"    Role: {kevin123.role}")
    if kevin123.role == 'gym_owner':
        print(f"    ⚠️  PROBLEM: Should be 'user' not 'gym_owner'")
    else:
        print(f"    ✅ Correct - will NOT see dashboard link")
else:
    print("\n❌ kevin123 not found")

print("\n" + "="*50)
print("✅ NAVBAR LOGIC (already correct):")
print("="*50)
print("{% if user.role == 'gym_owner' %}")
print("    Show '🏢 My Dashboard'")
print("{% endif %}")
print("\nOnly users with role='gym_owner' see the link!")
print("="*50 + "\n")
