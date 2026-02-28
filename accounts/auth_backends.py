"""
Custom Authentication Backend for MongoDB (MongoEngine)
This backend allows Django authentication to work with MongoDB users
"""

from django.contrib.auth.backends import BaseBackend, ModelBackend as DjangoModelBackend
from django.conf import settings
from accounts.mongo_models import UserProfile as MongoUserProfile


class SafeModelBackend(DjangoModelBackend):
    """
    Extended ModelBackend that safely handles MongoDB ObjectIds
    Returns None for non-integer user IDs instead of raising ValidationError
    """
    
    def get_user(self, user_id):
        """
        Get user by ID, but safely handle MongoDB ObjectIds
        """
        # If user_id is a string that looks like MongoDB ObjectId (24 hex chars)
        # return None instead of trying to convert to integer
        if isinstance(user_id, str):
            if len(user_id) == 24 and all(c in '0123456789abcdef' for c in user_id.lower()):
                # This is a MongoDB ObjectId, not a SQL integer ID
                return None
        
        # Try to convert to integer
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return None
        
        # Let parent class handle SQL lookup
        return super().get_user(user_id)


class MongoEngineAuthBackend(BaseBackend):
    """
    Custom authentication backend for MongoEngine UserProfile
    Compatible with Django's authentication system
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user against MongoDB
        Args:
            request: HTTP request object
            username: Username or email
            password: Plain text password
        Returns:
            MongoUserProfile instance if authenticated, None otherwise
        """
        if username is None or password is None:
            return None
        
        try:
            # Try to find user by username or email
            try:
                user = MongoUserProfile.objects.get(username=username)
            except MongoUserProfile.DoesNotExist:
                try:
                    user = MongoUserProfile.objects.get(email=username)
                except MongoUserProfile.DoesNotExist:
                    return None
            
            # Check if user is active
            if not user.is_active:
                return None
            
            # Verify password
            if user.check_password(password):
                # Update last login
                from datetime import datetime
                user.last_login = datetime.utcnow()
                user.save()
                return user
            
            return None
            
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
    
    def get_user(self, user_id):
        """
        Get user by ID (MongoDB ObjectId)
        Required by Django authentication system
        """
        try:
            from bson import ObjectId
            # Convert string ID to ObjectId if needed
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            user = MongoUserProfile.objects.get(id=user_id)
            return user if user.is_active else None
        except (MongoUserProfile.DoesNotExist, Exception) as e:
            return None
    
    def has_perm(self, user_obj, perm, obj=None):
        """Check if user has specific permission"""
        if user_obj.is_superuser:
            return True
        return False
    
    def has_module_perms(self, user_obj, app_label):
        """Check if user has permissions to view app"""
        if user_obj.is_superuser or user_obj.is_staff:
            return True
        return False


class MongoUserWrapper:
    """
    Wrapper to make MongoEngine User compatible with Django sessions
    Django sessions require specific attributes
    """
    
    def __init__(self, mongo_user):
        self._user = mongo_user
    
    def __getattr__(self, name):
        return getattr(self._user, name)
    
    @property
    def pk(self):
        """Return primary key as string (MongoDB ObjectId)"""
        return str(self._user.id)
    
    @property
    def id(self):
        """Return ID as string"""
        return str(self._user.id)
    
    def get_username(self):
        return self._user.username
    
    def check_password(self, raw_password):
        return self._user.check_password(raw_password)
    
    def set_password(self, raw_password):
        return self._user.set_password(raw_password)
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def save(self):
        return self._user.save()
