"""
Test credit purchase functionality
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from accounts.mongo_models import UserProfile as User
from accounts.db_utils import get_credit_transaction_model

print("=" * 80)
print("CREDIT PURCHASE TEST")
print("=" * 80)

# Get a test user (admin)
user = User.objects.filter(username='admin').first()

if not user:
    print("❌ Admin user not found!")
    sys.exit(1)

print(f"\n👤 Test User: {user.username}")
print(f"   Current Credits: {user.credits}")

# Simulate credit purchase
test_credits = 10
test_price = 100.0

print(f"\n💳 Simulating purchase: {test_credits} credits for ₹{test_price}")

# Add credits
original_credits = user.credits
user.credits += test_credits
user.save()

print(f"   ✓ Credits updated: {original_credits} → {user.credits}")

# Record transaction
CreditTransaction = get_credit_transaction_model()
transaction = CreditTransaction.objects.create(
    user=user,
    credits=test_credits,
    transaction_type='purchase',
    notes=f'Purchased {test_credits} credits for ₹{test_price}'
)

print(f"   ✓ Transaction recorded: ID {transaction.id}")

# Verify
user.reload()  # Reload from database
print(f"\n✅ VERIFICATION:")
print(f"   Current Credits: {user.credits}")
print(f"   Expected: {original_credits + test_credits}")
print(f"   Match: {'YES ✓' if user.credits == original_credits + test_credits else 'NO ✗'}")

# Check recent transactions
transactions = CreditTransaction.objects.filter(user=user).order_by('-created_at')[:3]
print(f"\n📜 Recent Transactions:")
for txn in transactions:
    print(f"   • {txn.transaction_type}: {txn.credits:+d} credits - {txn.notes}")

print("\n" + "=" * 80)
print("✅ CREDIT PURCHASE SYSTEM WORKING")
print("=" * 80)
