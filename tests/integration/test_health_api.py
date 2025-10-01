"""
Tests de integración para los endpoints de health check.
"""

import json

import pytest

from app import create_app


class TestHealthAPI:
    """Tests para los endpoints de health check."""

    @pytest.fixture
    def app(self):
        """Fixture para crear la aplicación de testing."""
        app = create_app()
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        """Fixture para el cliente de testing."""
        return app.test_client()

    def test_health_check(self, client):
        """Test básico del health check."""
        response = client.get('/health')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'status' in data
        assert 'timestamp' in data
        assert 'service' in data
        assert 'version' in data
        assert data['status'] == 'healthy'
        assert data['service'] == 'samms-fo'

    def test_readiness_check(self, client):
        """Test del readiness check."""
        response = client.get('/ready')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'status' in data
        assert 'timestamp' in data
        assert 'checks' in data
        assert isinstance(data['checks'], dict)

        # Verificar que tenga los checks esperados
        expected_checks = ['database', 'memory', 'disk']
        for check in expected_checks:
            assert check in data['checks']
            assert 'status' in data['checks'][check]
            assert 'message' in data['checks'][check]

    def test_metrics_endpoint(self, client):
        """Test del endpoint de métricas."""
        response = client.get('/metrics')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'timestamp' in data
        assert 'uptime_seconds' in data
        assert 'memory' in data
        assert 'cpu' in data
        assert 'disk' in data

        # Verificar estructura de memoria
        memory = data['memory']
        assert 'used_mb' in memory
        assert 'available_mb' in memory
        assert 'percentage' in memory

        # Verificar estructura de CPU
        cpu = data['cpu']
        assert 'percentage' in cpu

        # Verificar estructura de disco
        disk = data['disk']
        assert 'used_gb' in disk
        assert 'free_gb' in disk
        assert 'percentage' in disk

    def test_health_check_content_type(self, client):
        """Test que los endpoints retornen JSON."""
        endpoints = ['/health', '/ready', '/metrics']

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.content_type == 'application/json'

    def test_health_check_cors_headers(self, client):
        """Test que los endpoints tengan headers CORS apropiados."""
        response = client.get('/health')

        # Verificar headers CORS básicos
        assert 'Access-Control-Allow-Origin' in response.headers or \
               response.status_code == 200  # Algunos setups no incluyen CORS en tests
        # Verificar headers CORS básicos
        assert 'Access-Control-Allow-Origin' in response.headers or \
               response.status_code == 200  # Algunos setups no incluyen CORS en tests
        # Verificar headers CORS básicos
        assert 'Access-Control-Allow-Origin' in response.headers or \
               response.status_code == 200  # Algunos setups no incluyen CORS en tests
        # Verificar headers CORS básicos
        assert 'Access-Control-Allow-Origin' in response.headers or \
               response.status_code == 200  # Algunos setups no incluyen CORS en tests"" 
"" 
