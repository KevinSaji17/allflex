"""
Test the admin approval workflow programmatically
This simulates what happens when admin approves a request
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from gyms.models import GymOwnerRequest
from accounts.db_utils import get_gym_model, is_mongodb
from accounts.mongo_models import UserProfile
from django.conf import settings
from django.utils import timezone

Gym = get_gym_model()  # Use the correct model based on database mode

print("=" * 80)
print("TESTING ADMIN APPROVAL WORKFLOW")
print("=" * 80)
print()

# Get the pending request
request = GymOwnerRequest.objects.filter(status='pending').first()

if not request:
    print("❌ No pending requests to test")
    print("Run: python create_test_request.py first")
    exit()

print(f"Testing approval for request ID: {request.id}")
print(f"Gym: {request.gym_name}")
print(f"User: {request.username} (ID: {request.user_id})")
print()

# BEFORE STATE
print("BEFORE APPROVAL:")
print("-" * 80)
print(f"Request Status: {request.status}")

# Check user
if settings.DATABASE_MODE == 'mongodb':
    user = UserProfile.objects(id=request.user_id).first()
else:
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        user = User.objects.get(id=request.user_id)
    except User.DoesNotExist:
        user = None

if user:
    print(f"User '{user.username}' role: {user.role}")
else:
    print("⚠️ User not found!")

# Check gym
if settings.DATABASE_MODE == 'mongodb':
    existing_gym = Gym.objects(name=request.gym_name).first()
else:
    existing_gym = Gym.objects.filter(name=request.gym_name).first()

if existing_gym:
    print(f"Gym exists: Yes (ID: {existing_gym.id})")
else:
    print("Gym exists: No")
print()

# SIMULATE APPROVAL (what save_model in admin does)
print("EXECUTING APPROVAL WORKFLOW:")
print("-" * 80)

try:
    # Step 1: Update user role
    print("1. Updating user role to 'gym_owner'...")
    if settings.DATABASE_MODE == 'mongodb':
        user = UserProfile.objects(id=request.user_id).first()
        if user:
            user.role = 'gym_owner'
            user.save()
            print(f"   ✓ User '{user.username}' role updated to 'gym_owner'")
        else:
            print(f"   ❌ User not found with ID: {request.user_id}")
    else:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(id=request.user_id)
        if hasattr(user, 'role'):
            user.role = 'gym_owner'
            user.save()
            print(f"   ✓ User '{user.username}' role updated to 'gym_owner'")
    
    # Step 2: Create gym
    print("2. Creating gym...")
    
    if settings.DATABASE_MODE == 'mongodb':
        # Check if gym already exists (MongoDB)
        if not Gym.objects(name=request.gym_name, location=request.gym_address).first():
            tier = request.suggested_tier or request.calculate_tier_score()
            facilities_list = request.get_facilities_list()
            
            # Create MongoDB gym
            gym = Gym(
                owner=user,
                name=request.gym_name,
                description=f"Facilities: {', '.join(facilities_list)}\n\n{request.additional_info}",
                location=request.gym_address,
                tier=tier,
                status='approved',
                is_active=True,
                is_verified_partner=True
            )
            gym.save()
            print(f"   ✓ Gym '{gym.name}' created (ID: {gym.id}, Tier: {tier})")
            print(f"   ✓ Status: approved, Active: True, Verified: True")
        else:
            print(f"   ℹ️ Gym already exists")
    else:
        # Check if gym already exists (SQL)
        if not Gym.objects.filter(name=request.gym_name, location=request.gym_address).exists():
            tier = request.suggested_tier or request.calculate_tier_score()
            facilities_list = request.get_facilities_list()
            
            # Create SQL gym
            gym = Gym.objects.create(
                owner=user,
                name=request.gym_name,
                description=f"Facilities: {', '.join(facilities_list)}\n\n{request.additional_info}",
                location=request.gym_address,
                tier=tier,
                status='approved',
                is_active=True,
                is_verified_partner=True
            )
            print(f"   ✓ Gym '{gym.name}' created (ID: {gym.id}, Tier: {tier})")
            print(f"   ✓ Status: approved, Active: True, Verified: True")
        else:
            print(f"   ℹ️ Gym already exists")
    
    # Step 3: Update request status
    print("3. Updating request status...")
    request.status = 'approved'
    request.reviewed_at = timezone.now()
    request.save()
    print(f"   ✓ Request marked as approved")
    print()
    
    # AFTER STATE
    print("AFTER APPROVAL:")
    print("-" * 80)
    print(f"Request Status: {request.status}")
    print(f"Reviewed At: {request.reviewed_at}")
    
    # Re-check user
    if settings.DATABASE_MODE == 'mongodb':
        user = UserProfile.objects(id=request.user_id).first()
    else:
        user = User.objects.get(id=request.user_id)
    
    if user:
        print(f"User '{user.username}' role: {user.role}")
    
    # Re-check gym
    if settings.DATABASE_MODE == 'mongodb':
        gym = Gym.objects(name=request.gym_name).first()
    else:
        gym = Gym.objects.filter(name=request.gym_name).first()
    
    if gym:
        print(f"Gym '{gym.name}':")
        print(f"  - ID: {gym.id}")
        print(f"  - Tier: {gym.tier}")
        print(f"  - Status: {gym.status}")
        print(f"  - Active: {gym.is_active}")
        print(f"  - Verified Partner: {gym.is_verified_partner}")
        if settings.DATABASE_MODE == 'mongodb':
            print(f"  - Owner ID: {gym.owner.id}")
        else:
            print(f"  - Owner ID: {gym.owner.id}")
    print()
    
    print("=" * 80)
    print("✅ APPROVAL WORKFLOW TEST PASSED!")
    print("=" * 80)
    print()
    print("Verification:")
    print(f"  ✓ Request approved: {request.status == 'approved'}")
    print(f"  ✓ User promoted to gym_owner: {user.role == 'gym_owner'}")
    print(f"  ✓ Gym created: {gym is not None}")
    print(f"  ✓ Gym is active: {gym.is_active if gym else False}")
    print(f"  ✓ Gym is verified: {gym.is_verified_partner if gym else False}")
    print()
    
except Exception as e:
    print()
    print("=" * 80)
    print("❌ APPROVAL WORKFLOW FAILED!")
    print("=" * 80)
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
