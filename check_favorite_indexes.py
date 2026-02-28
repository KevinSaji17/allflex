#!/usr/bin/env python
"""
Simple script to drop old unique index and show current state
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from accounts.db_utils import is_mongodb

if not is_mongodb():
    print("Not using MongoDB, nothing to do")
    sys.exit(0)

from accounts.mongo_models import FavoriteGym
import pymongo

print("=" * 60)
print("FavoriteGym Collection Info")
print("=" * 60)

try:
    # Get collection
    collection = FavoriteGym._get_collection()
    
    print("\nCurrent indexes:")
    for idx in collection.list_indexes():
        idx_name = idx.get('name', 'unknown')
        idx_key = idx.get('key', {})
        is_unique = idx.get('unique', False)
        print(f"  - {idx_name}: {dict(idx_key)}{' (UNIQUE)' if is_unique else ''}")
    
    # Try to drop the problematic index
    try:
        collection.drop_index('user_1_gym_1')
        print("\n✓ Dropped index: user_1_gym_1")
    except pymongo.errors.OperationFailure as e:
        if 'index not found' in str(e).lower():
            print("\n⚠ Index 'user_1_gym_1' does not exist (already dropped or never created)")
        else:
            print(f"\n✗ Error dropping index: {e}")
    
    print("\nIndexes after cleanup:")
    for idx in collection.list_indexes():
        idx_name = idx.get('name', 'unknown')
        idx_key = idx.get('key', {})
        is_unique = idx.get('unique', False)
        print(f"  - {idx_name}: {dict(idx_key)}{' (UNIQUE)' if is_unique else ''}")
    
    print("\nCurrent favorite gyms:")
    favorites = FavoriteGym.objects()
    print(f"  Total: {favorites.count()}")
    for fav in favorites[:5]:
        gym_display = fav.gym.name if fav.gym else fav.gym_name
        print(f"  - {fav.user.username}: {gym_display}")
    
    print("\n" + "=" * 60)
    print("✓ Done!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
