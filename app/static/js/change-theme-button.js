// Adaptación para Flask: sin dependencias externas
// Guarda la preferencia en localStorage y aplica el tema

function setTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
}

function getPreferredTheme() {
  const saved = localStorage.getItem('theme');
  if (saved) return saved;
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

document.addEventListener('DOMContentLoaded', function () {
  // Aplica el tema guardado o el del sistema
  setTheme(getPreferredTheme());

  const toggle = document.querySelector('.toggle');
  if (!toggle) return;

  // Estado inicial del botón
  toggle.setAttribute('aria-pressed', getPreferredTheme() === 'dark');

  toggle.addEventListener('click', function () {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    setTheme(isDark ? 'light' : 'dark');
    toggle.setAttribute('aria-pressed', !isDark);
  });
});
