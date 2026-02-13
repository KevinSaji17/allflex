from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),  # Changed from 'dashboard/'
    path('gym/approve/<int:gym_id>/', views.approve_gym, name='approve_gym'),
    path('gym/reject/<int:gym_id>/', views.reject_gym, name='reject_gym'),
] 