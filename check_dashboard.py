#!/usr/bin/env python
"""Check dashboard query for kevin123."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from accounts.db_utils import get_user_model, get_gym_model, get_gym_booking_model, is_mongodb

User = get_user_model()
Gym = get_gym_model()
GymBooking = get_gym_booking_model()

print("\n[DASHBOARD CHECK]")

# Get kevin
kevin = User.objects(username='kevin123').first()
print(f"✓ User: {kevin.username}, Role: {kevin.role}")

# Get owned gyms (same query as dashboard)
if is_mongodb():
    owned_gyms = list(Gym.objects(owner=kevin))
    print(f"✓ Owned gyms (MongoDB query): {len(owned_gyms)}")
    for gym in owned_gyms:
        print(f"  - {gym.name} (ID: {gym.id})")
    
    # Get bookings
    bookings = GymBooking.objects(gym__in=owned_gyms).order_by('-booked_at')
    print(f"✓ Bookings: {bookings.count()}")
    for booking in bookings:
        print(f"  - {booking.user.username} @ {booking.gym.name} - Status: {booking.status}")
else:
    owned_gyms = Gym.objects.filter(owner=kevin)
    print(f"✓ Owned gyms (Django ORM): {owned_gyms.count()}")
    for gym in owned_gyms:
        print(f"  - {gym.name}")

print("\n✅ Dashboard query working!")
