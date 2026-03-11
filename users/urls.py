from django.urls import path
from django.views.generic import RedirectView
from . import views
from .views import plans_and_credits, fixed_plans, purchase_credits, toggle_favorite_gym, user_profile

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', RedirectView.as_view(url='/accounts/login/', permanent=False)),
    path('signup/', RedirectView.as_view(url='/accounts/signup/', permanent=False)),
    path('logout/', RedirectView.as_view(url='/accounts/logout/', permanent=False)),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('profile/', user_profile, name='user_profile'),
    path('plans/', plans_and_credits, name='plans'),
    path('fixed-plans/', fixed_plans, name='fixed_plans'),
    path('purchase-credits/', purchase_credits, name='purchase_credits'),
    path('find-gyms/', views.find_gyms_by_pincode, name='find_gyms_by_pincode'),
    path('book/', views.create_booking, name='create_booking'),
    path('my-bookings/', views.get_user_bookings, name='get_user_bookings'),
    path('calendar/', views.booking_calendar, name='booking_calendar'),
    path('cancel-booking/<str:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('dashboard-stats/', views.get_dashboard_stats, name='get_dashboard_stats'),
    path('use-visit/', views.use_visit, name='use_visit'),
    path('toggle-favorite/', toggle_favorite_gym, name='toggle_favorite_gym'),
    path('booking-history/', views.booking_history, name='booking_history'),
    path('gym-checkin/', views.gym_checkin, name='gym_checkin'),
    path('gym-checkout/', views.gym_checkout, name='gym_checkout'),
    path('end-workout/', views.end_workout, name='user_end_workout'),
    path('generate-otp/', views.generate_booking_otp, name='generate_booking_otp'),
    path('booking-details/<str:booking_id>/', views.get_booking_details, name='get_booking_details'),
] 