from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, OrderStatusHistory

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['get_cost']
    
    def get_cost(self, obj):
        return f"${obj.get_cost():.2f}"
    get_cost.short_description = 'Total Cost'

class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['created_at']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_id', 'user', 'full_name', 'status', 
        'payment_status', 'total_amount', 'created_at'
    ]
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['order_id', 'user__username', 'first_name', 'last_name', 'email']
    readonly_fields = ['order_id', 'created_at', 'updated_at', 'total_items']
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'user', 'status', 'payment_status')
        }),
        ('Customer Information', {
            'fields': (
                ('first_name', 'last_name'),
                ('email', 'phone'),
                'address',
                ('city', 'postal_code', 'country')
            )
        }),
        ('Order Details', {
            'fields': (
                'total_amount', 'shipping_cost', 'tax_amount',
                'notes', 'admin_notes'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'shipped_at', 'delivered_at')
        }),
    )
    
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered']
    
    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} orders marked as processing.')
    mark_as_processing.short_description = "Mark selected orders as processing"
    
    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='shipped')
        self.message_user(request, f'{updated} orders marked as shipped.')
    mark_as_shipped.short_description = "Mark selected orders as shipped"
    
    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(request, f'{updated} orders marked as delivered.')
    mark_as_delivered.short_description = "Mark selected orders as delivered"

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'get_cost']
    list_filter = ['order__status', 'order__created_at']
    search_fields = ['order__order_id', 'product__name']