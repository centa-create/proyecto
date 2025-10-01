// Genera estrellas aleatorias en los divs con clase 'stars'
document.addEventListener('DOMContentLoaded', function() {
  console.log('🚀 Ejecutando star-bg.js - Generando fondo estrellado');

  document.querySelectorAll('.stars').forEach(function(starsDiv) {
    console.log('⭐ Encontrado div .stars:', starsDiv);

    // Si ya tiene estrellas, no regenerar
    if (starsDiv.children.length > 0) {
      console.log('⭐ Estrellas ya generadas, saltando...');
      return;
    }

    // Limpiar contenido anterior
    starsDiv.innerHTML = '';

    // Crear diferentes tipos de estrellas con distribución equilibrada
    const starTypes = ['star-small', 'star-medium', 'star-large'];
    const totalStars = 600; // Más estrellas para mayor densidad

    // Distribución: 60% pequeñas, 30% medianas, 10% grandes
    const distribution = [0.6, 0.3, 0.1];

    for (let i = 0; i < totalStars; i++) {
      const star = document.createElement('span');

      // Posicionamiento aleatorio
      star.style.left = Math.random() * 100 + '%';
      star.style.top = Math.random() * 100 + '%';
      star.style.position = 'absolute';

      // Seleccionar tipo basado en distribución
      let random = Math.random();
      let starTypeIndex = 0;
      for (let j = 0; j < distribution.length; j++) {
        random -= distribution[j];
        if (random <= 0) {
          starTypeIndex = j;
          break;
        }
      }

      const starClass = starTypes[starTypeIndex];
      star.className = starClass;

      // Añadir retraso de animación aleatorio
      star.style.animationDelay = (Math.random() * 4) + 's';

      starsDiv.appendChild(star);
    }

    console.log('✅ Estrellas generadas:', totalStars, 'estrellas');
  });
});
