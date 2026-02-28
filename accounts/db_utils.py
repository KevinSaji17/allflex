"""
Database abstraction layer for AllFlex
Supports both MongoDB (MongoEngine) and Django ORM (SQLite)
"""

from django.conf import settings


def get_database_mode():
    """Get current database mode from settings"""
    return getattr(settings, 'DATABASE_MODE', 'sqlite')


def is_mongodb():
    """Check if using MongoDB"""
    return get_database_mode() == 'mongodb'


def get_user_model():
    """Get appropriate User model based on database mode"""
    if is_mongodb():
        from accounts.mongo_models import UserProfile
        return UserProfile
    else:
        from accounts.models import UserProfile
        return UserProfile


def get_gym_model():
    """Get appropriate Gym model based on database mode"""
    if is_mongodb():
        from accounts.mongo_models import Gym
        return Gym
    else:
        from gyms.models import Gym
        return Gym


def get_booking_model():
    """Get appropriate Booking model based on database mode"""
    if is_mongodb():
        from accounts.mongo_models import Booking
        return Booking
    else:
        from gyms.models import Booking
        return Booking


def get_credit_pack_model():
    """Get appropriate CreditPack model based on database mode"""
    if is_mongodb():
        from accounts.mongo_models import CreditPack
        return CreditPack
    else:
        from users.models import CreditPack
        return CreditPack


def get_credit_transaction_model():
    """Get appropriate CreditTransaction model based on database mode"""
    if is_mongodb():
        from accounts.mongo_models import CreditTransaction
        return CreditTransaction
    else:
        from users.models import CreditTransaction
        return CreditTransaction


def get_gym_booking_model():
    """Get appropriate GymBooking model based on database mode"""
    if is_mongodb():
        from accounts.mongo_models import GymBooking
        return GymBooking
    else:
        from users.models import GymBooking
        return GymBooking


def get_rating_model():
    """Get appropriate Rating model based on database mode"""
    if is_mongodb():
        from accounts.mongo_models import Rating
        return Rating
    else:
        from gyms.models import Rating
        return Rating


def get_payout_request_model():
    """Get appropriate PayoutRequest model based on database mode"""
    if is_mongodb():
        from accounts.mongo_models import PayoutRequest
        return PayoutRequest
    else:
        from gyms.models import PayoutRequest
        return PayoutRequest


def get_user_credit_balance_model():
    """Get appropriate UserCreditBalance model based on database mode"""
    if is_mongodb():
        from accounts.mongo_models import UserCreditBalance
        return UserCreditBalance
    else:
        from users.models import UserCreditBalance
        return UserCreditBalance


def create_user(username, email, password, **extra_fields):
    """
    Create user in appropriate database
    Returns user instance
    """
    User = get_user_model()
    
    if is_mongodb():
        # MongoEngine user creation
        user = User(
            username=username,
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save()
        return user
    else:
        # Django ORM user creation
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            **extra_fields
        )
        return user


def get_user_by_username(username):
    """Get user by username"""
    User = get_user_model()
    
    try:
        if is_mongodb():
            return User.objects.get(username=username)
        else:
            return User.objects.get(username=username)
    except User.DoesNotExist:
        return None


def get_user_by_id(user_id):
    """Get user by ID (handles both int and ObjectId)"""
    User = get_user_model()
    
    try:
        if is_mongodb():
            from bson import ObjectId
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            return User.objects.get(id=user_id)
        else:
            return User.objects.get(pk=user_id)
    except (User.DoesNotExist, Exception):
        return None


def get_favorite_gym_model():
    """Get appropriate FavoriteGym model based on database mode"""
    if is_mongodb():
        from accounts.mongo_models import FavoriteGym
        return FavoriteGym
    else:
        from users.models import FavoriteGym
        return FavoriteGym


def get_user_fitness_profile_model():
    """Get appropriate UserFitnessProfile model based on database mode"""
    if is_mongodb():
        from accounts.mongo_models import UserFitnessProfile
        return UserFitnessProfile
    else:
        from users.models import UserFitnessProfile
        return UserFitnessProfile
