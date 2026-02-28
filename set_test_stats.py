#!/usr/bin/env python
"""
Set fitness profile stats manually for testing
Run: python set_test_stats.py <username> <visits> <credits_spent>
Example: python set_test_stats.py admin 5 25
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.db_utils import is_mongodb, get_user_fitness_profile_model

User = get_user_model()
UserFitnessProfile = get_user_fitness_profile_model()

if is_mongodb():
    from accounts.mongo_models import UserProfile as MongoUserProfile


def set_stats(username, visits, credits_spent):
    """Manually set stats for a user"""
    try:
        user = User.objects.get(username=username)
        print(f"Found user: {user.username}")
        
        if is_mongodb():
            # Get MongoDB UserProfile
            mongo_user_profile = MongoUserProfile.objects(django_user=user).first()
            if not mongo_user_profile:
                print(f"No MongoDB UserProfile found for {username}")
                return False
                
            # Get or create fitness profile
            fitness_profile = UserFitnessProfile.objects(user=mongo_user_profile).first()
            if not fitness_profile:
                print(f"Creating new fitness profile...")
                fitness_profile = UserFitnessProfile(user=mongo_user_profile)
        else:
            # SQLite
            fitness_profile, created = UserFitnessProfile.objects.get_or_create(user=user)
            if created:
                print(f"Created new fitness profile")
        
        # Set stats
        fitness_profile.total_visits = visits
        fitness_profile.total_credits_spent = credits_spent
        fitness_profile.save()
        
        print(f"✓ Updated {username}:")
        print(f"  Total visits: {visits}")
        print(f"  Total credits spent: {credits_spent}")
        return True
        
    except User.DoesNotExist:
        print(f"User '{username}' not found")
        return False
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python set_test_stats.py <username> <visits> <credits_spent>")
        print("Example: python set_test_stats.py admin 5 25")
        sys.exit(1)
    
    username = sys.argv[1]
    try:
        visits = int(sys.argv[2])
        credits_spent = int(sys.argv[3])
    except ValueError:
        print("Error: visits and credits_spent must be integers")
        sys.exit(1)
    
    print("=" * 60)
    print("Setting Fitness Profile Stats")
    print("=" * 60)
    
    success = set_stats(username, visits, credits_spent)
    
    if success:
        print("\n✓ Stats updated successfully!")
        print("\nNote: These stats will be automatically updated when new bookings are created.")
    else:
        print("\n✗ Failed to update stats")
        sys.exit(1)
