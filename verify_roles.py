#!/usr/bin/env python
"""Verify roles are correct."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from accounts.db_utils import get_user_model

User = get_user_model()

print("\n" + "="*50)
print("DATABASE ROLES VERIFICATION")
print("="*50)

kevin = User.objects(username='kevin').first()
kevin123 = User.objects(username='kevin123').first()

print("\n✓ Current roles in database:")
if kevin:
    print(f"\nkevin:")
    print(f"  role = '{kevin.role}'")
    if kevin.role == 'gym_owner':
        print(f"  ✅ CORRECT - Should see dashboard")
    else:
        print(f"  ❌ WRONG - Should be 'gym_owner'")

if kevin123:
    print(f"\nkevin123:")
    print(f"  role = '{kevin123.role}'")
    if kevin123.role == 'user':
        print(f"  ✅ CORRECT - Should NOT see dashboard")
    else:
        print(f"  ❌ WRONG - Should be 'user'")

print("\n" + "="*50)
print("If roles are correct, LOGOUT and LOGIN again!")
print("="*50 + "\n")
