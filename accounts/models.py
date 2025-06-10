from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from PIL import Image

class User(AbstractUser):
    """Extended User model with roles and profile information"""
    
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('admin', 'Administrator'),
    ]
    
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='customer',
        help_text='User role determines permissions'
    )
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(
        upload_to='avatars/', 
        null=True, 
        blank=True,
        help_text='Profile picture'
    )
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def get_absolute_url(self):
        return reverse('accounts:profile')
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip()
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name or self.username
    
    # Role-based permission methods
    def is_customer(self):
        return self.role == 'customer'
    
    def is_vendor(self):
        return self.role == 'vendor'
    
    def is_admin_user(self):
        return self.role == 'admin' or self.is_superuser
    
    def can_create_products(self):
        return self.role in ['vendor', 'admin'] or self.is_superuser
    
    def can_manage_orders(self):
        return self.role in ['vendor', 'admin'] or self.is_superuser
    
    def can_view_all_orders(self):
        return self.role == 'admin' or self.is_superuser
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize avatar image
        if self.avatar:
            img = Image.open(self.avatar.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.avatar.path)


class UserProfile(models.Model):
    """Extended profile information for users"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    website = models.URLField(blank=True)
    company = models.CharField(max_length=100, blank=True)
    newsletter_subscription = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"