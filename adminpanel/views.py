from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import UserProfile
from gyms.models import Gym
from django.contrib import messages

# Create your views here.

@login_required
def admin_dashboard(request):
    # Basic check to ensure only admins can access
    if request.user.role != 'admin':
        return redirect('home')

    total_users = UserProfile.objects.count()
    total_gyms = Gym.objects.count()
    pending_gyms = Gym.objects.filter(status='pending')
    
    context = {
        'total_users': total_users,
        'total_gyms': total_gyms,
        'pending_gyms': pending_gyms,
        'pending_gyms_count': pending_gyms.count(),
        'all_users': UserProfile.objects.all(),
        'all_gyms': Gym.objects.all(),
    }
    return render(request, 'adminpanel/dashboard.html', context)

@login_required
def approve_gym(request, gym_id):
    if request.user.role != 'admin':
        return redirect('home')
    
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
    
    gym = get_object_or_404(Gym, id=gym_id)
    gym.status = 'rejected'
    gym.is_active = False
    gym.save()
    messages.success(request, f'Gym "{gym.name}" has been rejected.')
    return redirect('admin_dashboard')
