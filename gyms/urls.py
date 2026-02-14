from django.urls import path
from . import views

urlpatterns = [
    path('', views.gym_dashboard, name='gym_dashboard'),
    path('browse/', views.gym_browse, name='gym_browse'),
    path('submit/', views.gym_submit, name='gym_submit'),
    path('<int:gym_id>/', views.gym_detail, name='gym_detail'),
] 