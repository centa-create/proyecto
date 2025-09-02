// Gráficos en tiempo real para el panel admin (ejemplo con Chart.js)

document.addEventListener('DOMContentLoaded', function() {
  if (document.getElementById('chart-ventas')) {
    fetch('/admin/api/sales_by_day')
      .then(res => res.json())
      .then(data => {
        const ctx = document.getElementById('chart-ventas').getContext('2d');
        new Chart(ctx, {
          type: 'line',
          data: {
            labels: data.labels,
            datasets: [{
              label: 'Ventas por día',
              data: data.totals,
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
      });
  }
});
