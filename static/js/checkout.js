// Checkout JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeCheckout();
    initializePaymentMethods();
    initializeAddressForm();
    initializeOrderSummary();
});

// Initialize checkout functionality
function initializeCheckout() {
    const checkoutForm = document.getElementById('checkoutForm');
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', handleCheckoutSubmit);
    }
    
    // Initialize form validation
    initializeFormValidation();
    
    // Initialize step navigation
    initializeStepNavigation();
}

// Handle checkout form submission
function handleCheckoutSubmit(e) {
    e.preventDefault();
    const form = e.target;
    
    // Validate form
    if (!validateCheckoutForm(form)) {
        return;
    }
    
    // Show loading state
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
    submitButton.disabled = true;
    
    // Prepare form data
    const formData = new FormData(form);
    
    fetch('/checkout/process/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.redirect_url) {
                window.location.href = data.redirect_url;
            } else {
                showToast('Order placed successfully!', 'success');
                setTimeout(() => {
                    window.location.href = '/orders/';
                }, 2000);
            }
        } else {
            showToast(data.message || 'Error processing order', 'error');
            if (data.errors) {
                displayFormErrors(data.errors);
            }
        }
    })
    .catch(error => {
        console.error('Checkout error:', error);
        showToast('Error processing order', 'error');
    })
    .finally(() => {
        submitButton.innerHTML = originalText;
        submitButton.disabled = false;
    });
}

// Validate checkout form
function validateCheckoutForm(form) {
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });
    
    // Validate email
    const emailField = form.querySelector('input[type="email"]');
    if (emailField && emailField.value && !isValidEmail(emailField.value)) {
        showFieldError(emailField, 'Please enter a valid email address');
        isValid = false;
    }
    
    // Validate phone
    const phoneField = form.querySelector('input[name="phone"]');
    if (phoneField && phoneField.value && !isValidPhone(phoneField.value)) {
        showFieldError(phoneField, 'Please enter a valid phone number');
        isValid = false;
    }
    
    return isValid;
}

