"""
Admin Session Middleware
Handles session conflicts between MongoDB users and SQL admin users
"""

from django.contrib.auth import logout
from django.shortcuts import redirect


class AdminSessionMiddleware:
    """
    Middleware to handle session conflicts when MongoDB users try to access admin
    Clears incompatible sessions when accessing admin panel
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check if accessing admin panel
        if request.path.startswith('/admin/'):
            # Check if user is authenticated
            if request.user.is_authenticated:
                # Check if user ID looks like MongoDB ObjectId (24 hex chars)
                user_id = str(getattr(request.user, 'id', ''))
                if len(user_id) == 24 and all(c in '0123456789abcdef' for c in user_id.lower()):
                    # This is a MongoDB user trying to access admin
                    # Check if they're not a staff/superuser
                    if not (getattr(request.user, 'is_staff', False) and 
                           getattr(request.user, 'is_superuser', False)):
                        # Clear the session and redirect to admin login
                        logout(request)
                        if request.path != '/admin/login/':
                            return redirect('/admin/login/')
        
        response = self.get_response(request)
        return response
