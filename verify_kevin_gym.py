"""
Verify Kevin's gym exists and check gym owner dashboard access
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from accounts.db_utils import get_user_model, get_gym_model, get_gym_booking_model, is_mongodb

User = get_user_model()
Gym = get_gym_model()
GymBooking = get_gym_booking_model()

print("\n" + "=" * 80)
print("VERIFYING KEVIN'S GYM AND ACCESS")
print("=" * 80)

# Check kevin123 user
if is_mongodb():
    kevin = User.objects(username='kevin123').first()
else:
    kevin = User.objects.filter(username='kevin123').first()

if not kevin:
    print("\n❌ User 'kevin123' not found!")
    sys.exit(1)

print(f"\n✓ User found: {kevin.username}")
print(f"  Email: {kevin.email}")
print(f"  Role: {kevin.role}")
print(f"  Credits: {kevin.credits}")

# Check Kevin's Fitness Hub
if is_mongodb():
    gym = Gym.objects(name="Kevin's Fitness Hub").first()
    all_gyms = list(Gym.objects())
else:
    gym = Gym.objects.filter(name="Kevin's Fitness Hub").first()
    all_gyms = list(Gym.objects.all())

print(f"\n📊 Total gyms in database: {len(all_gyms)}")

if gym:
    print(f"\n✓ Gym found: {gym.name}")
    print(f"  Owner: {gym.owner.username if gym.owner else 'N/A'}")
    print(f"  Location: {gym.location}")
    print(f"  Tier: {gym.tier}")
    print(f"  Status: {gym.status}")
    print(f"  Active: {gym.is_active}")
    print(f"  Verified: {gym.is_verified_partner}")
    print(f"  GPS: {gym.latitude}, {gym.longitude}")
    print(f"  Wallet: ₹{gym.wallet_balance}")
else:
    print(f"\n❌ Kevin's Fitness Hub NOT FOUND in database!")
    print(f"\nExisting gyms:")
    for g in all_gyms[:5]:
        print(f"  - {g.name} (Owner: {g.owner.username if g.owner else 'N/A'})")

# Check bookings for Kevin's gym
if gym:
    if is_mongodb():
        bookings = list(GymBooking.objects(gym=gym))
        kevin_owned_gyms = list(Gym.objects(owner=kevin))
        all_bookings_for_kevin = list(GymBooking.objects(gym__in=kevin_owned_gyms))
    else:
        bookings = list(GymBooking.objects.filter(gym=gym))
        kevin_owned_gyms = list(Gym.objects.filter(owner=kevin))
        all_bookings_for_kevin = list(GymBooking.objects.filter(gym__in=kevin_owned_gyms))
    
    print(f"\n📋 Bookings for Kevin's Fitness Hub: {len(bookings)}")
    print(f"📋 Total gyms owned by kevin123: {len(kevin_owned_gyms)}")
    print(f"📋 Total bookings for kevin's gyms: {len(all_bookings_for_kevin)}")
    
    for owned_gym in kevin_owned_gyms:
        print(f"  - {owned_gym.name}")

# Check gym owner dashboard access
print(f"\n🔐 Gym Owner Dashboard Access:")
if kevin.role == 'gym_owner':
    print(f"  ✓ kevin123 has gym_owner role - CAN access /gym-dashboard/")
else:
    print(f"  ❌ kevin123 role is '{kevin.role}', NOT 'gym_owner'")
    print(f"  ❌ Will be redirected from /gym-dashboard/")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80 + "\n")
