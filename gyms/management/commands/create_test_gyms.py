"""
Management command to create 10 test gyms for booking
"""
from django.core.management.base import BaseCommand
from accounts.mongo_models import Gym, UserProfile as User
from gyms.models import GymOwnerRequest


class Command(BaseCommand):
    help = 'Create 10 test gyms for booking system testing'

    def handle(self, *args, **kwargs):
        # Get admin user as gym owner
        admin = User.objects.filter(username='admin').first()
        if not admin:
            self.stdout.write(self.style.ERROR('Admin user not found!'))
            return

        # Define 10 test gyms with variety of tiers and locations
        test_gyms = [
            {
                'name': 'Elite Fitness Hub',
                'location': 'Koramangala, Bangalore, Karnataka 560034',
                'tier': 4,
                'description': 'Premium gym with spa, pool, and personal trainers'
            },
            {
                'name': 'Power Gym Indiranagar',
                'location': 'Indiranagar, Bangalore, Karnataka 560038',
                'tier': 3,
                'description': 'Well-equipped gym with cardio and weights'
            },
            {
                'name': 'Fitness First Whitefield',
                'location': 'Whitefield, Bangalore, Karnataka 560066',
                'tier': 4,
                'description': 'Premium fitness center with all amenities'
            },
            {
                'name': 'Anytime Fitness HSR Layout',
                'location': 'HSR Layout, Bangalore, Karnataka 560102',
                'tier': 3,
                'description': '24/7 gym with modern equipment'
            },
            {
                'name': 'Cult.fit Marathahalli',
                'location': 'Marathahalli, Bangalore, Karnataka 560037',
                'tier': 3,
                'description': 'Group fitness classes and gym'
            },
            {
                'name': 'Talwalkars Gym MG Road',
                'location': 'MG Road, Bangalore, Karnataka 560001',
                'tier': 2,
                'description': 'Affordable gym with basic facilities'
            },
            {
                'name': 'Snap Fitness Jayanagar',
                'location': 'Jayanagar, Bangalore, Karnataka 560011',
                'tier': 2,
                'description': 'Compact gym with essential equipment'
            },
            {
                'name': 'Bodyline Fitness BTM Layout',
                'location': 'BTM Layout, Bangalore, Karnataka 560076',
                'tier': 2,
                'description': 'Budget-friendly gym for daily workouts'
            },
            {
                'name': 'Urban Gym Electronic City',
                'location': 'Electronic City, Bangalore, Karnataka 560100',
                'tier': 1,
                'description': 'Basic gym for regular exercise'
            },
            {
                'name': 'FitCafe Gym Bellandur',
                'location': 'Bellandur, Bangalore, Karnataka 560103',
                'tier': 1,
                'description': 'Simple gym with essential facilities'
            }
        ]

        self.stdout.write("=" * 80)
        self.stdout.write("CREATING 10 TEST GYMS FOR BOOKING SYSTEM")
        self.stdout.write("=" * 80)

        created_count = 0
        existing_count = 0

        for gym_data in test_gyms:
            # Check if gym already exists
            existing = Gym.objects.filter(name=gym_data['name']).first()
            if existing:
                self.stdout.write(f"⏭️  {gym_data['name']} - Already exists (Tier {existing.tier})")
                existing_count += 1
                continue
            
            # Create gym
            gym = Gym(
                name=gym_data['name'],
                owner=admin,
                description=gym_data['description'],
                location=gym_data['location'],
                tier=gym_data['tier'],
                capacity=100,
                status='approved',
                is_active=True,
                is_verified_partner=True,
                wallet_balance=0.0
            )
            gym.save()
            
            # Create matching gym owner request for consistency
            request = GymOwnerRequest.objects.create(
                user_id=str(admin.id),
                username=admin.username,
                gym_name=gym_data['name'],
                gym_address=gym_data['location'],
                owner_name='Admin',
                contact_number='9876543210',
                email=admin.email,
                years_in_business=5,
                total_members=500,
                additional_info=gym_data['description'],
                status='approved',
                suggested_tier=gym_data['tier']
            )
            
            self.stdout.write(self.style.SUCCESS(f"✅ {gym_data['name']} - Tier {gym_data['tier']}"))
            created_count += 1

        self.stdout.write("\n" + "=" * 80)
        self.stdout.write("SUMMARY")
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.SUCCESS(f"✅ Created: {created_count} new gyms"))
        self.stdout.write(f"⏭️  Existing: {existing_count} gyms")
        self.stdout.write(f"📊 Total gyms in database: {Gym.objects.count()}")

        # Show tier distribution
        tier_counts = {}
        for gym in Gym.objects.all():
            tier_counts[gym.tier] = tier_counts.get(gym.tier, 0) + 1

        self.stdout.write(f"\n📈 Tier Distribution:")
        for tier in sorted(tier_counts.keys()):
            self.stdout.write(f"   Tier {tier}: {tier_counts[tier]} gyms")

        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("✅ GYMS READY FOR BOOKING TESTING"))
        self.stdout.write("=" * 80)
