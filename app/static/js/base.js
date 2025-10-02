/**
 * Base Template - JavaScript Funcionalidad Global
 * Efectos y utilidades compartidas en toda la aplicación
 */

document.addEventListener('DOMContentLoaded', function() {
    // Efecto ripple en botones
    document.querySelectorAll('button, .btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            let ripple = document.createElement('span');
            ripple.className = 'ripple';
            ripple.style.left = (e.offsetX - 10) + 'px';
            ripple.style.top = (e.offsetY - 10) + 'px';
            this.appendChild(ripple);
            setTimeout(() => ripple.remove(), 600);
        });
    });

    // Animación de validación en formularios
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                form.classList.add('was-validated');
                e.preventDefault();
                e.stopPropagation();
            }
        }, false);
    });

    // Actualizar contador del carrito
    async function updateCartCount() {
        try {
            const res = await fetch("/api/cart/");
            const data = await res.json();
            const count = data.items.reduce((acc, item) => acc + item.quantity, 0);
            const cartCountElem = document.getElementById("cartCount");
            if (cartCountElem) {
                cartCountElem.textContent = count;
                cartCountElem.style.display = count > 0 ? "inline-block" : "none";
            }
        } catch (e) {
            console.warn('Error updating cart count:', e);
        }
    }

    // Inicializar contador del carrito
    updateCartCount();

    // Notificaciones Push básicas
    if ('Notification' in window && 'serviceWorker' in navigator) {
        function askNotificationPermission() {
            if (Notification.permission === 'default') {
                Notification.requestPermission();
            }
        }

        function showTestNotification() {
            if (Notification.permission === 'granted') {
                navigator.serviceWorker.getRegistration().then(function(reg) {
                    if (reg) {
                        reg.showNotification('¡Bienvenido a SAMMS.FO!', {
                            body: 'Activa las notificaciones para recibir ofertas y novedades.',
                            icon: '/static/logo.png',
                            vibrate: [100, 50, 100]
                        });
                    }
                });
            }
        }

        // Solicitar permiso al cargar
        window.addEventListener('load', askNotificationPermission);

        // Botón flotante para probar notificaciones
        const notificationBtn = document.createElement('button');
        notificationBtn.innerText = '🔔';
        notificationBtn.title = 'Probar notificación push';
        notificationBtn.className = 'floating-notification-btn';
        notificationBtn.onclick = showTestNotification;
        document.body.appendChild(notificationBtn);
    }

    // Función global para agregar al carrito (usada en templates)
    window.addToCart = async function(productId, productName = '') {
        try {
            // Aquí iría la lógica real para agregar al carrito
            console.log(`Agregando producto ${productId} al carrito`);

            // Mostrar notificación de éxito
            showToast(`"${productName || 'Producto'}" agregado al carrito exitosamente`, 'success');

            // Actualizar contador
            await updateCartCount();

        } catch (error) {
            console.error('Error adding to cart:', error);
            showToast('Error al agregar al carrito', 'error');
        }
    };

    // Función para mostrar toasts/notificaciones
    function showToast(message, type = 'info') {
        // Crear toast básico
        const toast = document.createElement('div');
        toast.className = `alert alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} position-fixed`;
        toast.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 300px;
            animation: slideInRight 0.3s ease-out;
        `;
        toast.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'times-circle' : 'info-circle'} me-2"></i>
            ${message}
        `;

        document.body.appendChild(toast);

        // Auto-remover después de 4 segundos
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }
});

// Animaciones CSS para toasts
const toastStyles = `
@keyframes slideInRight {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

@keyframes slideOutRight {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(100%); opacity: 0; }
}
`;

// Agregar estilos de toast al head
const styleElement = document.createElement('style');
styleElement.textContent = toastStyles;
document.head.appendChild(styleElement);