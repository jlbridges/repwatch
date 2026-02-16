
# test_logout.py

import pytest
pytestmark = pytest.mark.django_db # utilizing the provided django DB

@pytest.mark.django_db  # checks agaisnt the provided login, and dashboard html provided
def test_user_can_logout(client, test_user, test_password, login_url, logout_url):
    client.post(login_url, {
        "login": test_user.username,
        "password": test_password,
    })

    assert "_auth_user_id" in client.session

    response = client.post(logout_url)

    assert response.status_code == 302
    assert "_auth_user_id" not in client.session