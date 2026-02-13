from django.core.management.base import BaseCommand
from accounts.models import UserProfile

class Command(BaseCommand):
    help = 'Setup all users for testing'

    def handle(self, *args, **options):
        # Delete existing demo users
        UserProfile.objects.filter(username__in=['admin', 'gymowner', 'user']).delete()
        
        # Create Admin User
        admin_user = UserProfile.objects.create_user(
            username='admin',
            email='admin@allflex.com',
            password='admin123',
            role='admin'
        )
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        self.stdout.write(self.style.SUCCESS('Admin user created: admin / admin123'))

        # Create Gym Owner User  
        gym_owner = UserProfile.objects.create_user(
            username='gymowner',
            email='gym@allflex.com',
            password='gym123',
            role='gym_owner'
        )
        self.stdout.write(self.style.SUCCESS('Gym Owner user created: gymowner / gym123'))

        # Create Regular User
        regular_user = UserProfile.objects.create_user(
            username='user',
            email='user@allflex.com',
            password='user123',
            role='user'
        )
        self.stdout.write(self.style.SUCCESS('Regular user created: user / user123'))

        self.stdout.write(self.style.SUCCESS('All users created successfully!'))
