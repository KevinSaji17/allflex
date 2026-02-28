"""
Management command to seed credit packs in MongoDB
Run: python manage.py seed_mongo_credit_packs
"""

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Seed credit packs into MongoDB'

    def handle(self, *args, **options):
        if getattr(settings, 'DATABASE_MODE', 'sqlite') != 'mongodb':
            self.stdout.write(self.style.ERROR('DATABASE_MODE is not set to mongodb'))
            return
        
        from accounts.mongo_models import CreditPack
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('Seeding Credit Packs to MongoDB'))
        self.stdout.write('=' * 60 + '\n')
        
        # Clear existing credit packs
        existing_count = CreditPack.objects.count()
        if existing_count > 0:
            self.stdout.write(f'⚠️  Found {existing_count} existing credit pack(s)')
            confirm = input('Delete existing packs and recreate? (yes/no): ')
            if confirm.lower() == 'yes':
                CreditPack.objects.delete()
                self.stdout.write(self.style.WARNING(f'🗑️  Deleted {existing_count} pack(s)'))
            else:
                self.stdout.write('Cancelled.')
                return
        
        # Define credit packs
        packs = [
            {
                'name': 'Starter Pack',
                'tier': 1,
                'credits': 20,
                'price': 499.00,
                'validity_days': 30,
                'description': 'Perfect for beginners. Try out different gyms!',
                'is_active': True,
                'is_best_value': False,
            },
            {
                'name': 'Active Pack',
                'tier': 1,
                'credits': 50,
                'price': 899.00,
                'validity_days': 60,
                'description': 'Great for regular gym-goers. Best value!',
                'is_active': True,
                'is_best_value': True,
            },
            {
                'name': 'Champion Pack',
                'tier': 1,
                'credits': 100,
                'price': 1499.00,
                'validity_days': 90,
                'description': 'For fitness enthusiasts. Maximum savings!',
                'is_active': True,
                'is_best_value': False,
            },
            {
                'name': 'Premium Starter',
                'tier': 2,
                'credits': 20,
                'price': 799.00,
                'validity_days': 30,
                'description': 'Access Tier 2 gyms with better facilities',
                'is_active': True,
                'is_best_value': False,
            },
            {
                'name': 'Premium Active',
                'tier': 2,
                'credits': 50,
                'price': 1599.00,
                'validity_days': 60,
                'description': 'Best value for Tier 2 gym access',
                'is_active': True,
                'is_best_value': True,
            },
            {
                'name': 'Elite Starter',
                'tier': 3,
                'credits': 20,
                'price': 1099.00,
                'validity_days': 30,
                'description': 'Experience premium Tier 3 gyms',
                'is_active': True,
                'is_best_value': False,
            },
            {
                'name': 'Elite Champion',
                'tier': 3,
                'credits': 50,
                'price': 2299.00,
                'validity_days': 60,
                'description': 'Ultimate access to elite gyms',
                'is_active': True,
                'is_best_value': True,
            },
        ]
        
        created_count = 0
        for pack_data in packs:
            try:
                pack = CreditPack(**pack_data)
                pack.save()
                
                cpm = pack.price_per_credit()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ {pack.name}: {pack.credits} credits @ ₹{pack.price} '
                        f'(₹{cpm}/credit, Tier {pack.tier})'
                    )
                )
                created_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error creating {pack_data["name"]}: {e}'))
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS(f'✅ Created {created_count} credit pack(s)'))
        self.stdout.write('=' * 60)
        self.stdout.write('\nVerify in MongoDB Atlas:')
        self.stdout.write('Database → Browse Collections → credit_packs\n')
