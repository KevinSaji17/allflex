import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from accounts.mongo_models import GymBooking

# Get a recent booking
booking = GymBooking.objects.first()

if booking:
    print(f"Booking found: {booking.user.username} at {booking.gym.name}")
    print(f"Time Slot: '{booking.time_slot}' (empty={len(booking.time_slot)==0})")
    print(f"Booked At: {booking.booked_at}")
    print(f"Booking Date: {booking.booking_date}")
    print(f"Status: {booking.status}")
else:
    print("No bookings found")
