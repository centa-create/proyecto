// Simulación de carga de productos con loader neón
document.addEventListener('DOMContentLoaded', function() {
    var loader = document.getElementById('feed-loader');
    var content = document.getElementById('feed-content');
    loader.style.display = 'flex';
    content.style.display = 'none';
    setTimeout(function() {
        loader.style.display = 'none';
        content.style.display = 'block';
        // Inicializar carrusel después de que se muestre el contenido
        initializeCarousel3D();
    }, 1200); // 1.2 segundos de carga simulada
});

// Función para agregar productos al carrito
function addToCart(productId, productName) {
    // Mostrar notificación de éxito
    showCarouselNotification(`"${productName}" agregado al carrito exitosamente`, 'success');

    // Aquí iría la lógica real para agregar al carrito
    // Por ahora solo mostramos la notificación
}

// Función para mostrar notificaciones del carrusel
function showCarouselNotification(message, type) {
    // Remover notificación anterior si existe
    const existingNotification = document.querySelector('.carousel-notification');
    if (existingNotification) {
        existingNotification.remove();
    }

    // Crear nueva notificación
    const notification = document.createElement('div');
    notification.className = `carousel-notification carousel-notification-${type}`;
    notification.innerHTML = `
        <div class="carousel-notification-content">
            <span class="carousel-notification-icon">
                ${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}
            </span>
            <span class="carousel-notification-text">${message}</span>
        </div>
    `;

    // Agregar al DOM
    document.body.appendChild(notification);

    // Animar entrada
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);

    // Auto-remover después de 4 segundos
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }, 4000);
}

// Función para crear partículas
function createParticles() {
    const container = document.querySelector('.carousel-particles');
    if (!container) return;
    for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div');
        particle.className = 'carousel-particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 10 + 's';
        particle.style.animationDuration = (Math.random() * 5 + 5) + 's';
        container.appendChild(particle);
    }
}

