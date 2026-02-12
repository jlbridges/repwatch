def test_protected_view_requires_login(client, dashboard_url):
    response = client.get(dashboard_url)

    assert response.status_code == 302
    assert "login" in response.url.lower()


def test_authenticated_user_can_access_dashboard(
    client, test_user, test_password, login_url, dashboard_url
):
    client.post(login_url, {
        "login": test_user.email,
        "password": test_password,
    })

    response = client.get(dashboard_url)

    assert response.status_code == 200
    # adjust to something you know appears on the dashboard
    assert b"Dashboard" in response.content