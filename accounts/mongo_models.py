"""
MongoEngine models for AllFlex - MongoDB version
These models replace Django ORM models when DATABASE_MODE=mongodb
"""

from mongoengine import (
    Document, EmbeddedDocument,
    StringField, IntField, FloatField, BooleanField,
    DateTimeField, EmailField, ImageField,
    ReferenceField, ListField, EmbeddedDocumentField,
    PULL, CASCADE, NULLIFY
)
from datetime import datetime, timedelta
from django.conf import settings
import hashlib


class FakePkField:
    """
    Fake primary key field to make MongoEngine models compatible with Django's auth system
    Django's login expects user._meta.pk.value_to_string(user) to work
    """
    def value_to_string(self, obj):
        """Convert the pk value to a string for session storage"""
        return str(obj.id) if obj.id else None


class UserProfile(Document):
    """MongoDB User Profile Model - Django-compatible custom user"""
    
    # Role and Plan choices
    ROLE_CHOICES = ('user', 'gym_owner', 'admin')
    PLAN_CHOICES = ('basic', 'plus', 'pro', 'elite', 'none')
    
    # Authentication fields (Django AbstractUser compatible)
    username = StringField(required=True, unique=True, max_length=150)
    email = EmailField(required=True, max_length=254)
    password = StringField(required=True, max_length=128)
    first_name = StringField(max_length=150, default='')
    last_name = StringField(max_length=150, default='')
    
    # Django permission fields
    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)
    is_superuser = BooleanField(default=False)
    
    # AllFlex custom fields
    role = StringField(choices=ROLE_CHOICES, default='user', max_length=10)
    plan = StringField(choices=PLAN_CHOICES, default='none', max_length=10)
    credits = IntField(default=0, min_value=0)
    streak = IntField(default=0, min_value=0)
    qr_code = StringField(default='')  # Store filename or path
    
    # Timestamps
    date_joined = DateTimeField(default=datetime.utcnow)
    last_login = DateTimeField(null=True)
    
    meta = {
        'collection': 'users',
        'indexes': [
            {'fields': ['username'], 'unique': True},
            {'fields': ['email'], 'unique': True},
            'role',
            'is_active',
            {'fields': ['role', 'is_active']},
        ]
    }
    
    def __str__(self):
        return self.username
    
    # Django compatibility properties
    @property
    def pk(self):
        """Django compatibility - primary key as string"""
        return str(self.id) if self.id else None
    
    def get_username(self):
        """Django compatibility method"""
        return self.username
    
    def check_password(self, raw_password):
        """Check if password matches (Django-compatible)"""
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)
    
    def set_password(self, raw_password):
        """Hash and set password (Django-compatible)"""
        from django.contrib.auth.hashers import make_password
        self.password = make_password(raw_password)
    
    def get_session_auth_hash(self):
        """
        Return an HMAC of the password field for session validation.
        Django uses this to invalidate sessions when password changes.
        """
        from django.utils.crypto import salted_hmac
        from django.conf import settings
        key_salt = "accounts.mongo_models.UserProfile.get_session_auth_hash"
        return salted_hmac(key_salt, self.password, algorithm='sha256').hexdigest()
    
    def has_perm(self, perm, obj=None):
        """Django permission compatibility"""
        return self.is_superuser
    
    def has_module_perms(self, app_label):
        """Django permission compatibility"""
        return self.is_superuser or self.is_staff
    
    def get_role_display(self):
        """Get display name for role"""
        role_map = {'user': 'User', 'gym_owner': 'Gym Owner', 'admin': 'Admin'}
        return role_map.get(self.role, self.role.title())
    
    def get_plan_display(self):
        """Get display name for plan"""
        plan_map = {
            'basic': 'Basic', 'plus': 'Plus', 'pro': 'Pro',
            'elite': 'Elite', 'none': 'None'
        }
        return plan_map.get(self.plan, self.plan.title())
    
    @property
    def is_anonymous(self):
        return False
    
    @property
    def is_authenticated(self):
        return True
    
    def _get_pk_val(self):
        """Django compatibility - get primary key value"""
        return self.pk
    
    def serializable_value(self, field_name):
        """Django compatibility - serialize field values"""
        if field_name == 'pk':
            return self.pk
        return getattr(self, field_name, None)


# CRITICAL: Monkey-patch the UserProfile._meta to add pk attribute for Django auth compatibility
# Django's login() function expects user._meta.pk.value_to_string(user) to work
UserProfile._meta.pk = FakePkField()


