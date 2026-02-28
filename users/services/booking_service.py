"""
Booking Service Layer
---------------------
Pure utility functions for booking lifecycle management.
All functions are stateless and deal with MongoEngine documents directly.
"""
from datetime import datetime, timedelta
from accounts.db_utils import (
    get_gym_booking_model,
    get_credit_transaction_model,
    is_mongodb,
)

BOOKING_COST = 5  # flat credits per booking


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def validate_booking_date(booking_date: datetime) -> dict:
    """Return {'ok': True} or {'ok': False, 'error': str}."""
    if booking_date.date() < datetime.now().date():
        return {'ok': False, 'error': 'Cannot book a slot in the past.'}
    # Limit to 30 days in advance
    if booking_date.date() > (datetime.now() + timedelta(days=30)).date():
        return {'ok': False, 'error': 'Cannot book more than 30 days in advance.'}
    return {'ok': True}


def check_duplicate_booking(user, gym_name: str, booking_date: datetime) -> bool:
    """
    Return True if user already has an active (non-cancelled) booking
    for the same gym on the same calendar day.
    """
    GymBooking = get_gym_booking_model()
    day_start = booking_date.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)
    if is_mongodb():
        return GymBooking.objects(
            user=user,
            gym_name__iexact=gym_name,
            booking_date__gte=day_start,
            booking_date__lt=day_end,
            status__nin=['cancelled'],
        ).count() > 0
    else:
        return GymBooking.objects.filter(
            user=user,
            gym_name__iexact=gym_name,
            booking_date__gte=day_start,
            booking_date__lt=day_end,
        ).exclude(status='cancelled').exists()


# ---------------------------------------------------------------------------
# Credit helpers
# ---------------------------------------------------------------------------

def deduct_credits(user, amount: int, description: str = '') -> None:
    """Deduct credits from user and persist. Raises ValueError if insufficient."""
    if user.credits < amount:
        raise ValueError(
            f'Not enough credits. Need {amount}, you have {user.credits}.'
        )
    user.credits -= amount
    user.save()


def refund_credits(user, amount: int, description: str = '') -> None:
    """Add credits back to user and persist."""
    user.credits += amount
    user.save()


def log_transaction(user, gym_obj, credits_delta: int, tx_type: str, notes: str = '') -> None:
    """
    Write a CreditTransaction record.
    credits_delta < 0 for spend, > 0 for refund/purchase.
    """
    CreditTransaction = get_credit_transaction_model()
    tx_kwargs = dict(
        user=user,
        credits=credits_delta,
        transaction_type=tx_type,
        notes=notes,
    )
    if gym_obj:
        tx_kwargs['gym'] = gym_obj
    CreditTransaction.objects.create(**tx_kwargs)


# ---------------------------------------------------------------------------
# Streak calculation
# ---------------------------------------------------------------------------

def calculate_streak(user) -> int:
    """
    Calculate the current consecutive-day workout streak for *user*.
    A "streak day" is any calendar day that has at least one booking
    with status != 'cancelled'.
    Returns the number of consecutive days ending today (or yesterday).
    """
    GymBooking = get_gym_booking_model()
    if is_mongodb():
        bookings = GymBooking.objects(
            user=user,
            status__nin=['cancelled'],
        ).only('booking_date').order_by('-booking_date')
    else:
        bookings = (
            GymBooking.objects
            .filter(user=user)
            .exclude(status='cancelled')
            .order_by('-booking_date')
            .values_list('booking_date', flat=True)
        )

    # Collect unique calendar dates (UTC)
    unique_dates = sorted(
        {b.booking_date.date() for b in bookings if b.booking_date},
        reverse=True,
    )

    if not unique_dates:
        return 0

    today = datetime.utcnow().date()
    # Streak can start from today or yesterday (allow for timezone slack)
    if unique_dates[0] < today - timedelta(days=1):
        return 0  # Last workout was more than yesterday — streak broken

    streak = 0
    expected = unique_dates[0]
    for d in unique_dates:
        if d == expected:
            streak += 1
            expected -= timedelta(days=1)
        else:
            break
    return streak


def update_streak(user) -> int:
    """Recalculate and persist the streak on the UserProfile. Returns new value."""
    new_streak = calculate_streak(user)
    if user.streak != new_streak:
        user.streak = new_streak
        user.save()
    return new_streak


# ---------------------------------------------------------------------------
# Dashboard stats
# ---------------------------------------------------------------------------

def get_dashboard_stats(user) -> dict:
    """
    Return aggregated stats for the user dashboard:
      - total_bookings  : all non-cancelled bookings
      - monthly_bookings: bookings in the current calendar month
      - credits_spent   : total credits charged across non-cancelled bookings
      - upcoming        : confirmed bookings from today onward
      - streak          : consecutive-day streak (recalculated live)
      - current_credits : user.credits right now
    """
    GymBooking = get_gym_booking_model()
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = today.replace(day=1)

    if is_mongodb():
        all_bookings = GymBooking.objects(user=user, status__nin=['cancelled'])
        monthly = all_bookings.filter(
            booking_date__gte=month_start,
            booking_date__lt=today + timedelta(days=1),
        )
        upcoming = GymBooking.objects(
            user=user,
            booking_date__gte=today,
            status='booked',
        ).order_by('booking_date')[:5]
    else:
        all_bookings = GymBooking.objects.filter(user=user).exclude(status='cancelled')
        monthly = all_bookings.filter(booking_date__gte=month_start)
        upcoming = (
            GymBooking.objects.filter(user=user, booking_date__gte=today, status='booked')
            .order_by('booking_date')[:5]
        )

    total = all_bookings.count()
    credits_spent = sum(b.credits_charged or 0 for b in all_bookings)
    streak = calculate_streak(user)

    upcoming_list = []
    for b in upcoming:
        bd = b.booking_date
        upcoming_list.append({
            'id': str(b.id),
            'gym_name': b.gym_name or 'Unknown Gym',
            'booking_date': bd.strftime('%Y-%m-%d') if bd else '',
            'booking_date_display': bd.strftime('%d %b %Y') if bd else '',
            'time_slot': b.time_slot or '—',
            'status': b.status,
        })

    return {
        'total_bookings': total,
        'monthly_bookings': monthly.count(),
        'credits_spent': credits_spent,
        'upcoming': upcoming_list,
        'streak': streak,
        'current_credits': user.credits,
    }
