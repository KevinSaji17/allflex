from django.urls import path
from . import views

urlpatterns = [
    path('', views.gym_dashboard, name='gym_dashboard'),
    path('browse/', views.gym_browse, name='gym_browse'),
    path('submit/', views.gym_submit, name='gym_submit'),
    path('request-account/', views.gym_owner_request_form, name='gym_owner_request_form'),
    path('search-gym-name/', views.search_gym_name, name='search_gym_name'),
    path('verify-otp/', views.verify_booking_otp, name='verify_booking_otp'),
    path('end-workout/', views.end_workout, name='end_workout'),
    path('<str:gym_id>/', views.gym_detail, name='gym_detail'),
] 