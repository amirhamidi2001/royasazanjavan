/**
 * Cart Management with AJAX
 * Handles add, remove, and clear operations without page reload
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Get CSRF token from cookies
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
    
    const csrftoken = getCookie('csrftoken');
    
    // Update cart badge in header
    function updateCartBadge(quantity) {
        const cartBadges = document.querySelectorAll('.cart-badge, .cart-count');
        cartBadges.forEach(badge => {
            badge.textContent = quantity;
            if (quantity > 0) {
                badge.style.display = 'inline-block';
            } else {
                badge.style.display = 'none';
            }
        });
    }
    
    // Show notification message
    function showNotification(message, type = 'success') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    // Format number with thousand separator
    function formatNumber(number) {
    return new Intl.NumberFormat('en-US').format(number);
}
    
    // Handle Add to Cart (for course list pages)
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const courseId = this.dataset.courseId;
            const url = this.dataset.url || `/cart/add/${courseId}/`;
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification(data.message, data.added ? 'success' : 'info');
                    updateCartBadge(data.cart_total_quantity);
                    
                    // Update button text if course was added
                    if (data.added) {
                        this.innerHTML = '<i class="bi bi-check-circle"></i> در سبد خرید';
                        this.classList.remove('btn-accent');
                        this.classList.add('btn-secondary');
                        this.disabled = true;
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('خطا در افزودن به سبد خرید', 'danger');
            });
        });
    });
    
    // Handle Remove from Cart
    const removeButtons = document.querySelectorAll('.remove-item');
    removeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const form = this.closest('form');
            const cartItem = this.closest('.cart-item');
            const courseId = cartItem.dataset.courseId;
            const url = form.action;
            
            if (confirm('آیا از حذف این دوره از سبد خرید مطمئن هستید؟')) {
                fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Remove item with animation
                        cartItem.style.transition = 'opacity 0.3s';
                        cartItem.style.opacity = '0';
                        
                        setTimeout(() => {
                            cartItem.remove();
                            
                            // Update summary
                            updateCartSummary(data.cart_total_quantity, data.cart_total_price);
                            updateCartBadge(data.cart_total_quantity);
                            showNotification(data.message, 'success');
                            
                            // Check if cart is empty
                            const remainingItems = document.querySelectorAll('.cart-item');
                            if (remainingItems.length === 0) {
                                location.reload(); // Reload to show empty cart message
                            }
                        }, 300);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showNotification('خطا در حذف از سبد خرید', 'danger');
                });
            }
        });
    });
    
    // Handle Clear Cart
    const clearCartButton = document.querySelector('.clear-cart-form button');
    if (clearCartButton) {
        clearCartButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            if (confirm('آیا از خالی کردن سبد خرید مطمئن هستید؟')) {
                const form = this.closest('form');
                
                fetch(form.action, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showNotification(data.message, 'success');
                        setTimeout(() => {
                            location.reload();
                        }, 500);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showNotification('خطا در خالی کردن سبد خرید', 'danger');
                });
            }
        });
    }
    
    // Update cart summary in sidebar
    function updateCartSummary(quantity, totalPrice) {
        const quantityElement = document.getElementById('cart-summary-quantity');
        const subtotalElement = document.getElementById('cart-summary-subtotal');
        const totalElement = document.getElementById('cart-summary-total');
        
        if (quantityElement) {
            quantityElement.textContent = `${quantity} دوره`;
        }
        
        if (subtotalElement) {
            subtotalElement.textContent = `${formatNumber(totalPrice)} تومان`;
        }
        
        if (totalElement) {
            totalElement.textContent = `${formatNumber(totalPrice)} تومان`;
        }
    }
    
    // Apply coupon code (placeholder - implement backend logic)
    const applyCouponBtn = document.getElementById('apply-coupon-btn');
    if (applyCouponBtn) {
        applyCouponBtn.addEventListener('click', function() {
            const couponInput = document.getElementById('coupon-code');
            const couponCode = couponInput.value.trim();
            
            if (!couponCode) {
                showNotification('لطفاً کد تخفیف را وارد کنید', 'warning');
                return;
            }
            
            // TODO: Implement coupon validation on backend
            fetch('/cart/apply-coupon/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ coupon_code: couponCode })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('کد تخفیف با موفقیت اعمال شد', 'success');
                    // Update discount and total
                    const discountElement = document.getElementById('cart-summary-discount');
                    if (discountElement) {
                        discountElement.textContent = `${formatNumber(data.discount_amount)} تومان`;
                    }
                    updateCartSummary(data.cart_total_quantity, data.cart_total_price);
                } else {
                    showNotification(data.message || 'کد تخفیف نامعتبر است', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('خطا در اعمال کد تخفیف', 'danger');
            });
        });
    }
    
    // Update cart count on page load
    fetch('/cart/count/', {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        updateCartBadge(data.cart_total_quantity);
    })
    .catch(error => console.error('Error fetching cart count:', error));
});
