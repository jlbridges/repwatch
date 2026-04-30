import pytest
from django.urls import reverse
from django.test import override_settings


@pytest.mark.django_db
@override_settings(SESSION_EXPIRE_AT_BROWSER_CLOSE=True)
def test_logout_on_browser_close(client, test_user, test_password, login_url):
    # Login
    client.post(login_url, {
        "email": test_user.email,
        "password": test_password,
    })

    # Simulate browser close → clear session
    client.cookies.clear()

    # Try accessing dashboard
    response = client.get(reverse("dashboard"))

    # Should be logged out
    assert response.status_code == 302
    assert "/login" in response.url