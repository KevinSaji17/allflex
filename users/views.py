from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import CreditPack, UserCreditBalance, CreditTransaction, GymBooking, TIER_CREDIT_COSTS
from gyms.models import Gym
from allflex.gym_recommender import get_gyms_by_pincode
import json

# Credits cost per gym tier (1 booking)
TIER_CREDITS = TIER_CREDIT_COSTS

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
    if request.user.is_authenticated:
        return redirect('role_redirect')
    return render(request, 'users/home.html')

def plans(request):
    return render(request, 'users/plans.html')

@login_required
def user_dashboard(request):
    return render(request, 'users/dashboard.html')

@login_required
@require_http_methods(["POST"])
def find_gyms_by_pincode(request):
    """
    AJAX endpoint to find gyms by pincode
    """
    try:
        data = json.loads(request.body)
        pincode = data.get('pincode', '').strip()
        
        if not pincode:
            return JsonResponse({'error': 'Please enter a pincode'}, status=400)
        
        # Get gyms from AI service (name -> info)
        gym_data = get_gyms_by_pincode(pincode)

        # Try to enrich with DB gym IDs when names match approved gyms
        if isinstance(gym_data, dict) and gym_data:
            approved = Gym.objects.filter(status='approved', is_active=True)
            by_name = {g.name.strip().lower(): g for g in approved}
            enriched = {}
            for gym_name, info in gym_data.items():
                gym_obj = by_name.get((gym_name or '').strip().lower())
                if isinstance(info, dict):
                    enriched_info = dict(info)
                    if gym_obj:
                        enriched_info.setdefault('id', gym_obj.id)
                    enriched[gym_name] = enriched_info
                else:
                    # keep string distance format
                    if gym_obj:
                        enriched[gym_name] = {'distance': info, 'id': gym_obj.id}
                    else:
                        enriched[gym_name] = info
            gym_data = enriched

        return JsonResponse(gym_data)
        
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
    Create a booking and deduct credits immediately (booking time).
    POST body: {"gym_id": 123, "tier": 1}
    """
    try:
        data = json.loads(request.body)
        gym_id = data.get('gym_id')
        gym_name = (data.get('gym_name') or '').strip()
        tier = int(data.get('tier', 1))
        if tier not in TIER_CREDITS:
            tier = 1

        # Demo behavior: every booking costs a flat 5 credits
        cost = 5

        gym = None
        if gym_id:
            gym = Gym.objects.filter(id=gym_id, status='approved', is_active=True).first()
        elif gym_name:
            gym = Gym.objects.filter(name__iexact=gym_name, status='approved', is_active=True).first()

        if not gym:
            return JsonResponse({'error': 'Gym not available'}, status=404)

        user = request.user
        if user.credits < cost:
            return JsonResponse({
                'error': f'Not enough credits. Need {cost}, you have {user.credits}.'
            }, status=400)

        user.credits -= cost
        user.save(update_fields=['credits'])

        booking = GymBooking.objects.create(
            user=user,
            gym=gym,
            tier=tier,
            credits_charged=cost,
            notes='',
        )

        CreditTransaction.objects.create(
            user=user,
            credits=-cost,
            transaction_type='visit',
            gym=gym,
            notes=f'Booking #{booking.id}',
        )

        return JsonResponse({
            'success': True,
            'booking_id': booking.id,
            'new_balance': user.credits,
            'charged': cost,
            'gym': {'id': gym.id, 'name': gym.name},
        })

    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid input'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def plans_and_credits(request):
    packs = CreditPack.objects.all().order_by('credits')
    user_balance = None
    if request.user.is_authenticated:
        user_balance = request.user.credits  # Access credits directly
    else:
        user_balance = 0
    tier_costs = TIER_CREDITS
    visits_left = {tier: user_balance // cost for tier, cost in tier_costs.items()}
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
    # Unlimited plans for the Plans page tab (same data as fixed_plans)
    unlimited_plans = [
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
