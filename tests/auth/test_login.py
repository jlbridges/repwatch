
# test_login.py

import pytest
pytestmark = pytest.mark.django_db # utilizing the provided django DB


@pytest.mark.django_db  # checks agaisnt the provided login, and dashboard html provided
def test_user_can_login(client, test_user, test_password, login_url):
    response = client.post(login_url, {
        "login": test_user.username,   # allauth default
        "password": test_password,
    })

    assert response.status_code == 302
    assert "_auth_user_id" in client.session


def test_login_fails_with_wrong_password(client, test_user, login_url):
    response = client.post(login_url, {
        "login": test_user.username,
        "password": "WrongPassword123",
    })

    assert response.status_code == 200
    assert "_auth_user_id" not in client.session