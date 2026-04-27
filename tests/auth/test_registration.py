
import pytest
from unittest.mock import patch
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
@patch("core.forms.validate_address")
def test_user_can_register(mock_validate, client):
    """User should be able to register successfully with a valid address."""

    mock_validate.return_value = {
        "address_line1": "1101 Oberlin Rd",
        "city": "Raleigh",
        "state": "NC",
        "zipcode": "27605",
    }

    response = client.post(reverse("registration"), {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane@example.com",
        "password1": "StrongPass123!",
        "password2": "StrongPass123!",
        "address_line1": "1101 Oberlin Rd",
        "address_line2": "",
        "city": "Raleigh",
        "state": "NC",
        "zipcode": "27605",
    })

    assert response.status_code == 302
    assert User.objects.filter(email="jane@example.com").exists()


@pytest.mark.django_db
@patch("core.forms.validate_address")
def test_registration_fails_with_mismatched_passwords(mock_validate, client):
    """Registration should fail if passwords do not match."""

    mock_validate.return_value = {
        "address_line1": "1101 Oberlin Rd",
        "city": "Raleigh",
        "state": "NC",
        "zipcode": "27605",
    }

    response = client.post(reverse("registration"), {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane@example.com",
        "password1": "StrongPass123!",
        "password2": "WrongPassword123!",
        "address_line1": "1101 Oberlin Rd",
        "address_line2": "",
        "city": "Raleigh",
        "state": "NC",
        "zipcode": "27605",
    })

    assert response.status_code == 200
    assert not User.objects.filter(email="jane@example.com").exists()