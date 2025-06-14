// Shopping Cart JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeCart();
    initializeQuantityControls();
    initializeCartSummary();
});

// Initialize cart functionality
function initializeCart() {
    // Add to cart forms
    const addToCartForms = document.querySelectorAll('.add-to-cart-form');
    addToCartForms.forEach(form => {
        form.addEventListener('submit', handleAddToCart);
    });
    
    // Remove from cart buttons
    const removeButtons = document.querySelectorAll('.remove-from-cart');
    removeButtons.forEach(button => {
        button.addEventListener('click', handleRemoveFromCart);
    });
    
    // Update cart count on page load
    updateCartCount();
}

// Handle add to cart
function handleAddToCart(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const productId = form.dataset.productId;
    const quantity = formData.get('quantity') || 1;
    
    // Show loading state
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.textContent = 'Adding...';
    submitButton.disabled = true;
    
    fetch('/cart/add/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Product added to cart!', 'success');
            updateCartCount(data.cart_count);
            updateCartSummary(data.cart_total);
            
            // Add animation to cart icon
            animateCartIcon();
        } else {
            showToast(data.message || 'Error adding product to cart', 'error');
        }
    })
    .catch(error => {
        console.error('Add to cart error:', error);
        showToast('Error adding product to cart', 'error');
    })
    .finally(() => {
        // Reset button state
        submitButton.textContent = originalText;
        submitButton.disabled = false;
    });
}

