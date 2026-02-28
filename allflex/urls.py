"""
URL configuration for allflex project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from gyms.admin_views import mongodb_gyms_view, mongodb_gym_edit, mongodb_gym_delete

urlpatterns = [
    path('admin/gyms/mongodb-gyms/', mongodb_gyms_view, name='mongodb_gyms_view'),
    path('admin/gyms/mongodb-gyms/<str:gym_id>/edit/', mongodb_gym_edit, name='mongodb_gym_edit'),
    path('admin/gyms/mongodb-gyms/<str:gym_id>/delete/', mongodb_gym_delete, name='mongodb_gym_delete'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('gym-dashboard/', include('gyms.urls')),
    path('gyms/', include('gyms.urls')),  # Alternative URL prefix
    path('admin-dashboard/', include('adminpanel.urls')),
    path('', include('users.urls')),
]
