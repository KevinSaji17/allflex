#!/usr/bin/env python
"""
Initialize fitness profile for current user
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.db_utils import is_mongodb

User = get_user_model()

print("Getting user 'admin'...")
try:
    user = User.objects.get(username='admin')
    print(f"✓ Found user: {user.username} (ID: {user.id})")
    print(f"  Email: {user.email}")
    print(f"  Credits: {user.credits}")
except User.DoesNotExist:
    print("✗ User 'admin' not found")
    sys.exit(1)

if is_mongodb():
    print("\nUsing MongoDB...")
    from accounts.mongo_models import UserProfile as MongoUserProfile, UserFitnessProfile
    
    print("Getting MongoDB UserProfile...")
    try:
        mongo_profile = MongoUserProfile.objects.get(django_user=user)
        print(f"✓ Found MongoDB UserProfile (ID: {mongo_profile.id})")
    except MongoUserProfile.DoesNotExist:
        print("✗ MongoDB UserProfile not found")
        sys.exit(1)
    
    print("\nGetting/Creating UserFitnessProfile...")
    fitness_profile = UserFitnessProfile.objects(user=mongo_profile).first()
    
    if not fitness_profile:
        print("  Creating new fitness profile...")
        fitness_profile = UserFitnessProfile(
            user=mongo_profile,
            total_visits=0,
            total_credits_spent=0
        )
        fitness_profile.save()
        print("✓ Created new fitness profile")
    else:
        print(f"✓ Found existing fitness profile")
        print(f"  Total visits: {fitness_profile.total_visits}")
        print(f"  Total credits spent: {fitness_profile.total_credits_spent}")
        
        # Update to 0 if needed
        if fitness_profile.total_visits != 0 or fitness_profile.total_credits_spent != 0:
            print("\n  Resetting to 0...")
            fitness_profile.total_visits = 0
            fitness_profile.total_credits_spent = 0
            fitness_profile.save()
            print("✓ Reset stats to 0")
else:
    print("\nUsing SQLite...")
    from users.models import UserFitnessProfile
    
    fitness_profile, created = UserFitnessProfile.objects.get_or_create(
        user=user,
        defaults={'total_visits': 0, 'total_credits_spent': 0}
    )
    
    if created:
        print("✓ Created new fitness profile")
    else:
        print(f"✓ Found fitness profile") 
        print(f"  Total visits: {fitness_profile.total_visits}")
        print(f"  Total credits spent: {fitness_profile.total_credits_spent}")

print("\n" + "=" * 60)
print("✓ Fitness profile is ready!")
print("=" * 60)
print("\nNext steps:")
print("1. Go to dashboard and make a test booking")  
print("2. Check profile page - stats should update automatically")
