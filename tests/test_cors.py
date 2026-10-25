def test_cors_preflight_headers(client):
    headers = {
        "Origin": "http://localhost:28080",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "content-type",
    }
    response = client.options("/api/payments", headers=headers)
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers

def test_cors_response_headers_on_get(client):
    headers = {"Origin": "http://localhost:28080"}
    response = client.get("/health", headers=headers)
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
