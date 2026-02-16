
# test_access_control.py

import pytest
pytestmark = pytest.mark.django_db  # utilizing the provided django DB


@pytest.mark.django_db # checks agaisnt the provided login, and dashboard html provided
def test_authenticated_user_can_access_dashboard(client, test_user, test_password, login_url, dashboard_url):
    client.post(login_url, {
        "login": test_user.username,
        "password": test_password,
    })

    response = client.get(dashboard_url)

    assert response.status_code == 200
    assert test_user.username.encode() in response.content