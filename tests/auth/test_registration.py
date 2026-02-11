from django.contrib.auth.models import User


def test_user_can_register(client, signup_url):
    payload = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password1": "NewUserPass123",
        "password2": "NewUserPass123",
        # if you added address fields, include them here
        # "address": "123 Main St, Raleigh, NC",
    }

    response = client.post(signup_url, payload)

    assert response.status_code == 302
    assert User.objects.filter(username="newuser").exists()


def test_registration_fails_with_mismatched_passwords(client, signup_url):
    payload = {
        "username": "baduser",
        "email": "baduser@example.com",
        "password1": "Password123",
        "password2": "Different123",
    }

    response = client.post(signup_url, payload)

    assert response.status_code == 200
    assert b"password" in response.content.lower()
    assert not User.objects.filter(username="baduser").exists()