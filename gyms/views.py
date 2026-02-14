from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Gym, Booking
from django.db.models import Sum
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django import forms

# Create your views here.

@login_required
def gym_dashboard(request):
    # Only gym owners can access
    if request.user.role != 'gym_owner':
        return redirect('home')

    # Gyms owned by the logged-in user
    owned_gyms = Gym.objects.filter(owner=request.user)

    bookings = Booking.objects.filter(gym__in=owned_gyms).order_by('-timestamp')
    total_bookings = bookings.count()
    total_wallet_balance = owned_gyms.aggregate(total_balance=Sum('wallet_balance'))['total_balance'] or 0.00

    context = {
        'owned_gyms': owned_gyms,
        'bookings': bookings,
        'total_bookings': total_bookings,
        'total_wallet_balance': total_wallet_balance,
    }
    return render(request, 'gyms/dashboard.html', context)


def gym_browse(request):
    gyms = Gym.objects.filter(status='approved', is_active=True).order_by('name')
    return render(request, 'gyms/browse.html', {'gyms': gyms})


def gym_detail(request, gym_id: int):
    gym = get_object_or_404(Gym, id=gym_id, status='approved', is_active=True)
    return render(request, 'gyms/detail.html', {'gym': gym})


class GymSubmitForm(forms.ModelForm):
    class Meta:
        model = Gym
        fields = ['name', 'description', 'location', 'tier', 'capacity', 'logo']


@login_required
@require_http_methods(["GET", "POST"])
def gym_submit(request):
    if request.user.role != 'gym_owner':
        messages.error(request, 'Only gym owners can list a business.')
        return redirect('home')

    if request.method == 'POST':
        form = GymSubmitForm(request.POST, request.FILES)
        if form.is_valid():
            gym = form.save(commit=False)
            gym.owner = request.user
            gym.status = 'pending'
            gym.is_active = False
            gym.save()
            messages.success(request, 'Gym submitted. It will be reviewed by admin.')
            return redirect('gym_dashboard')
    else:
        form = GymSubmitForm()

    return render(request, 'gyms/submit.html', {'form': form})
