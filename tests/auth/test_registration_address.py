
# test for valid entry. Redirects to failed status if incorrect format is used.


import pytest
from django.urls import reverse
ACCOUNT_FORMS = {
    "signup": "yourapp.forms.CustomSignupForm",

}

@pytest.mark.django_db
def test_registration_valid_address(client):
    url = reverse("account_signup")
    payload = {
        "email": "test@example.com",
        "password1": "StrongPass123!",
        "password2": "StrongPass123!",
        "first_name": "Kevin",
        "address": "123 Main St, Raleigh, NC 27603"
    }

    response = client.post(url, payload)

    assert response.status_code == 302  # success redirect


@pytest.mark.django_db
def test_registration_invalid_address(client):
    url = reverse("account_signup")
    payload = {
        "email": "test@example.com",
        "password1": "StrongPass123!",
        "password2": "StrongPass123!",
        "first_name": "Kevin",
        "address": "Main St, Raleigh, NC"  # invalid
    }

    response = client.post(url, payload)

    assert response.status_code == 200  # form re-rendered
    assert b"Enter a valid address" in response.content