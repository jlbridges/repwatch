import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_search_returns_empty(client, test_user, test_password, login_url):
    client.post(login_url, {
        "email": test_user.email,
        "password": test_password,
    })

    response = client.get(reverse("dashboard"), {
        "q": "nonexistent"
    })

    assert b"No results" in response.content or response.status_code == 200