def test_user_can_logout(client, test_user, test_password, login_url, logout_url):
    # login first
    client.post(login_url, {
        "login": test_user.email,
        "password": test_password,
    })
    assert "_auth_user_id" in client.session

    response = client.post(logout_url)

    assert response.status_code == 302
    assert "_auth_user_id" not in client.session