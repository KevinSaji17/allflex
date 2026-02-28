"""
Custom admin views for MongoDB Gym management
"""
from django.contrib import admin
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views import View
from accounts.db_utils import get_gym_model, is_mongodb
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import path


@staff_member_required
def mongodb_gyms_view(request):
    """
    Custom admin view to display and manage MongoDB gyms
    """
    if not is_mongodb():
        messages.warning(request, "Gym management only available in MongoDB mode")
        return redirect('/admin/')
    
    Gym = get_gym_model()
    
    # Get all gyms
    all_gyms = list(Gym.objects.all())
    
    # Filter by status if provided
    status_filter = request.GET.get('status', '')
    if status_filter:
        gyms = [g for g in all_gyms if g.status == status_filter]
    else:
        gyms = all_gyms
    
    # Calculate stats  
    total_gyms = len(all_gyms)
    approved_gyms = len([g for g in all_gyms if g.status == 'approved'])
    pending_gyms = len([g for g in all_gyms if g.status == 'pending'])
    verified_partners = len([g for g in all_gyms if g.is_verified_partner])
    
    context = {
        'gyms': gyms,
        'total_gyms': total_gyms,
        'approved_gyms': approved_gyms,
        'pending_gyms': pending_gyms,
        'verified_partners': verified_partners,
        'status_filter': status_filter,
        'title': 'Manage Gyms (MongoDB)',
        'site_title': 'ALLFLEX Administration',
        'site_header': 'ALLFLEX Administration',
    }
    
    return render(request, 'admin/gyms/mongodb_gyms.html', context)


@staff_member_required
def mongodb_gym_edit(request, gym_id):
    """
    Edit a MongoDB gym
    """
    if not is_mongodb():
        messages.error(request, "Gym editing only available in MongoDB mode")
        return redirect('/admin/')
    
    Gym = get_gym_model()
    gym = Gym.objects(id=gym_id).first()
    
    if not gym:
        messages.error(request, "Gym not found")
        return redirect('/admin/gyms/mongodb-gyms/')
    
    if request.method == 'POST':
        # Update gym fields
        gym.name = request.POST.get('name', gym.name)
        gym.description = request.POST.get('description', gym.description)
        gym.location = request.POST.get('location', gym.location)
        gym.tier = int(request.POST.get('tier', gym.tier))
        gym.capacity = int(request.POST.get('capacity', gym.capacity))
        gym.status = request.POST.get('status', gym.status)
        gym.is_active = request.POST.get('is_active') == 'on'
        gym.is_verified_partner = request.POST.get('is_verified_partner') == 'on'
        gym.save()
        
        messages.success(request, f"Gym '{gym.name}' updated successfully")
        return redirect('/admin/gyms/mongodb-gyms/')
    
    context = {
        'gym': gym,
        'title': f'Edit Gym: {gym.name}',
        'site_title': 'ALLFLEX Administration',
        'site_header': 'ALLFLEX Administration',
    }
    
    return render(request, 'admin/gyms/mongodb_gym_edit.html', context)


@staff_member_required  
def mongodb_gym_delete(request, gym_id):
    """
    Delete a MongoDB gym
    """
    if not is_mongodb():
        messages.error(request, "Gym deletion only available in MongoDB mode")
        return redirect('/admin/')
    
    Gym = get_gym_model()
    gym = Gym.objects(id=gym_id).first()
    
    if not gym:
        messages.error(request, "Gym not found")
        return redirect('/admin/gyms/mongodb-gyms/')
    
    gym_name = gym.name
    gym.delete()
    messages.success(request, f"Gym '{gym_name}' deleted successfully")
    
    return redirect('/admin/gyms/mongodb-gyms/')
