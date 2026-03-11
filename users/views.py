from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import TIER_CREDIT_COSTS
from accounts.db_utils import (
    get_gym_model, is_mongodb, get_user_by_id,
    get_credit_transaction_model, get_favorite_gym_model,
    get_user_fitness_profile_model, get_credit_pack_model,
    get_gym_booking_model
)
from allflex.gym_recommender import get_gyms_by_pincode
from datetime import datetime, timedelta, timezone as dt_timezone
import json
import pytz
from users.services.booking_service import (
    check_duplicate_booking,
    validate_booking_date,
    deduct_credits,
    refund_credits,
    log_transaction,
    update_streak,
    get_dashboard_stats as _get_dashboard_stats,
    BOOKING_COST,
)
from users.gps_utils import (
    haversine_distance,
    is_within_proximity,
    validate_gps_coordinates,
    format_distance,
)
from users.otp_utils import generate_otp, validate_otp

# Credits cost per gym tier (1 booking)
TIER_CREDITS = TIER_CREDIT_COSTS

# Tier labels for display
TIER_LABELS = {1: 'Basic', 2: 'Standard', 3: 'Premium', 4: 'Elite'}


def _assign_gym_tier(info: dict) -> int:
    """
    Auto-assign a tier (1-4) based on Gemini-returned gym attributes.

    Tier 4 – Elite  : rating >= 4.5  AND  3+ amenities
    Tier 3 – Premium: rating >= 4.3  AND  2+ amenities
    Tier 2 – Standard: rating >= 4.0  OR   2+ amenities
    Tier 1 – Basic  : everything else
    """
    try:
        rating = float(str(info.get('rating', '0')).strip())
    except (ValueError, TypeError):
        rating = 0.0

    amenity_count = sum([
        bool(info.get('has_ac')),
        bool(info.get('has_dressing_room')),
        bool(info.get('has_washroom')),
        bool(info.get('has_music')),
    ])

    if rating >= 4.5 and amenity_count >= 3:
        return 4
    if rating >= 4.3 and amenity_count >= 2:
        return 3
    if rating >= 4.0 or amenity_count >= 2:
        return 2
    return 1

# Custom icon/color/feature data for credit packs
CREDIT_PACK_STYLES = [
    {
        'name': 'Starter',
        'icon': 'bolt',
        'icon_bg': 'bg-blue-100',
        'icon_color': 'text-blue-500',
        'features': [
            'No expiry',
            'Best for casual users',
            'Flexible usage',
        ],
    },
    {
        'name': 'Active',
        'icon': 'fire',
        'icon_bg': 'bg-green-100',
        'icon_color': 'text-green-500',
        'features': [
            'Popular choice',
            'Great value',
            'Use anytime',
        ],
    },
    {
        'name': 'Pro',
        'icon': 'star',
        'icon_bg': 'bg-yellow-100',
        'icon_color': 'text-yellow-500',
        'features': [
            'Best for regulars',
            'Priority support',
            'No lock-in',
        ],
    },
    {
        'name': 'Elite',
        'icon': 'crown',
        'icon_bg': 'bg-purple-100',
        'icon_color': 'text-purple-500',
        'features': [
            'Maximum savings',
            'VIP perks',
            'Exclusive events',
        ],
    },
]

# Custom icon/color/feature data for unlimited plans
UNLIMITED_PLAN_STYLES = [
    {
        'icon': 'bolt',
        'icon_bg': 'bg-blue-100',
        'icon_color': 'text-blue-500',
    },
    {
        'icon': 'star',
        'icon_bg': 'bg-yellow-100',
        'icon_color': 'text-yellow-500',
    },
    {
        'icon': 'crown',
        'icon_bg': 'bg-purple-100',
        'icon_color': 'text-purple-500',
    },
]

# Create your views here.
def home(request):
    # Allow both authenticated and non-authenticated users to view home
    return render(request, 'users/home.html')

def plans(request):
    return render(request, 'users/plans.html')

@login_required
def user_dashboard(request):
    """
    Calculate user's workout streak based on consecutive days with gym visits
    """
    workout_streak = 0
    FavoriteGym = get_favorite_gym_model()

    # Use GymBooking model (the one actually written to by create_booking)
    GymBooking = get_gym_booking_model()

    try:
        if is_mongodb():
            # MongoDB query — use booked_at field from GymBooking
            bookings = list(GymBooking.objects(user=request.user).order_by('-booked_at'))
        else:
            # Django ORM query
            bookings = list(GymBooking.objects.filter(user=request.user).order_by('-booked_at'))

        if bookings:
            # Get unique dates (just the date part, not time)
            booking_dates = []
            for booking in bookings:
                raw_date = booking.booked_at if is_mongodb() else booking.booked_at
                booking_date = raw_date.date() if hasattr(raw_date, 'date') else raw_date
                if booking_date not in booking_dates:
                    booking_dates.append(booking_date)
            
            # Sort dates in descending order (most recent first)
            booking_dates.sort(reverse=True)
            
            # Calculate streak from today backwards
            today = datetime.now().date()
            current_check_date = today
            
            for booking_date in booking_dates:
                # If this booking is on the current check date, increment streak
                if booking_date == current_check_date:
                    workout_streak += 1
                    current_check_date -= timedelta(days=1)
                # If booking is older than expected, break the streak
                elif booking_date < current_check_date:
                    break
                # If booking is in the future (shouldn't happen), skip it
                
    except Exception as e:
        print(f"[DEBUG] Error calculating workout streak: {e}")
        workout_streak = 0
    
    # Get user's favorite gym IDs and names for marking favorites in UI
    favorite_gym_ids = []
    favorite_gym_names = []
    try:
        if is_mongodb():
            favorites = FavoriteGym.objects(user=request.user)
            for fav in favorites:
                if fav.gym:
                    favorite_gym_ids.append(str(fav.gym.id))
                    # Also add the gym's name
                    favorite_gym_names.append(fav.gym.name.lower())
                if fav.gym_name:
                    favorite_gym_names.append(fav.gym_name.lower())
        else:
            favorites = FavoriteGym.objects.filter(user=request.user)
            for fav in favorites:
                if fav.gym:
                    favorite_gym_ids.append(fav.gym.id)
                    # Also add the gym's name
                    favorite_gym_names.append(fav.gym.name.lower())
                if fav.gym_name:
                    favorite_gym_names.append(fav.gym_name.lower())
    except Exception as e:
        print(f"[DEBUG] Error getting favorite gyms: {e}")
    
    return render(request, 'users/dashboard.html', {
        'workout_streak': workout_streak,
        'favorite_gym_ids': json.dumps(favorite_gym_ids),
        'favorite_gym_names': json.dumps(favorite_gym_names),
    })

