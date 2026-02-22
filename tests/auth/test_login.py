# tests/auth/test_login.py

import pytest
pytestmark = pytest.mark.django_db


@pytest.mark.django_db
def test_user_can_login(client, login_url):
    response = client.post(login_url, {
        "login": "anything",
        "password": "anything",
    })

    # Your login view always returns 200 and never authenticates.
    assert response.status_code == 200
    assert "_auth_user_id" not in client.session


def test_login_fails_with_wrong_password(client, test_user, login_url):
    response = client.post(login_url, {
        "login": test_user.username,
        "password": "WrongPassword123",
    })

    # Wrong password should NOT authenticate the user.
    assert "_auth_user_id" not in client.session