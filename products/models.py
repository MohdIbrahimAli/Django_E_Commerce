from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from PIL import Image
import os

User = get_user_model()

class Category(models.Model):
    """Product categories"""
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='children'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:category_detail', kwargs={'slug': self.slug})


class Brand(models.Model):
    """Product brands"""
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='brands/', null=True, blank=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Main product model"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('out_of_stock', 'Out of Stock'),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Original price for discount display"
    )
    cost_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Cost price for profit calculation"
    )
    
    # Inventory
    sku = models.CharField(max_length=100, unique=True)
    stock = models.PositiveIntegerField(default=0)
    track_inventory = models.BooleanField(default=True)
    allow_backorders = models.BooleanField(default=False)
    
    # Relationships
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='products'
    )
    brand = models.ForeignKey(
        Brand, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='products'
    )
    vendor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='products',
        limit_choices_to={'role__in': ['vendor', 'admin']}
    )
    
    # Product attributes
    weight = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Weight in kg"
    )
    dimensions = models.CharField(
        max_length=100, 
        blank=True,
        help_text="L x W x H in cm"
    )
    
    # SEO and marketing
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    featured = models.BooleanField(default=False)
    
    # Status and timestamps
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'is_active']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['vendor', 'status']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Auto-generate SKU if not provided
        if not self.sku:
            self.sku = f"PRD{self.id or ''}{slugify(self.name)[:10].upper()}"
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})
    
    @property
    def is_in_stock(self):
        """Check if product is in stock"""
        if not self.track_inventory:
            return True
        return self.stock > 0 or self.allow_backorders
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        if self.compare_price and self.compare_price > self.price:
            return int(((self.compare_price - self.price) / self.compare_price) * 100)
        return 0
    
    @property
    def main_image(self):
        """Get the main product image"""
        main_img = self.images.filter(is_main=True).first()
        return main_img.image if main_img else None
    
    def can_be_ordered(self, quantity=1):
        """Check if product can be ordered in given quantity"""
        if not self.is_active or self.status != 'active':
            return False
        
        if not self.track_inventory:
            return True
        
        if self.stock >= quantity:
            return True
        
        return self.allow_backorders


class ProductImage(models.Model):
    """Product images"""
    
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='images'
    )
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_main = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"Image for {self.product.name}"
    
    def save(self, *args, **kwargs):
        # Ensure only one main image per product
        if self.is_main:
            ProductImage.objects.filter(
                product=self.product, 
                is_main=True
            ).update(is_main=False)
        
        super().save(*args, **kwargs)
        
        # Resize image
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 800 or img.width > 800:
                output_size = (800, 800)
                img.thumbnail(output_size)
                img.save(self.image.path)


class ProductAttribute(models.Model):
    """Product attributes like color, size, etc."""
    
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name


class ProductAttributeValue(models.Model):
    """Product attribute values"""
    
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='attributes'
    )
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE)
    value = models.CharField(max_length=200)
    
    class Meta:
        unique_together = ['product', 'attribute']
    
    def __str__(self):
        return f"{self.product.name} - {self.attribute.name}: {self.value}"


class Review(models.Model):
    """Product reviews"""
    
    RATING_CHOICES = [(i, i) for i in range(1, 6)]
    
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='reviews'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=200)
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['product', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}/5)"