@login_required
@require_http_methods(["POST"])
def find_gyms_by_pincode(request):
    """
    AJAX endpoint to find gyms by location (address, area, landmark, pincode, etc.)
    Uses Google Maps-style location search with Gemini AI
    """
    try:
        data = json.loads(request.body)
        location = data.get('pincode', '').strip()  # Variable name kept for compatibility
        
        if not location:
            return JsonResponse({'error': 'Please enter a location'}, status=400)
        
        print(f"[INFO] Finding gyms for location: {location}")
        
        # Get gyms from AI service (name -> info) - now location-aware
        gym_data = get_gyms_by_pincode(location)  # Uses location-based search
        
        print(f"[INFO] Got {len(gym_data)} results from AI for location: {location}")
        
        # INJECT TEST GYM: Kevin's Fitness Hub for Mumbai/400001 searches
        location_lower = location.lower()
        if '400001' in location or 'mumbai' in location_lower or 'fort' in location_lower or 'mah' in location_lower:
            print(f"[INFO] Injecting Kevin's Fitness Hub into results for Mumbai area")
            # Add Kevin's gym to the beginning of results
            if isinstance(gym_data, dict) and 'error' not in gym_data:
                gym_data = {"Kevin's Fitness Hub": {"distance": "1.2 km", "rating": 4.7}} | gym_data
            elif not gym_data or 'error' in gym_data:
                # If no results or error, return only Kevin's gym
                gym_data = {"Kevin's Fitness Hub": {"distance": "1.2 km", "rating": 4.7}}

        # Try to enrich with DB gym IDs when names match approved gyms
        # Wrapped in its own try/except so a DB timeout never kills the whole response
        if isinstance(gym_data, dict) and gym_data:
            try:
                Gym = get_gym_model()
                if is_mongodb():
                    approved = list(Gym.objects(status='approved', is_active=True))
                else:
                    approved = list(Gym.objects.filter(status='approved', is_active=True))
                by_name = {g.name.strip().lower(): g for g in approved}
                enriched = {}
                for gym_name, info in gym_data.items():
                    gym_obj = by_name.get((gym_name or '').strip().lower())
                    if isinstance(info, dict):
                        enriched_info = dict(info)
                        if gym_obj:
                            enriched_info['id'] = str(gym_obj.id)
                            enriched_info['is_verified_partner'] = gym_obj.is_verified_partner
                            # Use DB tier if available, otherwise auto-assign from Gemini data
                            enriched_info['tier'] = getattr(gym_obj, 'tier', None) or _assign_gym_tier(enriched_info)
                        else:
                            enriched_info['is_verified_partner'] = False
                            enriched_info['tier'] = _assign_gym_tier(enriched_info)
                        enriched_info['tier_label'] = TIER_LABELS.get(enriched_info['tier'], 'Basic')
                        enriched_info['tier_cost'] = TIER_CREDITS.get(enriched_info['tier'], 5)
                        enriched[gym_name] = enriched_info
                    else:
                        # keep string distance format
                        basic_info = {'distance': info, 'is_verified_partner': False}
                        if gym_obj:
                            basic_info['id'] = str(gym_obj.id)
                            basic_info['is_verified_partner'] = gym_obj.is_verified_partner
                            basic_info['tier'] = getattr(gym_obj, 'tier', None) or 1
                        else:
                            basic_info['tier'] = 1
                        basic_info['tier_label'] = TIER_LABELS.get(basic_info['tier'], 'Basic')
                        basic_info['tier_cost'] = TIER_CREDITS.get(basic_info['tier'], 5)
                        enriched[gym_name] = basic_info
                gym_data = enriched
            except Exception as db_err:
                # DB enrichment failed (e.g. MongoDB timeout) — still return raw gym data
                print(f"[WARNING] DB enrichment failed, returning unenriched gym data: {db_err}")
                for gym_name, info in gym_data.items():
                    if isinstance(info, dict):
                        info.setdefault('is_verified_partner', False)
                        tier = _assign_gym_tier(info)
                        info.setdefault('tier', tier)
                        info.setdefault('tier_label', TIER_LABELS.get(tier, 'Basic'))
                        info.setdefault('tier_cost', TIER_CREDITS.get(tier, 5))

        response = JsonResponse(gym_data)
        # Prevent caching  
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Service error: {str(e)}'}, status=500)


