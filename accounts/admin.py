from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from django.conf import settings


if settings.DATABASE_MODE == 'mongodb':
    from .mongo_models import UserProfile
    
    # We can't use @admin.register for MongoEngine models
    # Instead, we'll create a custom admin interface
    
    class MongoUserAdmin:
        """Custom admin for MongoDB users"""
        
        def __init__(self):
            # Register custom admin views if needed
            pass
    
    # For now, MongoDB users must be managed via Django shell or custom views
    # Standard Django admin doesn't support MongoEngine models directly
    pass
else:
    # For SQL mode, we can register standard User admin
    from django.contrib.auth import get_user_model
    from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
    
    User = get_user_model()
    
    class CustomUserAdmin(BaseUserAdmin):
        """Enhanced user admin with role management"""
        list_display = ['username', 'email', 'role_display', 'is_staff', 'is_active', 'date_joined']
        list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
        actions = ['make_gym_owner', 'make_regular_user', 'activate_users', 'deactivate_users']
        
        fieldsets = BaseUserAdmin.fieldsets + (
            ('Role & Subscription', {
                'fields': ('role', 'plan', 'credits') if hasattr(User, 'role') else ()
            }),
        )
        
        def role_display(self, obj):
            if hasattr(obj, 'role'):
                colors = {'user': '#17a2b8', 'gym_owner': '#28a745', 'admin': '#dc3545'}
                return format_html(
                    '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
                    colors.get(obj.role, '#6c757d'),
                    obj.role.replace('_', ' ').title()
                )
            return '-'
        role_display.short_description = 'Role'
        
        def make_gym_owner(self, request, queryset):
            """Promote users to gym owner role"""
            if hasattr(User, 'role'):
                updated = queryset.update(role='gym_owner')
                messages.success(request, f"Promoted {updated} user(s) to gym owner.")
            else:
                messages.error(request, "User model doesn't support role field.")
        make_gym_owner.short_description = "🏋️ Promote to gym owner"
        
        def make_regular_user(self, request, queryset):
            """Demote users to regular user role"""
            if hasattr(User, 'role'):
                updated = queryset.update(role='user')
                messages.success(request, f"Changed {updated} user(s) to regular user.")
            else:
                messages.error(request, "User model doesn't support role field.")
        make_regular_user.short_description = "👤 Change to regular user"
        
        def activate_users(self, request, queryset):
            """Activate selected users"""
            updated = queryset.update(is_active=True)
            messages.success(request, f"Activated {updated} user(s).")
        activate_users.short_description = "✓ Activate users"
        
        def deactivate_users(self, request, queryset):
            """Deactivate selected users"""
            updated = queryset.update(is_active=False)
            messages.success(request, f"Deactivated {updated} user(s).")
        deactivate_users.short_description = "✗ Deactivate users"
    
    # Unregister the default User admin and register our custom one
    try:
        admin.site.unregister(User)
    except admin.sites.NotRegistered:
        pass
    
    admin.site.register(User, CustomUserAdmin)