class Gym(Document):
    """MongoDB Gym Model"""
    TIER_CHOICES = (1, 2, 3, 4)
    STATUS_CHOICES = ('pending', 'approved', 'rejected')
    
    owner = ReferenceField(UserProfile, required=True, reverse_delete_rule=CASCADE)
    name = StringField(required=True, max_length=255)
    logo = StringField(null=True)  # Store filename or URL
    description = StringField(required=True)
    location = StringField(required=True, max_length=255)
    latitude = FloatField(null=True)  # GPS latitude
    longitude = FloatField(null=True)  # GPS longitude
    tier = IntField(required=True, choices=TIER_CHOICES)
    capacity = IntField(default=20, min_value=1)
    status = StringField(choices=STATUS_CHOICES, default='pending')
    is_active = BooleanField(default=False)
    is_verified_partner = BooleanField(default=True)
    wallet_balance = FloatField(default=0.0, min_value=0.0)
    
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'gyms',
        'indexes': [
            'owner',
            'status',
            'tier',
            {'fields': ['is_active', 'status', 'tier']},
            {'fields': ['location']},  # For geo queries
        ]
    }
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super(Gym, self).save(*args, **kwargs)


class Booking(Document):
    """MongoDB Booking Model"""
    user = ReferenceField(UserProfile, required=True, reverse_delete_rule=CASCADE)
    gym = ReferenceField(Gym, required=True, reverse_delete_rule=CASCADE)
    timestamp = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'bookings',
        'indexes': [
            'user',
            'gym',
            '-timestamp',  # Descending order
            {'fields': ['user', '-timestamp']},
        ]
    }
    
    def __str__(self):
        return f'{self.user.username} booking at {self.gym.name}'


class Rating(Document):
    """MongoDB Rating Model"""
    user = ReferenceField(UserProfile, required=True, reverse_delete_rule=CASCADE)
    gym = ReferenceField(Gym, required=True, reverse_delete_rule=CASCADE)
    stars = IntField(required=True, min_value=1, max_value=5)
    comment = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'ratings',
        'indexes': [
            'user',
            'gym',
            {'fields': ['gym', '-stars']},
            {'fields': ['user', 'gym'], 'unique': True},  # One rating per user per gym
        ]
    }
    
    def __str__(self):
        return f'Rating for {self.gym.name} by {self.user.username}'


class PayoutRequest(Document):
    """MongoDB Payout Request Model"""
    STATUS_CHOICES = ('pending', 'approved', 'rejected')
    
    gym_owner = ReferenceField(UserProfile, required=True, reverse_delete_rule=CASCADE)
    amount = FloatField(required=True, min_value=0.0)
    status = StringField(choices=STATUS_CHOICES, default='pending')
    created_at = DateTimeField(default=datetime.utcnow)
    processed_at = DateTimeField(null=True)
    notes = StringField(default='')
    
    meta = {
        'collection': 'payout_requests',
        'indexes': [
            'gym_owner',
            'status',
            '-created_at',
            {'fields': ['gym_owner', 'status']},
        ]
    }
    
    def __str__(self):
        return f'Payout request from {self.gym_owner.username} for {self.amount}'


class CreditPack(Document):
    """MongoDB Credit Pack Model"""
    TIER_CHOICES = (1, 2, 3, 4)
    
    name = StringField(required=True, max_length=255)
    tier = IntField(choices=TIER_CHOICES, default=1)
    credits = IntField(required=True, min_value=1)
    price = FloatField(required=True, min_value=0.0)
    validity_days = IntField(required=True, min_value=1)
    description = StringField(default='')
    is_active = BooleanField(default=True)
    is_best_value = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'credit_packs',
        'indexes': [
            'tier',
            'is_active',
            {'fields': ['tier', 'price']},
        ]
    }
    
    def __str__(self):
        return f'{self.name} - {self.credits} credits (Tier {self.tier}) - ₹{self.price}'
    
    def price_per_credit(self):
        return round(self.price / self.credits, 2)
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.utcnow()
        return super(CreditPack, self).save(*args, **kwargs)


class UserCreditPack(Document):
    """MongoDB User Credit Pack Model"""
    user = ReferenceField(UserProfile, required=True, reverse_delete_rule=CASCADE)
    credit_pack = ReferenceField(CreditPack, required=True, reverse_delete_rule=NULLIFY)
    remaining_credits = IntField(required=True, min_value=0)
    purchased_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField(required=True)
    is_active = BooleanField(default=True)
    
    meta = {
        'collection': 'user_credit_packs',
        'indexes': [
            'user',
            '-purchased_at',
            {'fields': ['user', 'is_active']},
            {'fields': ['expires_at']},
        ]
    }
    
    def __str__(self):
        return f'{self.user.username} - {self.remaining_credits} credits remaining'
    
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
    
    def deduct_credit(self):
        """Deduct one credit if available and not expired"""
        if self.remaining_credits > 0 and not self.is_expired():
            self.remaining_credits -= 1
            if self.remaining_credits == 0:
                self.is_active = False
            self.save()
            return True
        return False


