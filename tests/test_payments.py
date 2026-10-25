def test_get_payments_list(client):
    response = client.get("/api/payments")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) > 0

    first_item = data["items"][0]
    assert "id" in first_item
    assert "amount" in first_item
    assert "currency" in first_item
    assert "status" in first_item
    assert "timestamp" in first_item
    assert first_item["amount"] > 0

def test_filter_payments_by_status(client):
    response = client.get("/api/payments?status=COMPLETED")
    assert response.status_code == 200
    data = response.json()
    assert all(item["status"] == "COMPLETED" for item in data["items"])

def test_search_payments(client):
    response = client.get("/api/payments?search=Apex")
    assert response.status_code == 200
    data = response.json()
    assert any("Apex" in item["customer"] for item in data["items"])

def test_get_payment_by_id_success(client):
    list_res = client.get("/api/payments")
    existing_id = list_res.json()["items"][0]["id"]

    res = client.get(f"/api/payments/{existing_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == existing_id

def test_get_payment_by_id_not_found(client):
    res = client.get("/api/payments/TXN-NONEXISTENT-999")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()

def test_create_payment_valid(client):
    payload = {
        "amount": 4500.50,
        "currency": "USD",
        "customer": "Test Enterprise Client Inc.",
        "method": "Fedwire",
        "description": "Integration automated test payment",
        "status": "COMPLETED"
    }
    res = client.post("/api/payments", json=payload)
    assert res.status_code == 201
    created = res.json()
    assert created["id"].startswith("TXN-")
    assert created["amount"] == 4500.50
    assert created["customer"] == "Test Enterprise Client Inc."
    assert created["status"] == "COMPLETED"

    # Verify newly created item is in list
    verify_res = client.get(f"/api/payments/{created['id']}")
    assert verify_res.status_code == 200

def test_create_payment_invalid_amount(client):
    payload = {
        "amount": -50.00,  # Invalid: must be > 0
        "currency": "USD",
        "customer": "Invalid Corp"
    }
    res = client.post("/api/payments", json=payload)
    assert res.status_code == 422  # Unprocessable Entity
