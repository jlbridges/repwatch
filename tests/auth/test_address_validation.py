import pytest
from django.urls import reverse


# address validation on the registration page


@pytest.mark.django_db
def test_registration_valid_address(client):
    url = reverse("registration")

    response = client.post(url, {
        "first_name": "Kevin",
        "last_name": "Smith",
        "email": "kevin@example.com",
        "password1": "StrongPass123!",
        "password2": "StrongPass123!",
        "address_line1": "123 Main St",
        "address_line2": "",
        "city": "Raleigh",
        "state": "NC",
        "zipcode": "27603",
    })

    assert response.status_code == 302


@pytest.mark.django_db
def test_registration_invalid_zipcode(client):
    url = reverse("registration")

    response = client.post(url, {
        "first_name": "Kevin",
        "last_name": "Smith",
        "email": "kevin@example.com",
        "password1": "StrongPass123!",
        "password2": "StrongPass123!",
        "address_line1": "123 Main St",
        "address_line2": "",
        "city": "Raleigh",
        "state": "NC",
        "zipcode": "ABC123",  # invalid
    })

    # Form should re-render
    assert response.status_code == 200

    # Exact message from clean_zipcode
    assert b"Enter a valid 5-digit ZIP code." in response.content

import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_registration_invalid_state(client):
    url = reverse("registration")

    response = client.post(url, {
        "first_name": "Kevin",
        "last_name": "Smith",
        "email": "kevin@example.com",
        "password1": "StrongPass123!",
        "password2": "StrongPass123!",
        "address_line1": "123 Main St",
        "address_line2": "",
        "city": "Raleigh",
        "state": "CA",  # invalid
        "zipcode": "27603",
    })

    assert response.status_code == 200

    form = response.context["form"]
    assert "state" in form.errors
    assert form.errors["state"] == [
    "Select a valid choice. CA is not one of the available choices."
]