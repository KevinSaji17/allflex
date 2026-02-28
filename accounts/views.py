from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import generic
from .forms import get_signup_form
from django.http import HttpResponseRedirect
from .db_utils import is_mongodb, create_user, get_user_model
from django.contrib.auth import views as auth_views
from django.contrib.auth import login as auth_login, BACKEND_SESSION_KEY, HASH_SESSION_KEY, SESSION_KEY
from django.contrib.auth.signals import user_logged_in


def custom_login(request, user, backend=None):
    """
    Custom login function for MongoDB users that bypasses Django's _meta.pk access
    This replaces django.contrib.auth.login() for MongoEngine users
    """
    session_auth_hash = ''
    if user is None:
        user = request.user
    if hasattr(user, 'get_session_auth_hash'):
        session_auth_hash = user.get_session_auth_hash()

    if SESSION_KEY in request.session:
        if str(user.pk) != request.session.get(SESSION_KEY):
            # To avoid reusing another user's session, create a new, empty session
            request.session.flush()
    else:
        request.session.cycle_key()

    if backend is None:
        from django.contrib.auth import _get_backends
        backends = _get_backends(return_tuples=True)
        if len(backends) == 1:
            _, backend = backends[0]
        else:
            # Try to get the backend from the user object
            backend = getattr(user, 'backend', None)
            if backend is None:
                backend = 'accounts.auth_backends.MongoEngineAuthBackend'

    # Store user ID as string directly (bypasses _meta.pk.value_to_string)
    request.session[SESSION_KEY] = str(user.pk)
    request.session[BACKEND_SESSION_KEY] = backend
    request.session[HASH_SESSION_KEY] = session_auth_hash
    if hasattr(request, 'user'):
        request.user = user
    from django.middleware.csrf import rotate_token
    rotate_token(request)
    user_logged_in.send(sender=user.__class__, request=request, user=user)


class CustomLoginView(auth_views.LoginView):
    """Custom LoginView that uses our custom_login function for MongoDB users"""
    template_name = 'registration/login.html'
    
    def form_valid(self, form):
        """Security check complete. Log the user in using custom login."""
        user = form.get_user()
        if is_mongodb():
            # Use our custom login function for MongoDB users
            custom_login(self.request, user, backend='accounts.auth_backends.MongoEngineAuthBackend')
        else:
            # Use Django's default login for SQLite users
            auth_login(self.request, user)
        return HttpResponseRedirect(self.get_success_url())

# Create your views here.

class SignUpView(generic.FormView):
    """
    Dynamic SignUpView that works with both SQLite and MongoDB
    Uses FormView instead of CreateView for MongoDB compatibility
    Role is determined by which submit button is clicked
    """
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'
    
    def get_form_class(self):
        """Return appropriate form class based on database mode"""
        return get_signup_form()

    def form_valid(self, form):
        # Determine role from which button was clicked
        signup_type = self.request.POST.get('signup_type', 'user')
        
        # Validate signup_type (security check)
        if signup_type not in ['user', 'gym_owner']:
            signup_type = 'user'  # Default to user if invalid
        
        if is_mongodb():
            # MongoDB: Create user manually using MongoEngine
            username = form.cleaned_data['username']
            email = form.cleaned_data.get('email', '')
            password = form.cleaned_data['password1']
            
            user = create_user(
                username=username,
                email=email,
                password=password,
                role=signup_type,  # Set role based on button clicked
                credits=0,  # Users start with 0 credits, must purchase
                is_active=True
            )
            return HttpResponseRedirect(self.get_success_url())
        else:
            # SQLite: Use ModelForm's save method
            user = form.save(commit=False)
            user.role = signup_type  # Set role based on button clicked
            user.credits = 0  # Users start with 0 credits, must purchase
            user.save()
            return HttpResponseRedirect(self.get_success_url())

def role_based_redirect(request):
    if request.user.is_authenticated:
        # Since UserProfile is the custom user model, access role directly
        if request.user.role == 'admin':
            return HttpResponseRedirect(reverse('admin_dashboard'))
        elif request.user.role == 'gym_owner':  # CORRECT role name
            return HttpResponseRedirect(reverse('gym_dashboard'))
        else:
            # Regular user is redirected to their dashboard
            return HttpResponseRedirect(reverse('user_dashboard'))  # CHANGED from 'home' to 'user_dashboard'
    # Non-authenticated users go to home
    return HttpResponseRedirect(reverse('home'))
