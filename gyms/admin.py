from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.contrib import messages
from django.conf import settings
from django.shortcuts import redirect
from .models import Booking as SQLiteBooking, Rating as SQLiteRating, PayoutRequest as SQLitePayoutRequest
from .models import CreditPack, UserCreditPack, GymOwnerRequest
from .models import Gym as SQLiteGym  # SQLite Gym model
from .admin_models import GymAdminLink

# Import db_utils for flexible model loading
from accounts.db_utils import get_gym_model, is_mongodb


@admin.register(GymOwnerRequest)
class GymOwnerRequestAdmin(admin.ModelAdmin):
    list_display = ['gym_name', 'owner_name', 'username', 'suggested_tier', 'status', 'created_at', 'action_buttons']
    list_filter = ['status', 'suggested_tier', 'created_at']
    search_fields = ['gym_name', 'owner_name', 'email', 'gym_address', 'username']
    readonly_fields = ['user_id', 'username', 'created_at', 'updated_at', 'ai_recommendation', 'suggested_tier', 'facilities_summary', 'reviewed_at']
    actions = ['approve_requests', 'reject_requests']
    
    class Media:
        css = {
            'all': ()
        }
        
    def changelist_view(self, request, extra_context=None):
        """Add link to manage gyms view"""
        extra_context = extra_context or {}
        extra_context['show_gyms_link'] = True
        return super().changelist_view(request, extra_context=extra_context)
    
    fieldsets = (
        ('Request Information', {
            'fields': ('username', 'user_id', 'status', 'created_at', 'updated_at', 'reviewed_at')
        }),
        ('Gym Details', {
            'fields': ('gym_name', 'gym_address')
        }),
        ('Owner Information', {
            'fields': ('owner_name', 'contact_number', 'email')
        }),
        ('Business Details', {
            'fields': ('years_in_business', 'total_members')
        }),
        ('Facilities Checklist', {
            'fields': ('facilities_summary', 'has_ac', 'has_changing_rooms', 'has_showers', 'has_lockers', 
                      'has_parking', 'has_trainers', 'has_cardio', 'has_weights', 'has_machines',
                      'has_group_classes', 'has_spa', 'has_pool', 'has_cafeteria', 'has_music', 'has_wifi')
        }),
        ('Documents', {
            'fields': ('business_proof',)
        }),
        ('Additional Information', {
            'fields': ('additional_info',)
        }),
        ('AI Assessment', {
            'fields': ('ai_recommendation', 'suggested_tier'),
            'classes': ('collapse',)
        }),
        ('Admin Review', {
            'fields': ('admin_notes',)
        }),
    )
    
    def facilities_summary(self, obj):
        facilities = obj.get_facilities_list()
        tier = obj.calculate_tier_score()
        return format_html(
            '<div style="background: #f0f9ff; padding: 10px; border-radius: 5px;">'
            '<strong>Total Facilities:</strong> {}<br>'
            '<strong>Calculated Tier:</strong> <span style="color: #0891b2; font-weight: bold;">Tier {}</span><br>'
            '<strong>Facilities:</strong> {}</div>',
            len(facilities), tier, ', '.join(facilities) if facilities else 'None'
        )
    facilities_summary.short_description = "Facilities Summary"
    
    def action_buttons(self, obj):
        if obj.status == 'pending':
            return format_html(
                '<a class="button" href="/admin/gyms/gymownerrequest/{}/change/">Review</a>',
                obj.pk
            )
        elif obj.status == 'approved':
            return format_html('<span style="color: green;">✓ Approved</span>')
        else:
            return format_html('<span style="color: red;">✗ Rejected</span>')
    action_buttons.short_description = "Actions"
    
    def approve_requests(self, request, queryset):
        """Admin action to approve gym owner requests and create gyms"""
        from accounts.db_utils import get_gym_model
        Gym = get_gym_model()
        
        approved_count = 0
        for req in queryset.filter(status='pending'):
            try:
                # Recalculate tier to ensure it's up to date
                req.suggested_tier = req.calculate_tier_score()
                
                # Get the user object
                if settings.DATABASE_MODE == 'mongodb':
                    from accounts.mongo_models import UserProfile
                    user = UserProfile.objects(id=req.user_id).first()
                else:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    try:
                        user = User.objects.get(id=req.user_id)
                    except (User.DoesNotExist, ValueError):
                        messages.error(request, f"Error: User with ID {req.user_id} not found for {req.gym_name}")
                        continue
                
                if not user:
                    messages.error(request, f"Error: User with ID {req.user_id} not found for {req.gym_name}")
                    continue
                
                # Update user role to gym_owner
                user.role = 'gym_owner'
                user.save()
                
                # Create gym using the recalculated tier
                tier = req.suggested_tier
                
                if settings.DATABASE_MODE == 'mongodb':
                    # MongoDB Gym
                    gym = Gym(
                        owner=user,
                        name=req.gym_name,
                        description=f"Facilities: {', '.join(req.get_facilities_list())}\n\n{req.additional_info}",
                        location=req.gym_address,
                        tier=tier,
                        status='approved',
                        is_active=True,
                        is_verified_partner=True
                    )
                    gym.save()
                else:
                    # SQL Gym
                    gym = Gym.objects.create(
                        owner=user,
                        name=req.gym_name,
                        description=f"Facilities: {', '.join(req.get_facilities_list())}\n\n{req.additional_info}",
                        location=req.gym_address,
                        tier=tier,
                        status='approved',
                        is_active=True,
                        is_verified_partner=True
                    )
                
                # Update request status
                req.status = 'approved'
                req.reviewed_at = timezone.now()
                req.save()
                approved_count += 1
                
            except Exception as e:
                messages.error(request, f"Error approving {req.gym_name}: {str(e)}")
        
        if approved_count > 0:
            messages.success(request, f"Successfully approved {approved_count} gym owner request(s) and created gym(s).")
    
    approve_requests.short_description = "✓ Approve selected requests and grant gym owner role"
    
    def reject_requests(self, request, queryset):
        """Admin action to reject gym owner requests"""
        updated = queryset.filter(status='pending').update(
            status='rejected',
            reviewed_at=timezone.now()
        )
        messages.success(request, f"Rejected {updated} gym owner request(s).")
    
    reject_requests.short_description = "✗ Reject selected requests"
    
    def save_model(self, request, obj, form, change):
        # Check if any facility fields were changed
        facility_fields = [
            'has_ac', 'has_changing_rooms', 'has_showers', 'has_lockers', 'has_parking',
            'has_trainers', 'has_cardio', 'has_weights', 'has_machines', 'has_group_classes',
            'has_spa', 'has_pool', 'has_cafeteria', 'has_music', 'has_wifi'
        ]
        
        facilities_changed = any(field in form.changed_data for field in facility_fields)
        
        # Recalculate tier if facilities were changed
        if facilities_changed or not obj.suggested_tier:
            old_tier = obj.suggested_tier
            obj.suggested_tier = obj.calculate_tier_score()
            
            # Update AI recommendation based on new tier
            facilities = obj.get_facilities_list()
            tier_names = {1: 'Basic', 2: 'Standard', 3: 'Premium', 4: 'Elite'}
            obj.ai_recommendation = (
                f"Tier {obj.suggested_tier} ({tier_names.get(obj.suggested_tier, 'Unknown')}) "
                f"- Based on {len(facilities)} facilities: {', '.join(facilities) if facilities else 'None'}. "
                f"Score-based tier calculation from facilities assessment."
            )
            
            if old_tier and old_tier != obj.suggested_tier:
                messages.info(request, f"Tier recalculated: Tier {old_tier} → Tier {obj.suggested_tier}")
        
        if change and 'status' in form.changed_data:
            obj.reviewed_at = timezone.now()
            
            # If approved, create gym and update user role
            if obj.status == 'approved':
                try:
                    from accounts.db_utils import get_gym_model
                    Gym = get_gym_model()
                    
                    # Get the user object
                    if settings.DATABASE_MODE == 'mongodb':
                        from accounts.mongo_models import UserProfile
                        user = UserProfile.objects(id=obj.user_id).first()
                    else:
                        from django.contrib.auth import get_user_model
                        User = get_user_model()
                        try:
                            user = User.objects.get(id=obj.user_id)
                        except (User.DoesNotExist, ValueError):
                            messages.error(request, f"Error: User with ID {obj.user_id} not found")
                            user = None
                    
                    if user:
                        # Update user role
                        user.role = 'gym_owner'
                        user.save()
                        
                        # Create gym if not exists (use recalculated tier)
                        tier = obj.suggested_tier or obj.calculate_tier_score()
                        
                        if settings.DATABASE_MODE == 'mongodb':
                            # Check MongoDB gym exists
                            if not Gym.objects(name=obj.gym_name, location=obj.gym_address).first():
                                gym = Gym(
                                    owner=user,
                                    name=obj.gym_name,
                                    description=f"Facilities: {', '.join(obj.get_facilities_list())}\n\n{obj.additional_info}",
                                    location=obj.gym_address,
                                    tier=tier,
                                    status='approved',
                                    is_active=True,
                                    is_verified_partner=True
                                )
                                gym.save()
                                messages.success(request, f"Gym '{obj.gym_name}' created and user promoted to gym owner.")
                        else:
                            # Check SQL gym exists
                            if not Gym.objects.filter(name=obj.gym_name, location=obj.gym_address).exists():
                                Gym.objects.create(
                                    owner=user,
                                    name=obj.gym_name,
                                    description=f"Facilities: {', '.join(obj.get_facilities_list())}\n\n{obj.additional_info}",
                                    location=obj.gym_address,
                                    tier=tier,
                                    status='approved',
                                    is_active=True,
                                    is_verified_partner=True
                                )
                                messages.success(request, f"Gym '{obj.gym_name}' created and user promoted to gym owner.")
                    else:
                        messages.error(request, f"Cannot find user with ID {obj.user_id}")
                except Exception as e:
                    messages.error(request, f"Error creating gym: {str(e)}")
        
        super().save_model(request, obj, form, change)


