import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from gyms.models import Gym

print("\n" + "="*70)
print("CHECKING GYMS FOR BADGE STATUS")
print("="*70)

gyms = Gym.objects.all()
print(f"\nTotal Gyms: {gyms.count()}")

for gym in gyms:
    print(f"\nGym: {gym.name}")
    print(f"  Status: {gym.status}")
    print(f"  Is Active: {gym.is_active}")
    print(f"  Is Verified Partner: {gym.is_verified_partner}")
    print(f"  ID: {gym.id}")

print("\n" + "="*70)
print("CHECKING 'Gold's Gym Central' SPECIFICALLY")
print("="*70)

golds = Gym.objects.filter(name__icontains="Gold").first()
if golds:
    print(f"\nFound: {golds.name}")
    print(f"  is_verified_partner = {golds.is_verified_partner}")
    print(f"  Type: {type(golds.is_verified_partner)}")
else:
    print("\n❌ No gym with 'Gold' in name found")

print("\n" + "="*70)
