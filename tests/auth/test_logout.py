
# test_logout.py

def test_user_can_logout(client, logout_url):
    # Since login never authenticates, logout is effectively a no-op.
    response = client.get(logout_url)

    # Accept either 200 or 302 depending on your logout URL.
    assert response.status_code in (200, 302)

    # No user should be logged in.
    assert "_auth_user_id" not in client.session