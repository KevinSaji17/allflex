import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from accounts.db_utils import get_gym_booking_model, is_mongodb
from accounts.mongo_models import UserProfile

GymBooking = get_gym_booking_model()

# Find user with username 'testuser_booking'
if is_mongodb():
    user = UserProfile.objects(username='testuser_booking').first()
else:
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.filter(username='testuser_booking').first()

if not user:
    print("❌ User testuser_booking not found")
else:
    print(f"Found user: {user.username}")
    
    # Find and delete all bookings for this user
    if is_mongodb():
        bookings = GymBooking.objects(user=user)
    else:
        bookings = GymBooking.objects.filter(user=user)
    
    count = bookings.count()
    print(f"Found {count} booking(s) to delete")
    
    for booking in bookings:
        print(f"\nDeleting booking:")
        print(f"  ID: {booking.id}")
        print(f"  Gym: {booking.gym_name}")
        print(f"  Status: {booking.status}")
        print(f"  Checked In At: {booking.checked_in_at}")
        booking.delete()
    
    print(f"\n✅ Deleted {count} booking(s) successfully!")
