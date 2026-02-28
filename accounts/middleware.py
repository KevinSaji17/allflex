"""
Custom middleware for MongoDB authentication
Handles user retrieval from sessions when using MongoDB
"""

from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.utils.functional import SimpleLazyObject
from .db_utils import is_mongodb


def get_mongodb_user(request):
    """
    Get user from session for MongoDB mode
    Bypasses Django's default integer pk conversion
    """
    if not hasattr(request, '_cached_user'):
        from django.contrib import auth
        
        # Check if we're in MongoDB mode
        if is_mongodb():
            # Get user ID from session (MongoDB ObjectId as string)
            user_id = request.session.get(SESSION_KEY)
            backend_path = request.session.get(BACKEND_SESSION_KEY)
            
            if user_id and backend_path:
                # Import the backend and get user directly
                from django.contrib.auth import load_backend
                backend = load_backend(backend_path)
                user = backend.get_user(user_id)
                if user is None:
                    # If user not found, return AnonymousUser
                    from django.contrib.auth.models import AnonymousUser
                    user = AnonymousUser()
            else:
                # No session, return AnonymousUser
                from django.contrib.auth.models import AnonymousUser
                user = AnonymousUser()
            
            request._cached_user = user
        else:
            # Use Django's default auth for SQLite
            request._cached_user = auth.get_user(request)
    
    return request._cached_user


class MongoAuthenticationMiddleware(AuthenticationMiddleware):
    """
    Custom authentication middleware that handles MongoDB users properly
    Replaces Django's default AuthenticationMiddleware when using MongoDB
    """
    
    def process_request(self, request):
        """Add user to request, handling MongoDB ObjectId properly"""
        if is_mongodb():
            # Use our custom get_mongodb_user function
            request.user = SimpleLazyObject(lambda: get_mongodb_user(request))
        else:
            # Use Django's default for SQLite
            super().process_request(request)
