from django.urls import path
from django.contrib.auth import views as auth_views
from .views import SignUpView, role_based_redirect, CustomLoginView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('redirect/', role_based_redirect, name='role_redirect'),
] 