# tests/test_registration_view.py
import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_registration_missing_address(client):
    url = reverse("account_signup")
    payload = {
        "email": "test@example.com",
        "password1": "StrongPass123!",
        "password2": "StrongPass123!",
        "first_name": "Kevin",
        "address": ""
    }

    response = client.post(url, payload)

    assert response.status_code == 200
    assert b"Enter a valid address" in response.content


@pytest.mark.django_db
def test_registration_invalid_address_no_zip(client):
    url = reverse("account_signup")
    payload = {
        "email": "test@example.com",
        "password1": "StrongPass123!",
        "password2": "StrongPass123!",
        "first_name": "Kevin",
        "address": "123 Main St, Raleigh, NC"
    }

    response = client.post(url, payload)

    assert response.status_code == 200
    assert b"Enter a valid address" in response.content


@pytest.mark.django_db
def test_registration_invalid_address_malformed(client):
    url = reverse("account_signup")
    payload = {
        "email": "test@example.com",
        "password1": "StrongPass123!",
        "password2": "StrongPass123!",
        "first_name": "Kevin",
        "address": "xyz"
    }

    response = client.post(url, payload)

    assert response.status_code == 200
    assert b"Enter a valid address" in response.content