/**
 * Pasarela de Pago Simulada - JavaScript
 * Funcionalidad interactiva para la simulación de pagos
 */

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('payment-form');
    const payButton = document.getElementById('pay-button');
    let currentPaymentMethod = 'card';
    let processingStates = ['initial', 'validating', 'processing', 'confirming', 'completed'];
    let currentStateIndex = 0;

    // Función para cambiar método de pago
    function switchPaymentMethod(method) {
        currentPaymentMethod = method;

        // Actualizar UI de métodos
        document.querySelectorAll('.payment-method-card').forEach(card => {
            card.classList.remove('selected');
        });
        document.querySelector(`[data-method="${method}"]`).classList.add('selected');

        // Mostrar campos correspondientes
        document.querySelectorAll('.payment-details').forEach(detail => {
            detail.classList.remove('active');
        });
        document.getElementById(`${method}-details`).classList.add('active');

        // Resetear validación
        form.classList.remove('was-validated');
    }

    // Event listeners para métodos de pago
    document.querySelectorAll('.payment-method-card').forEach(card => {
        card.addEventListener('click', function() {
            const method = this.dataset.method;
            document.querySelector(`input[value="${method}"]`).checked = true;
            switchPaymentMethod(method);
        });
    });

    // Formatear número de tarjeta con detección de tipo
    document.getElementById('card_number').addEventListener('input', function(e) {
        let value = e.target.value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
        let formatted = value.match(/.{1,4}/g)?.join(' ') || value;
        e.target.value = formatted;

        // Detectar tipo de tarjeta
        const cardIcon = document.getElementById('card-icon');
        if (value.startsWith('4')) {
            cardIcon.className = 'fab fa-cc-visa text-primary';
        } else if (value.startsWith('5') || value.startsWith('2')) {
            cardIcon.className = 'fab fa-cc-mastercard text-warning';
        } else if (value.startsWith('3')) {
            cardIcon.className = 'fab fa-cc-amex text-info';
        } else {
            cardIcon.className = 'fas fa-credit-card text-secondary';
        }
    });

    // Formatear fecha de expiración
    document.getElementById('expiry').addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length >= 2) {
            value = value.substring(0, 2) + '/' + value.substring(2, 4);
        }
        e.target.value = value;
    });

    // Validación de campos
    function validateForm() {
        let isValid = true;
        form.classList.add('was-validated');

        if (currentPaymentMethod === 'card') {
            const cardNumber = document.getElementById('card_number').value.replace(/\s/g, '');
            const expiry = document.getElementById('expiry').value;
            const cvv = document.getElementById('cvv').value;
            const cardName = document.getElementById('card_name').value;

            // Validar número de tarjeta (Luhn algorithm básico)
            if (cardNumber.length < 13 || cardNumber.length > 19) {
                isValid = false;
                document.getElementById('card_number').setCustomValidity('Número inválido');
            } else {
                document.getElementById('card_number').setCustomValidity('');
            }

            // Validar fecha
            const [month, year] = expiry.split('/');
            const currentDate = new Date();
            const currentYear = currentDate.getFullYear() % 100;
            const currentMonth = currentDate.getMonth() + 1;

            if (!month || !year || month < 1 || month > 12 ||
                (parseInt(year) < currentYear) ||
                (parseInt(year) === currentYear && parseInt(month) < currentMonth)) {
                isValid = false;
                document.getElementById('expiry').setCustomValidity('Fecha inválida');
            } else {
                document.getElementById('expiry').setCustomValidity('');
            }

            // Validar CVV
            if (cvv.length < 3 || cvv.length > 4) {
                isValid = false;
                document.getElementById('cvv').setCustomValidity('CVV inválido');
            } else {
                document.getElementById('cvv').setCustomValidity('');
            }

            // Validar nombre
            if (cardName.trim().length < 2) {
                isValid = false;
                document.getElementById('card_name').setCustomValidity('Nombre requerido');
            } else {
                document.getElementById('card_name').setCustomValidity('');
            }
        }

        return isValid;
    }

    // Función para cambiar estado de procesamiento
    function setProcessingState(state) {
        document.querySelectorAll('.processing-state').forEach(s => {
            s.classList.remove('active');
        });
        document.getElementById(`state-${state}`).classList.add('active');
    }

    // Función para simular procesamiento paso a paso
    function simulateProcessing() {
        const simulateError = document.getElementById('simulate_error').checked;
        const fastProcessing = document.getElementById('fast_processing').checked;
        const delay = fastProcessing ? 800 : 1500;

        currentStateIndex = 0;
        setProcessingState('validating');

        const processNext = () => {
            currentStateIndex++;

            if (currentStateIndex < processingStates.length) {
                // Simular error aleatorio
                if (simulateError && currentStateIndex === 2 && Math.random() < 0.1) {
                    setProcessingState('error');
                    document.getElementById('error-message').textContent =
                        'Error de conexión con el banco. Inténtalo de nuevo.';
                    payButton.disabled = false;
                    payButton.classList.remove('processing');
                    return;
                }

                setProcessingState(processingStates[currentStateIndex]);
                setTimeout(processNext, delay);
            } else {
                // Completado - enviar formulario
                setTimeout(() => {
                    form.submit();
                }, 1000);
            }
        };

        setTimeout(processNext, delay);
    }

    // Función para reintentar pago
    window.retryPayment = function() {
        setProcessingState('initial');
        payButton.disabled = false;
        payButton.classList.remove('processing');
    };

    // Procesar pago
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        // Iniciar procesamiento
        payButton.disabled = true;
        payButton.classList.add('processing');
        simulateProcessing();
    });

    // Inicializar
    switchPaymentMethod('card');
    setProcessingState('initial');
});