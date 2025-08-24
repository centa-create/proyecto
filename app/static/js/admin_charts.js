// Gráficos en tiempo real para el panel admin (ejemplo con Chart.js)
document.addEventListener('DOMContentLoaded', function() {
  if (document.getElementById('chart-ventas')) {
    const ctx = document.getElementById('chart-ventas').getContext('2d');
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
        datasets: [{
          label: 'Ventas',
          data: [120, 190, 300, 500, 200, 300, 450],
          borderColor: '#fff',
          backgroundColor: 'rgba(255,255,255,0.2)',
          tension: 0.4
        }]
      },
      options: {
        plugins: { legend: { labels: { color: '#fff' } } },
        scales: { x: { ticks: { color: '#fff' } }, y: { ticks: { color: '#fff' } } }
      }
    });
  }
});
