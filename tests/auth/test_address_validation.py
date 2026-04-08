import pytest
from unittest.mock import patch
from django.urls import reverse


@pytest.mark.django_db
@patch("core.forms.validate_address")
def test_registration_valid_address(mock_validate, client):
    """Registration should succeed when Smarty validates the address."""

    mock_validate.return_value = {
        "address_line1": "1101 Oberlin Rd",
        "city": "Raleigh",
        "state": "NC",
        "zipcode": "27605",
    }

    response = client.post(reverse("registration"), {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "password1": "StrongPass123!",
        "password2": "StrongPass123!",
        "address_line1": "1101 Oberlin Rd",
        "address_line2": "",
        "city": "Raleigh",
        "state": "NC",
        "zipcode": "27605",
    })

    assert response.status_code == 302


@pytest.mark.django_db
@patch("core.forms.validate_address")
def test_registration_invalid_zipcode(mock_validate, client):
    """Registration should fail if Smarty rejects the address."""

    mock_validate.return_value = None

    response = client.post(reverse("registration"), {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "password1": "StrongPass123!",
        "password2": "StrongPass123!",
        "address_line1": "123 Fake St",
        "address_line2": "",
        "city": "Raleigh",
        "state": "NC",
        "zipcode": "99999",
    })

    assert response.status_code == 200
    assert "Address could not be validated" in response.content.decode()


@pytest.mark.django_db
@patch("core.forms.validate_address")
def test_registration_invalid_state(mock_validate, client):

    mock_validate.return_value = None

    response = client.post(reverse("registration"), {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "password1": "StrongPass123!",
        "password2": "StrongPass123!",
        "address_line1": "1101 Oberlin Rd",
        "address_line2": "",
        "city": "Raleigh",
        "state": "CA",
        "zipcode": "90210",
    })

    assert response.status_code == 200
    assert "state" in response.context["form"].errors
    assert "Select a valid choice" in response.context["form"].errors["state"][0]