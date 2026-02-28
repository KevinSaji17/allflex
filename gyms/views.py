from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django import forms
from accounts.db_utils import get_gym_model, get_booking_model, is_mongodb

# Create your views here.

@login_required
def gym_dashboard(request):
    # Only gym owners can access
    if request.user.role != 'gym_owner':
        return redirect('home')

    Gym = get_gym_model()
    Booking = get_booking_model()

    # Gyms owned by the logged-in user
    if is_mongodb():
        # MongoDB queries
        owned_gyms = Gym.objects(owner=request.user)
        bookings = Booking.objects(gym__in=owned_gyms).order_by('-timestamp')
        total_bookings = bookings.count()
        # Calculate total wallet balance manually for MongoDB
        total_wallet_balance = sum(gym.wallet_balance for gym in owned_gyms)
    else:
        # Django ORM queries
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
    Gym = get_gym_model()
    
    if is_mongodb():
        gyms = Gym.objects(status='approved', is_active=True).order_by('name')
    else:
        gyms = Gym.objects.filter(status='approved', is_active=True).order_by('name')
    
    return render(request, 'gyms/browse.html', {'gyms': gyms})


def gym_detail(request, gym_id):
    Gym = get_gym_model()

    if is_mongodb():
        try:
            gym = Gym.objects.get(id=gym_id, status='approved', is_active=True)
        except Exception:
            from django.http import Http404
            raise Http404("Gym not found")
    else:
        gym = get_object_or_404(Gym, id=gym_id, status='approved', is_active=True)
    
    return render(request, 'gyms/detail.html', {'gym': gym})


class GymSubmitForm(forms.ModelForm):
    class Meta:
        from gyms.models import Gym as SQLiteGym
        model = SQLiteGym
        fields = ['name', 'description', 'location', 'tier', 'capacity', 'logo']


class MongoGymSubmitForm(forms.Form):
    """Form for MongoDB Gym submission"""
    name = forms.CharField(max_length=255, required=True)
    description = forms.CharField(widget=forms.Textarea, required=True)
    location = forms.CharField(max_length=255, required=True)
    tier = forms.ChoiceField(choices=[(1, 'Tier 1'), (2, 'Tier 2'), (3, 'Tier 3'), (4, 'Tier 4')], required=True)
    capacity = forms.IntegerField(min_value=1, initial=20, required=True)
    logo = forms.ImageField(required=False)


@login_required
@require_http_methods(["GET", "POST"])
def gym_submit(request):
    """Landing page for gym submission - shows different content based on user role"""
    # Handle gym submission from gym_owners
    if request.method == 'POST' and request.user.role == 'gym_owner':
        Gym = get_gym_model()
        if is_mongodb():
            form = MongoGymSubmitForm(request.POST, request.FILES)
            if form.is_valid():
                gym = Gym(
                    owner=request.user,
                    name=form.cleaned_data['name'],
                    description=form.cleaned_data['description'],
                    location=form.cleaned_data['location'],
                    tier=int(form.cleaned_data['tier']),
                    capacity=form.cleaned_data['capacity'],
                    status='pending',
                    is_active=False
                )
                if form.cleaned_data.get('logo'):
                    logo_file = form.cleaned_data['logo']
                    gym.logo = logo_file.name
                gym.save()
                messages.success(request, '✅ Gym submitted successfully! It will be reviewed by our team within 48 hours.')
                return redirect('gym_dashboard')
        else:
            form = GymSubmitForm(request.POST, request.FILES)
            if form.is_valid():
                gym = form.save(commit=False)
                gym.owner = request.user
                gym.status = 'pending'
                gym.is_active = False
                gym.save()
                messages.success(request, '✅ Gym submitted successfully! It will be reviewed by our team within 48 hours.')
                return redirect('gym_dashboard')
    
    # Always send everyone to the full request form (with AI tier classification)
    return redirect('gym_owner_request_form')


