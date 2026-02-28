"""
Management command to check MongoDB migration readiness
Run: python manage.py check_mongo_ready
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Check if MongoDB migration is ready'

    def handle(self, *args, **options):
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('MongoDB Migration Readiness Check'))
        self.stdout.write('=' * 60 + '\n')
        
        checks_passed = 0
        checks_failed = 0
        
        # Check 1: Python packages
        self.stdout.write('📦 Checking Python packages...')
        try:
            import mongoengine
            import pymongo
            import dns.resolver
            self.stdout.write(self.style.SUCCESS('  ✅ mongoengine installed'))
            self.stdout.write(self.style.SUCCESS('  ✅ pymongo installed'))
            self.stdout.write(self.style.SUCCESS('  ✅ dnspython installed'))
            checks_passed += 3
        except ImportError as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Missing package: {e}'))
            self.stdout.write('  Run: pip install -r requirements.txt')
            checks_failed += 1
        
        # Check 2: Environment variables
        self.stdout.write('\n🔐 Checking environment variables...')
        env_vars = {
            'DATABASE_MODE': os.getenv('DATABASE_MODE'),
            'MONGO_DB_NAME': os.getenv('MONGO_DB_NAME'),
            'MONGO_DB_USER': os.getenv('MONGO_DB_USER'),
            'MONGO_DB_PASSWORD': os.getenv('MONGO_DB_PASSWORD'),
            'MONGO_DB_HOST': os.getenv('MONGO_DB_HOST'),
        }
        
        for var, value in env_vars.items():
            if value and 'REPLACE' not in value.upper():
                self.stdout.write(self.style.SUCCESS(f'  ✅ {var} = {value[:20]}...'))
                checks_passed += 1
            else:
                self.stdout.write(self.style.ERROR(f'  ❌ {var} = {value or "NOT SET"}'))
                self.stdout.write(f'     Update .env file with your MongoDB Atlas {var}')
                checks_failed += 1
        
        # Check 3: Database mode
        self.stdout.write('\n🗄️  Checking database mode...')
        db_mode = getattr(settings, 'DATABASE_MODE', 'sqlite')
        if db_mode == 'mongodb':
            self.stdout.write(self.style.SUCCESS(f'  ✅ DATABASE_MODE = {db_mode}'))
            checks_passed += 1
        else:
            self.stdout.write(self.style.WARNING(f'  ⚠️  DATABASE_MODE = {db_mode}'))
            self.stdout.write('     Set DATABASE_MODE=mongodb in .env to use MongoDB')
            checks_failed += 1
        
        # Check 4: MongoDB connection
        if db_mode == 'mongodb':
            self.stdout.write('\n🔌 Testing MongoDB connection...')
            try:
                import mongoengine
                db = mongoengine.get_db()
                self.stdout.write(self.style.SUCCESS(f'  ✅ Connected to: {db.name}'))
                
                # Try to list collections
                collections = db.list_collection_names()
                if collections:
                    self.stdout.write(self.style.SUCCESS(f'  ✅ Found {len(collections)} collection(s)'))
                else:
                    self.stdout.write(self.style.WARNING('  ⚠️  No collections yet (run setup_mongodb)'))
                checks_passed += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ Connection failed: {e}'))
                self.stdout.write('     Check your .env credentials and MongoDB Atlas network access')
                checks_failed += 1
        
        # Check 5: Models exist
        self.stdout.write('\n📋 Checking MongoDB models...')
        try:
            from accounts.mongo_models import (
                UserProfile, Gym, Booking, CreditPack, 
                CreditTransaction, GymBooking
            )
            self.stdout.write(self.style.SUCCESS('  ✅ All MongoDB models imported successfully'))
            checks_passed += 1
        except ImportError as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Error importing models: {e}'))
            checks_failed += 1
        
        # Check 6: Auth backend
        self.stdout.write('\n🔑 Checking authentication backend...')
        backends = getattr(settings, 'AUTHENTICATION_BACKENDS', [])
        if 'accounts.auth_backends.MongoEngineAuthBackend' in backends:
            self.stdout.write(self.style.SUCCESS('  ✅ MongoEngineAuthBackend configured'))
            checks_passed += 1
        else:
            self.stdout.write(self.style.ERROR('  ❌ MongoEngineAuthBackend not in AUTHENTICATION_BACKENDS'))
            checks_failed += 1
        
        # Check 7: Management commands exist
        self.stdout.write('\n⚙️  Checking management commands...')
        commands = [
            'setup_mongodb',
            'create_mongo_superuser',
            'test_mongo_auth',
            'seed_mongo_credit_packs',
        ]
        for cmd in commands:
            cmd_path = f'accounts/management/commands/{cmd}.py'
            if os.path.exists(cmd_path):
                self.stdout.write(self.style.SUCCESS(f'  ✅ {cmd}'))
                checks_passed += 1
            else:
                self.stdout.write(self.style.ERROR(f'  ❌ {cmd} (file not found)'))
                checks_failed += 1
        
        # Summary
        total = checks_passed + checks_failed
        percentage = (checks_passed / total * 100) if total > 0 else 0
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('Summary')
        self.stdout.write('=' * 60)
        self.stdout.write(f'Checks passed: {checks_passed}')
        self.stdout.write(f'Checks failed: {checks_failed}')
        self.stdout.write(f'Success rate: {percentage:.0f}%')
        self.stdout.write('=' * 60)
        
        if checks_failed == 0:
            self.stdout.write('\n' + '🎉' * 20)
            self.stdout.write(self.style.SUCCESS('\n✅ ALL CHECKS PASSED!'))
            self.stdout.write('\nYour MongoDB migration is ready!')
            self.stdout.write('\nNext steps:')
            self.stdout.write('1. python manage.py setup_mongodb')
            self.stdout.write('2. python manage.py create_mongo_superuser')
            self.stdout.write('3. python manage.py runserver')
            self.stdout.write('4. Go to: http://127.0.0.1:8000/accounts/signup/')
            self.stdout.write('5. Check MongoDB Atlas for your data\n')
        elif checks_failed <= 2:
            self.stdout.write('\n⚠️  ' + '=' * 54)
            self.stdout.write(self.style.WARNING('\n⚠️  ALMOST READY - Fix the issues above'))
            self.stdout.write('\nMost likely needed:')
            self.stdout.write('- Update MONGO_DB_HOST in .env file (get from MongoDB Atlas)')
            self.stdout.write('- Run: pip install -r requirements.txt\n')
        else:
            self.stdout.write('\n❌ ' + '=' * 54)
            self.stdout.write(self.style.ERROR('\n❌ NOT READY - Please fix the issues above'))
            self.stdout.write('\nRecommended steps:')
            self.stdout.write('1. Read: MONGODB_SETUP.md')
            self.stdout.write('2. Update .env file with MongoDB credentials')
            self.stdout.write('3. Run: pip install -r requirements.txt')
            self.stdout.write('4. Run this check again\n')
