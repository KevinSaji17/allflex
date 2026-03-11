import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from accounts.db_utils import get_gym_booking_model, is_mongodb
from accounts.mongo_models import UserProfile

# Get booking model
GymBooking = get_gym_booking_model()

# Get all checked-in bookings
if is_mongodb():
    bookings = GymBooking.objects(status='checked_in').order_by('-checked_in_at')
else:
    bookings = GymBooking.objects.filter(status='checked_in').order_by('-checked_in_at')

print(f"Total checked-in bookings: {bookings.count()}")
print()

for booking in bookings:
    print(f"User: {booking.user.username}")
    print(f"Gym: {booking.gym_name}")
    print(f"Status: {booking.status}")
    print(f"Checked In At: {booking.checked_in_at}")
    print(f"Type: {type(booking.checked_in_at)}")
    if booking.checked_in_at:
        print(f"Has timezone info: {booking.checked_in_at.tzinfo}")
    print()
