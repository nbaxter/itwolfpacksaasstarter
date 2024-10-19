from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'is_subscribed', 'subscription_status', 'is_staff')
    list_filter = ('is_subscribed', 'subscription_status', 'is_staff')
    ordering = ('email',)
    search_fields = ('email', 'first_name', 'last_name')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Subscription', {'fields': ('is_subscribed', 'stripe_customer_id', 
                                   'subscription_status', 'subscription_id')}),
    )