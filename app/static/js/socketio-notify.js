// Cliente Socket.IO para notificaciones en tiempo real
const socket = io();
socket.on('connect', () => {
  console.log('Conectado a WebSocket');
});
socket.on('nueva_notificacion', function(data) {
  if (window.Notification && Notification.permission === 'granted') {
    new Notification('¡Tienes una nueva notificación!', { body: data.mensaje });
  }
});
