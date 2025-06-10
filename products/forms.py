from django import forms
from django.forms import inlineformset_factory
from .models import Product, ProductImage, Category, Brand, Review

class ProductForm(forms.ModelForm):
    """Form for creating/editing products"""
    
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'brand', 'description', 'short_description',
            'price', 'compare_price', 'sku', 'stock', 'track_inventory',
            'allow_backorders', 'weight', 'dimensions', 'status',
            'featured', 'meta_title', 'meta_description'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'brand': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 8}),
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'compare_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'dimensions': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'meta_title': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'track_inventory': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'allow_backorders': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter categories and brands to active only
        self.fields['category'].queryset = Category.objects.filter(is_active=True)
        self.fields['brand'].queryset = Brand.objects.filter(is_active=True)
        
        # Set vendor if creating new product
        if user and not self.instance.pk:
            self.instance.vendor = user


class ProductImageForm(forms.ModelForm):
    """Form for product images"""
    
    class Meta:
        model = ProductImage
        fields = ['image', 'alt_text', 'is_main']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'alt_text': forms.TextInput(attrs={'class': 'form-control'}),
            'is_main': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# Formset for multiple product images
ProductImageFormSet = inlineformset_factory(
    Product,
    ProductImage,
    form=ProductImageForm,
    extra=3,
    can_delete=True
)


class ProductSearchForm(forms.Form):
    """Product search and filter form"""
    
    query = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search products...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.filter(is_active=True),
        required=False,
        empty_label="All Brands",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    min_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Price'
        })
    )
    max_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Price'
        })
    )
    in_stock_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    SORT_CHOICES = [
        ('name', 'Name A-Z'),
        ('-name', 'Name Z-A'),
        ('price', 'Price Low to High'),
        ('-price', 'Price High to Low'),
        ('-created_at', 'Newest First'),
        ('created_at', 'Oldest First'),
    ]
    
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial='-created_at',
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class ReviewForm(forms.ModelForm):
    """Form for product reviews"""
    
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=Review.RATING_CHOICES,
                attrs={'class': 'form-control'}
            ),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Review title'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write your review here...'
            }),
        }


class CategoryForm(forms.ModelForm):
    """Form for creating/editing categories"""
    
    class Meta:
        model = Category
        fields = ['name', 'description', 'parent', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclude self from parent choices when editing
        if self.instance and self.instance.pk:
            self.fields['parent'].queryset = Category.objects.exclude(
                pk=self.instance.pk
            )


class BrandForm(forms.ModelForm):
    """Form for creating/editing brands"""
    
    class Meta:
        model = Brand
        fields = ['name', 'description', 'logo', 'website']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
        }