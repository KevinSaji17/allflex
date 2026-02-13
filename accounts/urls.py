from django.urls import path
from django.contrib.auth import views as auth_views
from .views import SignUpView, role_based_redirect

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('redirect/', role_based_redirect, name='role_redirect'),
] 