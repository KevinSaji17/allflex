"""
Sync gyms with approved requests - remove orphaned data and create missing gyms
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from gyms.models import GymOwnerRequest
from accounts.mongo_models import Gym, UserProfile as User

print("=" * 80)
print("STEP 1: Remove orphaned test gyms")
print("=" * 80)

# Remove test gyms that don't have matching requests
orphaned_gyms = ['FitZone Premium Gym', 'PowerHouse Fitness', 'Wellness Yoga Studio']
for gym_name in orphaned_gyms:
    gym = Gym.objects.filter(name=gym_name).first()
    if gym:
        print(f"Deleting orphaned gym: {gym_name}")
        gym.delete()
        print(f"  ✓ Deleted")

print("\n" + "=" * 80)
print("STEP 2: Create gyms for approved requests")
print("=" * 80)

approved_requests = GymOwnerRequest.objects.filter(status='approved')

for req in approved_requests:
    # Check if gym already exists
    existing_gym = Gym.objects.filter(name=req.gym_name).first()
    if existing_gym:
        print(f"Gym already exists: {req.gym_name}")
        continue
    
    # Get the owner user
    try:
        owner = User.objects.get(username=req.username)
    except User.DoesNotExist:
        print(f"✗ Owner not found for {req.gym_name} (username: {req.username})")
        continue
    
    # Create the gym
    gym = Gym(
        name=req.gym_name,
        owner=owner,
        description=f"Premium fitness facility at {req.gym_address}",
        location=req.gym_address,
        tier=req.suggested_tier,
        capacity=100,
        status='approved',
        is_active=True,
        is_verified_partner=True,  # Approved gyms get verified partner status
        wallet_balance=0.0
    )
    gym.save()
    
    print(f"\n✓ Created gym: {req.gym_name}")
    print(f"  Owner: {owner.username}")
    print(f"  Tier: {req.suggested_tier}")
    print(f"  Location: {req.gym_address}")
    print(f"  Verified Partner: Yes")
    
    # Update owner role to gym_owner if not already
    if owner.role != 'gym_owner':
        owner.role = 'gym_owner'
        owner.save()
        print(f"  ✓ Updated {owner.username} role to gym_owner")

print("\n" + "=" * 80)
print("STEP 3: Verify final state")
print("=" * 80)

all_gyms = Gym.objects.all()
print(f"\nTotal gyms now: {all_gyms.count()}")

for gym in all_gyms:
    owner_username = gym.owner.username if gym.owner else 'N/A'
    matching_req = GymOwnerRequest.objects.filter(gym_name=gym.name, status='approved').first()
    status = "✓ HAS MATCHING APPROVED REQUEST" if matching_req else "✗ NO MATCHING REQUEST"
    print(f"\n{gym.name} (Owner: {owner_username})")
    print(f"  {status}")
    print(f"  Tier: {gym.tier}, Status: {gym.status}, Verified: {gym.is_verified_partner}")

print("\n" + "=" * 80)
print("SYNC COMPLETE!")
print("=" * 80)
