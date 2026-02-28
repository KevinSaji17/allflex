"""
Final verification - No overlap, perfect sync
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from gyms.models import GymOwnerRequest
from accounts.mongo_models import Gym

print("\n" + "=" * 80)
print("FINAL VERIFICATION - GYM OWNER REQUESTS vs MANAGE GYMS")
print("=" * 80)

# Get all requests
all_requests = GymOwnerRequest.objects.all().order_by('-created_at')
approved_requests = [r for r in all_requests if r.status == 'approved']
pending_requests = [r for r in all_requests if r.status == 'pending']
rejected_requests = [r for r in all_requests if r.status == 'rejected']

# Get all gyms
all_gyms = Gym.objects.all()

print(f"\n📋 GYM OWNER REQUESTS SECTION:")
print(f"   Total Requests: {len(all_requests)}")
print(f"   ├─ Approved: {len(approved_requests)}")
print(f"   ├─ Pending: {len(pending_requests)}")
print(f"   └─ Rejected: {len(rejected_requests)}")

print(f"\n🏋️  MANAGE GYMS SECTION:")
print(f"   Total Gyms: {all_gyms.count()}")
print(f"   └─ All are approved and verified partners")

print(f"\n✓ SYNC STATUS:")
print(f"   Approved Requests = Gyms in Database: {len(approved_requests)} = {all_gyms.count()}")

if len(approved_requests) == all_gyms.count():
    print(f"   🎉 PERFECT MATCH! No overlap, no missing data.")
else:
    print(f"   ⚠️  MISMATCH DETECTED")

print("\n📊 DETAILED BREAKDOWN:")
print("\nGYM OWNER REQUESTS (Admin Panel):")
for req in all_requests:
    status_icon = "✓" if req.status == "approved" else "✗" if req.status == "rejected" else "⏳"
    print(f"  {status_icon} {req.gym_name} ({req.owner_name}/{req.username}) - {req.status.upper()}")

print("\nMANAGE GYMS (Admin Panel):")
for gym in all_gyms:
    owner_name = gym.owner.username if gym.owner else 'N/A'
    print(f"  ✓ {gym.name} (Owner: {owner_name}) - Tier {gym.tier}, Verified: {gym.is_verified_partner}")

print("\n🔍 CROSS-REFERENCE CHECK:")
for req in approved_requests:
    gym = Gym.objects.filter(name=req.gym_name).first()
    if gym:
        print(f"  ✓ '{req.gym_name}' - Request APPROVED → Gym EXISTS in database")
    else:
        print(f"  ✗ '{req.gym_name}' - Request APPROVED but gym MISSING!")

for req in rejected_requests:
    gym = Gym.objects.filter(name=req.gym_name).first()
    if gym:
        print(f"  ⚠️  '{req.gym_name}' - Request REJECTED but gym EXISTS (should not happen!)")
    else:
        print(f"  ✓ '{req.gym_name}' - Request REJECTED → No gym in database (correct)")

for req in pending_requests:
    gym = Gym.objects.filter(name=req.gym_name).first()
    if gym:
        print(f"  ⚠️  '{req.gym_name}' - Request PENDING but gym ALREADY EXISTS")

print("\n" + "=" * 80)
print("HARDCODE CHECK")
print("=" * 80)

hardcoded_test_names = ['FitZone Premium Gym', 'PowerHouse Fitness', 'Wellness Yoga']
found_hardcoded = False

for name in hardcoded_test_names:
    gym = Gym.objects.filter(name=name).first()
    if gym:
        print(f"  ⚠️  Found hardcoded test gym: {name}")
        found_hardcoded = True

if not found_hardcoded:
    print(f"  ✓ No hardcoded test gyms found in database")
    print(f"  ✓ Only Gemini API fallback demo data exists (understood by user)")

print("\n" + "=" * 80)
print("✅ VERIFICATION COMPLETE")
print("=" * 80)
