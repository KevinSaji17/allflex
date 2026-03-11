#!/usr/bin/env python
"""Test find gyms injection and dashboard."""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from accounts.db_utils import get_user_model, get_gym_model, get_gym_booking_model, is_mongodb
from allflex.gym_recommender import get_gyms_by_pincode

User = get_user_model()
Gym = get_gym_model()
GymBooking = get_gym_booking_model()

print("\n" + "="*60)
print("TEST 1: FIND GYMS SEARCH (Mumbai 400001)")
print("="*60)

# Simulate the find gyms search
location = "400001"
gym_data = get_gyms_by_pincode(location)
print(f"\n✓ Got {len(gym_data)} gyms from Gemini AI")

# Check if Kevin's gym needs to be injected
location_lower = location.lower()
if '400001' in location or 'mumbai' in location_lower:
    print(f"✓ Mumbai area detected - injecting Kevin's Fitness Hub")
    if isinstance(gym_data, dict) and 'error' not in gym_data:
        gym_data = {"Kevin's Fitness Hub": {"distance": "1.2 km", "rating": 4.7}} | gym_data
    else:
        gym_data = {"Kevin's Fitness Hub": {"distance": "1.2 km", "rating": 4.7}}

print(f"\n✅ Total gyms after injection: {len(gym_data)}")
if "Kevin's Fitness Hub" in gym_data:
    print(f"✅ Kevin's Fitness Hub IS in results!")
    gym_details = gym_data["Kevin's Fitness Hub"]
    print(f"   Details: {gym_details}")
else:
    print(f"❌ Kevin's Fitness Hub NOT in results")

print("\nFirst 5 gyms in results:")
for i, name in enumerate(list(gym_data.keys())[:5]):
    print(f"  {i+1}. {name}")

print("\n" + "="*60)
print("TEST 2: DASHBOARD QUERY (kevin123)")
print("="*60)

# Get kevin
kevin = User.objects(username='kevin123').first()
print(f"\n✓ User: {kevin.username}, Role: {kevin.role}")

# Dashboard query
if is_mongodb():
    owned_gyms = list(Gym.objects(owner=kevin))
    print(f"✓ Owned gyms: {len(owned_gyms)}")
    for gym in owned_gyms:
        print(f"  - {gym.name}")
        print(f"    Location: {gym.location}")
        print(f"    Status: {gym.status}")
    
    # Bookings
    if owned_gyms:
        bookings = GymBooking.objects(gym__in=owned_gyms).order_by('-booked_at')
        print(f"\n✓ Bookings: {bookings.count()}")
        for booking in bookings[:5]:
            print(f"  - {booking.user.username} @ {booking.gym.name}")
            print(f"    Status: {booking.status}, Booked: {booking.booked_at}")
    
    # Stats
    total_bookings = GymBooking.objects(gym__in=owned_gyms).count()
    completed_visits = GymBooking.objects(gym__in=owned_gyms, status='completed').count()
    currently_checked_in = GymBooking.objects(gym__in=owned_gyms, status='checked_in').count()
    
    print(f"\n📊 Dashboard Stats:")
    print(f"   Total Bookings: {total_bookings}")
    print(f"   Verified Visits: {completed_visits}")
    print(f"   Currently At Gym: {currently_checked_in}")

print("\n" + "="*60)
print("✅ ALL TESTS COMPLETE")
print("="*60)
print("\n🌐 Test the app:")
print("   1. Login: http://127.0.0.1:8000/login/")
print("   2. Find Gyms: http://127.0.0.1:8000/dashboard/ (search 400001)")
print("   3. Dashboard: http://127.0.0.1:8000/gym-dashboard/")
print("\n📝 Login as: kevin123 / kevin123\n")
