"""
Management command to test MongoDB authentication
Run: python manage.py test_mongo_auth
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import getpass


class Command(BaseCommand):
    help = 'Test MongoDB authentication system'

    def handle(self, *args, **options):
        if getattr(settings, 'DATABASE_MODE', 'sqlite') != 'mongodb':
            self.stdout.write(self.style.ERROR('DATABASE_MODE is not set to mongodb'))
            return
        
        from accounts.mongo_models import UserProfile
        from accounts.auth_backends import MongoEngineAuthBackend
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('MongoDB Authentication Test'))
        self.stdout.write('=' * 60 + '\n')
        
        # List all users
        users = UserProfile.objects.all()
        self.stdout.write(f'📊 Total users in database: {users.count()}\n')
        
        if users.count() == 0:
            self.stdout.write(self.style.WARNING('No users found in database.'))
            self.stdout.write('Create a user with: python manage.py create_mongo_superuser\n')
            return
        
        # Show users
        self.stdout.write('Users:')
        for user in users:
            status = '✅' if user.is_active else '❌'
            self.stdout.write(f'{status} {user.username} ({user.email}) - Role: {user.role}')
        
        # Test authentication
        self.stdout.write('\n' + '-' * 60)
        self.stdout.write('Test Login (or press Ctrl+C to skip)')
        self.stdout.write('-' * 60 + '\n')
        
        try:
            username = input('Username: ').strip()
            if not username:
                return
            
            password = getpass.getpass('Password: ')
            if not password:
                return
            
            # Test authentication backend
            backend = MongoEngineAuthBackend()
            user = backend.authenticate(request=None, username=username, password=password)
            
            if user:
                self.stdout.write('\n' + '=' * 60)
                self.stdout.write(self.style.SUCCESS('✅ Authentication Successful!'))
                self.stdout.write('=' * 60)
                self.stdout.write(f'👤 Username: {user.username}')
                self.stdout.write(f'📧 Email: {user.email}')
                self.stdout.write(f'🎭 Role: {user.role}')
                self.stdout.write(f'💳 Credits: {user.credits}')
                self.stdout.write(f'📅 Date Joined: {user.date_joined}')
                self.stdout.write(f'🔑 User ID (MongoDB ObjectId): {user.id}')
                self.stdout.write(f'✅ Is Active: {user.is_active}')
                self.stdout.write(f'👔 Is Staff: {user.is_staff}')
                self.stdout.write(f'⭐ Is Superuser: {user.is_superuser}')
                self.stdout.write('\n🎉 MongoDB authentication is working correctly!\n')
            else:
                self.stdout.write('\n' + '=' * 60)
                self.stdout.write(self.style.ERROR('❌ Authentication Failed'))
                self.stdout.write('=' * 60)
                self.stdout.write('Possible reasons:')
                self.stdout.write('1. Incorrect username or password')
                self.stdout.write('2. User is inactive (is_active=False)')
                self.stdout.write('3. User does not exist\n')
                
        except KeyboardInterrupt:
            self.stdout.write('\n\nTest cancelled.\n')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Error during authentication test: {e}\n'))
