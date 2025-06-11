from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Product URLs
    path('', views.ProductListView.as_view(), name='product_list'),
    path('create/', views.ProductCreateView.as_view(), name='product_create'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('<slug:slug>/edit/', views.ProductUpdateView.as_view(), name='product_update'),
    path('<slug:slug>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    
    # Category URLs
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    
    # Brand URLs
    path('brand/<slug:slug>/', views.BrandDetailView.as_view(), name='brand_detail'),
    
    # Review URLs
    path('<slug:slug>/review/', views.add_review, name='add_review'),
    
    # Search
    path('search/', views.product_search, name='product_search'),
]