// Función principal para inicializar el carrusel 3D
function initializeCarousel3D() {
    const carousel = document.getElementById('popular-products-carousel');
    if (!carousel) return;

    const wrapper = document.getElementById('carousel-wrapper');
    const cards = document.querySelectorAll('.carousel-3d-card');
    const indicators = document.querySelectorAll('.carousel-indicator');
    const prevBtn = document.getElementById('carousel-prev');
    const nextBtn = document.getElementById('carousel-next');

    if (!wrapper || cards.length === 0) return;

    let currentIndex = 0;
    let autoRotateInterval;
    let isPaused = false;
    let rotationAngle = 0;

    // Configuración del carrusel
    const config = {
        autoRotate: true,
        autoRotateDelay: 3000, // 3 segundos
        rotationStep: 90, // grados por tarjeta
        transitionDuration: '0.8s',
        hoverPause: true
    };

    // Función para actualizar la rotación del carrusel
    function updateCarouselRotation(targetAngle, smooth = true) {
        if (smooth) {
            wrapper.style.transition = `transform ${config.transitionDuration} cubic-bezier(0.4, 0, 0.2, 1)`;
        } else {
            wrapper.style.transition = 'none';
        }

        wrapper.style.transform = `rotateY(${targetAngle}deg)`;
        rotationAngle = targetAngle;
    }

    // Función para ir a un índice específico
    function goToIndex(index, smooth = true) {
        if (index < 0) index = cards.length - 1;
        if (index >= cards.length) index = 0;

        currentIndex = index;
        const targetAngle = -index * config.rotationStep;
        updateCarouselRotation(targetAngle, smooth);

        // Actualizar indicadores
        updateIndicators();

        // Reset progress bar
        const progressBar = document.getElementById('carousel-progress-bar');
        if (progressBar && config.autoRotate) {
            progressBar.style.width = '0%';
            setTimeout(() => {
                progressBar.style.width = '100%';
                progressBar.style.animationPlayState = 'running';
            }, 10);
        }
    }

    // Función para actualizar indicadores
    function updateIndicators() {
        indicators.forEach((indicator, index) => {
            indicator.classList.toggle('active', index === currentIndex);
        });
    }

    // Función para iniciar rotación automática
    function startAutoRotate() {
        if (config.autoRotate && !isPaused) {
            autoRotateInterval = setInterval(() => {
                goToIndex(currentIndex + 1);
            }, config.autoRotateDelay);
            const progressBar = document.getElementById('carousel-progress-bar');
            if (progressBar) {
                progressBar.style.width = '0%';
                setTimeout(() => {
                    progressBar.style.width = '100%';
                    progressBar.style.animationPlayState = 'running';
                }, 10);
            }
        }
    }

    // Función para detener rotación automática
    function stopAutoRotate() {
        if (autoRotateInterval) {
            clearInterval(autoRotateInterval);
            autoRotateInterval = null;
        }
        const progressBar = document.getElementById('carousel-progress-bar');
        if (progressBar) {
            progressBar.style.animationPlayState = 'paused';
        }
    }

    // Función para pausar/reanudar
    function togglePause() {
        isPaused = !isPaused;
        if (isPaused) {
            stopAutoRotate();
        } else {
            startAutoRotate();
        }
    }

    // Event listeners para controles
    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            goToIndex(currentIndex - 1);
            if (config.autoRotate) {
                stopAutoRotate();
                setTimeout(startAutoRotate, 5000); // Reiniciar auto-rotación después de 5s
            }
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            goToIndex(currentIndex + 1);
            if (config.autoRotate) {
                stopAutoRotate();
                setTimeout(startAutoRotate, 5000);
            }
        });
    }

    // Event listeners para indicadores
    indicators.forEach((indicator, index) => {
        indicator.addEventListener('click', () => {
            goToIndex(index);
            if (config.autoRotate) {
                stopAutoRotate();
                setTimeout(startAutoRotate, 5000);
            }
        });
    });

    // Event listeners para tarjetas (hover y teclado)
    cards.forEach((card, index) => {
        // Hover para pausar/reanudar
        if (config.hoverPause) {
            card.addEventListener('mouseenter', () => {
                stopAutoRotate();
                // Agregar efecto de escala
                card.style.transform += ' scale(1.05)';
            });

            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                const rotateX = (y - centerY) / 15;
                const rotateY = (centerX - x) / 15;
                card.style.transform = `rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.05)`;
            });

            card.addEventListener('mouseleave', () => {
                if (!isPaused) {
                    startAutoRotate();
                }
                // Remover efecto de escala y tilt
                card.style.transform = '';
            });
        }

        // Soporte para teclado
        card.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                goToIndex(index);
            }
        });

        // Hacer tarjetas enfocables
        card.setAttribute('tabindex', '0');
    });

    // Event listeners para el contenedor del carrusel
    carousel.addEventListener('mouseenter', () => {
        if (config.hoverPause) {
            stopAutoRotate();
        }
    });

    carousel.addEventListener('mouseleave', () => {
        if (config.hoverPause && !isPaused) {
            startAutoRotate();
        }
    });

    // Soporte para gestos táctiles (swipe)
    let touchStartX = 0;
    let touchEndX = 0;

    carousel.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
        stopAutoRotate();
    });

    carousel.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
        if (!isPaused) {
            setTimeout(startAutoRotate, 3000);
        }
    });

    function handleSwipe() {
        const swipeThreshold = 50;
        const diff = touchStartX - touchEndX;

        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) {
                // Swipe izquierda - siguiente
                goToIndex(currentIndex + 1);
            } else {
                // Swipe derecha - anterior
                goToIndex(currentIndex - 1);
            }
        }
    }

    // Soporte para navegación por teclado global
    document.addEventListener('keydown', (e) => {
        if (e.target.closest('.carousel-3d-container')) {
            switch (e.key) {
                case 'ArrowLeft':
                    e.preventDefault();
                    goToIndex(currentIndex - 1);
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    goToIndex(currentIndex + 1);
                    break;
                case ' ': // Espacio
                    e.preventDefault();
                    togglePause();
                    break;
            }
        }
    });

    // Efectos de sonido (opcional)
    function playSound(frequency, duration) {
        if ('AudioContext' in window || 'webkitAudioContext' in window) {
            try {
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();

                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);

                oscillator.frequency.setValueAtTime(frequency, audioContext.currentTime);
                oscillator.type = 'sine';

                gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);

                oscillator.start(audioContext.currentTime);
                oscillator.stop(audioContext.currentTime + duration);
            } catch (e) {
                // Silenciar errores de audio
            }
        }
    }

    // Agregar sonidos sutiles a interacciones
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => playSound(600, 0.1));
        card.addEventListener('click', () => playSound(800, 0.15));
    });

    // Inicialización
    updateIndicators();
    startAutoRotate();
    createParticles();

    // Prevenir animaciones si el usuario prefiere movimiento reducido
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (prefersReducedMotion) {
        config.autoRotate = false;
        wrapper.style.transition = 'none';
        cards.forEach(card => {
            card.style.transition = 'none';
        });
    }

    // API pública para control externo
    window.carousel3D = {
        goToIndex,
        togglePause,
        next: () => goToIndex(currentIndex + 1),
        prev: () => goToIndex(currentIndex - 1),
        pause: () => {
            isPaused = true;
            stopAutoRotate();
        },
        resume: () => {
            isPaused = false;
            startAutoRotate();
        }
    };
}

// Agregar estilos CSS adicionales para notificaciones
const notificationStyles = `
.carousel-notification {
    position: fixed;
    top: 20px;
    right: 20px;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 12px;
    padding: 1rem 1.5rem;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
    z-index: 10000;
    transform: translateX(400px);
    transition: transform 0.3s ease;
    max-width: 300px;
}

.carousel-notification.show {
    transform: translateX(0);
}

.carousel-notification-content {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.carousel-notification-icon {
    font-size: 1.25rem;
    flex-shrink: 0;
}

.carousel-notification-text {
    font-weight: 500;
    color: #1e293b;
    line-height: 1.4;
}

.carousel-notification-success {
    border-color: #10b981;
    background: rgba(16, 185, 129, 0.1);
}

.carousel-notification-success .carousel-notification-icon {
    color: #10b981;
}

.carousel-notification-error {
    border-color: #ef4444;
    background: rgba(239, 68, 68, 0.1);
}

.carousel-notification-error .carousel-notification-icon {
    color: #ef4444;
}
`;

// Agregar estilos al head
const styleElement = document.createElement('style');
styleElement.textContent = notificationStyles;
document.head.appendChild(styleElement);