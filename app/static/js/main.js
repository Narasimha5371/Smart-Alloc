// Smart-Alloc Main JavaScript

document.addEventListener('DOMContentLoaded', function () {
    // --- Notification Polling ---
    fetchNotificationCount();
    setInterval(fetchNotificationCount, 30000); // Every 30 seconds

    // --- Auto-dismiss alerts ---
    setTimeout(function () {
        const alerts = document.querySelectorAll('.alert-dismissible.auto-dismiss');
        alerts.forEach(function (alert) {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        });
    }, 5000);

    // --- Flash message cookie cleanup ---
    deleteCookie('flash_message');
    deleteCookie('flash_type');

    // --- Progress slider value display ---
    document.querySelectorAll('input[type="range"].progress-slider').forEach(function (slider) {
        const display = slider.closest('form').querySelector('.progress-value');
        if (display) {
            display.textContent = slider.value + '%';
            slider.addEventListener('input', function () {
                display.textContent = this.value + '%';
            });
        }
    });

    // --- Confirm dialogs for delete actions ---
    document.querySelectorAll('[data-confirm]').forEach(function (el) {
        el.addEventListener('click', function (e) {
            if (!confirm(this.getAttribute('data-confirm'))) {
                e.preventDefault();
            }
        });
    });

    // --- File upload validation ---
    document.querySelectorAll('input[type="file"][accept]').forEach(function (input) {
        input.addEventListener('change', function () {
            const file = this.files[0];
            if (!file) return;

            // Check size (5MB)
            if (file.size > 5 * 1024 * 1024) {
                alert('File size exceeds 5MB limit.');
                this.value = '';
                return;
            }

            // Check extension
            const allowed = this.accept.split(',').map(a => a.trim().toLowerCase());
            const ext = '.' + file.name.split('.').pop().toLowerCase();
            if (!allowed.includes(ext)) {
                alert('Invalid file type. Allowed: ' + this.accept);
                this.value = '';
            }
        });
    });

    // --- Animate elements on load ---
    document.querySelectorAll('.animate-in').forEach(function (el, index) {
        el.style.animationDelay = (index * 0.05) + 's';
    });
});


function fetchNotificationCount() {
    fetch('/api/notifications/count')
        .then(response => response.json())
        .then(data => {
            const badge = document.getElementById('notification-count');
            if (badge) {
                if (data.count > 0) {
                    badge.textContent = data.count;
                    badge.style.display = 'inline-block';
                } else {
                    badge.style.display = 'none';
                }
            }
        })
        .catch(() => { /* Silently fail */ });
}


function deleteCookie(name) {
    document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
}
