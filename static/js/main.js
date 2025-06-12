// E-Commerce Site JavaScript
document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize all components
    initializeProductImages();
    initializeQuantityControls();
    initializeSearch();
    initializeMobileNav();
    initializeAlerts();
    initializeRatings();
    initializeProductFilters();
    
    // Product Image Gallery
    function initializeProductImages() {
        const thumbnails = document.querySelectorAll('.product-thumbnail');
        const mainImage = document.querySelector('.main-product-image');
        
        thumbnails.forEach(thumb => {
            thumb.addEventListener('click', function() {
                const newSrc = this.dataset.image;
                if (mainImage && newSrc) {
                    mainImage.src = newSrc;
                    
                    // Update active thumbnail
                    thumbnails.forEach(t => t.classList.remove('active'));
                    this.classList.add('active');
                }
            });
        });
    }
    
    // Quantity Controls
    function initializeQuantityControls() {
        const quantityControls = document.querySelectorAll('.quantity-controls');
        
        quantityControls.forEach(control => {
            const minusBtn = control.querySelector('.quantity-minus');
            const plusBtn = control.querySelector('.quantity-plus');
            const input = control.querySelector('.quantity-input');
            
            if (minusBtn && plusBtn && input) {
                minusBtn.addEventListener('click', function() {
                    const currentValue = parseInt(input.value) || 1;
                    if (currentValue > 1) {
                        input.value = currentValue - 1;
                        updateCartItem(input);
                    }
                });
                
                plusBtn.addEventListener('click', function() {
                    const currentValue = parseInt(input.value) || 1;
                    const maxStock = parseInt(input.dataset.max) || 999;
                    if (currentValue < maxStock) {
                        input.value = currentValue + 1;
                        updateCartItem(input);
                    }
                });
                
                input.addEventListener('change', function() {
                    const value = parseInt(this.value) || 1;
                    const maxStock = parseInt(this.dataset.max) || 999;
                    
                    if (value < 1) {
                        this.value = 1;
                    } else if (value > maxStock) {
                        this.value = maxStock;
                        showAlert('Maximum stock available: ' + maxStock, 'warning');
                    }
                    
                    updateCartItem(this);
                });
            }
        });
    }
    
    // Update cart item via AJAX
    function updateCartItem(input) {
        const form = input.closest('form');
        if (form && form.dataset.updateUrl) {
            const formData = new FormData(form);
            
            fetch(form.dataset.updateUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateCartTotals(data);
                } else {
                    showAlert(data.error || 'Error updating cart', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('Error updating cart', 'danger');
            });
        }
    }
    
    // Update cart totals in DOM
    function updateCartTotals(data) {
        const elements = {
            subtotal: document.querySelector('.cart-subtotal'),
            total: document.querySelector('.cart-total'),
            count: document.querySelector('.cart-count')
        };
        
        if (elements.subtotal && data.subtotal) {
            elements.subtotal.textContent = data.subtotal;
        }
        if (elements.total && data.total) {
            elements.total.textContent = data.total;
        }
        if (elements.count && data.count !== undefined) {
            elements.count.textContent = data.count;
            elements.count.style.display = data.count > 0 ? 'flex' : 'none';
        }
    }
    
    // Search functionality
    function initializeSearch() {
        const searchForm = document.querySelector('.search-form');
        const searchInput = document.querySelector('.search-input');
        const searchSuggestions = document.querySelector('.search-suggestions');
        
        if (searchInput) {
            let searchTimeout;
            
            searchInput.addEventListener('input', function() {
                clearTimeout(searchTimeout);
                const query = this.value.trim();
                
                if (query.length >= 2) {
                    searchTimeout = setTimeout(() => {
                        fetchSearchSuggestions(query);
                    }, 300);
                } else {
                    hideSearchSuggestions();
                }
            });
            
            // Hide suggestions when clicking outside
            document.addEventListener('click', function(e) {
                if (!searchForm.contains(e.target)) {
                    hideSearchSuggestions();
                }
            });
        }
    }
    
    // Fetch search suggestions
    function fetchSearchSuggestions(query) {
        fetch(`/products/search-suggestions/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                displaySearchSuggestions(data.suggestions);
            })
            .catch(error => {
                console.error('Search error:', error);
            });
    }
    
    // Display search suggestions
    function displaySearchSuggestions(suggestions) {
        const container = document.querySelector('.search-suggestions');
        if (!container) return;
        
        if (suggestions.length === 0) {
            hideSearchSuggestions();
            return;
        }
        
        container.innerHTML = suggestions.map(item => `
            <a href="${item.url}" class="search-suggestion-item">
                <img src="${item.image}" alt="${item.name}" class="suggestion-image">
                <div class="suggestion-content">
                    <div class="suggestion-title">${item.name}</div>
                    <div class="suggestion-price">${item.price}</div>
                </div>
            </a>
        `).join('');
        
        container.style.display = 'block';
    }
    
    // Hide search suggestions
    function hideSearchSuggestions() {
        const container = document.querySelector('.search-suggestions');
        if (container) {
            container.style.display = 'none';
        }
    }
    
    // Mobile navigation
    function initializeMobileNav() {
        const mobileToggle = document.querySelector('.mobile-nav-toggle');
        const mobileNav = document.querySelector('.mobile-nav');
        const mobileOverlay = document.querySelector('.mobile-nav-overlay');
        
        if (mobileToggle && mobileNav) {
            mobileToggle.addEventListener('click', function() {
                mobileNav.classList.toggle('active');
                document.body.classList.toggle('mobile-nav-open');
            });
            
            if (mobileOverlay) {
                mobileOverlay.addEventListener('click', function() {
                    mobileNav.classList.remove('active');
                    document.body.classList.remove('mobile-nav-open');
                });
            }
        }
    }
    
    // Alert system
    function initializeAlerts() {
        const alerts = document.querySelectorAll('.alert');
        
        alerts.forEach(alert => {
            const closeBtn = alert.querySelector('.alert-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', function() {
                    alert.style.opacity = '0';
                    setTimeout(() => {
                        alert.remove();
                    }, 300);
                });
            }
            
            // Auto-hide success alerts
            if (alert.classList.contains('alert-success')) {
                setTimeout(() => {
                    alert.style.opacity = '0';
                    setTimeout(() => {
                        alert.remove();
                    }, 300);
                }, 5000);
            }
        });
    }
    
    // Show alert
    function showAlert(message, type = 'info') {
        const alertContainer = document.querySelector('.alert-container') || document.body;
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="alert-close">&times;</button>
        `;
        
        alertContainer.appendChild(alert);
        
        // Initialize close functionality
        const closeBtn = alert.querySelector('.alert-close');
        closeBtn.addEventListener('click', function() {
            alert.remove();
        });
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }
    
    // Star ratings
    function initializeRatings() {
        const ratingInputs = document.querySelectorAll('.rating-input');
        
        ratingInputs.forEach(container => {
            const stars = container.querySelectorAll('.rating-star');
            const input = container.querySelector('input[type="hidden"]');
            
            stars.forEach((star, index) => {
                star.addEventListener('click', function() {
                    const rating = index + 1;
                    input.value = rating;
                    
                    // Update visual state
                    stars.forEach((s, i) => {
                        s.classList.toggle('active', i < rating);
                    });
                });
                
                star.addEventListener('mouseenter', function() {
                    const rating = index + 1;
                    stars.forEach((s, i) => {
                        s.classList.toggle('hover', i < rating);
                    });
                });
            });
            
            container.addEventListener('mouseleave', function() {
                stars.forEach(s => s.classList.remove('hover'));
            });
        });
    }
    
    // Product filters
    function initializeProductFilters() {
        const filterForm = document.querySelector('.filter-form');
        const filterInputs = document.querySelectorAll('.filter-input');
        
        if (filterForm) {
            filterInputs.forEach(input => {
                input.addEventListener('change', function() {
                    // Auto-submit form on filter change
                    setTimeout(() => {
                        filterForm.submit();
                    }, 100);
                });
            });
        }
        
        // Price range slider
        const priceSlider = document.querySelector('.price-slider');
        if (priceSlider) {
            const minInput = document.querySelector('#min-price');
            const maxInput = document.querySelector('#max-price');
            
            // Initialize price range functionality
            initializePriceRange(priceSlider, minInput, maxInput);
        }
    }
    
    // Price range slider
    function initializePriceRange(slider, minInput, maxInput) {
        // This would typically use a library like noUiSlider
        // For now, we'll use simple input handling
        
        function updatePriceRange() {
            const min = parseFloat(minInput.value) || 0;
            const max = parseFloat(maxInput.value) || 10000;
            
            if (min > max) {
                minInput.value = max;
            }
        }
        
        minInput.addEventListener('change', updatePriceRange);
        maxInput.addEventListener('change', updatePriceRange);
    }
    
    // Add to cart functionality
    window.addToCart = function(productId, quantity = 1) {
        const url = '/cart/add/';
        const formData = new FormData();
        formData.append('product_id', productId);
        formData.append('quantity', quantity);
        formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));
        
        fetch(url, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('Product added to cart!', 'success');
                updateCartTotals(data);
            } else {
                showAlert(data.error || 'Error adding to cart', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Error adding to cart', 'danger');
        });
    };
    
    // Remove from cart
    window.removeFromCart = function(productId) {
        const url = '/cart/remove/';
        const formData = new FormData();
        formData.append('product_id', productId);
        formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));
        
        fetch(url, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('Product removed from cart', 'info');
                location.reload(); // Reload to update cart display
            } else {
                showAlert(data.error || 'Error removing from cart', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Error removing from cart', 'danger');
        });
    };
    
    // Utility function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Form validation
    window.validateForm = function(form) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                isValid = false;
            } else {
                field.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    };
    
    // Image lazy loading
    function initializeLazyLoading() {
        const images = document.querySelectorAll('img[data-src]');
        
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    observer.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    }
    
    // Initialize lazy loading if supported
    if ('IntersectionObserver' in window) {
        initializeLazyLoading();
    }
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Back to top button
    const backToTopBtn = document.querySelector('.back-to-top');
    if (backToTopBtn) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopBtn.style.display = 'block';
            } else {
                backToTopBtn.style.display = 'none';
            }
        });
        
        backToTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
});