"""
Create a test gym for gym owner kevin to test the dashboard
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from accounts.db_utils import get_user_model, get_gym_model, is_mongodb
from gyms.models import GymOwnerRequest

User = get_user_model()
Gym = get_gym_model()

print("\n" + "=" * 80)
print("CREATING TEST GYM FOR KEVIN (GYM OWNER)")
print("=" * 80)

# Find or create kevin user
if is_mongodb():
    kevin = User.objects(username='kevin123').first()
    if not kevin:
        print("❌ User 'kevin123' not found. Please create this user first.")
        sys.exit(1)
else:
    try:
        kevin = User.objects.get(username='kevin123')
    except User.DoesNotExist:
        print("❌ User 'kevin123' not found. Please create this user first.")
        sys.exit(1)

print(f"\n✓ Found user: {kevin.username}")
print(f"  Email: {kevin.email}")
print(f"  Current Role: {kevin.role}")

# Update role to gym_owner if needed
if kevin.role != 'gym_owner':
    kevin.role = 'gym_owner'
    kevin.save()
    print(f"  ✓ Updated role to: gym_owner")

# Create test gym
gym_data = {
    'name': "Kevin's Fitness Hub",
    'location': "123 Main Street, Mumbai, Maharashtra 400001",
    'description': "Premium fitness facility with state-of-the-art equipment, personal trainers, and spacious workout areas. Perfect for all fitness levels.",
    'tier': 2,
    'capacity': 50,
    'latitude': 18.9388,  # Mumbai coordinates
    'longitude': 72.8354,
}

print(f"\n📍 Creating gym: {gym_data['name']}")

# Check if gym already exists
if is_mongodb():
    existing = Gym.objects(name=gym_data['name']).first()
else:
    existing = Gym.objects.filter(name=gym_data['name']).first()

if existing:
    print(f"  ⚠️  Gym already exists! Updating it...")
    gym = existing
    gym.owner = kevin
    gym.location = gym_data['location']
    gym.description = gym_data['description']
    gym.tier = gym_data['tier']
    gym.capacity = gym_data['capacity']
    gym.latitude = gym_data['latitude']
    gym.longitude = gym_data['longitude']
    gym.status = 'approved'
    gym.is_active = True
    gym.is_verified_partner = True
    gym.save()
else:
    # Create new gym
    gym = Gym(
        name=gym_data['name'],
        owner=kevin,
        location=gym_data['location'],
        description=gym_data['description'],
        tier=gym_data['tier'],
        capacity=gym_data['capacity'],
        latitude=gym_data['latitude'],
        longitude=gym_data['longitude'],
        status='approved',
        is_active=True,
        is_verified_partner=True,
        wallet_balance=0.0
    )
    gym.save()
    print(f"  ✓ Gym created successfully!")

# Create matching GymOwnerRequest for consistency
existing_request = GymOwnerRequest.objects.filter(
    gym_name=gym_data['name'],
    username=kevin.username
).first()

if not existing_request:
    request = GymOwnerRequest.objects.create(
        user_id=str(kevin.id),
        username=kevin.username,
        gym_name=gym_data['name'],
        gym_address=gym_data['location'],
        owner_name=kevin.username,
        contact_number='9876543210',
        email=kevin.email,
        years_in_business=3,
        total_members=200,
        has_ac=True,
        has_changing_rooms=True,
        has_showers=True,
        has_lockers=True,
        has_parking=True,
        has_trainers=True,
        has_cardio=True,
        has_weights=True,
        has_machines=True,
        status='approved',
        suggested_tier=gym_data['tier']
    )
    print(f"  ✓ Created matching GymOwnerRequest")
else:
    print(f"  ✓ GymOwnerRequest already exists")

print("\n" + "=" * 80)
print("✅ TEST GYM CREATED SUCCESSFULLY!")
print("=" * 80)

print(f"\n📋 Gym Details:")
print(f"  Name: {gym.name}")
print(f"  Owner: {gym.owner.username}")
print(f"  Location: {gym.location}")
print(f"  Tier: {gym.tier}")
print(f"  GPS: {gym.latitude}, {gym.longitude}")
print(f"  Status: {gym.status}")
print(f"  Verified Partner: {gym.is_verified_partner}")
print(f"  Wallet Balance: ₹{gym.wallet_balance}")

print(f"\n🔍 Testing Tips:")
print(f"  1. Login as: kevin123")
print(f"  2. Visit: http://127.0.0.1:8000/gym-dashboard/")
print(f"  3. You should see '{gym.name}' in your gyms list")
print(f"  4. To find this gym in search, use pincode: 400001")
print(f"     Gemini AI should return nearby gyms including this one")

print("\n✓ Done!\n")
