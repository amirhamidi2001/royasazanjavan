/**
 * Checkout Page JavaScript
 * Handles coupon application and form enhancements
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Get CSRF token
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
    
    // Format number with thousand separator
    function formatNumber(number) {
        return new Intl.NumberFormat('fa-IR').format(number);
    }
    
    // Show notification
    function showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    // Handle coupon form submission
    const couponForm = document.getElementById('coupon-form');
    const couponInput = document.getElementById('coupon-code-input');
    const couponMessage = document.getElementById('coupon-message');
    const applyButton = document.getElementById('apply-coupon-btn');
    
    if (couponForm) {
        couponForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const code = couponInput.value.trim();
            
            if (!code) {
                showNotification('لطفاً کد تخفیف را وارد کنید', 'warning');
                return;
            }
            
            // Disable button during request
            applyButton.disabled = true;
            applyButton.innerHTML = '<span class="spinner-border spinner-border-sm"></span> در حال بررسی...';
            
            // Create form data
            const formData = new FormData(couponForm);
            
            fetch(couponForm.action, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update discount amount in summary
                    const discountRow = document.querySelector('.order-discount');
                    if (discountRow) {
                        discountRow.querySelector('#discount-amount').textContent = 
                            `-${formatNumber(data.discount_amount)} تومان`;
                    } else {
                        // Create discount row if not exists
                        const subtotalRow = document.querySelector('.order-subtotal');
                        const newRow = document.createElement('div');
                        newRow.className = 'order-discount d-flex justify-content-between text-success';
                        newRow.innerHTML = `
                            <span>تخفیف</span>
                            <span id="discount-amount">-${formatNumber(data.discount_amount)} تومان</span>
                        `;
                        subtotalRow.parentNode.insertBefore(newRow, subtotalRow.nextSibling);
                    }
                    
                    // Update total
                    document.getElementById('total-amount').textContent = 
                        `${formatNumber(data.total)} تومان`;
                    
                    // Update button price
                    const placeOrderBtn = document.querySelector('.place-order-btn .btn-price');
                    if (placeOrderBtn) {
                        placeOrderBtn.textContent = `${formatNumber(data.total)} تومان`;
                    }
                    
                    // Show success message
                    couponMessage.innerHTML = `
                        <div class="alert alert-success alert-sm mb-0">
                            <i class="bi bi-check-circle"></i> ${data.message}
                        </div>
                    `;
                    
                    showNotification(data.message, 'success');
                    
                    // Disable input and change button to remove
                    couponInput.disabled = true;
                    applyButton.innerHTML = '<i class="bi bi-x"></i> حذف';
                    applyButton.classList.remove('btn-outline-primary');
                    applyButton.classList.add('btn-outline-danger');
                    
                } else {
                    couponMessage.innerHTML = `
                        <div class="alert alert-danger alert-sm mb-0">
                            <i class="bi bi-x-circle"></i> ${data.message}
                        </div>
                    `;
                    showNotification(data.message, 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('خطا در اعمال کد تخفیف', 'danger');
            })
            .finally(() => {
                // Re-enable button
                applyButton.disabled = false;
                applyButton.innerHTML = 'اعمال';
            });
        });
    }
    
    // Form validation
    const checkoutForm = document.querySelector('.checkout-form');
    if (checkoutForm) {
        checkoutForm.addEventListener('submit', function(e) {
            const termsCheckbox = document.getElementById('id_terms');
            
            if (!termsCheckbox.checked) {
                e.preventDefault();
                showNotification('لطفاً شرایط و قوانین را بپذیرید', 'warning');
                termsCheckbox.focus();
                return false;
            }
            
            // Show loading state on submit button
            const submitBtn = checkoutForm.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                const btnText = submitBtn.querySelector('.btn-text');
                if (btnText) {
                    btnText.innerHTML = '<span class="spinner-border spinner-border-sm"></span> در حال پردازش...';
                }
            }
        });
    }
    
    // Phone number formatting
    const phoneInput = document.getElementById('id_phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            // Remove non-numeric characters
            let value = e.target.value.replace(/\D/g, '');
            e.target.value = value;
        });
    }
    
    // Zip code formatting
    const zipInput = document.getElementById('id_zip_code');
    if (zipInput) {
        zipInput.addEventListener('input', function(e) {
            // Remove non-numeric characters
            let value = e.target.value.replace(/\D/g, '');
            e.target.value = value;
        });
    }
    
    // Auto-fill from user profile (if available)
    const firstNameInput = document.getElementById('id_first_name');
    const lastNameInput = document.getElementById('id_last_name');
    const emailInput = document.getElementById('id_email');
    
    // Scroll to first error
    const firstError = document.querySelector('.invalid-feedback');
    if (firstError) {
        firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    // Collapsible sections
    const sectionHeaders = document.querySelectorAll('.section-header');
    sectionHeaders.forEach(header => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            const section = this.parentElement;
            const content = section.querySelector('.section-content');
            
            if (content.style.display === 'none') {
                content.style.display = 'block';
                section.classList.add('active');
            } else {
                // Don't allow collapsing required sections
                if (!section.id.includes('customer-info') && !section.id.includes('order-review')) {
                    content.style.display = 'none';
                    section.classList.remove('active');
                }
            }
        });
    });
});
