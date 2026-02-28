"""
Check sync between Gym Owner Requests and actual Gyms in database
"""
import os
import sys
import django

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from gyms.models import GymOwnerRequest
from accounts.mongo_models import Gym

print("=" * 80)
print("GYM OWNER REQUESTS STATUS")
print("=" * 80)

requests = GymOwnerRequest.objects.all().order_by('-created_at')
for req in requests:
    print(f"\nRequest: {req.gym_name}")
    print(f"  Owner: {req.owner_name} ({req.username})")
    print(f"  Status: {req.status}")
    print(f"  Tier: {req.suggested_tier}")
    print(f"  Created: {req.created_at}")

print("\n" + "=" * 80)
print("ACTUAL GYMS IN DATABASE")
print("=" * 80)

gyms = Gym.objects.all()
print(f"\nTotal gyms in database: {gyms.count()}")

for gym in gyms:
    owner_username = gym.owner.username if gym.owner else 'N/A'
    print(f"\nGym: {gym.name}")
    print(f"  Owner: {owner_username}")
    print(f"  Status: {gym.status}")
    print(f"  Tier: {gym.tier}")
    print(f"  Active: {gym.is_active}")
    print(f"  Verified Partner: {gym.is_verified_partner}")
    print(f"  Location: {gym.location[:60]}...")

print("\n" + "=" * 80)
print("MISMATCH CHECK")
print("=" * 80)

approved_requests = GymOwnerRequest.objects.filter(status='approved')
print(f"\nApproved requests: {approved_requests.count()}")
for req in approved_requests:
    # Check if corresponding gym exists
    matching_gym = Gym.objects.filter(name=req.gym_name).first()
    if matching_gym:
        print(f"✓ {req.gym_name} - HAS MATCHING GYM")
    else:
        print(f"✗ {req.gym_name} - NO MATCHING GYM (Request approved but gym not created)")

print(f"\nTotal gyms in database: {gyms.count()}")
for gym in gyms:
    # Check if there's a corresponding request
    matching_req = GymOwnerRequest.objects.filter(gym_name=gym.name).first()
    if matching_req:
        print(f"✓ {gym.name} - HAS MATCHING REQUEST (Status: {matching_req.status})")
    else:
        print(f"✗ {gym.name} - NO MATCHING REQUEST (Gym exists but no request record)")
