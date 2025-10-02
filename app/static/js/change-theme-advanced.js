function setTheme(theme) {
   document.body.setAttribute('data-theme', theme);
   localStorage.setItem('theme', theme);
   const btn = document.querySelector('.theme-toggle-advanced');
   if (btn) {
       btn.setAttribute('data-theme', theme);
   }
}
function getPreferredTheme() {
  // Verificar si hay un tema guardado en localStorage
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    return savedTheme;
  }

  // Por defecto usar tema oscuro para mostrar fondo estrellado
  return 'dark';
}
document.addEventListener('DOMContentLoaded', function () {
  const currentTheme = getPreferredTheme();
  console.log('🎨 Aplicando tema:', currentTheme);

  setTheme(currentTheme);

  const btn = document.querySelector('.theme-toggle-advanced');
  const icon = document.getElementById('themeIcon');

  if (!btn || !icon) {
    console.error('❌ Theme toggle button or icon not found');
    return;
  }

  console.log('✅ Theme toggle button found and initialized');

  // Asegurar que el botón sea visible y esté posicionado correctamente
  btn.style.opacity = '1';
  btn.style.visibility = 'visible';
  btn.style.position = 'fixed';
  btn.style.bottom = '24px';
  btn.style.left = '24px';
  btn.style.zIndex = '10001';

  // Inicializar tooltip de Bootstrap
  if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
    new bootstrap.Tooltip(btn);
    console.log('✅ Bootstrap tooltip initialized');
  } else {
    console.warn('⚠️ Bootstrap not available for tooltips');
  }
  function updateIcon(animated = false) {
    const isDark = document.body.getAttribute('data-theme') === 'dark';
    icon.textContent = isDark ? '🌙' : '🌞';
    if (animated) {
      icon.classList.add('theme-animating');
      setTimeout(() => {
        icon.classList.remove('theme-animating');
      }, 500);
    }
  }
  btn.setAttribute('data-theme', getPreferredTheme());
  updateIcon();
  btn.addEventListener('click', function () {
    const isDark = document.body.getAttribute('data-theme') === 'dark';
    const newTheme = isDark ? 'light' : 'dark';
    setTheme(newTheme);
    updateIcon(true);

    // Mostrar notificación de cambio de tema
    showThemeNotification(newTheme);
  });

  function showThemeNotification(theme) {
    // Remover notificación anterior si existe
    const existingNotification = document.querySelector('.theme-notification');
    if (existingNotification) {
      existingNotification.remove();
    }

    // Crear nueva notificación
    const notification = document.createElement('div');
    notification.className = 'theme-notification';
    notification.innerHTML = `
      <i class="fas fa-${theme === 'dark' ? 'moon' : 'sun'} me-2"></i>
      Tema ${theme === 'dark' ? 'oscuro' : 'claro'} activado
    `;

    // Estilos de la notificación
    Object.assign(notification.style, {
      position: 'fixed',
      top: '20px',
      right: '20px',
      background: theme === 'dark' ? 'rgba(24, 24, 24, 0.9)' : 'rgba(255, 255, 255, 0.9)',
      color: theme === 'dark' ? '#e2e8f0' : '#1a202c',
      padding: '12px 20px',
      borderRadius: '8px',
      border: `1px solid ${theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'}`,
      boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)',
      backdropFilter: 'blur(10px)',
      zIndex: '10002',
      fontWeight: '600',
      fontSize: '14px',
      opacity: '0',
      transform: 'translateX(400px)',
      transition: 'all 0.3s ease'
    });

    document.body.appendChild(notification);

    // Animar entrada
    setTimeout(() => {
      notification.style.opacity = '1';
      notification.style.transform = 'translateX(0)';
    }, 100);

    // Auto-remover después de 3 segundos
    setTimeout(() => {
      notification.style.opacity = '0';
      notification.style.transform = 'translateX(400px)';
      setTimeout(() => {
        if (notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
      }, 300);
    }, 3000);
  }
  // Actualizar el icono si el tema cambia por otros medios
  const observer = new MutationObserver(updateIcon);
  observer.observe(document.body, { attributes: true, attributeFilter: ['data-theme'] });

  // Función de debug para verificar estado del tema
  window.checkThemeStatus = function() {
    const currentTheme = document.body.getAttribute('data-theme');
    const savedTheme = localStorage.getItem('theme');
    const btnTheme = btn.getAttribute('data-theme');
    const iconText = icon.textContent;

    console.log('🎨 Estado del Tema:');
    console.log('  - Tema actual en body:', currentTheme);
    console.log('  - Tema guardado en localStorage:', savedTheme);
    console.log('  - Tema en botón:', btnTheme);
    console.log('  - Icono actual:', iconText);

    return { currentTheme, savedTheme, btnTheme, iconText };
  };

  // Agregar función global para forzar cambio de tema (útil para testing)
  window.forceTheme = function(theme) {
    console.log('🔧 Forzando cambio a tema:', theme);
    setTheme(theme);
    updateIcon(true);
    showThemeNotification(theme);
  };

  console.log('🎉 Theme system fully initialized!');
});
