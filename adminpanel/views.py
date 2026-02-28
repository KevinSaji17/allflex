from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.db_utils import get_user_model, get_gym_model, is_mongodb
from django.contrib import messages

# Create your views here.

@login_required
def admin_dashboard(request):
    # Basic check to ensure only admins can access
    if request.user.role != 'admin':
        return redirect('home')

    UserProfile = get_user_model()
    Gym = get_gym_model()
    
    if is_mongodb():
        total_users = UserProfile.objects.count()
        total_gyms = Gym.objects.count()
        pending_gyms = Gym.objects(status='pending')
        all_users = UserProfile.objects.all()
        all_gyms = Gym.objects.all()
    else:
        total_users = UserProfile.objects.count()
        total_gyms = Gym.objects.count()
        pending_gyms = Gym.objects.filter(status='pending')
        all_users = UserProfile.objects.all()
        all_gyms = Gym.objects.all()
    
    context = {
        'total_users': total_users,
        'total_gyms': total_gyms,
        'pending_gyms': pending_gyms,
        'pending_gyms_count': pending_gyms.count(),
        'all_users': all_users,
        'all_gyms': all_gyms,
    }
    return render(request, 'adminpanel/dashboard.html', context)

@login_required
def approve_gym(request, gym_id):
    if request.user.role != 'admin':
        return redirect('home')
    
    Gym = get_gym_model()
    
    if is_mongodb():
        try:
            gym = Gym.objects.get(id=gym_id)
        except Gym.DoesNotExist:
            from django.http import Http404
            raise Http404("Gym not found")
    else:
        gym = get_object_or_404(Gym, id=gym_id)
    
    gym.status = 'approved'
    gym.is_active = True
    gym.save()
    messages.success(request, f'Gym "{gym.name}" has been approved!')
    return redirect('admin_dashboard')

@login_required
def reject_gym(request, gym_id):
    if request.user.role != 'admin':
        return redirect('home')
    
    Gym = get_gym_model()
    
    if is_mongodb():
        try:
            gym = Gym.objects.get(id=gym_id)
        except Gym.DoesNotExist:
            from django.http import Http404
            raise Http404("Gym not found")
    else:
        gym = get_object_or_404(Gym, id=gym_id)
    
    gym.status = 'rejected'
    gym.is_active = False
    gym.save()
    messages.success(request, f'Gym "{gym.name}" has been rejected.')
    return redirect('admin_dashboard')
