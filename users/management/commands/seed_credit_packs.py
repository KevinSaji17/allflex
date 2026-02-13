from django.core.management.base import BaseCommand
from users.models import CreditPack

class Command(BaseCommand):
    help = 'Seed the default credit packs for ALLFLEX'

    def handle(self, *args, **options):
        packs = [
            {'name': 'Starter', 'credits': 25, 'price': 499, 'is_best_value': False},
            {'name': 'Pro Saver', 'credits': 50, 'price': 949, 'is_best_value': False},
            {'name': 'Power Pack', 'credits': 80, 'price': 1399, 'is_best_value': False},
            {'name': 'Ultra Value', 'credits': 120, 'price': 1799, 'is_best_value': True},
        ]
        for pack in packs:
            obj, created = CreditPack.objects.get_or_create(
                name=pack['name'],
                defaults={
                    'credits': pack['credits'],
                    'price': pack['price'],
                    'is_best_value': pack['is_best_value'],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created pack: {obj.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Pack already exists: {obj.name}"))
        self.stdout.write(self.style.SUCCESS('Seeding complete.')) 