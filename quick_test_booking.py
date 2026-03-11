#!/usr/bin/env python
"""Quick test to create a booking for Kevin's gym."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from accounts.db_utils import get_user_model, get_gym_model, get_gym_booking_model, is_mongodb
from datetime import date

User = get_user_model()
Gym = get_gym_model()
GymBooking = get_gym_booking_model()

print("\n[OK] Connected to MongoDB")

# Get kevin and his gym
kevin = User.objects(username='kevin123').first()
print(f"✓ User: {kevin.username}, Role: {kevin.role}")

kevins_gym = Gym.objects(owner=kevin).first()
print(f"✓ Gym: {kevins_gym.name}")

# Get/create test user
testuser = User.objects(username='testuser_booking').first()
if not testuser:
    testuser = User(
        username='testuser_booking',
         email='testuser_booking@example.com',
        role='user',
        credits=100
    )
    testuser.set_password('testpass123')
    testuser.save()
    print(f"✓ Created testuser")
else:
    print(f"✓ Testuser exists")

# Create booking
existing = GymBooking.objects(user=testuser, gym=kevins_gym, booking_date=date.today()).first()

if not existing:
    booking = GymBooking(
        user=testuser,
        gym=kevins_gym,
        gym_name=kevins_gym.name,
        tier=kevins_gym.tier,
        credits_charged=10,
        booking_date=date.today(),
        status='checked_in'
    )
    booking.save()
    print(f"✅ Created booking!")
else:
    print(f"✓ Booking exists")

# Show stats
total = GymBooking.objects(gym=kevins_gym).count()
active = GymBooking.objects(gym=kevins_gym, status='checked_in').count()

print(f"\n📊 Dashboard Stats:")
print(f"   Total Bookings: {total}")
print(f"   Currently Checked In: {active}")
print(f"\n✅ Dashboard: http://127.0.0.1:8000/gym-dashboard/")
print(f"✅ Browse: http://127.0.0.1:8000/gym-browse/")