class CreditTransaction(Document):
    """MongoDB Credit Transaction Model"""
    TRANSACTION_TYPES = ('purchase', 'visit', 'adjustment')
    
    user = ReferenceField(UserProfile, required=True, reverse_delete_rule=CASCADE)
    pack = ReferenceField(CreditPack, null=True, reverse_delete_rule=NULLIFY)
    gym = ReferenceField(Gym, null=True, reverse_delete_rule=NULLIFY)
    credits = IntField(required=True)  # Can be positive or negative
    transaction_type = StringField(choices=TRANSACTION_TYPES, required=True)
    timestamp = DateTimeField(default=datetime.utcnow)
    notes = StringField(default='')
    
    meta = {
        'collection': 'credit_transactions',
        'indexes': [
            'user',
            '-timestamp',
            'transaction_type',
            {'fields': ['user', '-timestamp']},
        ]
    }
    
    def __str__(self):
        return f"{self.user.username} {self.transaction_type} {self.credits} credits"


class GymBooking(Document):
    """MongoDB Gym Booking Model"""
    STATUS_CHOICES = ('booked', 'cancelled', 'checked_in', 'completed')

    user = ReferenceField(UserProfile, required=True, reverse_delete_rule=CASCADE)
    gym = ReferenceField(Gym, null=True, reverse_delete_rule=NULLIFY)  # nullable for AI-sourced gyms
    gym_name = StringField(default='')  # always populated, fallback when gym not in DB
    tier = IntField(default=1, min_value=1, max_value=4)
    credits_charged = IntField(default=0, min_value=0)
    status = StringField(choices=STATUS_CHOICES, default='booked')
    booked_at = DateTimeField(default=datetime.utcnow)
    booking_date = DateTimeField(default=datetime.utcnow)   # the date user wants to visit
    checked_in_at = DateTimeField(null=True)  # Timestamp when user checked in
    checked_out_at = DateTimeField(null=True)  # Timestamp when user checked out
    session_duration_minutes = IntField(null=True)  # Duration in minutes
    check_in_latitude = FloatField(null=True)  # User's GPS location at check-in
    check_in_longitude = FloatField(null=True)  # User's GPS location at check-in
    time_slot = StringField(default='')                      # e.g. "06:00 AM – 07:00 AM"
    notes = StringField(default='')
    otp = StringField(default='', max_length=6)  # 6-digit OTP for gym owner verification
    otp_verified = BooleanField(default=False)  # Track if OTP has been verified
    
    meta = {
        'collection': 'gym_bookings',
        'indexes': [
            'user',
            'gym',
            '-booked_at',
            'status',
            {'fields': ['user', '-booked_at']},
            {'fields': ['gym', 'status', 'booking_date']},
        ]
    }
    
    def __str__(self):
        return f"{self.user.username} booking at {self.gym.name}"


class UserCreditBalance(Document):
    """MongoDB User Credit Balance Model"""
    user = ReferenceField(UserProfile, required=True, unique=True, reverse_delete_rule=CASCADE)
    credits = IntField(default=0, min_value=0)
    last_updated = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'user_credit_balances',
        'indexes': [
            {'fields': ['user'], 'unique': True},
        ]
    }
    
    def __str__(self):
        return f"{self.user.username}: {self.credits} credits"
    
    def save(self, *args, **kwargs):
        self.last_updated = datetime.utcnow()
        return super(UserCreditBalance, self).save(*args, **kwargs)


class FavoriteGym(Document):
    """MongoDB FavoriteGym Model - Track user's favorite gyms"""
    user = ReferenceField(UserProfile, required=True, reverse_delete_rule=CASCADE)
    gym = ReferenceField(Gym, required=False, reverse_delete_rule=CASCADE)  # Optional for AI gyms
    gym_name = StringField(max_length=255, required=False)  # For AI-generated gyms not in DB
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'favorite_gyms',
        'indexes': [
            'user',
            'gym',
            {'fields': ['-created_at']},
        ]
    }
    
    def __str__(self):
        return f"{self.user.username} favorited {self.gym.name}"


class UserFitnessProfile(Document):
    """MongoDB UserFitnessProfile Model - Track user's fitness progress"""
    user = ReferenceField(UserProfile, required=True, unique=True, reverse_delete_rule=CASCADE)
    current_weight = FloatField(null=True)  # Weight in kg
    target_weight = FloatField(null=True)  # Target weight in kg
    height = FloatField(null=True)  # Height in cm
    age = IntField(null=True)
    fitness_goal = StringField(max_length=100, default='')  # E.g., Weight loss, Muscle gain
    total_visits = IntField(default=0, min_value=0)
    total_credits_spent = IntField(default=0, min_value=0)
    joined_date = DateTimeField(default=datetime.utcnow)
    last_updated = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'user_fitness_profiles',
        'indexes': [
            {'fields': ['user'], 'unique': True},
        ]
    }
    
    def __str__(self):
        return f"{self.user.username}'s Fitness Profile"
    
    def bmi(self):
        """Calculate BMI if height and weight are available"""
        if self.height and self.current_weight:
            height_in_meters = float(self.height) / 100
            return round(float(self.current_weight) / (height_in_meters ** 2), 2)
        return None
    
    def save(self, *args, **kwargs):
        self.last_updated = datetime.utcnow()
        return super(UserFitnessProfile, self).save(*args, **kwargs)
