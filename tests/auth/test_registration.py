
# test_registration.py

from django.contrib.auth.models import User
import pytest
pytestmark = pytest.mark.django_db  # utilizing the provided django DB


from django.contrib.auth.models import User

def test_user_can_register(client, signup_url):
    payload = {
        "first_name": "New",
        "last_name": "User",
        "email": "newuser@example.com",
        "password1": "NewUserPass123",
        "password2": "NewUserPass123",
        "address_line1": "123 Main St",
        "address_line2": "",
        "city": "Raleigh",
        "state": "NC",
        "zipcode": "27601",
    }

    response = client.post(signup_url, payload)

    assert response.status_code == 302
    assert User.objects.filter(email="newuser@example.com").exists()


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