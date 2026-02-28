from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from .models import CreditPack, UserCreditBalance, CreditTransaction


@admin.register(CreditPack)
class CreditPackAdmin(admin.ModelAdmin):
    list_display = ['name', 'credits_display', 'price_display', 'is_best_value']
    list_filter = ['is_best_value']
    search_fields = ['name']
    actions = ['mark_best_value', 'unmark_best_value']
    
    fieldsets = (
        ('Pack Details', {
            'fields': ('name', 'credits', 'price', 'is_best_value')
        }),
    )
    
    def credits_display(self, obj):
        return format_html(
            '<span style="font-size: 16px; font-weight: bold; color: #007bff;">{} Credits</span>',
            obj.credits
        )
    credits_display.short_description = 'Credits'
    
    def price_display(self, obj):
        price_per = obj.price_per_credit()
        return format_html(
            '<span style="font-size: 16px; font-weight: bold; color: #28a745;">₹{}</span><br>'
            '<small style="color: #6c757d;">₹{}/credit</small>',
            obj.price, price_per
        )
    price_display.short_description = 'Price'
    
    def mark_best_value(self, request, queryset):
        """Mark selected packs as best value"""
        updated = queryset.update(is_best_value=True)
        messages.success(request, f"Marked {updated} pack(s) as best value.")
    mark_best_value.short_description = "⭐ Mark as best value"
    
    def unmark_best_value(self, request, queryset):
        """Unmark best value"""
        updated = queryset.update(is_best_value=False)
        messages.success(request, f"Unmarked {updated} pack(s) as best value.")
    unmark_best_value.short_description = "Remove best value mark"


@admin.register(UserCreditBalance)
class UserCreditBalanceAdmin(admin.ModelAdmin):
    list_display = ['user', 'credits_display']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['user']
    
    def credits_display(self, obj):
        color = '#28a745' if obj.credits > 0 else '#dc3545'
        return format_html(
            '<span style="font-size: 18px; font-weight: bold; color: {};">{} Credits</span>',
            color, obj.credits
        )
    credits_display.short_description = 'Balance'


@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'transaction_type', 'credits_display', 'pack', 'gym', 'timestamp']
    list_filter = ['transaction_type', 'timestamp']
    search_fields = ['user__username', 'user__email', 'notes']
    date_hierarchy = 'timestamp'
    readonly_fields = ['user', 'pack', 'gym', 'timestamp']
    
    def credits_display(self, obj):
        if obj.transaction_type == 'purchase':
            color = '#28a745'
            sign = '+'
        else:
            color = '#dc3545'
            sign = '-'
        return format_html(
            '<span style="font-size: 16px; font-weight: bold; color: {};">{}{}</span>',
            color, sign, abs(obj.credits)
        )
    credits_display.short_description = 'Credits'
