"""
Management command to setup MongoDB collections and indexes
Run: python manage.py setup_mongodb
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import mongoengine


class Command(BaseCommand):
    help = 'Setup MongoDB collections and create indexes'

    def handle(self, *args, **options):
        if getattr(settings, 'DATABASE_MODE', 'sqlite') != 'mongodb':
            self.stdout.write(self.style.ERROR('DATABASE_MODE is not set to mongodb'))
            self.stdout.write('Update your .env file: DATABASE_MODE=mongodb')
            return
        
        self.stdout.write('=' * 60)
        self.stdout.write(self.style.SUCCESS('MongoDB Setup Starting...'))
        self.stdout.write('=' * 60)
        
        try:
            # Import all MongoDB models
            from accounts.mongo_models import (
                UserProfile, Gym, Booking, Rating, PayoutRequest,
                CreditPack, UserCreditPack, CreditTransaction,
                GymBooking, UserCreditBalance
            )
            
            models = [
                UserProfile, Gym, Booking, Rating, PayoutRequest,
                CreditPack, UserCreditPack, CreditTransaction,
                GymBooking, UserCreditBalance
            ]
            
            # Create indexes for each model
            for model in models:
                collection_name = model._get_collection_name()
                self.stdout.write(f'\n📦 Setting up: {collection_name}')
                
                try:
                    # Ensure indexes
                    model.ensure_indexes()
                    self.stdout.write(self.style.SUCCESS(f'✅ Indexes created for {collection_name}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'❌ Error creating indexes: {e}'))
            
            # Test connection
            self.stdout.write(f'\n🔍 Testing MongoDB connection...')
            db = mongoengine.get_db()
            collections = db.list_collection_names()
            self.stdout.write(self.style.SUCCESS(f'✅ Connected to database: {db.name}'))
            self.stdout.write(f'📊 Collections: {", ".join(collections) if collections else "None yet"}')
            
            # Create default superuser if none exists
            self.stdout.write(f'\n👤 Checking for superuser...')
            if UserProfile.objects.filter(is_superuser=True).count() == 0:
                self.stdout.write(self.style.WARNING('No superuser found. Create one with:'))
                self.stdout.write('python manage.py create_mongo_superuser')
            else:
                superuser_count = UserProfile.objects.filter(is_superuser=True).count()
                self.stdout.write(self.style.SUCCESS(f'✅ Found {superuser_count} superuser(s)'))
            
            self.stdout.write('\n' + '=' * 60)
            self.stdout.write(self.style.SUCCESS('✅ MongoDB Setup Complete!'))
            self.stdout.write('=' * 60)
            self.stdout.write('\nNext steps:')
            self.stdout.write('1. Run: python manage.py create_mongo_superuser (if needed)')
            self.stdout.write('2. Run: python manage.py runserver')
            self.stdout.write('3. Test signup at: http://127.0.0.1:8000/accounts/signup/')
            self.stdout.write('4. Check MongoDB Atlas dashboard to verify data\n')
            
        except Exception as e:
            self.stdout.write('\n' + '=' * 60)
            self.stdout.write(self.style.ERROR(f'❌ MongoDB Setup Failed'))
            self.stdout.write('=' * 60)
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
            self.stdout.write('\nTroubleshooting:')
            self.stdout.write('1. Check .env file has correct MongoDB credentials')
            self.stdout.write('2. Verify MongoDB Atlas network access (IP whitelist)')
            self.stdout.write('3. Ensure cluster is not paused')
            self.stdout.write('4. Test connection string in MongoDB Compass\n')
