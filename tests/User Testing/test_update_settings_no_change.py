import pytest


@pytest.mark.django_db
def test_update_settings_no_changes(client, test_user, login_url):
    client.post(login_url, {"email": test_user.email, "password": "SuperSecret123"})
    response = client.post("/settings/", {})
    assert response.status_code == 302