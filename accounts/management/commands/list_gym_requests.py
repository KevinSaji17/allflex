"""
Management command to list pending gym owner requests
Usage: python manage.py list_gym_requests [--status pending|approved|rejected]
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from gyms.models import GymOwnerRequest
from django.utils import timezone


class Command(BaseCommand):
    help = 'List gym owner requests'

    def add_arguments(self, parser):
        parser.add_argument(
            '--status',
            type=str,
            choices=['pending', 'approved', 'rejected', 'all'],
            default='pending',
            help='Filter by request status (default: pending)',
        )

    def handle(self, *args, **options):
        status_filter = options['status']
        
        # Get requests
        if status_filter == 'all':
            requests = GymOwnerRequest.objects.all()
        else:
            requests = GymOwnerRequest.objects.filter(status=status_filter)
        
        if not requests.exists():
            self.stdout.write(self.style.WARNING(f'No {status_filter} gym owner requests found.'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'\n{status_filter.upper()} GYM OWNER REQUESTS'))
        self.stdout.write('=' * 80)
        
        for idx, req in enumerate(requests, 1):
            self.stdout.write(f'\n{idx}. {req.gym_name}')
            self.stdout.write('-' * 80)
            self.stdout.write(f'   Owner: {req.owner_name} (@{req.username})')
            self.stdout.write(f'   User ID: {req.user_id}')
            self.stdout.write(f'   Email: {req.email}')
            self.stdout.write(f'   Phone: {req.contact_number}')
            self.stdout.write(f'   Location: {req.gym_address}')
            self.stdout.write(f'   Status: {req.status.upper()}')
            self.stdout.write(f'   Suggested Tier: Tier {req.suggested_tier or req.calculate_tier_score()}')
            self.stdout.write(f'   Facilities: {len(req.get_facilities_list())} ({", ".join(req.get_facilities_list()[:5])}{"..." if len(req.get_facilities_list()) > 5 else ""})')
            self.stdout.write(f'   Years in Business: {req.years_in_business}')
            self.stdout.write(f'   Total Members: {req.total_members}')
            self.stdout.write(f'   Submitted: {req.created_at.strftime("%Y-%m-%d %H:%M")}')
            if req.reviewed_at:
                self.stdout.write(f'   Reviewed: {req.reviewed_at.strftime("%Y-%m-%d %H:%M")}')
            if req.admin_notes:
                self.stdout.write(f'   Admin Notes: {req.admin_notes}')
        
        self.stdout.write('')
        self.stdout.write('=' * 80)
        self.stdout.write(self.style.SUCCESS(f'Total: {requests.count()} request(s)'))
        self.stdout.write('')
        
        # Show action hint
        if status_filter == 'pending':
            self.stdout.write(self.style.WARNING('\nTo approve requests, use the Django admin panel at /admin/'))
            self.stdout.write('Or promote users manually with: python manage.py promote_gym_owner <username>')
