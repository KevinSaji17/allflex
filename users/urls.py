from django.urls import path
from . import views
from .views import plans_and_credits, fixed_plans

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('plans/', plans_and_credits, name='plans'),
    path('fixed-plans/', fixed_plans, name='fixed_plans'),
    path('find-gyms/', views.find_gyms_by_pincode, name='find_gyms_by_pincode'),
    path('use-visit/', views.use_visit, name='use_visit'),
] 