# MongoDB-aware Gym Admin
class MongoGymAdmin(admin.ModelAdmin):
    """Custom admin for Gym model that works with both MongoDB and SQLite"""
    
    list_display = ['name', 'owner_username', 'tier_display', 'status_display', 'is_active', 'is_verified_partner', 'wallet_balance', 'location_preview', 'created_at']
    list_filter = ['tier', 'status', 'is_active', 'is_verified_partner', 'created_at']
    search_fields = ['name', 'location']
    actions = ['approve_gyms', 'reject_gyms', 'activate_gyms', 'deactivate_gyms', 'verify_partner', 'unverify_partner', 'delete_gyms_and_demote_owners']
    list_per_page = 25
    date_hierarchy = 'created_at' if not is_mongodb() else None
    
    # Make all fields editable
    fields = ('name', 'owner', 'description', 'location', 'tier', 'capacity', 'status', 'is_active', 'is_verified_partner', 'wallet_balance')
    
    def location_preview(self, obj):
        """Show truncated location"""
        location = obj.location[:50] + '...' if len(obj.location) > 50 else obj.location
        return location
    location_preview.short_description = 'Location'
    
    def get_queryset(self, request):
        """Get gyms from MongoDB or SQLite based on DATABASE_MODE"""
        if is_mongodb():
            # Return MongoDB gyms as a list
            from accounts.mongo_models import Gym as MongoGym
            return list(MongoGym.objects.all())
        else:
            # Return SQLite gyms as QuerySet
            return super().get_queryset(request)
    
    def save_model(self, request, obj, form, change):
        """Save the model"""
        obj.save()
        if change:
            messages.success(request, f"✅ Updated gym: {obj.name}")
        else:
            messages.success(request, f"✅ Created new gym: {obj.name}")
    
    def owner_username(self, obj):
        """Display owner username"""
        try:
            return obj.owner.username if obj.owner else 'N/A'
        except:
            return 'N/A'
    owner_username.short_description = 'Owner'
    
    def tier_display(self, obj):
        colors = {1: '#28a745', 2: '#17a2b8', 3: '#ffc107', 4: '#dc3545'}
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">Tier {}</span>',
            colors.get(obj.tier, '#6c757d'),
            obj.tier
        )
    tier_display.short_description = 'Tier'
    
    def status_display(self, obj):
        colors = {'pending': '#ffc107', 'approved': '#28a745', 'rejected': '#dc3545'}
        status_text = obj.status.capitalize() if hasattr(obj, 'status') else 'Unknown'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            status_text
        )
    status_display.short_description = 'Status'
    
    def approve_gyms(self, request, queryset):
        """Approve selected gyms and mark as verified partners"""
        if is_mongodb():
            updated = 0
            for gym in queryset:
                gym.status = 'approved'
                gym.is_active = True
                gym.is_verified_partner = True
                gym.save()
                updated += 1
            messages.success(request, f"Approved {updated} gym(s) and marked as ALLFLEX verified partners.")
        else:
            updated = queryset.update(status='approved', is_active=True, is_verified_partner=True)
            messages.success(request, f"Approved {updated} gym(s) and marked as ALLFLEX verified partners.")
    approve_gyms.short_description = "✓ Approve selected gyms"
    
    def reject_gyms(self, request, queryset):
        """Reject selected gyms"""
        if is_mongodb():
            updated = 0
            for gym in queryset:
                gym.status = 'rejected'
                gym.is_active = False
                gym.save()
                updated += 1
            messages.success(request, f"Rejected {updated} gym(s).")
        else:
            updated = queryset.update(status='rejected', is_active=False)
            messages.success(request, f"Rejected {updated} gym(s).")
    reject_gyms.short_description = "✗ Reject selected gyms"
    
    def activate_gyms(self, request, queryset):
        """Activate selected gyms"""
        if is_mongodb():
            updated = 0
            for gym in queryset:
                gym.is_active = True
                gym.save()
                updated += 1
            messages.success(request, f"Activated {updated} gym(s).")
        else:
            updated = queryset.update(is_active=True)
            messages.success(request, f"Activated {updated} gym(s).")
    activate_gyms.short_description = "🟢 Activate selected gyms"
    
    def deactivate_gyms(self, request, queryset):
        """Deactivate selected gyms"""
        if is_mongodb():
            updated = 0
            for gym in queryset:
                gym.is_active = False
                gym.save()
                updated += 1
            messages.success(request, f"Deactivated {updated} gym(s).")
        else:
            updated = queryset.update(is_active=False)
            messages.success(request, f"Deactivated {updated} gym(s).")
    deactivate_gyms.short_description = "🔴 Deactivate selected gyms"
    
    def verify_partner(self, request, queryset):
        """Mark selected gyms as verified partners"""
        if is_mongodb():
            updated = 0
            for gym in queryset:
                gym.is_verified_partner = True
                gym.save()
                updated += 1
            messages.success(request, f"✅ Verified {updated} gym(s) as ALLFLEX partners. They will now show the blue checkmark badge.")
        else:
            updated = queryset.update(is_verified_partner=True)
            messages.success(request, f"✅ Verified {updated} gym(s) as ALLFLEX partners. They will now show the blue checkmark badge.")
    verify_partner.short_description = "✓ Mark as verified partner"
    
    def unverify_partner(self, request, queryset):
        """Remove verified partner status"""
        if is_mongodb():
            updated = 0
            for gym in queryset:
                gym.is_verified_partner = False
                gym.save()
                updated += 1
            messages.warning(request, f"Removed verified partner status from {updated} gym(s). Badge will no longer show.")
        else:
            updated = queryset.update(is_verified_partner=False)
            messages.warning(request, f"Removed verified partner status from {updated} gym(s). Badge will no longer show.")
    unverify_partner.short_description = "✗ Remove verified partner status"
    
    def delete_gyms_and_demote_owners(self, request, queryset):
        """Delete gyms and demote owners to regular users if they have no other gyms"""
        deleted_count = 0
        demoted_count = 0
        gym_names = []
        
        for gym in queryset:
            gym_name = gym.name
            gym_names.append(gym_name)
            
            # Get owner
            owner = gym.owner
            if owner:
                # Check if owner has other gyms
                if is_mongodb():
                    from accounts.mongo_models import Gym as MongoGym
                    other_gyms = MongoGym.objects(owner=owner, id__ne=gym.id).count()
                else:
                    other_gyms = SQLiteGym.objects.filter(owner=owner).exclude(id=gym.id).count()
                
                # If this is their only gym, demote them to regular user
                if other_gyms == 0:
                    old_role = owner.role
                    owner.role = 'user'
                    owner.save()
                    demoted_count += 1
                    messages.info(request, f"👤 Demoted {owner.username} from '{old_role}' to 'user' (no remaining gyms)")
            
            # Delete the gym
            gym.delete()
            deleted_count += 1
        
        messages.success(request, f"🗑️ Deleted {deleted_count} gym(s): {', '.join(gym_names[:3])}{'...' if len(gym_names) > 3 else ''}")
        if demoted_count > 0:
            messages.warning(request, f"⚠️ {demoted_count} gym owner(s) were demoted to regular users. Consider notifying them via email.")
    delete_gyms_and_demote_owners.short_description = "🗑️ Delete gyms and demote owners"
    
    def delete_model(self, request, obj):
        """Override delete to handle owner demotion"""
        from accounts.db_utils import get_user_model
        User = get_user_model()
        
        gym_name = obj.name
        owner = obj.owner
        
        # Check if owner has other gyms
        if owner:
            if is_mongodb():
                from accounts.mongo_models import Gym as MongoGym
                other_gyms = MongoGym.objects(owner=owner, id__ne=obj.id).count()
            else:
                other_gyms = SQLiteGym.objects.filter(owner=owner).exclude(id=obj.id).count()
            
            # If this is their only gym, demote them
            if other_gyms == 0:
                owner.role = 'user'
                owner.save()
                messages.warning(request, f"⚠️ {owner.username} has been demoted to regular user (last gym removed)")
        
        # Delete the gym
        super().delete_model(request, obj)
        messages.success(request, f"🗑️ Deleted gym: {gym_name}")
    
    def has_add_permission(self, request):
        """Allow adding gyms"""
        return True
    
    def has_change_permission(self, request, obj=None):
        """Allow editing gyms"""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Allow deleting gyms"""
        return True


# Register Gym admin - only for SQLite
# For MongoDB, use custom admin views at /admin/gyms/mongodb-gyms/
if not is_mongodb():
    try:
        admin.site.register(SQLiteGym, MongoGymAdmin)
    except admin.sites.AlreadyRegistered:
        pass


# Add Gyms link to admin dashboard for MongoDB mode
@admin.register(GymAdminLink)
class GymAdminLinkAdmin(admin.ModelAdmin):
    """
    Shows 'Gyms' section on admin dashboard that redirects to MongoDB gym management
    """
    
    def changelist_view(self, request, extra_context=None):
        """Redirect to MongoDB gyms view"""
        return redirect('/admin/gyms/mongodb-gyms/')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(SQLiteBooking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'gym', 'gym_tier', 'timestamp', 'credits_deducted']
    list_filter = ['gym__tier', 'timestamp']
    search_fields = ['user__username', 'gym__name']
    date_hierarchy = 'timestamp'
    
    def gym_tier(self, obj):
        colors = {1: '#28a745', 2: '#17a2b8', 3: '#ffc107', 4: '#dc3545'}
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px; border-radius: 3px;">Tier {}</span>',
            colors.get(obj.gym.tier, '#6c757d'),
            obj.gym.tier
        )
    gym_tier.short_description = 'Gym Tier'
    
    def credits_deducted(self, obj):
        return format_html(
            '<span style="color: #dc3545; font-weight: bold;">-1 Credit</span>'
        )
    credits_deducted.short_description = 'Credits Used'

@admin.register(SQLiteRating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['gym', 'user', 'stars_display', 'comment_preview']
    list_filter = ['stars', 'gym__tier']
    search_fields = ['gym__name', 'user__username', 'comment']
    
    def stars_display(self, obj):
        stars = '⭐' * obj.stars
        return format_html('<span style="font-size: 18px;">{}</span>', stars)
    stars_display.short_description = 'Rating'
    
    def comment_preview(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
    comment_preview.short_description = 'Comment'

@admin.register(SQLitePayoutRequest)
class PayoutRequestAdmin(admin.ModelAdmin):
    list_display = ['gym_owner', 'amount_display', 'status_display', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['gym_owner__username']
    date_hierarchy = 'created_at'
    actions = ['approve_payouts', 'reject_payouts']
    
    def amount_display(self, obj):
        return format_html(
            '<span style="font-size: 16px; font-weight: bold; color: #28a745;">₹{}</span>',
            obj.amount
        )
    amount_display.short_description = 'Amount'
    
    def status_display(self, obj):
        colors = {'pending': '#ffc107', 'approved': '#28a745', 'rejected': '#dc3545'}
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def approve_payouts(self, request, queryset):
        """Approve payout requests"""
        updated = queryset.filter(status='pending').update(status='approved')
        messages.success(request, f"Approved {updated} payout request(s).")
    approve_payouts.short_description = "✓ Approve selected payouts"
    
    def reject_payouts(self, request, queryset):
        """Reject payout requests"""
        updated = queryset.filter(status='pending').update(status='rejected')
        messages.success(request, f"Rejected {updated} payout request(s).")
    reject_payouts.short_description = "✗ Reject selected payouts"

@admin.register(CreditPack)
class CreditPackAdmin(admin.ModelAdmin):
    list_display = ['name', 'tier_display', 'credits_display', 'price_display', 'validity_display', 'is_active']
    list_filter = ['tier', 'is_active']
    search_fields = ['name', 'description']
    ordering = ['tier', 'price']
    
    def tier_display(self, obj):
        colors = {1: '#28a745', 2: '#17a2b8', 3: '#ffc107', 4: '#dc3545'}
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">Tier {}</span>',
            colors.get(obj.tier, '#6c757d'),
            obj.tier
        )
    tier_display.short_description = 'Tier'
    
    def credits_display(self, obj):
        return format_html(
            '<span style="font-size: 16px; font-weight: bold; color: #007bff;">{} Credits</span>',
            obj.credits
        )
    credits_display.short_description = 'Credits'
    
    def price_display(self, obj):
        return format_html(
            '<span style="font-size: 16px; font-weight: bold; color: #28a745;">₹{}</span>',
            obj.price
        )
    price_display.short_description = 'Price'
    
    def validity_display(self, obj):
        return format_html(
            '<span style="color: #6c757d;">{} days</span>',
            obj.validity_days
        )
    validity_display.short_description = 'Validity'

@admin.register(UserCreditPack)
class UserCreditPackAdmin(admin.ModelAdmin):
    list_display = ['user', 'credit_pack', 'credits_status', 'purchased_at', 'expires_at', 'status_badge']
    list_filter = ['is_active', 'credit_pack__tier', 'purchased_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['purchased_at', 'expires_at']
    date_hierarchy = 'purchased_at'
    
    def credits_status(self, obj):
        total = obj.credit_pack.credits
        remaining = obj.remaining_credits
        percentage = (remaining / total) * 100 if total > 0 else 0
        
        if percentage > 50:
            color = '#28a745'
        elif percentage > 20:
            color = '#ffc107'
        else:
            color = '#dc3545'
        
        return format_html(
            '<div style="display: flex; align-items: center; gap: 10px;">'
            '<span style="font-weight: bold; color: {};">{}/{}</span>'
            '<div style="width: 100px; height: 10px; background: #e9ecef; border-radius: 5px; overflow: hidden;">'
            '<div style="width: {}%; height: 100%; background: {}; transition: width 0.3s;"></div>'
            '</div>'
            '</div>',
            color, remaining, total, percentage, color
        )
    credits_status.short_description = 'Credits Remaining'
    
    def status_badge(self, obj):
        if obj.is_expired():
            return format_html('<span style="background-color: #dc3545; color: white; padding: 5px 10px; border-radius: 3px;">Expired</span>')
        elif not obj.is_active:
            return format_html('<span style="background-color: #6c757d; color: white; padding: 5px 10px; border-radius: 3px;">Inactive</span>')
        else:
            return format_html('<span style="background-color: #28a745; color: white; padding: 5px 10px; border-radius: 3px;">Active</span>')
    status_badge.short_description = 'Status'
