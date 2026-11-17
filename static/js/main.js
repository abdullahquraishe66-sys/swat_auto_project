// Fetch unread counts
document.addEventListener('DOMContentLoaded', function() {
    // ... existing code ...
    
    // Fetch notification and message counts
    if (document.getElementById('notificationBadge')) {
        fetchNotificationCount();
        setInterval(fetchNotificationCount, 30000); // Every 30 seconds
    }
    
    if (document.getElementById('unreadBadge')) {
        fetchUnreadMessageCount();
        setInterval(fetchUnreadMessageCount, 30000);
    }
});

function fetchNotificationCount() {
    const badge = document.getElementById('notificationBadge');
    if (!badge) return;
    
    fetch('/notifications/unread-count/')
        .then(response => response.json())
        .then(data => {
            if (data.count > 0) {
                badge.textContent = data.count > 99 ? '99+' : data.count;
                badge.style.display = 'flex';
            } else {
                badge.style.display = 'none';
            }
        })
        .catch(error => console.error('Error fetching notification count:', error));
}

function fetchUnreadMessageCount() {
    const badge = document.getElementById('unreadBadge');
    if (!badge) return;
    
    fetch('/chat/unread-count/')
        .then(response => response.json())
        .then(data => {
            if (data.count > 0) {
                badge.textContent = data.count > 99 ? '99+' : data.count;
                badge.style.display = 'flex';
            } else {
                badge.style.display = 'none';
            }
        })
        .catch(error => console.error('Error fetching message count:', error));
}
// ============================================
// STEP 13 - UI/UX ENHANCEMENTS
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    
    // ===== Scroll Reveal Animations =====
    const revealElements = document.querySelectorAll('.reveal');
    
    if (revealElements.length > 0) {
        const revealObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('revealed');
                    revealObserver.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });
        
        revealElements.forEach(el => revealObserver.observe(el));
    }
    
    // ===== Scroll to Top Button =====
    const scrollBtn = document.createElement('button');
    scrollBtn.className = 'scroll-to-top';
    scrollBtn.innerHTML = '<i class="bi bi-arrow-up"></i>';
    scrollBtn.setAttribute('aria-label', 'Scroll to top');
    document.body.appendChild(scrollBtn);
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 400) {
            scrollBtn.classList.add('visible');
        } else {
            scrollBtn.classList.remove('visible');
        }
    });
    
    scrollBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    // ===== Image Lazy Load =====
    const images = document.querySelectorAll('img:not([loading])');
    images.forEach(img => {
        img.setAttribute('loading', 'lazy');
    });
    
    // ===== Loading Button States =====
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.classList.contains('loading')) {
                submitBtn.classList.add('loading');
                submitBtn.disabled = true;
            }
        });
    });
    
    // ===== Auto-dismiss Alerts =====
    document.querySelectorAll('.alert:not(.alert-permanent)').forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s, transform 0.5s';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });
    
    // ===== Password Strength Indicator =====
    const passwordInputs = document.querySelectorAll('input[type="password"][id*="password1"]');
    passwordInputs.forEach(input => {
        const strengthBar = document.createElement('div');
        strengthBar.className = 'password-strength';
        strengthBar.innerHTML = '<div class="password-strength-bar"></div>';
        input.parentElement.appendChild(strengthBar);
        
        input.addEventListener('input', function() {
            const password = this.value;
            const bar = strengthBar.querySelector('.password-strength-bar');
            
            let strength = 0;
            if (password.length >= 8) strength++;
            if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
            if (/\d/.test(password)) strength++;
            if (/[^a-zA-Z\d]/.test(password)) strength++;
            
            bar.className = 'password-strength-bar';
            if (password.length === 0) {
                bar.style.width = '0';
            } else if (strength <= 1) {
                bar.classList.add('weak');
            } else if (strength <= 3) {
                bar.classList.add('medium');
            } else {
                bar.classList.add('strong');
            }
        });
    });
    
    // ===== Copy to Clipboard =====
    document.querySelectorAll('[data-copy]').forEach(el => {
        el.style.cursor = 'pointer';
        el.addEventListener('click', () => {
            const text = el.dataset.copy;
            navigator.clipboard.writeText(text).then(() => {
                showToast('Copied to clipboard!', 'success');
            });
        });
    });
    
    // ===== Confirm Delete Links =====
    document.querySelectorAll('[data-confirm]').forEach(el => {
        el.addEventListener('click', function(e) {
            const message = this.dataset.confirm || 'Are you sure?';
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
    
    // ===== Smooth Scroll for Anchor Links =====
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#' || href.length === 1) return;
            
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                const offsetTop = target.getBoundingClientRect().top + window.scrollY - 80;
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // ===== Number Count Up Animation =====
    const counters = document.querySelectorAll('[data-count]');
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = parseInt(entry.target.dataset.count);
                const duration = 1500;
                const start = performance.now();
                const startValue = 0;
                
                const animate = (currentTime) => {
                    const elapsed = currentTime - start;
                    const progress = Math.min(elapsed / duration, 1);
                    const easeOut = 1 - Math.pow(1 - progress, 3);
                    const current = Math.floor(startValue + (target - startValue) * easeOut);
                    
                    entry.target.textContent = current.toLocaleString();
                    
                    if (progress < 1) {
                        requestAnimationFrame(animate);
                    }
                };
                
                requestAnimationFrame(animate);
                counterObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    counters.forEach(counter => counterObserver.observe(counter));
    
    // ===== Ripple Effect on Buttons =====
    document.querySelectorAll('.btn, .nav-link').forEach(btn => {
        btn.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            
            ripple.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.4);
                top: ${e.clientY - rect.top - size/2}px;
                left: ${e.clientX - rect.left - size/2}px;
                pointer-events: none;
                transform: scale(0);
                animation: rippleEffect 0.6s ease-out;
            `;
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
    
    // Add ripple animation
    if (!document.getElementById('ripple-style')) {
        const style = document.createElement('style');
        style.id = 'ripple-style';
        style.textContent = `
            @keyframes rippleEffect {
                to {
                    transform: scale(2);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
});

// ===== Global showToast Function =====
if (typeof window.showToast !== 'function') {
    window.showToast = function(message, type = 'info') {
        const container = document.getElementById('toastContainer') || (() => {
            const c = document.createElement('div');
            c.id = 'toastContainer';
            c.className = 'toast-container';
            document.body.appendChild(c);
            return c;
        })();
        
        const toast = document.createElement('div');
        toast.className = 'toast-notification ' + type;
        
        const icons = {
            success: 'bi-check-circle-fill',
            error: 'bi-x-circle-fill',
            warning: 'bi-exclamation-triangle-fill',
            info: 'bi-info-circle-fill'
        };
        
        toast.innerHTML = `
            <i class="bi ${icons[type] || icons.info}"></i>
            <span>${message}</span>
        `;
        
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'fadeOut 0.3s ease-out forwards';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    };
}