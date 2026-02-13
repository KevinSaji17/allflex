from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Gym, Booking
from django.db.models import Sum

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