@login_required
def gym_owner_request_form(request):
    """Separate page for gym owner account request form"""
    if request.method == 'POST':
        from .models import GymOwnerRequest
        
        # Extract form data
        gym_name = request.POST.get('gym_name')
        gym_address = request.POST.get('gym_address')
        owner_name = request.POST.get('owner_name')
        contact_number = request.POST.get('contact_number')
        email = request.POST.get('email')
        years_in_business = request.POST.get('years_in_business')
        total_members = request.POST.get('total_members')
        additional_info = request.POST.get('additional_info', '')
        business_proof = request.FILES.get('business_proof', None)
        
        # Facilities checklist
        has_ac = 'has_ac' in request.POST
        has_changing_rooms = 'has_changing_rooms' in request.POST
        has_showers = 'has_showers' in request.POST
        has_lockers = 'has_lockers' in request.POST
        has_parking = 'has_parking' in request.POST
        has_trainers = 'has_trainers' in request.POST
        has_cardio = 'has_cardio' in request.POST
        has_weights = 'has_weights' in request.POST
        has_machines = 'has_machines' in request.POST
        has_group_classes = 'has_group_classes' in request.POST
        has_spa = 'has_spa' in request.POST
        has_pool = 'has_pool' in request.POST
        has_cafeteria = 'has_cafeteria' in request.POST
        has_music = 'has_music' in request.POST
        has_wifi = 'has_wifi' in request.POST
        
        try:
            # Get user information
            user_id = str(request.user.id)
            username = request.user.username
            
            # Create request object
            gym_request = GymOwnerRequest.objects.create(
                user_id=user_id,
                username=username,
                gym_name=gym_name,
                gym_address=gym_address,
                owner_name=owner_name,
                contact_number=contact_number,
                email=email,
                years_in_business=int(years_in_business) if years_in_business else 0,
                total_members=int(total_members) if total_members else 0,
                has_ac=has_ac,
                has_changing_rooms=has_changing_rooms,
                has_showers=has_showers,
                has_lockers=has_lockers,
                has_parking=has_parking,
                has_trainers=has_trainers,
                has_cardio=has_cardio,
                has_weights=has_weights,
                has_machines=has_machines,
                has_group_classes=has_group_classes,
                has_spa=has_spa,
                has_pool=has_pool,
                has_cafeteria=has_cafeteria,
                has_music=has_music,
                has_wifi=has_wifi,
                additional_info=additional_info,
                business_proof=business_proof
            )
            
            # Calculate tier
            suggested_tier = gym_request.calculate_tier_score()
            gym_request.suggested_tier = suggested_tier
            
            # Get AI analysis
            import google.genai as genai
            from django.conf import settings
            
            ai_recommendation = "AI analysis unavailable"
            try:
                api_key = getattr(settings, 'GEMINI_API_KEY', None)
                if api_key and api_key.strip() and api_key != 'YOUR_API_KEY_HERE':
                    client = genai.Client(api_key=api_key)
                    
                    facilities_list = gym_request.get_facilities_list()
                    analysis_prompt = f"""Analyze this gym owner account request:

Gym: {gym_name}
Location: {gym_address}
Years in Business: {years_in_business}
Total Members: {total_members}
Facilities ({len(facilities_list)}): {', '.join(facilities_list)}

Provide brief assessment (under 150 words):
1. Legitimacy Score (1-10)
2. Recommended Tier ({suggested_tier} by system)
3. Risk Level (Low/Medium/High)
4. Recommendation (Approve/Review/Reject)"""
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=analysis_prompt
                    )
                    ai_recommendation = response.text.strip()
            except Exception as e:
                ai_recommendation = f"AI analysis error: {str(e)}"
            
            gym_request.ai_recommendation = ai_recommendation
            gym_request.save()
            
            messages.success(
                request,
                f'✅ Request submitted! ID: #{gym_request.id} | Suggested Tier: {suggested_tier} | '
                f'Review within 24-48 hours. Email: {email}'
            )
            return redirect('user_dashboard')
            
        except Exception as e:
            messages.error(request, f'❌ Error: {str(e)}')
    
    return render(request, 'gyms/request_form.html')


