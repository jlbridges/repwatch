
# test_access_control.py

import pytest
from core.models import Profile
pytestmark = pytest.mark.django_db  # utilizing the provided django DB


@pytest.mark.django_db
def test_authenticated_user_can_access_dashboard(
    client, test_user, test_password, login_url, dashboard_url
):
    client.post(login_url, {
        "email": test_user.email,
        "password": test_password,
    })

    response = client.get(dashboard_url)

    assert response.status_code == 200
    assert b"My Reps" in response.content  # or another known dashboard string