@login_required
@require_http_methods(["POST"])
def use_visit(request):
    """
    Deprecated: Use booking endpoint instead.
    POST body: { "gym_name": "...", "tier": 1 } (tier defaults to 1)
    """
    try:
        data = json.loads(request.body)
        gym_name = (data.get('gym_name') or '').strip() or 'Unknown Gym'
        tier = int(data.get('tier', 1))
        if tier not in TIER_CREDITS:
            tier = 1
        cost = TIER_CREDITS[tier]

        return JsonResponse({
            'error': 'This action is no longer available. Please book a slot instead.'
        }, status=410)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def create_booking(request):
    """
    Create a booking and deduct credits immediately.
    Works for both DB-registered gyms and AI-generated gym results.
    POST body: {"gym_id": "...", "gym_name": "...", "tier": 1, "booking_date": "YYYY-MM-DD", "time_slot": "06:00 AM – 07:00 AM"}
    """
    try:
        data = json.loads(request.body)
        gym_id = (data.get('gym_id') or '').strip()
        gym_name = (data.get('gym_name') or '').strip()
        tier = int(data.get('tier', 1))
        booking_date_str = (data.get('booking_date') or '').strip()
        time_slot = (data.get('time_slot') or '').strip()

        if tier not in TIER_CREDITS:
            tier = 1
        if not time_slot:
            return JsonResponse({'error': 'Please select a time slot.'}, status=400)
        if not booking_date_str:
            return JsonResponse({'error': 'Please select a date.'}, status=400)

        # Parse booking date
        try:
            booking_date = datetime.strptime(booking_date_str, '%Y-%m-%d')
        except ValueError:
            return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

        # Validate booking date (past / too far ahead)
        date_check = validate_booking_date(booking_date)
        if not date_check['ok']:
            return JsonResponse({'error': date_check['error']}, status=400)

        # Cost is tier-based: Tier1=5, Tier2=9, Tier3=13, Tier4=18
        cost = TIER_CREDITS.get(tier, 5)

        Gym = get_gym_model()
        GymBooking = get_gym_booking_model()

        # Try to find gym in DB (optional — AI gyms won't be here)
        gym_obj = None
        if gym_id:
            try:
                if is_mongodb():
                    gym_obj = Gym.objects.get(id=gym_id)
                else:
                    gym_obj = Gym.objects.filter(id=gym_id).first()
            except Exception:
                gym_obj = None

        if not gym_obj and gym_name:
            try:
                if is_mongodb():
                    gym_obj = Gym.objects(name__iexact=gym_name, status='approved', is_active=True).first()
                else:
                    gym_obj = Gym.objects.filter(name__iexact=gym_name, status='approved', is_active=True).first()
            except Exception:
                gym_obj = None

        display_name = gym_obj.name if gym_obj else (gym_name or 'Unknown Gym')

        if not display_name:
            return JsonResponse({'error': 'Gym name is required'}, status=400)

        # Get the real user instance (not SimpleLazyObject)
        user = get_user_by_id(request.user.id)

        # ── Duplicate booking check ──────────────────────────────────────────
        if check_duplicate_booking(user, display_name, booking_date):
            return JsonResponse(
                {'error': f'You already have a booking at {display_name} on that date.'},
                status=400,
            )

        # ── Credit check & deduction ─────────────────────────────────────────
        if user.credits < cost:
            return JsonResponse({
                'error': f'Not enough credits. Need {cost}, you have {user.credits}. '
                         f'Buy more credits from the Plans page.'
            }, status=400)

        deduct_credits(user, cost, description=f'Booking at {display_name}')

        # Create booking (OTP will be generated on-demand when user requests it)
        booking_kwargs = dict(
            user=user,
            gym_name=display_name,
            tier=tier,
            credits_charged=cost,
            booking_date=booking_date,
            time_slot=time_slot,
            notes='Booked via dashboard',
            otp='',
            otp_verified=False,
        )
        if gym_obj:
            booking_kwargs['gym'] = gym_obj

        booking = GymBooking.objects.create(**booking_kwargs)

        # Update fitness profile stats (only credits spent, visits counted on checkout)
        try:
            UserFitnessProfile = get_user_fitness_profile_model()
            if is_mongodb():
                # In MongoDB, user is already the UserProfile model
                fitness_profile = UserFitnessProfile.objects(user=user).first()
                if not fitness_profile:
                    fitness_profile = UserFitnessProfile(user=user)
                # Only track credits spent here, visits are tracked on checkout
                fitness_profile.total_credits_spent = fitness_profile.total_credits_spent + cost
                fitness_profile.save()
            else:
                fitness_profile, created = UserFitnessProfile.objects.get_or_create(user=user)
                # Only track credits spent here, visits are tracked on checkout
                fitness_profile.total_credits_spent += cost
                fitness_profile.save()
        except Exception as e:
            print(f"[WARNING] Failed to update fitness profile stats: {e}")

        # Log credit transaction
        log_transaction(
            user, gym_obj,
            credits_delta=-cost,
            tx_type='visit',
            notes=f'Booking at {display_name} on {booking_date_str} {time_slot} (#{booking.id})',
        )

        # Recalculate streak after booking
        new_streak = update_streak(user)

        return JsonResponse({
            'success': True,
            'booking_id': str(booking.id),
            'gym_name': display_name,
            'booking_date': booking_date_str,
            'time_slot': time_slot,
            'new_balance': user.credits,
            'charged': cost,
            'streak': new_streak,
        })

    except (TypeError, ValueError) as e:
        return JsonResponse({'error': f'Invalid input: {str(e)}'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_user_bookings(request):
    """Return recent bookings for the logged-in user as JSON."""
    try:
        GymBooking = get_gym_booking_model()
        if is_mongodb():
            bookings = GymBooking.objects(user=request.user).order_by('-booking_date')[:50]
        else:
            bookings = GymBooking.objects.filter(user=request.user).order_by('-booking_date')[:50]

        result = []
        for b in bookings:
            name = b.gym_name if b.gym_name else (b.gym.name if b.gym else 'Unknown Gym')
            bd = b.booking_date or b.booked_at
            result.append({
                'id': str(b.id),
                'gym_name': name,
                'credits_charged': b.credits_charged,
                'status': b.status,
                'time_slot': b.time_slot if b.time_slot else '—',
                'booking_date': bd.strftime('%Y-%m-%d') if bd else '',
                'booking_date_display': bd.strftime('%d %b %Y') if bd else '',
                'booked_at': b.booked_at.strftime('%d %b %Y, %I:%M %p') if b.booked_at else '',
            })
        return JsonResponse({'bookings': result})
    except Exception as e:
        return JsonResponse({'bookings': [], 'error': str(e)})


@login_required
def booking_calendar(request):
    """Render the booking calendar page."""
    return render(request, 'users/booking_calendar.html')


@login_required
@require_http_methods(['POST'])
def cancel_booking(request, booking_id):
    """
    Cancel a booking and refund credits.
    POST /cancel-booking/<booking_id>/
    Only the booking owner can cancel, and only while status == 'booked'.
    """
    try:
        GymBooking = get_gym_booking_model()
        user = get_user_by_id(request.user.id)

        # Fetch booking belonging to this user
        if is_mongodb():
            try:
                booking = GymBooking.objects.get(id=booking_id, user=user)
            except Exception:
                return JsonResponse({'error': 'Booking not found.'}, status=404)
        else:
            booking = GymBooking.objects.filter(id=booking_id, user=user).first()
            if not booking:
                return JsonResponse({'error': 'Booking not found.'}, status=404)

        if booking.status == 'cancelled':
            return JsonResponse({'error': 'This booking is already cancelled.'}, status=400)
        if booking.status in ('checked_in', 'completed'):
            return JsonResponse(
                {'error': 'Cannot cancel a booking that has been checked in or completed.'},
                status=400,
            )

        # Refund 25% of credits as whole number
        full_amount = booking.credits_charged or BOOKING_COST
        refund_amount = int(full_amount * 0.25)  # 25% refund, rounded down to whole number
        refund_credits(user, refund_amount, description=f'Refund for cancelled booking #{booking_id}')

        # Log the refund transaction
        gym_obj = None
        try:
            gym_obj = booking.gym
        except Exception:
            gym_obj = None

        log_transaction(
            user, gym_obj,
            credits_delta=refund_amount,
            tx_type='adjustment',
            notes=f'Refund: cancelled booking at {booking.gym_name} on '
                  f'{booking.booking_date.strftime("%d %b %Y") if booking.booking_date else "N/A"} (#{booking_id})',
        )

        # Mark booking cancelled
        booking.status = 'cancelled'
        booking.save()

        # Recalculate streak after cancel
        new_streak = update_streak(user)

        return JsonResponse({
            'success': True,
            'booking_id': booking_id,
            'new_balance': user.credits,
            'refunded': refund_amount,
            'streak': new_streak,
            'message': f'Booking cancelled. {refund_amount} credits refunded.',
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_dashboard_stats(request):
    """
    GET /dashboard-stats/
    Returns JSON stats for the current user:
    total_bookings, monthly_bookings, credits_spent, upcoming[], streak, current_credits
    """
    try:
        user = get_user_by_id(request.user.id)
        stats = _get_dashboard_stats(user)
        return JsonResponse(stats)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def plans_and_credits(request):
    CreditPack = get_credit_pack_model()
    packs = CreditPack.objects.all() if is_mongodb() else CreditPack.objects.all().order_by('credits')
    user_balance = 0
    if request.user.is_authenticated:
        user_balance = request.user.credits  # Access credits directly from user model
        print(f"[DEBUG] User: {request.user.username}, Credits: {user_balance}")
    else:
        print("[DEBUG] User is not authenticated")
    tier_costs = TIER_CREDITS
    visits_left = {tier: user_balance // cost for (tier, cost) in tier_costs.items()}
    print(f"[DEBUG] Tier costs: {tier_costs}")
    print(f"[DEBUG] Visits left: {visits_left}")
    # Precompute visits per pack per tier for template
    pack_data = []
    for i, pack in enumerate(packs):
        visits = [(tier, pack.credits // cost) for tier, cost in tier_costs.items()]
        # Assign style by index or by name
        style = CREDIT_PACK_STYLES[i % len(CREDIT_PACK_STYLES)]
        pack_data.append({
            'pack': pack,
            'visits': visits,
            'icon': style['icon'],
            'icon_bg': style['icon_bg'],
            'icon_color': style['icon_color'],
            'features': style['features'],
        })
    # Points-based plans for the Plans page tab
    unlimited_plans = [
        {
            'name': 'Starter Pack',
            'price': 599,
            'credits': 25,
            'validity': 30,
            'features': [
                '25 credits for gym visits',
                '~5 visits to Tier 1 gyms',
                'Valid for 30 days',
                'Perfect for casual users',
            ],
            'highlight': False,
            'visits_breakdown': 'T1: 5 visits | T2: 2 visits | T3: 1 visit | T4: 1 visit',
        },
        {
            'name': 'Regular Pack',
            'price': 1499,
            'credits': 60,
            'validity': 60,
            'features': [
                '60 credits for gym visits',
                '~12 visits to Tier 1 gyms',
                'Valid for 60 days',
                'Great for regular gymgoers',
                'Best value for money',
            ],
            'highlight': True,
            'visits_breakdown': 'T1: 12 visits | T2: 6 visits | T3: 4 visits | T4: 3 visits',
        },
        {
            'name': 'Power Pack',
            'price': 2799,
            'credits': 120,
            'validity': 90,
            'features': [
                '120 credits for gym visits',
                '~24 visits to Tier 1 gyms',
                'Valid for 90 days',
                'Maximum savings per credit',
                'Ideal for fitness enthusiasts',
            ],
            'highlight': False,
            'visits_breakdown': 'T1: 24 visits | T2: 13 visits | T3: 9 visits | T4: 6 visits',
        },
    ]
    for i, plan in enumerate(unlimited_plans):
        style = UNLIMITED_PLAN_STYLES[i % len(UNLIMITED_PLAN_STYLES)]
        plan['icon'] = style['icon']
        plan['icon_bg'] = style['icon_bg']
        plan['icon_color'] = style['icon_color']

    return render(request, 'users/plans_credits.html', {
        'pack_data': pack_data,
        'user_balance': user_balance,
        'visits_left': visits_left,
        'tier_costs': tier_costs,
        'plans': unlimited_plans,
    })

def fixed_plans(request):
    # You can customize these plans as needed
    plans = [
        {
            'name': 'Unlimited Basic',
            'price': 1999,
            'features': [
                'Unlimited gym visits',
                'Access to all Tier 1 gyms',
                'No lock-in, cancel anytime',
            ],
            'highlight': False,
        },
        {
            'name': 'Unlimited Plus',
            'price': 2999,
            'features': [
                'Unlimited gym visits',
                'Access to all Tier 1 & 2 gyms',
                'Priority support',
                'No lock-in, cancel anytime',
            ],
            'highlight': True,
        },
        {
            'name': 'Unlimited Elite',
            'price': 4999,
            'features': [
                'Unlimited gym visits',
                'Access to all gyms (Tiers 1-4)',
                'Personalized onboarding',
                'Exclusive events',
                'No lock-in, cancel anytime',
            ],
            'highlight': False,
        },
    ]
    # Add icon/color to each plan
    for i, plan in enumerate(plans):
        style = UNLIMITED_PLAN_STYLES[i % len(UNLIMITED_PLAN_STYLES)]
        plan['icon'] = style['icon']
        plan['icon_bg'] = style['icon_bg']
        plan['icon_color'] = style['icon_color']
    return render(request, 'users/fixed_plans.html', {'plans': plans})

@login_required
@require_http_methods(["POST"])
def purchase_credits(request):
    """
    Handle credit pack purchase
    """
    try:
        data = json.loads(request.body)
        credits = int(data.get('credits', 0))
        price = float(data.get('price', 0))
        
        if credits <= 0 or price <= 0:
            return JsonResponse({'success': False, 'error': 'Invalid credit pack'}, status=400)
        
        # Get actual user instance (not SimpleLazyObject) for MongoDB compatibility
        user = get_user_by_id(request.user.id)
        
        # Add credits to user account
        user.credits += credits
        user.save()
        
        # Get the correct CreditTransaction model (MongoDB or SQLite)
        CreditTransaction = get_credit_transaction_model()
        
        # Record the transaction
        CreditTransaction.objects.create(
            user=user,
            credits=credits,
            transaction_type='purchase',
            notes=f'Purchased {credits} credits for ₹{price}'
        )
        
        return JsonResponse({
            'success': True,
            'new_balance': user.credits,
            'message': f'Successfully purchased {credits} credits!'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid request format'}, status=400)


@login_required
@require_http_methods(["POST"])
def toggle_favorite_gym(request):
    """
    Toggle favorite status for a gym
    """
    try:
        data = json.loads(request.body)
        gym_id = data.get('gym_id')
        
        gym_name = (data.get('gym_name') or '').strip()
        
        if not gym_id and not gym_name:
            return JsonResponse({'success': False, 'error': 'Gym ID or gym name is required'}, status=400)
        
        # Get models
        Gym = get_gym_model()
        FavoriteGym = get_favorite_gym_model()
        
        # Get actual user instance (not SimpleLazyObject)
        user = get_user_by_id(request.user.id)
        
        # Try to get the gym from DB if gym_id is provided
        gym = None
        if gym_id:
            if is_mongodb():
                from bson import ObjectId
                try:
                    gym_id_obj = ObjectId(gym_id) if isinstance(gym_id, str) else gym_id
                    gym = Gym.objects.get(id=gym_id_obj)
                except Exception:
                    pass  # Gym not in DB, will use gym_name
            else:
                try:
                    gym = Gym.objects.get(pk=gym_id)
                except Gym.DoesNotExist:
                    pass  # Gym not in DB, will use gym_name
        
        # Check if already favorited
        if is_mongodb():
            if gym:
                existing = FavoriteGym.objects(user=user, gym=gym).first()
            else:
                # For AI gyms, check by normalized gym name (case-insensitive, punctuation removed)
                existing = FavoriteGym.objects(user=user, gym_name__iexact=gym_name).first()
        else:
            if gym:
                existing = FavoriteGym.objects.filter(user=user, gym=gym).first()
            else:
                # For AI gyms, check by normalized gym name (case-insensitive)
                existing = FavoriteGym.objects.filter(user=user, gym_name__iexact=gym_name).first()
        
        if existing:
            # Remove from favorites
            existing.delete()
            return JsonResponse({
                'success': True,
                'favorited': False,
                'message': 'Removed from favorites'
            })
        else:
            # Add to favorites
            if gym:
                FavoriteGym.objects.create(user=user, gym=gym)
            else:
                FavoriteGym.objects.create(user=user, gym_name=gym_name)
            return JsonResponse({
                'success': True,
                'favorited': True,
                'message': 'Added to favorites'
            })
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid request format'}, status=400)
    except Exception as e:
        print(f"[ERROR] toggle_favorite_gym: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def user_profile(request):
    """
    Display and update user profile with fitness tracking
    """
    from pymongo.errors import NetworkTimeout
    from datetime import datetime, timedelta
    import hashlib
    
    UserFitnessProfile = get_user_fitness_profile_model()
    FavoriteGym = get_favorite_gym_model()
    GymBooking = get_gym_booking_model()
    
    fitness_profile = None
    favorite_gyms = []
    db_error = None
    
    # Get or create fitness profile (wrapped in try/except for MongoDB timeouts)
    try:
        if is_mongodb():
            fitness_profile = UserFitnessProfile.objects(user=request.user).first()
            if not fitness_profile:
                print(f"[INFO] Creating new fitness profile for {request.user.username}")
                fitness_profile = UserFitnessProfile(user=request.user)
                fitness_profile.save()
            else:
                print(f"[INFO] Found fitness profile for {request.user.username}: visits={fitness_profile.total_visits}, credits_spent={fitness_profile.total_credits_spent}")
            
            # Get favorite gyms with last visited info
            favorite_gyms_objs = FavoriteGym.objects(user=request.user).order_by('-created_at')
            favorite_gyms = []
            for fav in favorite_gyms_objs:
                # Get last booking for this gym
                last_booking = GymBooking.objects(user=request.user, gym_name=fav.gym_name).order_by('-booking_date').first()
                favorite_gyms.append({
                    'gym': fav.gym,
                    'gym_name': fav.gym_name,
                    'created_at': fav.created_at,
                    'last_visited': last_booking.booking_date if last_booking else None
                })
            
            # Get recent bookings for activity feed
            recent_bookings = GymBooking.objects(user=request.user).order_by('-booked_at').limit(10)
            
        else:
            fitness_profile, created = UserFitnessProfile.objects.get_or_create(user=request.user)
            if created:
                print(f"[INFO] Created new fitness profile for {request.user.username}")
            else:
                print(f"[INFO] Found fitness profile for {request.user.username}: visits={fitness_profile.total_visits}, credits_spent={fitness_profile.total_credits_spent}")
            
            # Get favorite gyms with last visited info
            favorite_gyms_objs = FavoriteGym.objects.filter(user=request.user).order_by('-created_at')
            favorite_gyms = []
            for fav in favorite_gyms_objs:
                # Get last booking for this gym
                last_booking = GymBooking.objects.filter(user=request.user, gym__id=fav.gym.id if fav.gym else None).order_by('-booking_date').first()
                favorite_gyms.append({
                    'gym': fav.gym,
                    'gym_name': fav.gym_name if hasattr(fav, 'gym_name') else (fav.gym.name if fav.gym else 'Unknown'),
                    'created_at': fav.created_at,
                    'last_visited': last_booking.booking_date if last_booking else None
                })
            
            # Get recent bookings for activity feed
            recent_bookings = GymBooking.objects.filter(user=request.user).order_by('-booked_at')[:10]
            
    except NetworkTimeout as e:
        print(f"[WARNING] MongoDB timeout in user_profile: {e}")
        db_error = "Database connection is slow. Some profile data may not load. Please refresh in a moment."
        recent_bookings = []
    except Exception as e:
        print(f"[ERROR] Error loading profile data: {e}")
        db_error = "Error loading profile data. Please try again."
        recent_bookings = []
    
    if request.method == 'POST':
        # Update profile
        try:
            if fitness_profile:
                # Handle profile photo upload
                if 'profile_photo' in request.FILES:
                    # Delete old photo if it exists
                    if fitness_profile.profile_photo:
                        try:
                            fitness_profile.profile_photo.delete(save=False)
                        except:
                            pass
                    fitness_profile.profile_photo = request.FILES['profile_photo']
                
                # Update other fields
                fitness_profile.current_weight = request.POST.get('current_weight') or None
                fitness_profile.target_weight = request.POST.get('target_weight') or None
                fitness_profile.height = request.POST.get('height') or None
                fitness_profile.age = request.POST.get('age') or None
                fitness_profile.fitness_goal = request.POST.get('fitness_goal', '')
                fitness_profile.save()
            
            return redirect('user_profile')
        except NetworkTimeout as e:
            print(f"[WARNING] MongoDB timeout updating profile: {e}")
            db_error = "Database connection timeout. Your changes may not have been saved. Please try again."
        except Exception as e:
            print(f"[ERROR] Updating profile: {e}")
            db_error = f"Error updating profile: {str(e)}"
    
    # Calculate achievements
    visits = fitness_profile.total_visits if fitness_profile else 0
    achievements = []
    if visits >= 1:
        achievements.append({'name': 'First Visit', 'icon': '🎯', 'unlocked': True})
    if visits >= 5:
        achievements.append({'name': '5 Visits', 'icon': '🔥', 'unlocked': True})
    if visits >= 10:
        achievements.append({'name': '10 Visits', 'icon': '💪', 'unlocked': True})
    else:
        achievements.append({'name': '10 Visits', 'icon': '💪', 'unlocked': False})
    if visits >= 25:
        achievements.append({'name': '25 Visits', 'icon': '🌟', 'unlocked': True})
    else:
        achievements.append({'name': '25 Visits', 'icon': '🌟', 'unlocked': False})
    if visits >= 50:
        achievements.append({'name': '50 Visits', 'icon': '🏆', 'unlocked': True})
    else:
        achievements.append({'name': '50 Visits', 'icon': '🏆', 'unlocked': False})
    if visits >= 100:
        achievements.append({'name': '100 Visits', 'icon': '👑', 'unlocked': True})
    else:
        achievements.append({'name': '100 Visits', 'icon': '👑', 'unlocked': False})
    
    # Generate referral code
    referral_code = hashlib.md5(f"{request.user.id}{request.user.username}".encode()).hexdigest()[:8].upper()
    
    # Calculate progress toward fitness goal
    goal_progress = 0
    if fitness_profile and fitness_profile.current_weight and fitness_profile.target_weight:
        start_weight = fitness_profile.current_weight
        target_weight = fitness_profile.target_weight
        # Simple progress calculation - can be enhanced
        weight_diff = abs(start_weight - target_weight)
        if weight_diff > 0:
            goal_progress = min(100, (visits / 30) * 100)  # Assuming 30 visits is good progress
    
    # Get user role
    user_role = 'Regular User'
    if hasattr(request.user, 'is_superuser') and request.user.is_superuser:
        user_role = 'Admin'
    elif hasattr(request.user, 'role'):
        if request.user.role == 'gym_owner':
            user_role = 'Gym Owner'
        elif request.user.role == 'admin':
            user_role = 'Admin'
    
    # Calculate weekly trend (comparing last 7 days vs previous 7 days)
    now = datetime.now()
    last_week_start = now - timedelta(days=7)
    prev_week_start = now - timedelta(days=14)
    
    try:
        if is_mongodb():
            last_week_visits = GymBooking.objects(user=request.user, booked_at__gte=last_week_start).count()
            prev_week_visits = GymBooking.objects(user=request.user, booked_at__gte=prev_week_start, booked_at__lt=last_week_start).count()
        else:
            last_week_visits = GymBooking.objects.filter(user=request.user, booked_at__gte=last_week_start).count()
            prev_week_visits = GymBooking.objects.filter(user=request.user, booked_at__gte=prev_week_start, booked_at__lt=last_week_start).count()
        
        weekly_trend = 'up' if last_week_visits > prev_week_visits else ('down' if last_week_visits < prev_week_visits else 'same')
    except:
        weekly_trend = 'same'
        last_week_visits = 0
    
    context = {
        'profile': fitness_profile,
        'favorite_gyms': favorite_gyms,
        'bmi': fitness_profile.bmi() if fitness_profile else None,
        'db_error': db_error,
        'achievements': achievements,
        'referral_code': referral_code,
        'goal_progress': goal_progress,
        'user_role': user_role,
        'recent_bookings': recent_bookings,
        'weekly_trend': weekly_trend,
        'last_week_visits': last_week_visits,
    }
    
    return render(request, 'users/profile.html', context)


@login_required
def booking_history(request):
    """
    Get all bookings for the user
    """
    try:
        GymBooking = get_gym_booking_model()
        
        if is_mongodb():
            bookings = GymBooking.objects(user=request.user).order_by('-booked_at')
        else:
            bookings = GymBooking.objects.filter(user=request.user).order_by('-booked_at')
        
        booking_list = []
        for booking in bookings:
            booking_data = {
                'id': str(booking.id),
                'gym_name': booking.gym_name,
                'tier': booking.tier,
                'credits_charged': booking.credits_charged,
                'status': booking.status,
                'booked_at': booking.booked_at.isoformat() if hasattr(booking.booked_at, 'isoformat') else str(booking.booked_at),
                'booking_date': booking.booking_date.isoformat() if hasattr(booking.booking_date, 'isoformat') else str(booking.booking_date),
                'booking_date_display': booking.booking_date.strftime('%b %d, %Y') if hasattr(booking.booking_date, 'strftime') else str(booking.booking_date),
                'time_slot': booking.time_slot if hasattr(booking, 'time_slot') else '—',
            }
            booking_list.append(booking_data)
        
        return JsonResponse({'success': True, 'bookings': booking_list})
    
    except Exception as e:
        print(f"[ERROR] booking_history: {e}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(['POST'])
def gym_checkin(request):
    """
    Check-in to gym with GPS verification and fraud prevention.
    Requires: booking_id, user_latitude, user_longitude
    """
    try:
        data = json.loads(request.body)
        booking_id = data.get('booking_id')
        user_lat = data.get('latitude')
        user_lon = data.get('longitude')
        
        # Validate inputs
        if not booking_id:
            return JsonResponse({'success': False, 'error': 'Booking ID is required'}, status=400)
        
        if user_lat is None or user_lon is None:
            return JsonResponse({'success': False, 'error': 'GPS location is required for check-in'}, status=400)
        
        # Validate GPS coordinates
        if not validate_gps_coordinates(float(user_lat), float(user_lon)):
            return JsonResponse({'success': False, 'error': 'Invalid GPS coordinates'}, status=400)
        
        # Get booking
        GymBooking = get_gym_booking_model()
        
        if is_mongodb():
            booking = GymBooking.objects(id=booking_id, user=request.user).first()
        else:
            booking = GymBooking.objects.filter(id=booking_id, user=request.user).first()
        
        if not booking:
            return JsonResponse({'success': False, 'error': 'Booking not found'}, status=404)
        
        # Check if already checked in
        if booking.status == 'checked_in':
            return JsonResponse({'success': False, 'error': 'Already checked in. Use check-out to complete session.'}, status=400)
        
        if booking.status == 'completed':
            return JsonResponse({'success': False, 'error': 'This booking is already completed'}, status=400)
        
        # Get gym details
        gym = booking.gym
        if not gym:
            return JsonResponse({'success': False, 'error': 'Gym information not available'}, status=404)
        
        # Check if gym has GPS coordinates
        if gym.latitude is None or gym.longitude is None:
            return JsonResponse({
                'success': False, 
                'error': 'Gym location not configured. Please contact gym owner.'
            }, status=400)
        
        # Verify GPS proximity (within 100 meters)
        is_close, actual_distance = is_within_proximity(
            float(user_lat), 
            float(user_lon),
            float(gym.latitude),
            float(gym.longitude),
            max_distance_meters=100.0
        )
        
        if not is_close:
            return JsonResponse({
                'success': False,
                'error': f'You must be at the gym to check in. You are {format_distance(actual_distance)} away.',
                'distance': format_distance(actual_distance)
            }, status=403)
        
        # Check for duplicate check-ins today (fraud prevention)
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        if is_mongodb():
            today_checkins = GymBooking.objects(
                user=request.user,
                gym=gym,
                checked_in_at__gte=today_start,
                checked_in_at__lt=today_end,
                status__in=['checked_in', 'completed']
            ).count()
        else:
            today_checkins = GymBooking.objects.filter(
                user=request.user,
                gym=gym,
                checked_in_at__gte=today_start,
                checked_in_at__lt=today_end,
                status__in=['checked_in', 'completed']
            ).count()
        
        if today_checkins > 0:
            return JsonResponse({
                'success': False,
                'error': 'You have already checked in to this gym today. Cooldown: 1 check-in per gym per day.'
            }, status=403)
        
        # Perform check-in
        booking.status = 'checked_in'
        # Use IST timezone
        ist = pytz.timezone('Asia/Kolkata')
        booking.checked_in_at = datetime.now(ist).replace(tzinfo=None)
        booking.check_in_latitude = float(user_lat)
        booking.check_in_longitude = float(user_lon)
        booking.save()
        
        # Update user streak
        update_streak(request.user)
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully checked in to {gym.name}',
            'checked_in_at': booking.checked_in_at.isoformat(),
            'distance': format_distance(actual_distance)
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"[ERROR] gym_checkin: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(['POST'])
def gym_checkout(request):
    """
    Check-out from gym and calculate session duration.
    Requires: booking_id
    """
    try:
        data = json.loads(request.body)
        booking_id = data.get('booking_id')
        
        if not booking_id:
            return JsonResponse({'success': False, 'error': 'Booking ID is required'}, status=400)
        
        # Get booking
        GymBooking = get_gym_booking_model()
        
        if is_mongodb():
            booking = GymBooking.objects(id=booking_id, user=request.user).first()
        else:
            booking = GymBooking.objects.filter(id=booking_id, user=request.user).first()
        
        if not booking:
            return JsonResponse({'success': False, 'error': 'Booking not found'}, status=404)
        
        # Check if checked in
        if booking.status != 'checked_in':
            return JsonResponse({'success': False, 'error': 'You must check in before checking out'}, status=400)
        
        if not booking.checked_in_at:
            return JsonResponse({'success': False, 'error': 'Check-in time not recorded'}, status=400)
        
        # Perform check-out
        checkout_time = datetime.now()
        session_duration = checkout_time - booking.checked_in_at
        
        booking.status = 'completed'
        booking.checked_out_at = checkout_time
        booking.session_duration = session_duration
        
        if is_mongodb():
            # Store duration in minutes for MongoDB
            booking.session_duration_minutes = int(session_duration.total_seconds() / 60)
        
        booking.save()
        
        # Update fitness profile stats (increment visits on successful checkout)
        try:
            UserFitnessProfile = get_user_fitness_profile_model()
            if is_mongodb():
                profile = UserFitnessProfile.objects(user=request.user).first()
            else:
                profile = UserFitnessProfile.objects.filter(user=request.user).first()
            
            if profile:
                # Only increment visits on completed checkout (not on booking)
                profile.total_visits += 1
                profile.save()
        except Exception as e:
            print(f"[WARNING] Could not update fitness profile: {e}")
        
        duration_minutes = int(session_duration.total_seconds() / 60)
        duration_hours = duration_minutes // 60
        duration_mins = duration_minutes % 60
        
        duration_str = f"{duration_hours}h {duration_mins}m" if duration_hours > 0 else f"{duration_mins}m"
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully checked out from {booking.gym.name if booking.gym else booking.gym_name}',
            'checked_out_at': checkout_time.isoformat(),
            'session_duration': duration_str,
            'duration_minutes': duration_minutes
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"[ERROR] gym_checkout: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def end_workout(request):
    """
    User ends their workout session (same as checkout but clearer naming for OTP system).
    Updates booking status to 'completed', records checkout time, and calculates session duration.
    """
    try:
        data = json.loads(request.body)
        booking_id = data.get('booking_id')
        
        if not booking_id:
            return JsonResponse({'success': False, 'error': 'Booking ID is required'}, status=400)
        
        # Get booking model
        GymBooking = get_gym_booking_model()
        
        # Fetch booking
        if is_mongodb():
            booking = GymBooking.objects(id=booking_id, user=request.user).first()
        else:
            booking = GymBooking.objects.filter(id=booking_id, user=request.user).first()
        
        if not booking:
            return JsonResponse({'success': False, 'error': 'Booking not found'}, status=404)
        
        # Check if user is checked in
        if booking.status != 'checked_in':
            return JsonResponse({'success': False, 'error': 'You must be checked in to end workout'}, status=400)
        
        # Update booking - mark as completed
        # Use IST timezone for checkout
        ist = pytz.timezone('Asia/Kolkata')
        checkout_time = datetime.now(ist).replace(tzinfo=None)
        booking.status = 'completed'
        booking.checked_out_at = checkout_time
        
        # Calculate session duration
        if booking.checked_in_at:
            # Convert to aware datetimes if needed
            check_in = booking.checked_in_at
            check_out = checkout_time
            
            if check_in.tzinfo is None:
                check_in = check_in.replace(tzinfo=dt_timezone.utc)
            if check_out.tzinfo is None:
                check_out = check_out.replace(tzinfo=dt_timezone.utc)
            
            duration = check_out - check_in
            booking.session_duration_minutes = int(duration.total_seconds() / 60)
        
        booking.save()
        
        # Update fitness profile stats
        try:
            from accounts.db_utils import get_user_fitness_profile_model
            UserFitnessProfile = get_user_fitness_profile_model()
            
            if is_mongodb():
                fitness_profile = UserFitnessProfile.objects(user=request.user).first()
                if not fitness_profile:
                    fitness_profile = UserFitnessProfile(user=request.user)
                fitness_profile.total_gyms_visited += 1
                fitness_profile.save()
            else:
                fitness_profile, _ = UserFitnessProfile.objects.get_or_create(user=request.user)
                fitness_profile.total_gyms_visited += 1
                fitness_profile.save()
        except Exception as e:
            print(f"[WARNING] Failed to update fitness profile: {e}")
        
        # Format duration for display
        duration_str = 'N/A'
        if booking.session_duration_minutes:
            hours = booking.session_duration_minutes // 60
            mins = booking.session_duration_minutes % 60
            if hours > 0:
                duration_str = f"{hours}h {mins}m"
            else:
                duration_str = f"{mins} minutes"
        
        return JsonResponse({
            'success': True,
            'message': f'Workout completed at {booking.gym.name if booking.gym else booking.gym_name}!',
            'checked_out_at': checkout_time.strftime('%I:%M %p'),
            'session_duration': duration_str,
            'duration_minutes': booking.session_duration_minutes,
            'gym': booking.gym.name if booking.gym else booking.gym_name
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid request format'}, status=400)
    except Exception as e:
        print(f"[ERROR] end_workout: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def generate_booking_otp(request):
    """Generate OTP for a booking on-demand"""
    try:
        data = json.loads(request.body)
        booking_id = data.get('booking_id')
        
        if not booking_id:
            return JsonResponse({'error': 'Booking ID is required'}, status=400)
        
        # Get the booking
        from accounts.mongo_models import GymBooking
        try:
            booking = GymBooking.objects.get(id=booking_id)
        except GymBooking.DoesNotExist:
            return JsonResponse({'error': 'Booking not found'}, status=404)
        
        # Verify the booking belongs to the logged-in user
        if str(booking.user.id) != str(request.user.id):
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        # Only generate OTP for booked or checked_in status
        if booking.status not in ['booked', 'checked_in']:
            return JsonResponse({'error': f'Cannot generate OTP for {booking.status} booking'}, status=400)
        
        # Generate new OTP
        new_otp = generate_otp(6)
        booking.otp = new_otp
        booking.otp_verified = False  # Reset verification
        booking.save()
        
        return JsonResponse({
            'success': True,
            'otp': new_otp,
            'booking_id': str(booking.id)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request format'}, status=400)
    except Exception as e:
        print(f"[ERROR] generate_booking_otp: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def get_booking_details(request, booking_id):
    """Get booking details including gym location for directions"""
    try:
        from accounts.mongo_models import GymBooking
        try:
            booking = GymBooking.objects.get(id=booking_id)
        except GymBooking.DoesNotExist:
            return JsonResponse({'error': 'Booking not found'}, status=404)
        
        # Verify the booking belongs to the logged-in user
        if str(booking.user.id) != str(request.user.id):
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        # Get gym location
        gym_location = None
        if booking.gym:
            gym_location = booking.gym.location
        
        return JsonResponse({
            'success': True,
            'booking_id': str(booking.id),
            'gym_name': booking.gym_name,
            'gym_location': gym_location,
            'status': booking.status,
            'otp': booking.otp if booking.otp else None,
            'booking_date': booking.booking_date.strftime('%Y-%m-%d') if booking.booking_date else None,
            'time_slot': booking.time_slot if booking.time_slot else None,
        })
        
    except Exception as e:
        print(f"[ERROR] get_booking_details: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)