def search_gym_name(request):
    """API endpoint to search gym names using Gemini - Always returns valid data"""
    from django.http import JsonResponse
    
    query = request.GET.get('q', '').strip()
    
    # Always return sample data for short queries
    if len(query) < 3:
        return JsonResponse({
            'gyms': [
                {'name': 'Gold\'s Gym', 'address': f'{query} - Type more to search'},
            ]
        })
    
    try:
        import google.genai as genai
        from django.conf import settings
        import json, re
        import logging
        
        logger = logging.getLogger(__name__)
        api_key = getattr(settings, 'GEMINI_API_KEY', None)
        
        # Return sample data if no API key
        if not api_key or api_key.strip() == '' or api_key == 'YOUR_API_KEY_HERE':
            logger.warning("No valid Gemini API key found")
            return JsonResponse({
                'gyms': [
                    {'name': f'Gold\'s Gym {query}', 'address': f'{query} Main Street, Commercial Complex'},
                    {'name': f'Fitness First {query}', 'address': f'{query} Central Plaza, 2nd Floor'},
                    {'name': f'Anytime Fitness {query}', 'address': f'{query} Metro Station Road'},
                    {'name': f'Cult.fit {query}', 'address': f'{query} Tech Park'},
                    {'name': f'The Gym Company {query}', 'address': f'{query} Sports Complex'},
                ]
            })
        
        # Try Gemini search with cheap lite model
        client = genai.Client(api_key=api_key)
        
        search_prompt = f"""Find 5 real gyms near "{query}" in India. Return ONLY a JSON array:
[{{"name": "Gym Name", "address": "Full address, City, India"}}]
No markdown, no extra text. India locations only."""
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=search_prompt
        )
        
        response_text = response.text.strip()
        logger.info(f"Gemini response for '{query}': {response_text[:200]}")
        
        # Remove markdown code blocks if present
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*', '', response_text)
        response_text = response_text.strip()
        
        # Extract JSON array
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        
        if json_match:
            gyms = json.loads(json_match.group())
            if gyms and len(gyms) > 0:
                logger.info(f"Successfully found {len(gyms)} gyms for '{query}'")
                return JsonResponse({'gyms': gyms[:10]})
            else:
                logger.warning(f"Empty gym list returned for '{query}'")
                # Return message that no gyms found
                return JsonResponse({
                    'gyms': [
                        {'name': 'No gyms found', 'address': f'Try searching with city name (e.g., "{query}, Mumbai")'},
                    ]
                })
        else:
            logger.error(f"Failed to parse JSON from Gemini response for '{query}'")
            # Fallback to sample data
            return JsonResponse({
                'gyms': [
                    {'name': f'Gold\'s Gym {query}', 'address': f'{query}, India'},
                    {'name': f'Cult.fit {query}', 'address': f'{query}, India'},
                ]
            })
            
    except Exception as e:
        # Log the actual error for debugging
        import logging
        logger = logging.getLogger(__name__)
        error_str = str(e)
        logger.error(f"Error in search_gym_name for query '{query}': {error_str}", exc_info=True)
        
        # Check if it's a rate limit error
        is_rate_limit = '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str or 'quota' in error_str.lower()
        
        if is_rate_limit:
            logger.warning(f"Rate limit hit for gym search '{query}'. Returning demo Indian gyms.")
        
        # Return realistic demo gyms from major Indian cities
        # Extract city/area from query if possible
        query_lower = query.lower()
        
        if 'bangalore' in query_lower or 'bengaluru' in query_lower:
            demo_gyms = [
                {'name': 'Cult.fit Indiranagar', 'address': '100 Feet Road, Indiranagar, Bangalore, Karnataka'},
                {'name': 'Gold\'s Gym Koramangala', 'address': '5th Block, Koramangala, Bangalore, Karnataka'},
                {'name': 'Fitness First Whitefield', 'address': 'ITPL Main Road, Whitefield, Bangalore, Karnataka'},
            ]
        elif 'mumbai' in query_lower or 'bombay' in query_lower:
            demo_gyms = [
                {'name': 'Talwalkars Gym Bandra', 'address': 'Linking Road, Bandra West, Mumbai, Maharashtra'},
                {'name': 'Gold\'s Gym Andheri', 'address': 'Andheri West, Mumbai, Maharashtra'},
                {'name': 'Cult.fit Lower Parel', 'address': 'Lower Parel, Mumbai, Maharashtra'},
            ]
        elif 'delhi' in query_lower or 'ncr' in query_lower:
            demo_gyms = [
                {'name': 'Gold\'s Gym Connaught Place', 'address': 'Connaught Place, New Delhi, Delhi'},
                {'name': 'Anytime Fitness Saket', 'address': 'Saket, New Delhi, Delhi'},
                {'name': 'Fitness First Gurgaon', 'address': 'Sector 29, Gurgaon, Haryana'},
            ]
        else:
            # Generic Indian gyms
            demo_gyms = [
                {'name': f'Gold\'s Gym {query}', 'address': f'{query}, India'},
                {'name': f'Cult.fit {query}', 'address': f'{query}, India'},
                {'name': f'Fitness First {query}', 'address': f'{query}, India'},
            ]
        
        return JsonResponse({'gyms': demo_gyms})

