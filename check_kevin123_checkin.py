import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from accounts.db_utils import get_gym_booking_model, is_mongodb
from accounts.mongo_models import UserProfile

# Get booking model
GymBooking = get_gym_booking_model()

# Get kevin123's bookings
if is_mongodb():
    user = UserProfile.objects(username='kevin123').first()
    if user:
        bookings = GymBooking.objects(user=user).order_by('-booked_at')
        print(f"kevin123 bookings: {bookings.count()}")
        for booking in bookings:
            print(f"\nGym: {booking.gym_name}")
            print(f"  Status: {booking.status}")
            print(f"  Checked In At: {booking.checked_in_at}")
            print(f"  OTP: {booking.otp}")
            print(f"  Booking ID: {booking.id}")
