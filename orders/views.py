from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from cart.cart import Cart
from .models import Order, OrderItem, OrderStatusHistory
from .forms import OrderCreateForm

@login_required
def order_create(request):
    """Create a new order from cart"""
    cart = Cart(request)
    
    if len(cart) == 0:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart:cart_detail')
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST, user=request.user)
        if form.is_valid():
            with transaction.atomic():
                # Create order
                order = form.save(commit=False)
                order.user = request.user
                order.total_amount = cart.get_total_price()
                order.save()
                
                # Create order items
                for item in cart:
                    OrderItem.objects.create(
                        order=order,
                        product=item['product'],
                        price=item['price'],
                        quantity=item['quantity']
                    )
                
                # Create initial status history
                OrderStatusHistory.objects.create(
                    order=order,
                    status='pending',
                    notes='Order created',
                    changed_by=request.user
                )
                
                # Clear the cart
                cart.clear()
                
                messages.success(
                    request,
                    f'Your order {order.order_id} has been placed successfully!'
                )
                return redirect('orders:order_success', order_id=order.order_id)
    else:
        form = OrderCreateForm(user=request.user)
    
    return render(request, 'orders/order_create.html', {
        'cart': cart,
        'form': form
    })

@login_required
def order_success(request, order_id):
    """Order success page"""
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})

@login_required
def order_list(request):
    """List user's orders"""
    orders = Order.objects.filter(user=request.user)
    
    # Pagination
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'orders/order_list.html', {
        'page_obj': page_obj,
        'orders': page_obj
    })

@login_required
def order_detail(request, order_id):
    """Order detail view"""
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    
    # Allow admin/vendor to view all orders
    if not (request.user == order.user or request.user.is_admin_user()):
        messages.error(request, 'You do not have permission to view this order.')
        return redirect('orders:order_list')
    
    return render(request, 'orders/order_detail.html', {'order': order})