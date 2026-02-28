"""
Create a test gym owner request to verify approval workflow
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from gyms.models import GymOwnerRequest, Gym
from accounts.mongo_models import UserProfile
from django.conf import settings
from django.utils import timezone

print("Creating test gym owner request...")
print()

# Get a test user
if settings.DATABASE_MODE == 'mongodb':
    # Get any regular user (not gym_owner or admin)
    test_user = UserProfile.objects(role='user', is_active=True).first()
    if not test_user:
        # Create a test user
        from django.contrib.auth.hashers import make_password
        test_user = UserProfile(
            username='testgymowner',
            email='testgymowner@example.com',
            password=make_password('testpass123'),
            role='user',
            is_active=True
        )
        test_user.save()
        print(f"Created test user: {test_user.username}")
    else:
        print(f"Using existing user: {test_user.username} (ID: {test_user.id})")
else:
    from django.contrib.auth import get_user_model
    User = get_user_model()
    test_user = User.objects.filter(is_active=True).exclude(is_superuser=True).first()
    if not test_user:
        test_user = User.objects.create_user(
            username='testgymowner',
            email='testgymowner@example.com',
            password='testpass123'
        )
        if hasattr(test_user, 'role'):
            test_user.role = 'user'
            test_user.save()
        print(f"Created test user: {test_user.username}")
    else:
        print(f"Using existing user: {test_user.username} (ID: {test_user.id})")

print(f"User Role: {test_user.role}")
print()

# Create test gym owner request
print("Creating gym owner request...")
request = GymOwnerRequest.objects.create(
    user_id=str(test_user.id),
    username=test_user.username,
    gym_name="FitZone Premium Gym",
    gym_address="123 Main Street, Downtown, Mumbai, Maharashtra 400001",
    owner_name="John Doe",
    contact_number="+91-9876543210",
    email=test_user.email,
    years_in_business=5,
    total_members=250,
    # Premium facilities
    has_ac=True,
    has_changing_rooms=True,
    has_showers=True,
    has_lockers=True,
    has_parking=True,
    has_trainers=True,
    has_cardio=True,
    has_weights=True,
    has_machines=True,
    has_group_classes=True,
    has_spa=True,
    has_pool=False,
    has_cafeteria=True,
    has_music=True,
    has_wifi=True,
    additional_info="Established premium gym with modern equipment and experienced trainers.",
    status='pending'
)

# Calculate tier
tier = request.calculate_tier_score()
request.suggested_tier = tier
request.ai_recommendation = f"✓ Legitimate gym with {len(request.get_facilities_list())} facilities. Recommended Tier: {tier}. Risk: Low. Recommendation: APPROVE"
request.save()

print(f"✓ Created request ID: {request.id}")
print(f"  Gym: {request.gym_name}")
print(f"  Owner: {request.owner_name}")
print(f"  User: {request.username} (ID: {request.user_id})")
print(f"  Suggested Tier: {tier}")
print(f"  Facilities: {len(request.get_facilities_list())}")
print(f"  Status: {request.status}")
print()

print("✅ Test request created successfully!")
print()
print("Next steps:")
print(f"1. Go to: http://127.0.0.1:8000/admin/gyms/gymownerrequest/")
print(f"2. Find request ID {request.id} for '{request.gym_name}'")
print(f"3. Click to review")
print(f"4. Change status to 'Approved' and save")
print()
print("OR use bulk action:")
print(f"1. Select the request checkbox")
print("2. Choose 'Approve selected requests' action")
print("3. Click 'Go'")
print()
print("Expected results after approval:")
print(f"  - User '{test_user.username}' role changes from '{test_user.role}' to 'gym_owner'")
print(f"  - Gym '{request.gym_name}' is created with Tier {tier}")
print(f"  - Gym is set to active and verified")
