def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "service" in data
    assert "endpoints" in data
    assert data["endpoints"]["health"] == "/health"

def test_health_check_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Enterprise Payment & Notification Engine" in data["service"]
    assert "version" in data
    assert "timestamp" in data
    assert isinstance(data["uptime_seconds"], (int, float))
    assert data["uptime_seconds"] >= 0
    assert data["active_records"] >= 0
    assert data["active_notifications"] >= 0
