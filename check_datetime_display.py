import os
import sys
import django
from datetime import datetime, timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from django.conf import settings
from accounts.mongo_models import GymBooking
from django.utils import timezone as django_tz

print(f"Django TIME_ZONE setting: {settings.TIME_ZONE}")
print(f"Django USE_TZ setting: {settings.USE_TZ}")
print(f"Current Django timezone: {django_tz.get_current_timezone()}")
print()

# Get a booking
booking = GymBooking.objects.first()

if booking:
    print(f"Booking: {booking.user.username} at {booking.gym.name}")
    print(f"\nRaw booked_at from database: {booking.booked_at}")
    print(f"Type: {type(booking.booked_at)}")
    print(f"Has timezone info: {booking.booked_at.tzinfo}")
    print()
    
    # Try to make it timezone aware if it isn't
    if booking.booked_at.tzinfo is None:
        print("DateTime is NAIVE (no timezone info)")
        print("Django will treat this as if it's already in the TIME_ZONE setting")
        print()
        
        # Make it UTC aware
        utc_aware = booking.booked_at.replace(tzinfo=timezone.utc)
        print(f"If we make it UTC aware: {utc_aware}")
        
        # Convert to IST
        ist_time = utc_aware.astimezone(django_tz.get_current_timezone())
        print(f"Converted to IST: {ist_time}")
        print(f"Formatted: {ist_time.strftime('%b %d, %Y %I:%M %p')}")
    else:
        print("DateTime is timezone-aware")
        print(f"In current timezone: {django_tz.localtime(booking.booked_at)}")
else:
    print("No bookings found")
