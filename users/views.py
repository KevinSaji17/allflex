from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import CreditPack, UserCreditBalance, CreditTransaction
from gyms.models import Gym
from allflex.gym_recommender import get_gyms_by_pincode
import json

# Credits cost per gym tier (1 visit)
TIER_CREDITS = {1: 5, 2: 9, 3: 13, 4: 18}

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
        
        # Get gyms from AI service
        gym_data = get_gyms_by_pincode(pincode)
        
        return JsonResponse(gym_data)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Service error: {str(e)}'}, status=500)


@login_required
@require_http_methods(["POST"])
def use_visit(request):
    """
    MVP: Use 1 visit at a gym — deduct credits and log transaction.
    POST body: { "gym_name": "...", "tier": 1 } (tier defaults to 1)
    """
    try:
        data = json.loads(request.body)
        gym_name = (data.get('gym_name') or '').strip() or 'Unknown Gym'
        tier = int(data.get('tier', 1))
        if tier not in TIER_CREDITS:
            tier = 1
        cost = TIER_CREDITS[tier]

        user = request.user
        if user.credits < cost:
            return JsonResponse({
                'error': f'Not enough credits. Need {cost}, you have {user.credits}. Get more on Plans & Credits.'
            }, status=400)

        user.credits -= cost
        user.save(update_fields=['credits'])

        CreditTransaction.objects.create(
            user=user,
            credits=-cost,
            transaction_type='visit',
            gym=None,
            notes=gym_name,
        )

        return JsonResponse({
            'success': True,
            'new_balance': user.credits,
            'used': cost,
            'gym_name': gym_name,
        })
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
