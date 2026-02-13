/**
 * Cart Management System with AJAX Support
 * Handles Course and Product items
 * Version: 2.0
 */

(function() {
    'use strict';

    // Configuration from Django template
    const config = window.CART_CONFIG || {
        removeUrl: '/cart/ajax/remove/',
        clearUrl: '/cart/clear/',
        countUrl: '/cart/count/',
        csrfToken: '',
        messages: {
            removeConfirm: "آیا از حذف این محصول مطمئن هستید؟",
            clearConfirm: "آیا از خالی کردن سبد خرید مطمئن هستید؟",
            removeSuccess: "محصول حذف شد",
            clearSuccess: "سبد خرید خالی شد",
            removeError: "خطا در حذف محصول",
            clearError: "خطا در خالی کردن سبد",
            networkError: "خطای ارتباط با سرور"
        }
    };

    /**
     * Notification System
     */
    const Notification = {
        container: null,

        init() {
            // Create notification container if not exists
            if (!this.container) {
                this.container = document.createElement('div');
                this.container.className = 'cart-notifications';
                this.container.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    z-index: 9999;
                    min-width: 300px;
                    max-width: 400px;
                `;
                document.body.appendChild(this.container);
            }
        },

        show(message, type = 'success', duration = 4000) {
            this.init();

            const icons = {
                success: 'check-circle-fill',
                error: 'exclamation-circle-fill',
                warning: 'exclamation-triangle-fill',
                info: 'info-circle-fill'
            };

            const notification = document.createElement('div');
            notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
            notification.style.cssText = 'margin-bottom: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);';
            
            notification.innerHTML = `
                <i class="bi bi-${icons[type] || icons.info} me-2"></i>
                <span>${message}</span>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;

            this.container.appendChild(notification);

            // Auto remove
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => notification.remove(), 150);
            }, duration);

            return notification;
        },

        success(message) {
            return this.show(message, 'success');
        },

        error(message) {
            return this.show(message, 'error', 5000);
        },

        warning(message) {
            return this.show(message, 'warning');
        },

        info(message) {
            return this.show(message, 'info');
        }
    };

    /**
     * Utility Functions
     */
    const Utils = {
        getCookie(name) {
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
        },

        formatNumber(number) {
            return new Intl.NumberFormat('fa-IR').format(number);
        },

        updateCartBadge(quantity) {
            const badges = document.querySelectorAll('.cart-badge, .cart-count, [data-cart-count]');
            badges.forEach(badge => {
                badge.textContent = quantity;
                badge.style.display = quantity > 0 ? 'inline-block' : 'none';
                
                // Add animation
                badge.classList.add('cart-badge-update');
                setTimeout(() => badge.classList.remove('cart-badge-update'), 300);
            });
        },

        updateCartSummary(quantity, totalPrice) {
            const updates = [
                { id: 'cart-summary-quantity', value: `${quantity} آیتم` },
                { id: 'cart-summary-subtotal', value: `${this.formatNumber(totalPrice)} تومان` },
                { id: 'cart-summary-total', value: `${this.formatNumber(totalPrice)} تومان` }
            ];

            updates.forEach(({ id, value }) => {
                const element = document.getElementById(id);
                if (element) {
                    element.textContent = value;
                    element.classList.add('highlight-update');
                    setTimeout(() => element.classList.remove('highlight-update'), 500);
                }
            });
        }
    };

    /**
     * Cart Manager
     */
    const CartManager = {
        csrfToken: Utils.getCookie('csrftoken') || config.csrfToken,

        async fetchJSON(url, options = {}) {
            try {
                const response = await fetch(url, {
                    ...options,
                    headers: {
                        'X-CSRFToken': this.csrfToken,
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/json',
                        ...options.headers
                    }
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                return { success: true, data };
            } catch (error) {
                console.error('Fetch error:', error);
                return { success: false, error: error.message };
            }
        },

        async addToCart(productId, productType = 'course') {
            const url = `/cart/ajax/add/`;
            
            const result = await this.fetchJSON(url, {
                method: 'POST',
                body: JSON.stringify({ 
                    product_id: productId,
                    product_type: productType
                })
            });

            if (result.success && result.data.success) {
                const message = result.data.added 
                    ? 'محصول به سبد خرید اضافه شد'
                    : 'این محصول قبلاً در سبد خرید موجود است';
                
                Notification.show(message, result.data.added ? 'success' : 'info');
                Utils.updateCartBadge(result.data.cart_quantity || 0);
                
                return result.data;
            } else {
                Notification.error(result.data?.message || config.messages.networkError);
                return null;
            }
        },

        async removeFromCart(productId, productType, productName = '') {
            const confirmMessage = productName 
                ? `آیا از حذف "${productName}" از سبد خرید مطمئن هستید؟`
                : config.messages.removeConfirm;

            if (!confirm(confirmMessage)) {
                return null;
            }

            const url = config.removeUrl;
            
            const result = await this.fetchJSON(url, {
                method: 'POST',
                body: JSON.stringify({
                    product_id: productId,
                    product_type: productType
                })
            });

            if (result.success && result.data.success) {
                Notification.success(result.data.message || config.messages.removeSuccess);
                Utils.updateCartBadge(result.data.cart_quantity || 0);
                Utils.updateCartSummary(
                    result.data.cart_quantity || 0,
                    result.data.cart_total || 0
                );
                return result.data;
            } else {
                Notification.error(result.data?.message || config.messages.removeError);
                return null;
            }
        },

        async clearCart() {
            if (!confirm(config.messages.clearConfirm)) {
                return null;
            }

            const url = config.clearUrl;
            
            const result = await this.fetchJSON(url, {
                method: 'POST'
            });

            if (result.success && result.data.success) {
                Notification.success(result.data.message || config.messages.clearSuccess);
                setTimeout(() => window.location.reload(), 800);
                return result.data;
            } else {
                Notification.error(result.data?.message || config.messages.clearError);
                return null;
            }
        },

        async updateCartCount() {
            const result = await this.fetchJSON(config.countUrl);
            
            if (result.success) {
                Utils.updateCartBadge(result.data.cart_quantity || 0);
            }
        }
    };

    /**
     * Event Handlers
     */
    const EventHandlers = {
        setupRemoveButtons() {
            const removeButtons = document.querySelectorAll('.remove-item');
            
            removeButtons.forEach(button => {
                button.addEventListener('click', async (e) => {
                    e.preventDefault();
                    
                    const cartItem = button.closest('.cart-item');
                    if (!cartItem) return;

                    const productId = cartItem.dataset.productId;
                    const productType = cartItem.dataset.productType || 'course';
                    const form = button.closest('form');
                    const productName = form?.dataset.productName || '';

                    // Disable button during request
                    button.disabled = true;

                    const result = await CartManager.removeFromCart(
                        productId,
                        productType,
                        productName
                    );

                    if (result) {
                        // Animate removal
                        cartItem.style.transition = 'opacity 0.3s, transform 0.3s';
                        cartItem.style.opacity = '0';
                        cartItem.style.transform = 'translateX(20px)';
                        
                        setTimeout(() => {
                            cartItem.remove();
                            
                            // Check if cart is empty
                            const remainingItems = document.querySelectorAll('.cart-item');
                            if (remainingItems.length === 0) {
                                setTimeout(() => window.location.reload(), 500);
                            }
                        }, 300);
                    } else {
                        button.disabled = false;
                    }
                });
            });
        },

        setupClearButton() {
            const clearButton = document.querySelector('.clear-cart-form button');
            
            if (clearButton) {
                clearButton.addEventListener('click', async (e) => {
                    e.preventDefault();
                    
                    clearButton.disabled = true;
                    await CartManager.clearCart();
                    // Button will be re-enabled after page reload
                });
            }
        },

        setupAddToCartButtons() {
            const addButtons = document.querySelectorAll('.add-to-cart-btn, [data-add-to-cart]');
            
            addButtons.forEach(button => {
                button.addEventListener('click', async (e) => {
                    e.preventDefault();
                    
                    const productId = button.dataset.productId || button.dataset.courseId;
                    const productType = button.dataset.productType || 'course';
                    
                    if (!productId) {
                        console.error('Product ID not found');
                        return;
                    }

                    button.disabled = true;
                    const originalText = button.innerHTML;
                    button.innerHTML = '<i class="bi bi-hourglass-split"></i> در حال افزودن...';

                    const result = await CartManager.addToCart(productId, productType);

                    if (result && result.added) {
                        button.innerHTML = '<i class="bi bi-check-circle"></i> در سبد خرید';
                        button.classList.remove('btn-accent', 'btn-primary');
                        button.classList.add('btn-secondary');
                    } else {
                        button.innerHTML = originalText;
                        button.disabled = false;
                    }
                });
            });
        }
    };

    /**
     * Initialize on DOM ready
     */
    function init() {
        // Setup event handlers
        EventHandlers.setupRemoveButtons();
        EventHandlers.setupClearButton();
        EventHandlers.setupAddToCartButtons();

        // Update cart count on page load
        CartManager.updateCartCount();

        // Add CSS for animations
        const style = document.createElement('style');
        style.textContent = `
            @keyframes cart-badge-pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.2); }
            }
            
            .cart-badge-update {
                animation: cart-badge-pulse 0.3s ease-in-out;
            }
            
            @keyframes highlight-flash {
                0%, 100% { background-color: transparent; }
                50% { background-color: rgba(25, 135, 84, 0.2); }
            }
            
            .highlight-update {
                animation: highlight-flash 0.5s ease-in-out;
            }
            
            .cart-item {
                transition: opacity 0.3s, transform 0.3s;
            }
        `;
        document.head.appendChild(style);
    }

    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose to window for external use
    window.CartManager = CartManager;
    window.CartNotification = Notification;

})();
