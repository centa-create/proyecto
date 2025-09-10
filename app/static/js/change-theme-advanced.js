function setTheme(theme) {
  document.body.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
  document.querySelector('.theme-toggle-advanced').setAttribute('data-theme', theme);
}
function getPreferredTheme() {
  const saved = localStorage.getItem('theme');
  if (saved) return saved;
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}
document.addEventListener('DOMContentLoaded', function () {
  setTheme(getPreferredTheme());
  const btn = document.querySelector('.theme-toggle-advanced');
  const icon = document.getElementById('themeIcon');
  if (!btn || !icon) return;
  
  // Asegurar que el botón sea visible
  btn.style.opacity = '1';
  btn.style.visibility = 'visible';
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
  setTheme(isDark ? 'light' : 'dark');
  updateIcon(true);
  });
  // Actualizar el icono si el tema cambia por otros medios
  const observer = new MutationObserver(updateIcon);
  observer.observe(document.body, { attributes: true, attributeFilter: ['data-theme'] });
});
