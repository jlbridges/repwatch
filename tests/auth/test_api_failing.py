import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_dashboard_handles_api_failure(client, test_user, test_password, login_url, monkeypatch):
    client.post(login_url, {
        "email": test_user.email,
        "password": test_password,
    })

    def mock_api(*args, **kwargs):
        raise Exception("API failed")

    monkeypatch.setattr(
        "core.services.geocodio_service.get_representatives_from_address",
        mock_api
    )

    response = client.get(reverse("dashboard"))

    assert response.status_code == 200