// Handle remove from cart
function handleRemoveFromCart(e) {
    e.preventDefault();
    const button = e.target;
    const itemId = button.dataset.itemId;
    
    if (confirm('Are you sure you want to remove this item from your cart?')) {
        fetch(`/cart/remove/${itemId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remove item from DOM
                const cartItem = button.closest('.cart-item');
                cartItem.style.transition = 'opacity 0.3s ease';
                cartItem.style.opacity = '0';
                setTimeout(() => {
                    cartItem.remove();
                    updateCartSummary();
                }, 300);
                
                updateCartCount(data.cart_count);
                showToast('Item removed from cart', 'info');
            } else {
                showToast(data.message || 'Error removing item', 'error');
            }
        })
        .catch(error => {
            console.error('Remove from cart error:', error);
            showToast('Error removing item from cart', 'error');
        });
    }
}

// Initialize quantity controls
function initializeQuantityControls() {
    const quantityInputs = document.querySelectorAll('.quantity-input');
    quantityInputs.forEach(input => {
        input.addEventListener('change', handleQuantityChange);
        
        // Add plus/minus buttons
        const container = input.parentElement;
        if (!container.querySelector('.quantity-btn')) {
            const minusBtn = document.createElement('button');
            minusBtn.type = 'button';
            minusBtn.className = 'btn btn-sm btn-outline-secondary quantity-btn minus-btn';
            minusBtn.innerHTML = '-';
            
            const plusBtn = document.createElement('button');
            plusBtn.type = 'button';
            plusBtn.className = 'btn btn-sm btn-outline-secondary quantity-btn plus-btn';
            plusBtn.innerHTML = '+';
            
            container.insertBefore(minusBtn, input);
            container.appendChild(plusBtn);
            
            minusBtn.addEventListener('click', () => {
                const currentValue = parseInt(input.value);
                if (currentValue > 1) {
                    input.value = currentValue - 1;
                    input.dispatchEvent(new Event('change'));
                }
            });
            
            plusBtn.addEventListener('click', () => {
                const currentValue = parseInt(input.value);
                const maxValue = parseInt(input.max) || 999;
                if (currentValue < maxValue) {
                    input.value = currentValue + 1;
                    input.dispatchEvent(new Event('change'));
                }
            });
        }
    });
}

// Handle quantity change
function handleQuantityChange(e) {
    const input = e.target;
    const itemId = input.dataset.itemId;
    const quantity = parseInt(input.value);
    
    if (quantity < 1) {
        input.value = 1;
        return;
    }
    
    // Debounce the update
    clearTimeout(window.quantityUpdateTimeout);
    window.quantityUpdateTimeout = setTimeout(() => {
        updateCartItemQuantity(itemId, quantity, input);
    }, 500);
}

// Update cart item quantity
function updateCartItemQuantity(itemId, quantity, input) {
    const originalValue = input.value;
    
    fetch('/cart/update/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            item_id: itemId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update item total
            const cartItem = input.closest('.cart-item');
            const itemTotalElement = cartItem.querySelector('.item-total');
            if (itemTotalElement) {
                itemTotalElement.textContent = `${data.item_total}`;
            }
            
            updateCartCount(data.cart_count);
            updateCartSummary();
            showToast('Cart updated!', 'success');
        } else {
            // Revert to original value
            input.value = originalValue;
            showToast(data.message || 'Error updating cart', 'error');
        }
    })
    .catch(error => {
        console.error('Update cart error:', error);
        input.value = originalValue;
        showToast('Error updating cart', 'error');
    });
}

// Update cart count in header
function updateCartCount(count) {
    if (count === undefined) {
        // Fetch current count
        fetch('/cart/count/')
            .then(response => response.json())
            .then(data => {
                updateCartCountDisplay(data.count);
            });
    } else {
        updateCartCountDisplay(count);
    }
}

// Update cart count display
function updateCartCountDisplay(count) {
    const cartCountElements = document.querySelectorAll('.cart-count');
    cartCountElements.forEach(element => {
        element.textContent = count;
        element.style.display = count > 0 ? 'inline' : 'none';
    });
}

// Update cart summary
function updateCartSummary(total) {
    if (total !== undefined) {
        const totalElements = document.querySelectorAll('.cart-total');
        totalElements.forEach(element => {
            element.textContent = `${total}`;
        });
        return;
    }
    
    // Calculate total from cart items
    let cartTotal = 0;
    const cartItems = document.querySelectorAll('.cart-item');
    
    cartItems.forEach(item => {
        const priceElement = item.querySelector('.item-price');
        const quantityElement = item.querySelector('.quantity-input');
        
        if (priceElement && quantityElement) {
            const price = parseFloat(priceElement.dataset.price || priceElement.textContent.replace(',', ''));
            const quantity = parseInt(quantityElement.value);
            cartTotal += price * quantity;
        }
    });
    
    // Update total display
    const totalElements = document.querySelectorAll('.cart-total');
    totalElements.forEach(element => {
        element.textContent = `${cartTotal.toFixed(2)}`;
    });
}

// Initialize cart summary
function initializeCartSummary() {
    updateCartSummary();
    
    // Apply coupon functionality
    const couponForm = document.getElementById('couponForm');
    if (couponForm) {
        couponForm.addEventListener('submit', handleCouponApply);
    }
    
    // Remove coupon functionality
    const removeCouponBtn = document.getElementById('removeCouponBtn');
    if (removeCouponBtn) {
        removeCouponBtn.addEventListener('click', handleCouponRemove);
    }
}

// Handle coupon apply
function handleCouponApply(e) {
    e.preventDefault();
    const form = e.target;
    const couponCode = form.querySelector('input[name="coupon_code"]').value.trim();
    
    if (!couponCode) {
        showToast('Please enter a coupon code', 'error');
        return;
    }
    
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.textContent = 'Applying...';
    submitButton.disabled = true;
    
    fetch('/cart/apply-coupon/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ coupon_code: couponCode })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Coupon applied successfully!', 'success');
            updateCartSummaryWithDiscount(data);
        } else {
            showToast(data.message || 'Invalid coupon code', 'error');
        }
    })
    .catch(error => {
        console.error('Apply coupon error:', error);
        showToast('Error applying coupon', 'error');
    })
    .finally(() => {
        submitButton.textContent = originalText;
        submitButton.disabled = false;
    });
}

// Handle coupon remove
function handleCouponRemove(e) {
    e.preventDefault();
    
    fetch('/cart/remove-coupon/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Coupon removed', 'info');
            location.reload(); // Refresh to update cart display
        } else {
            showToast(data.message || 'Error removing coupon', 'error');
        }
    })
    .catch(error => {
        console.error('Remove coupon error:', error);
        showToast('Error removing coupon', 'error');
    });
}

// Update cart summary with discount
function updateCartSummaryWithDiscount(data) {
    const summaryContainer = document.querySelector('.cart-summary');
    if (summaryContainer) {
        const discountHTML = `
            <div class="discount-info">
                <div class="d-flex justify-content-between">
                    <span>Discount (${data.coupon_code}):</span>
                    <span class="text-success">-${data.discount_amount}</span>
                </div>
                <button type="button" id="removeCouponBtn" class="btn btn-sm btn-outline-danger mt-2">
                    Remove Coupon
                </button>
            </div>
        `;
        
        // Update or add discount section
        let discountSection = summaryContainer.querySelector('.discount-info');
        if (discountSection) {
            discountSection.outerHTML = discountHTML;
        } else {
            const totalSection = summaryContainer.querySelector('.cart-total').parentElement;
            totalSection.insertAdjacentHTML('beforebegin', discountHTML);
        }
        
        // Update total
        const totalElements = document.querySelectorAll('.cart-total');
        totalElements.forEach(element => {
            element.textContent = `${data.final_total}`;
        });
        
        // Re-initialize remove coupon button
        const newRemoveCouponBtn = document.getElementById('removeCouponBtn');
        if (newRemoveCouponBtn) {
            newRemoveCouponBtn.addEventListener('click', handleCouponRemove);
        }
    }
}

// Animate cart icon when item added
function animateCartIcon() {
    const cartIcon = document.querySelector('.cart-icon');
    if (cartIcon) {
        cartIcon.style.transform = 'scale(1.2)';
        cartIcon.style.transition = 'transform 0.3s ease';
        
        setTimeout(() => {
            cartIcon.style.transform = 'scale(1)';
        }, 300);
    }
}

// Clear cart functionality
function clearCart() {
    if (confirm('Are you sure you want to clear your cart?')) {
        fetch('/cart/clear/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                showToast('Error clearing cart', 'error');
            }
        })
        .catch(error => {
            console.error('Clear cart error:', error);
            showToast('Error clearing cart', 'error');
        });
    }
}

// Save cart for later (for authenticated users)
function saveCartForLater() {
    fetch('/cart/save/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Cart saved for later!', 'success');
        } else {
            showToast(data.message || 'Error saving cart', 'error');
        }
    })
    .catch(error => {
        console.error('Save cart error:', error);
        showToast('Error saving cart', 'error');
    });
}