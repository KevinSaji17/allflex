"""
Reset total_visits to 0 for users who have no completed bookings.
This fixes the issue where bookings were counted but then cancelled.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from accounts.db_utils import is_mongodb, get_user_model, get_gym_booking_model, get_user_fitness_profile_model

def reset_visits():
    """Reset total_visits based on actual completed bookings"""
    User = get_user_model()
    GymBooking = get_gym_booking_model()
    UserFitnessProfile = get_user_fitness_profile_model()
    
    if is_mongodb():
        users = User.objects.all()
    else:
        users = User.objects.all()
    
    for user in users:
        # Count only completed bookings
        if is_mongodb():
            completed_count = GymBooking.objects(user=user, status='completed').count()
        else:
            completed_count = GymBooking.objects.filter(user=user, status='completed').count()
        
        # Update fitness profile
        if is_mongodb():
            profile = UserFitnessProfile.objects(user=user).first()
        else:
            profile = UserFitnessProfile.objects.filter(user=user).first()
        
        if profile:
            old_visits = profile.total_visits
            profile.total_visits = completed_count
            profile.save()
            
            if old_visits != completed_count:
                print(f"✓ {user.username}: {old_visits} → {completed_count} visits")
            else:
                print(f"  {user.username}: {completed_count} visits (no change)")

if __name__ == '__main__':
    print("Resetting total_visits based on completed bookings...\n")
    reset_visits()
    print("\n✅ Done! Total visits now reflect only completed gym sessions.")
