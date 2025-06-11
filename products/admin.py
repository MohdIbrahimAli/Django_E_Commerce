from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Brand, Product, ProductImage, ProductAttribute, ProductAttributeValue, Review

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Preview'

class ProductAttributeValueInline(admin.TabularInline):
    model = ProductAttributeValue
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'website']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'brand', 'price', 'stock', 
        'status', 'is_active', 'featured', 'created_at'
    ]
    list_filter = ['status', 'is_active', 'featured', 'category', 'brand', 'created_at']
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['status', 'is_active', 'featured']
    inlines = [ProductImageInline, ProductAttributeValueInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'short_description', 'category', 'brand', 'vendor')
        }),
        ('Pricing', {
            'fields': ('price', 'compare_price', 'cost_price')
        }),
        ('Inventory', {
            'fields': ('sku', 'stock', 'track_inventory', 'allow_backorders')
        }),
        ('Product Details', {
            'fields': ('weight', 'dimensions')
        }),
        ('SEO & Marketing', {
            'fields': ('meta_title', 'meta_description', 'featured')
        }),
        ('Status', {
            'fields': ('status', 'is_active')
        }),
    )
    
    actions = ['mark_as_active', 'mark_as_inactive', 'mark_as_featured']
    
    def mark_as_active(self, request, queryset):
        updated = queryset.update(status='active', is_active=True)
        self.message_user(request, f'{updated} products marked as active.')
    mark_as_active.short_description = "Mark selected products as active"
    
    def mark_as_inactive(self, request, queryset):
        updated = queryset.update(status='inactive', is_active=False)
        self.message_user(request, f'{updated} products marked as inactive.')
    mark_as_inactive.short_description = "Mark selected products as inactive"
    
    def mark_as_featured(self, request, queryset):
        updated = queryset.update(featured=True)
        self.message_user(request, f'{updated} products marked as featured.')
    mark_as_featured.short_description = "Mark selected products as featured"

@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'is_approved', 'is_verified_purchase', 'created_at']
    list_filter = ['rating', 'is_approved', 'is_verified_purchase', 'created_at']
    search_fields = ['product__name', 'user__username', 'title', 'comment']
    list_editable = ['is_approved']
    readonly_fields = ['created_at', 'updated_at']