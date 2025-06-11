from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Product, Category, Brand, Review
from .forms import ProductForm, ProductImageFormSet, ProductSearchForm, ReviewForm
from cart.forms import CartAddProductForm

class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True, status='active')
        
        # Search functionality
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query) |
                Q(short_description__icontains=query)
            )
        
        # Category filter
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Brand filter
        brand_slug = self.request.GET.get('brand')
        if brand_slug:
            queryset = queryset.filter(brand__slug=brand_slug)
        
        # Price filter
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Sort
        sort_by = self.request.GET.get('sort', '-created_at')
        if sort_by:
            queryset = queryset.order_by(sort_by)
        
        return queryset.select_related('category', 'brand')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['brands'] = Brand.objects.filter(is_active=True)
        context['search_form'] = ProductSearchForm(self.request.GET)
        context['featured_products'] = Product.objects.filter(
            is_active=True, 
            status='active', 
            featured=True
        )[:4]
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        
        # Add to cart form
        context['cart_product_form'] = CartAddProductForm()
        
        # Product reviews
        context['reviews'] = product.reviews.filter(is_approved=True)
        context['average_rating'] = product.reviews.filter(
            is_approved=True
        ).aggregate(Avg('rating'))['rating__avg'] or 0
        
        # Review form for authenticated users
        if self.request.user.is_authenticated:
            # Check if user has already reviewed this product
            existing_review = product.reviews.filter(user=self.request.user).first()
            if not existing_review:
                context['review_form'] = ReviewForm()
        
        # Related products
        context['related_products'] = Product.objects.filter(
            category=product.category,
            is_active=True,
            status='active'
        ).exclude(pk=product.pk)[:4]
        
        return context

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_create.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.vendor = self.request.user
        response = super().form_valid(form)
        
        # Create image formset
        image_formset = ProductImageFormSet(
            self.request.POST, 
            self.request.FILES, 
            instance=self.object
        )
        if image_formset.is_valid():
            image_formset.save()
        
        messages.success(self.request, 'Product created successfully!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['image_formset'] = ProductImageFormSet(
                self.request.POST, 
                self.request.FILES
            )
        else:
            context['image_formset'] = ProductImageFormSet()
        return context

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_edit.html'
    
    def get_queryset(self):
        # Users can only edit their own products
        return Product.objects.filter(vendor=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['image_formset'] = ProductImageFormSet(
                self.request.POST, 
                self.request.FILES, 
                instance=self.object
            )
        else:
            context['image_formset'] = ProductImageFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Handle image formset
        image_formset = ProductImageFormSet(
            self.request.POST, 
            self.request.FILES, 
            instance=self.object
        )
        if image_formset.is_valid():
            image_formset.save()
        
        messages.success(self.request, 'Product updated successfully!')
        return response

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products:product_list')
    
    def get_queryset(self):
        return Product.objects.filter(vendor=self.request.user)

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'products/category_detail.html'
    context_object_name = 'category'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.object
        
        # Get products in this category
        products = Product.objects.filter(
            category=category,
            is_active=True,
            status='active'
        ).select_related('brand')
        
        # Pagination
        paginator = Paginator(products, 12)
        page_number = self.request.GET.get('page')
        context['products'] = paginator.get_page(page_number)
        
        return context

class BrandDetailView(DetailView):
    model = Brand
    template_name = 'products/brand_detail.html'
    context_object_name = 'brand'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        brand = self.object
        
        # Get products from this brand
        products = Product.objects.filter(
            brand=brand,
            is_active=True,
            status='active'
        ).select_related('category')
        
        # Pagination
        paginator = Paginator(products, 12)
        page_number = self.request.GET.get('page')
        context['products'] = paginator.get_page(page_number)
        
        return context

def product_search(request):
    """Advanced product search"""
    form = ProductSearchForm(request.GET)
    products = Product.objects.filter(is_active=True, status='active')
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        brand = form.cleaned_data.get('brand')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        in_stock_only = form.cleaned_data.get('in_stock_only')
        sort_by = form.cleaned_data.get('sort_by')
        
        if query:
            products = products.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query) |
                Q(short_description__icontains=query)
            )
        
        if category:
            products = products.filter(category=category)
        
        if brand:
            products = products.filter(brand=brand)
        
        if min_price is not None:
            products = products.filter(price__gte=min_price)
        
        if max_price is not None:
            products = products.filter(price__lte=max_price)
        
        if in_stock_only:
            products = products.filter(stock__gt=0)
        
        if sort_by:
            products = products.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'products/product_search.html', {
        'form': form,
        'products': page_obj,
        'page_obj': page_obj,
        'query': request.GET.get('query', ''),
    })

@login_required
def add_review(request, slug):
    """Add a review for a product"""
    product = get_object_or_404(Product, slug=slug)
    
    # Check if user has already reviewed this product
    existing_review = Review.objects.filter(product=product, user=request.user).first()
    if existing_review:
        messages.error(request, 'You have already reviewed this product.')
        return redirect('products:product_detail', slug=slug)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            
            messages.success(request, 'Your review has been added successfully!')
            return redirect('products:product_detail', slug=slug)
    else:
        form = ReviewForm()
    
    return render(request, 'products/add_review.html', {
        'form': form,
        'product': product
    })