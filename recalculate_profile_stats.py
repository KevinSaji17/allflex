#!/usr/bin/env python
"""
Recalculate fitness profile stats from existing bookings
Run: python recalculate_profile_stats.py
"""
import os
import sys
import django
from pymongo.errors import NetworkTimeout, ServerSelectionTimeoutError

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.db_utils import is_mongodb, get_user_fitness_profile_model, get_gym_booking_model

User = get_user_model()
UserFitnessProfile = get_user_fitness_profile_model()
GymBooking = get_gym_booking_model()

if is_mongodb():
    from accounts.mongo_models import UserProfile as MongoUserProfile


def recalculate_all_stats():
    """Recalculate total_visits and total_credits_spent for all users"""
    users = User.objects.all()
    
    print(f"Found {users.count()} users")
    
    for user in users:
        print(f"\nProcessing user: {user.username}")
        
        # Get all bookings for this user
        total_visits = 0
        total_credits_spent = 0
        
        try:
            if is_mongodb():
                print(f"  Getting MongoDB UserProfile...")
                # In MongoDB, bookings reference UserProfile not Django User
                try:
                    mongo_user_profile = MongoUserProfile.objects(django_user=user).timeout(5000).first()
                except (NetworkTimeout, ServerSelectionTimeoutError) as e:
                    print(f"  ⚠ MongoDB timeout getting UserProfile: {e}")
                    print(f"  Skipping {user.username}")
                    continue
                    
                if not mongo_user_profile:
                    print(f"  No MongoDB UserProfile found for {user.username}")
                    continue
                    
                print(f"  Querying MongoDB bookings...")
                try:
                    bookings = list(GymBooking.objects(user=mongo_user_profile).timeout(5000))
                except (NetworkTimeout, ServerSelectionTimeoutError) as e:
                    print(f"  ⚠ MongoDB timeout getting bookings: {e}")
                    print(f"  Skipping {user.username}")
                    continue
            else:
                print(f"  Querying SQLite bookings...")
                bookings = list(GymBooking.objects.filter(user=user))
            
            print(f"  Found {len(bookings)} bookings")
            
            total_visits = len(bookings)
            total_credits_spent = sum(booking.credits_charged or 0 for booking in bookings)
            
            print(f"  Total visits: {total_visits}")
            print(f"  Total credits spent: {total_credits_spent}")
            
            # Update or create fitness profile
            if is_mongodb():
                try:
                    fitness_profile = UserFitnessProfile.objects(user=mongo_user_profile).timeout(5000).first()
                except (NetworkTimeout, ServerSelectionTimeoutError) as e:
                    print(f"  ⚠ MongoDB timeout getting fitness profile: {e}")
                    print(f"  Skipping {user.username}")
                    continue
                    
                if not fitness_profile:
                    print(f"  Creating new fitness profile...")
                    fitness_profile = UserFitnessProfile(user=mongo_user_profile)
                fitness_profile.total_visits = total_visits
                fitness_profile.total_credits_spent = total_credits_spent
                try:
                    fitness_profile.save()
                except (NetworkTimeout, ServerSelectionTimeoutError) as e:
                    print(f"  ⚠ MongoDB timeout saving fitness profile: {e}")
                    print(f"  Skipping {user.username}")
                    continue
            else:
                fitness_profile, created = UserFitnessProfile.objects.get_or_create(user=user)
                fitness_profile.total_visits = total_visits
                fitness_profile.total_credits_spent = total_credits_spent
                fitness_profile.save()
            
            print(f"✓ {user.username}: {total_visits} visits, {total_credits_spent} credits spent")
        except Exception as e:
            print(f"✗ Error updating {user.username}: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    print("=" * 60)
    print("Recalculating Fitness Profile Stats")
    print("=" * 60)
    recalculate_all_stats()
    print("\nDone!")
