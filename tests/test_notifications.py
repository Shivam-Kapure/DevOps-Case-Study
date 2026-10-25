def test_get_notifications_list(client):
    response = client.get("/api/notifications")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert isinstance(data["items"], list)
    assert len(data["items"]) > 0

    first = data["items"][0]
    assert "id" in first
    assert "event_type" in first
    assert "channel" in first
    assert "recipient" in first
    assert "status" in first
    assert "timestamp" in first
    assert "payload_summary" in first

def test_filter_notifications_by_status(client):
    response = client.get("/api/notifications?status=DELIVERED")
    assert response.status_code == 200
    data = response.json()
    assert all(item["status"] == "DELIVERED" for item in data["items"])

def test_get_notification_by_id_success(client):
    list_res = client.get("/api/notifications")
    existing_id = list_res.json()["items"][0]["id"]

    res = client.get(f"/api/notifications/{existing_id}")
    assert res.status_code == 200
    assert res.json()["id"] == existing_id

def test_get_notification_by_id_not_found(client):
    res = client.get("/api/notifications/NOTIF-999999-NOTFOUND")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()
