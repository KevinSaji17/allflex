from django.urls import path
from . import views

urlpatterns = [
    path('', views.gym_dashboard, name='gym_dashboard'),
] 