// Show field error
function showFieldError(field, message) {
    clearFieldError(field);
    field.classList.add('is-invalid');
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

// Clear field error
function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

// Display form errors
function displayFormErrors(errors) {
    Object.keys(errors).forEach(fieldName => {
        const field = document.querySelector(`[name="${fieldName}"]`);
        if (field) {
            showFieldError(field, errors[fieldName][0]);
        }
    });
}

// Initialize payment methods
function initializePaymentMethods() {
    const paymentRadios = document.querySelectorAll('input[name="payment_method"]');
    paymentRadios.forEach(radio => {
        radio.addEventListener('change', handlePaymentMethodChange);
    });
    
    // Initialize Stripe if available
    if (typeof Stripe !== 'undefined' && window.stripePublicKey) {
        initializeStripe();
    }
    
    // Initialize Razorpay if available
    if (typeof Razorpay !== 'undefined' && window.razorpayKeyId) {
        initializeRazorpay();
    }
}

// Handle payment method change
function handlePaymentMethodChange(e) {
    const paymentMethod = e.target.value;
    const paymentDetails = document.querySelectorAll('.payment-details');
    
    // Hide all payment details
    paymentDetails.forEach(detail => {
        detail.style.display = 'none';
    });
    
    // Show selected payment method details
    const selectedDetail = document.getElementById(`${paymentMethod}-details`);
    if (selectedDetail) {
        selectedDetail.style.display = 'block';
    }
}

// Initialize Stripe
function initializeStripe() {
    const stripe = Stripe(window.stripePublicKey);
    const elements = stripe.elements();
    
    // Create card element
    const cardElement = elements.create('card', {
        style: {
            base: {
                fontSize: '16px',
                color: '#424770',
                '::placeholder': {
                    color: '#aab7c4',
                },
            },
        },
    });
    
    const cardContainer = document.getElementById('card-element');
    if (cardContainer) {
        cardElement.mount('#card-element');
        
        // Handle real-time validation errors from the card Element
        cardElement.on('change', function(event) {
            const displayError = document.getElementById('card-errors');
            if (event.error) {
                displayError.textContent = event.error.message;
            } else {
                displayError.textContent = '';
            }
        });
        
        // Store elements for later use
        window.stripeElements = { stripe, elements, cardElement };
    }
}

// Initialize Razorpay
function initializeRazorpay() {
    // Razorpay will be initialized when payment is processed
    window.razorpayReady = true;
}

// Initialize address form
function initializeAddressForm() {
    const sameAsShippingCheckbox = document.getElementById('same_as_shipping');
    if (sameAsShippingCheckbox) {
        sameAsShippingCheckbox.addEventListener('change', handleSameAsShippingChange);
    }
    
    const addressSelects = document.querySelectorAll('.address-select');
    addressSelects.forEach(select => {
        select.addEventListener('change', handleAddressSelectChange);
    });
    
    // Initialize country/state/city dropdowns
    initializeLocationDropdowns();
}

// Handle same as shipping address change
function handleSameAsShippingChange(e) {
    const billingAddressForm = document.getElementById('billing-address-form');
    if (billingAddressForm) {
        if (e.target.checked) {
            billingAddressForm.style.display = 'none';
            copyShippingToBilling();
        } else {
            billingAddressForm.style.display = 'block';
        }
    }
}

// Copy shipping address to billing
function copyShippingToBilling() {
    const shippingFields = document.querySelectorAll('[name^="shipping_"]');
    shippingFields.forEach(field => {
        const billingFieldName = field.name.replace('shipping_', 'billing_');
        const billingField = document.querySelector(`[name="${billingFieldName}"]`);
        if (billingField) {
            billingField.value = field.value;
        }
    });
}

// Handle address select change
function handleAddressSelectChange(e) {
    const addressId = e.target.value;
    const addressType = e.target.dataset.addressType;
    
    if (addressId === 'new') {
        document.getElementById(`${addressType}-address-form`).style.display = 'block';
    } else if (addressId) {
        // Load selected address
        loadSavedAddress(addressId, addressType);
        document.getElementById(`${addressType}-address-form`).style.display = 'none';
    }
}

// Load saved address
function loadSavedAddress(addressId, addressType) {
    fetch(`/api/address/${addressId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const address = data.address;
                Object.keys(address).forEach(key => {
                    const field = document.querySelector(`[name="${addressType}_${key}"]`);
                    if (field) {
                        field.value = address[key];
                    }
                });
            }
        })
        .catch(error => {
            console.error('Load address error:', error);
        });
}

// Initialize location dropdowns
function initializeLocationDropdowns() {
    const countrySelects = document.querySelectorAll('.country-select');
    countrySelects.forEach(select => {
        select.addEventListener('change', function() {
            const stateSelect = this.parentElement.parentElement.querySelector('.state-select');
            loadStates(this.value, stateSelect);
        });
    });
    
    const stateSelects = document.querySelectorAll('.state-select');
    stateSelects.forEach(select => {
        select.addEventListener('change', function() {
            const citySelect = this.parentElement.parentElement.querySelector('.city-select');
            loadCities(this.value, citySelect);
        });
    });
}

// Load states based on country
function loadStates(countryId, stateSelect) {
    if (!countryId || !stateSelect) return;
    
    stateSelect.innerHTML = '<option value="">Loading...</option>';
    
    fetch(`/api/states/?country=${countryId}`)
        .then(response => response.json())
        .then(data => {
            stateSelect.innerHTML = '<option value="">Select State</option>';
            data.states.forEach(state => {
                const option = document.createElement('option');
                option.value = state.id;
                option.textContent = state.name;
                stateSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Load states error:', error);
            stateSelect.innerHTML = '<option value="">Error loading states</option>';
        });
}

// Load cities based on state
function loadCities(stateId, citySelect) {
    if (!stateId || !citySelect) return;
    
    citySelect.innerHTML = '<option value="">Loading...</option>';
    
    fetch(`/api/cities/?state=${stateId}`)
        .then(response => response.json())
        .then(data => {
            citySelect.innerHTML = '<option value="">Select City</option>';
            data.cities.forEach(city => {
                const option = document.createElement('option');
                option.value = city.id;
                option.textContent = city.name;
                citySelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Load cities error:', error);
            citySelect.innerHTML = '<option value="">Error loading cities</option>';
        });
}

// Initialize order summary
function initializeOrderSummary() {
    updateOrderSummary();
    
    // Initialize shipping method selection
    const shippingRadios = document.querySelectorAll('input[name="shipping_method"]');
    shippingRadios.forEach(radio => {
        radio.addEventListener('change', handleShippingMethodChange);
    });
}

// Handle shipping method change
function handleShippingMethodChange(e) {
    const shippingCost = parseFloat(e.target.dataset.cost || 0);
    updateOrderSummary(shippingCost);
}

// Update order summary
function updateOrderSummary(shippingCost = 0) {
    fetch('/api/cart/summary/')
        .then(response => response.json())
        .then(data => {
            const subtotal = data.subtotal;
            const tax = data.tax;
            const total = subtotal + shippingCost + tax;
            
            // Update summary display
            const subtotalElement = document.getElementById('order-subtotal');
            const shippingElement = document.getElementById('order-shipping');
            const taxElement = document.getElementById('order-tax');
            const totalElement = document.getElementById('order-total');
            
            if (subtotalElement) subtotalElement.textContent = `${subtotal.toFixed(2)}`;
            if (shippingElement) shippingElement.textContent = `${shippingCost.toFixed(2)}`;
            if (taxElement) taxElement.textContent = `${tax.toFixed(2)}`;
            if (totalElement) totalElement.textContent = `${total.toFixed(2)}`;
        })
        .catch(error => {
            console.error('Update order summary error:', error);
        });
}

// Initialize step navigation
function initializeStepNavigation() {
    const stepButtons = document.querySelectorAll('.step-btn');
    stepButtons.forEach(button => {
        button.addEventListener('click', handleStepNavigation);
    });
    
    const nextButtons = document.querySelectorAll('.next-step');
    nextButtons.forEach(button => {
        button.addEventListener('click', handleNextStep);
    });
    
    const prevButtons = document.querySelectorAll('.prev-step');
    prevButtons.forEach(button => {
        button.addEventListener('click', handlePrevStep);
    });
}

// Handle step navigation
function handleStepNavigation(e) {
    const targetStep = e.target.dataset.step;
    showStep(targetStep);
}

// Handle next step
function handleNextStep(e) {
    const currentStep = e.target.dataset.currentStep;
    const nextStep = parseInt(currentStep) + 1;
    
    // Validate current step before proceeding
    if (validateStep(currentStep)) {
        showStep(nextStep);
    }
}

// Handle previous step
function handlePrevStep(e) {
    const currentStep = e.target.dataset.currentStep;
    const prevStep = parseInt(currentStep) - 1;
    showStep(prevStep);
}

// Show specific step
function showStep(stepNumber) {
    const steps = document.querySelectorAll('.checkout-step');
    const stepIndicators = document.querySelectorAll('.step-indicator');
    
    steps.forEach((step, index) => {
        if (index + 1 == stepNumber) {
            step.style.display = 'block';
            step.classList.add('active');
        } else {
            step.style.display = 'none';
            step.classList.remove('active');
        }
    });
    
    stepIndicators.forEach((indicator, index) => {
        if (index + 1 <= stepNumber) {
            indicator.classList.add('completed');
        } else {
            indicator.classList.remove('completed');
        }
    });
}

// Validate step
function validateStep(stepNumber) {
    const step = document.querySelector(`[data-step="${stepNumber}"]`);
    if (!step) return true;
    
    const requiredFields = step.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            showFieldError(field, 'This field is required');
            isValid = false;
        } else {
            clearFieldError(field);
        }
    });
    
    return isValid;
}

// Utility functions
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidPhone(phone) {
    const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
    return phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ''));
}

// Initialize form validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}