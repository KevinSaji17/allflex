"""
Management command to promote MongoDB users to gym owners
Usage: python manage.py promote_gym_owner <username>
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


class Command(BaseCommand):
    help = 'Promote a user to gym owner role (MongoDB only)'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user to promote')
        parser.add_argument(
            '--demote',
            action='store_true',
            help='Demote user back to regular user role',
        )

    def handle(self, *args, **options):
        if settings.DATABASE_MODE != 'mongodb':
            raise CommandError('This command only works with MongoDB. Set DATABASE_MODE=mongodb in settings.')
        
        from accounts.mongo_models import UserProfile
        
        username = options['username']
        demote = options.get('demote', False)
        
        # Find user
        user = UserProfile.objects(username=username).first()
        if not user:
            raise CommandError(f'User "{username}" not found.')
        
        # Update role
        old_role = user.role
        new_role = 'user' if demote else 'gym_owner'
        
        if old_role == new_role:
            self.stdout.write(self.style.WARNING(f'User "{username}" is already a {new_role}.'))
            return
        
        user.role = new_role
        user.save()
        
        if demote:
            self.stdout.write(self.style.SUCCESS(
                f'Successfully demoted user "{username}" from {old_role} to {new_role}.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'Successfully promoted user "{username}" from {old_role} to {new_role}.'
            ))
        
        # Display user info
        self.stdout.write('')
        self.stdout.write('User Details:')
        self.stdout.write(f'  Username: {user.username}')
        self.stdout.write(f'  Email: {user.email}')
        self.stdout.write(f'  Role: {user.role}')
        self.stdout.write(f'  Plan: {user.plan}')
        self.stdout.write(f'  Credits: {user.credits}')
        self.stdout.write(f'  Active: {user.is_active}')
