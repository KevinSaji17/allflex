from django.contrib import admin
from .models import Gym, Booking, Rating, PayoutRequest, CreditPack, UserCreditPack

@admin.register(Gym)
class GymAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'tier', 'status', 'is_active', 'wallet_balance']
    list_filter = ['tier', 'status', 'is_active']
    search_fields = ['name', 'location', 'owner__username']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'gym', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['user__username', 'gym__name']

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['gym', 'user', 'stars', 'comment']
    list_filter = ['stars']
    search_fields = ['gym__name', 'user__username']

@admin.register(PayoutRequest)
class PayoutRequestAdmin(admin.ModelAdmin):
    list_display = ['gym_owner', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['gym_owner__username']

@admin.register(CreditPack)
class CreditPackAdmin(admin.ModelAdmin):
    list_display = ['name', 'tier', 'credits', 'price', 'validity_days', 'is_active']
    list_filter = ['tier', 'is_active']
    search_fields = ['name']

@admin.register(UserCreditPack)
class UserCreditPackAdmin(admin.ModelAdmin):
    list_display = ['user', 'credit_pack', 'remaining_credits', 'purchased_at', 'expires_at', 'is_active']
    list_filter = ['is_active', 'purchased_at', 'expires_at']
    search_fields = ['user__username', 'credit_pack__name']
    readonly_fields = ['purchased_at']
