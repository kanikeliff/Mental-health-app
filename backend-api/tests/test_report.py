import pytest
def test_report_endpoint(client):
    r = client.get(
        "/report",
        headers={"Authorization": "Bearer dev"}
    )

    assert r.status_code == 200

    j = r.json()
    assert "summary" in j

