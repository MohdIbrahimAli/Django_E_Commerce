from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordResetView, 
    PasswordResetDoneView, PasswordResetConfirmView, 
    PasswordResetCompleteView
)
from django.core.exceptions import PermissionDenied
from django.db import transaction

from .models import User, UserProfile
from .forms import (
    CustomUserCreationForm, CustomLoginForm, 
    UserUpdateForm, ProfileUpdateForm
)


class CustomLoginView(LoginView):
    """Custom login view with enhanced features"""
    
    form_class = CustomLoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(0)
        
        messages.success(
            self.request, 
            f'Welcome back, {form.get_user().get_short_name()}!'
        )
        return super().form_valid(form)


class RegisterView(CreateView):
    """User registration view"""
    
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('home')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Log the user in
        login(self.request, self.object)
        
        # Create user profile
        UserProfile.objects.create(user=self.object)
        
        messages.success(
            self.request, 
            f'Welcome to our store, {self.object.get_short_name()}! '
            f'Your account has been created successfully.'
        )
        
        return response


class ProfileView(LoginRequiredMixin, UpdateView):
    """User profile view and update"""
    
    model = User
    form_class = UserUpdateForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(
            user=self.request.user
        )
        
        context['profile_form'] = ProfileUpdateForm(
            instance=profile,
            prefix='profile'
        )
        context['user'] = self.request.user
        
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        user_form = self.get_form()
        
        # Get or create profile
        profile, created = UserProfile.objects.get_or_create(
            user=self.request.user
        )
        profile_form = ProfileUpdateForm(
            request.POST,
            instance=profile,
            prefix='profile'
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            return self.form_valid(user_form, profile_form)
        else:
            return self.form_invalid(user_form, profile_form)
    
    def form_valid(self, user_form, profile_form):
        with transaction.atomic():
            user_form.save()
            profile_form.save()
        
        messages.success(
            self.request, 
            'Your profile has been updated successfully!'
        )
        return redirect(self.success_url)
    
    def form_invalid(self, user_form, profile_form):
        context = self.get_context_data()
        context['form'] = user_form
        context['profile_form'] = profile_form
        return self.render_to_response(context)


class CustomLogoutView(LogoutView):
    """Custom logout view"""
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'You have been logged out successfully.')
        return super().dispatch(request, *args, **kwargs)


# Password Reset Views with custom templates
class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    success_url = reverse_lazy('accounts:password_reset_done')
    
    def form_valid(self, form):
        messages.success(
            self.request,
            'Password reset email has been sent to your email address.'
        )
        return super().form_valid(form)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')
    
    def form_valid(self, form):
        messages.success(
            self.request,
            'Your password has been reset successfully! You can now log in.'
        )
        return super().form_valid(form)


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'


@login_required
def dashboard_view(request):
    """Dashboard view for different user roles"""
    
    user = request.user
    context = {
        'user': user,
        'total_orders': 0,
        'recent_orders': [],
    }
    
    # Role-specific dashboard content
    if user.is_customer():
        from orders.models import Order
        orders = Order.objects.filter(user=user)
        context['total_orders'] = orders.count()
        context['recent_orders'] = orders[:5]
        
    elif user.is_vendor():
        from products.models import Product
        from orders.models import OrderItem
        
        products = Product.objects.filter(vendor=user)
        context['total_products'] = products.count()
        context['total_sales'] = OrderItem.objects.filter(
            product__vendor=user
        ).count()
        
    elif user.is_admin_user():
        from products.models import Product
        from orders.models import Order
        
        context['total_users'] = User.objects.count()
        context['total_products'] = Product.objects.count()
        context['total_orders'] = Order.objects.count()
    
    return render(request, 'accounts/dashboard.html', context)


def user_detail_view(request, username):
    """Public user profile view"""
    
    user = get_object_or_404(User, username=username)
    
    # Only show public information
    context = {
        'profile_user': user,
        'is_own_profile': request.user == user,
    }
    
    if user.is_vendor():
        from products.models import Product
        context['products'] = Product.objects.filter(
            vendor=user, 
            is_active=True
        )[:6]
    
    return render(request, 'accounts/user_detail.html', context)