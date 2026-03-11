#!/usr/bin/env python
"""Test dashboard access and create a booking for Kevin's gym for testing."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.db_utils import is_mongodb, get_gym_model, get_user_model

User = get_user_model()
Gym = get_gym_model()

# Get kevin123 user
if is_mongodb():
    kevin = User.objects(username='kevin123').first()
else:
    kevin = User.objects.filter(username='kevin123').first()

if not kevin:
    print("\n❌ User 'kevin123' not found!")
    exit(1)
print(f"\n✓ User: {kevin.username}, Role: {kevin.role}, Credits: {kevin.credits}")

# Get Kevin's gym
if is_mongodb():
    kevins_gym = Gym.objects.filter(owner=kevin).first()
else:
    kevins_gym = Gym.objects.filter(owner=kevin).first()

if kevins_gym:
    print(f"✓ Gym: {kevins_gym.name}")
    print(f"  Location: {kevins_gym.location}")
    print(f"  Status: {kevins_gym.status}, Active: {kevins_gym.is_active}")
    print(f"  Tier: {kevins_gym.tier}, Verified: {kevins_gym.is_verified_partner}")
    
    # Check if gym is in browse query
    if is_mongodb():
        approved_gyms = Gym.objects.filter(status='approved', is_active=True)
    else:
        approved_gyms = Gym.objects.filter(status='approved', is_active=True)
    
    gym_list = list(approved_gyms)
    print(f"\n✓ Total approved gyms: {len(gym_list)}")
    
    if kevins_gym in gym_list:
        print(f"✅ Kevin's gym IS in browse list!")
    else:
        print(f"❌ Kevin's gym NOT in browse list")
    
    # Create a test booking from testuser
    from accounts.db_utils import get_gym_booking_model
    GymBooking = get_gym_booking_model()
    
    # Get or create testuser
    if is_mongodb():
        testuser = User.objects(username='testuser_for_booking').first()
        created = False
        if not testuser:
            testuser = User(
                username='testuser_for_booking',
                email='testuser@example.com',
                role='user',
                credits=100
            )
            testuser.set_password('testpass123')
            testuser.save()
            created = True
    else:
        testuser, created = User.objects.get_or_create(
            username='testuser_for_booking',
            defaults={
                'email': 'testuser@example.com',
                'role': 'user',
                'credits': 100
            }
        )
        if created:
            testuser.set_password('testpass123')
            testuser.save()
    
    if created:
        print(f"\n✓ Created testuser: {testuser.username}")
    else:
        print(f"\n✓ Using existing testuser: {testuser.username}")
    
    # Create a test booking
    from datetime import date
    
    if is_mongodb():
        existing_bookings = GymBooking.objects(
            user=testuser,
            gym=kevins_gym,
            booked_date=date.today()
        ).count()
    else:
        existing_bookings = GymBooking.objects.filter(
        user=testuser,
        gym=kevins_gym,
        booked_date=date.today()
    ).count()
    
    if existing_bookings == 0:
        if is_mongodb():
            booking = GymBooking(
                user=testuser,
                gym=kevins_gym,
                booked_date=date.today(),
                status='checked_in',  # Simulate active check-in
                credits_deducted=kevins_gym.tier * 5
            )
            booking.save()
        else:
            booking = GymBooking.objects.create(
                user=testuser,
                gym=kevins_gym,
                booked_date=date.today(),
                status='checked_in',  # Simulate active check-in
                credits_deducted=kevins_gym.tier * 5
            )
        print(f"✅ Created test booking: {booking.id}")
        print(f"   Status: {booking.status}")
        print(f"   Credits deducted: {booking.credits_deducted}")
    else:
        print(f"✓ Booking already exists for today")
    
    # Get dashboard stats
    if is_mongodb():
        owned_gyms = list(Gym.objects(owner=kevin))
        all_bookings = GymBooking.objects(gym__in=owned_gyms)
        completed = GymBooking.objects(gym__in=owned_gyms, status='completed').count()
        active = GymBooking.objects(gym__in=owned_gyms, status='checked_in').count()
    else:
        owned_gyms = Gym.objects.filter(owner=kevin)
        all_bookings = GymBooking.objects.filter(gym__in=owned_gyms)
        completed = all_bookings.filter(status='completed').count()
        active = all_bookings.filter(status='checked_in').count()
    
    total = all_bookings.count()
    
    print(f"\n📊 DASHBOARD STATS:")
    print(f"   Total Bookings: {total}")
    print(f"   Verified Visits: {completed}")
    print(f"   Currently At Gym: {active}")
    print(f"   Wallet Balance: ₹{kevins_gym.wallet_balance}")
    
    print(f"\n✅ Dashboard should work at: http://127.0.0.1:8000/gym-dashboard/")
    print(f"✅ Browse gym at: http://127.0.0.1:8000/gym-browse/")
    print(f"✅ Gym detail at: http://127.0.0.1:8000/gym/{kevins_gym.id}/")
    
else:
    print("❌ No gym found for kevin123")
