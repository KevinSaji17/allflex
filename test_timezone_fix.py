import os
import sys
import django
from datetime import timezone as dt_timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from accounts.mongo_models import GymBooking
from django.utils import timezone
from django.template.defaultfilters import date as date_filter

print("Testing datetime conversion...")
print()

booking = GymBooking.objects.first()

if booking:
    print(f"Booking: {booking.user.username} at {booking.gym.name}")
    print()
    
    # Original naive UTC
    print(f"Original (naive UTC): {booking.booked_at}")
    
    # Make timezone-aware
    if booking.booked_at.tzinfo is None:
        aware_dt = booking.booked_at.replace(tzinfo=dt_timezone.utc)
        print(f"Made UTC-aware: {aware_dt}")
        
        # Convert to IST
        ist_dt = timezone.localtime(aware_dt)
        print(f"Converted to IST: {ist_dt}")
        
        # Format like template will
        formatted = date_filter(ist_dt, "M d, Y g:i A")
        print(f"Formatted: {formatted}")
        print()
        print(f"✅ Old display: Mar 11, 2026 3:48 PM")
        print(f"✅ New display: {formatted}")
else:
    print("No bookings found")
