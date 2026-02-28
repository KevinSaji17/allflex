#!/usr/bin/env python
"""
Drop the old unique index on favorite_gyms collection
This index was causing duplicate key errors for AI gyms
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

from mongoengine import connect
from django.conf import settings
import pymongo
import os

print("=" * 60)
print("Dropping Old Unique Index from favorite_gyms")
print("=" * 60)

# Get MongoDB settings from env
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'allflex_db')
MONGO_DB_USER = os.getenv('MONGO_DB_USER', '')
MONGO_DB_PASSWORD = os.getenv('MONGO_DB_PASSWORD', '')
MONGO_DB_HOST = os.getenv('MONGO_DB_HOST', '')

# Build connection string
if MONGO_DB_USER and MONGO_DB_PASSWORD and MONGO_DB_HOST:
    MONGODB_CONNECTION_STRING = (
        f"mongodb+srv://{MONGO_DB_USER}:{MONGO_DB_PASSWORD}@{MONGO_DB_HOST}/"
        f"{MONGO_DB_NAME}?retryWrites=true&w=majority"
    )
else:
    MONGODB_CONNECTION_STRING = f"mongodb://localhost:27017/{MONGO_DB_NAME}"

# Connect to MongoDB
client = pymongo.MongoClient(MONGODB_CONNECTION_STRING, serverSelectionTimeoutMS=5000)
db = client[MONGO_DB_NAME]
collection = db['favorite_gyms']

print("\nCurrent indexes:")
try:
    for idx in collection.list_indexes():
        print(f"  - {idx['name']}: {idx.get('key')}")
except Exception as e:
    print(f"Error listing indexes: {e}")
    sys.exit(1)

# Try to drop the old unique index
try:
    collection.drop_index('user_1_gym_1')
    print("\n✓ Dropped index: user_1_gym_1")
except Exception as e:
    print(f"\n⚠ Could not drop index user_1_gym_1: {e}")

print("\nIndexes after cleanup:")
for idx in collection.list_indexes():
    print(f"  - {idx['name']}: {idx.get('key')}")

print("\n" + "=" * 60)
print("✓ Index cleanup complete!")
print("=" * 60)
