import pytest


@pytest.mark.django_db
def test_homepage_loads(client):
    response = client.get("/")
    assert response.status_code == 200