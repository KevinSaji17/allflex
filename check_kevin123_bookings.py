import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from accounts.db_utils import get_gym_booking_model, is_mongodb
from accounts.mongo_models import UserProfile

# Get booking model
GymBooking = get_gym_booking_model()

# Find kevin123 user
if is_mongodb():
    user = UserProfile.objects(username='kevin123').first()
else:
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.filter(username='kevin123').first()

if not user:
    print("User kevin123 not found")
else:
    print(f"User: {user.username}")
    print()
    
    # Get all bookings
    if is_mongodb():
        bookings = GymBooking.objects(user=user).order_by('-booked_at')
    else:
        bookings = GymBooking.objects.filter(user=user).order_by('-booked_at')
    
    print(f"Total bookings: {bookings.count()}")
    print()
    
    for booking in bookings:
        print(f"Gym: {booking.gym_name}")
        print(f"  Status: {booking.status}")
        print(f"  Booking Date: {booking.booking_date}")
        print(f"  Booked At: {booking.booked_at}")
        print(f"  Time Slot: {booking.time_slot}")
        if hasattr(booking, 'otp'):
            print(f"  OTP: {booking.otp}")
        print()
