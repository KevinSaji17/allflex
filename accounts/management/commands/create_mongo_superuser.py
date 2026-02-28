"""
Management command to create a superuser in MongoDB
Run: python manage.py create_mongo_superuser
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import getpass


class Command(BaseCommand):
    help = 'Create a superuser in MongoDB'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username for the superuser',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email for the superuser',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Password for the superuser',
        )

    def handle(self, *args, **options):
        if getattr(settings, 'DATABASE_MODE', 'sqlite') != 'mongodb':
            self.stdout.write(self.style.ERROR('DATABASE_MODE is not set to mongodb'))
            return
        
        from accounts.mongo_models import UserProfile
        
        self.stdout.write(self.style.SUCCESS('\n=== Create MongoDB Superuser ===\n'))
        
        # Get username
        username = options.get('username')
        while not username:
            username = input('Username: ').strip()
            if not username:
                self.stdout.write(self.style.ERROR('Username cannot be empty'))
        
        # Check if user exists
        if UserProfile.objects.filter(username=username).first():
            self.stdout.write(self.style.ERROR(f'User "{username}" already exists'))
            return
        
        # Get email
        email = options.get('email')
        while not email:
            email = input('Email: ').strip()
            if not email:
                self.stdout.write(self.style.ERROR('Email cannot be empty'))
        
        # Check if email exists
        if UserProfile.objects.filter(email=email).first():
            self.stdout.write(self.style.ERROR(f'Email "{email}" already exists'))
            return
        
        # Get password
        password = options.get('password')
        while not password:
            password = getpass.getpass('Password: ')
            if not password:
                self.stdout.write(self.style.ERROR('Password cannot be empty'))
            else:
                password2 = getpass.getpass('Password (again): ')
                if password != password2:
                    self.stdout.write(self.style.ERROR('Passwords do not match'))
                    password = None
        
        try:
            # Create superuser
            user = UserProfile(
                username=username,
                email=email,
                is_staff=True,
                is_superuser=True,
                is_active=True,
                role='admin',
                credits=1000  # Give admin some credits for testing
            )
            user.set_password(password)
            user.save()
            
            self.stdout.write(self.style.SUCCESS(f'\n✅ Superuser "{username}" created successfully!'))
            self.stdout.write(f'📧 Email: {email}')
            self.stdout.write(f'👤 Role: admin')
            self.stdout.write(f'💳 Credits: 1000')
            self.stdout.write(f'\nYou can now login at: http://127.0.0.1:8000/accounts/login/\n')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Error creating superuser: {e}\n'))
