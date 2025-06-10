from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User, UserProfile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Enhanced admin interface for User model"""
    
    list_display = [
        'username', 'email', 'first_name', 'last_name', 
        'role', 'is_verified', 'is_active', 'date_joined'
    ]
    list_filter = [
        'role', 'is_active', 'is_verified', 'date_joined'
    ]
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['-date_joined']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Role & Permissions', {
            'fields': ('role', 'is_verified')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'address', 'city', 'postal_code', 'country')
        }),
        ('Profile', {
            'fields': ('avatar', 'date_of_birth')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('first_name', 'last_name', 'email', 'role')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile')
    
    actions = ['make_verified', 'make_unverified', 'promote_to_vendor']
    
    def make_verified(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(
            request, 
            f'{updated} users marked as verified.'
        )
    make_verified.short_description = "Mark selected users as verified"
    
    def make_unverified(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(
            request, 
            f'{updated} users marked as unverified.'
        )
    make_unverified.short_description = "Mark selected users as unverified"
    
    def promote_to_vendor(self, request, queryset):
        updated = queryset.filter(role='customer').update(role='vendor')
        self.message_user(
            request, 
            f'{updated} customers promoted to vendor status.'
        )
    promote_to_vendor.short_description = "Promote customers to vendors"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile model"""
    
    list_display = ['user', 'company', 'website', 'newsletter_subscription']
    list_filter = ['newsletter_subscription', 'email_notifications']
    search_fields = ['user__username', 'company']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Profile Information', {
            'fields': ('bio', 'website', 'company')
        }),
        ('Notification Preferences', {
            'fields': ('newsletter_subscription', 'email_notifications', 'sms_notifications')
        }),
    )
