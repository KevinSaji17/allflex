import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from accounts.db_utils import get_user_model, get_gym_model

User = get_user_model()
Gym = get_gym_model()

print("\n" + "="*70)
print("CREATING TEST GYMS IN DATABASE")
print("="*70)

# Get or create a gym owner  
gym_owner = User.objects.filter(role='gym_owner').first()
if not gym_owner:
    print("\n⚠️  No gym owner found. Creating test gym owner...")
    gym_owner = User(
        username='testgymowner',
        email='gymowner@test.com',
        role='gym_owner'
    )
    gym_owner.set_password('test123')
    gym_owner.save()
    print(f"✅ Created gym owner: {gym_owner.username}")
else:
    print(f"✅ Using existing gym owner: {gym_owner.username}")

# Create test gyms
test_gyms = [
    {
        'name': 'FitZone Premium Gym',
        'description': 'Premium fitness center with state-of-the-art equipment',
        'location': '123 MG Road, Bangalore, Karnataka 560001',
        'tier': 3,
        'capacity': 50,
        'status': 'approved',
        'is_active': True,
        'is_verified_partner': True,
    },
    {
        'name': 'PowerHouse Fitness',
        'description': 'Strength training and bodybuilding gym',
        'location': '456 Indiranagar, Bangalore, Karnataka 560038',
        'tier': 2,
        'capacity': 40,
        'status': 'approved',
        'is_active': True,
        'is_verified_partner': True,
    },
    {
        'name': 'Wellness Yoga & Gym',
        'description': 'Combined yoga and gym facility',
        'location': '789 Koramangala, Bangalore, Karnataka 560034',
        'tier': 2,
        'capacity': 30,
        'status': 'pending',
        'is_active': False,
        'is_verified_partner': False,
    },
]

created_count = 0
for gym_data in test_gyms:
    # Check if gym already exists
    existing = Gym.objects.filter(name=gym_data['name']).first()
    if existing:
        print(f"\n⚠️  Gym already exists: {gym_data['name']}")
        continue
    
    gym = Gym(owner=gym_owner, **gym_data)
    gym.save()
    created_count += 1
    
    status_emoji = "✅" if gym.status == 'approved' else "⏳"
    badge_emoji = "🔵" if gym.is_verified_partner else "⚪"
    print(f"\n{status_emoji} Created: {gym.name}")
    print(f"   Status: {gym.status}")
    print(f"   Badge: {badge_emoji} is_verified_partner = {gym.is_verified_partner}")
    print(f"   Location: {gym.location}")
    print(f"   ID: {gym.id}")

print("\n" + "="*70)
print(f"SUMMARY: Created {created_count} new gym(s)")
print("="*70)

# Show all gyms
all_gyms = Gym.objects.all()
print(f"\n📊 Total gyms in database: {all_gyms.count()}")
approved_count = Gym.objects.filter(status='approved').count()
print(f"✅ Approved: {approved_count}")
print(f"⏳ Pending: {all_gyms.count() - approved_count}")

print("\n" + "="*70)
print("NEXT STEPS:")
print("="*70)
print("1. Restart the Django server")
print("2. Search for 'Bangalore' or 'Indiranagar' on the dashboard")
print("3. You should see FitZone Premium Gym with 🔵 ALLFLEX badge!")
print("4. Click the heart to favorite it")
print("5. Check admin panel to approve 'Wellness Yoga & Gym'")
print("="*70 + "\n")
