from accounts.models import UserProfile

def user_profile_context(request):
    context = {}
    if request.user.is_authenticated:
        # Since UserProfile is the custom user model, request.user IS the profile
        context['user_profile'] = request.user
    return context