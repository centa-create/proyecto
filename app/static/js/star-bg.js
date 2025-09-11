// Genera estrellas aleatorias en los divs con clase 'stars'
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.stars').forEach(function(starsDiv) {
    starsDiv.innerHTML = '';
    for (let i = 0; i < 80; i++) {
      const star = document.createElement('span');
      star.style.left = Math.random() * 100 + 'vw';
      star.style.top = Math.random() * 100 + 'vh';
      star.style.width = (Math.random() * 2 + 1) + 'px';
      star.style.height = star.style.width;
      star.style.opacity = (Math.random() * 0.5 + 0.5).toFixed(2);
      star.style.animationDelay = (Math.random() * 2) + 's';
      starsDiv.appendChild(star);
    }
  });
});
