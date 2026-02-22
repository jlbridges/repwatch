



# tests/test_address_form.py
import pytest
from yourapp.forms import CustomSignupForm

BASE_VALID_DATA = {
    "email": "test@example.com",
    "password1": "StrongPass123!",
    "password2": "StrongPass123!",
    "first_name": "Kevin",
}

@pytest.mark.django_db
def test_address_missing():
    data = BASE_VALID_DATA | {"address": ""}
    form = CustomSignupForm(data=data)
    assert form.is_valid() is False
    assert "address" in form.errors


@pytest.mark.django_db
def test_address_no_street_number():
    data = BASE_VALID_DATA | {"address": "Main St, Raleigh, NC 27603"}
    form = CustomSignupForm(data=data)
    assert form.is_valid() is False
    assert "address" in form.errors


@pytest.mark.django_db
def test_address_missing_zip():
    data = BASE_VALID_DATA | {"address": "123 Main St, Raleigh, NC"}
    form = CustomSignupForm(data=data)
    assert form.is_valid() is False
    assert "address" in form.errors


@pytest.mark.django_db
def test_address_missing_state():
    data = BASE_VALID_DATA | {"address": "123 Main St, Raleigh, 27603"}
    form = CustomSignupForm(data=data)
    assert form.is_valid() is False
    assert "address" in form.errors


@pytest.mark.django_db
def test_address_malformed():
    data = BASE_VALID_DATA | {"address": "abcdefg"}
    form = CustomSignupForm(data=data)
    assert form.is_valid() is False
    assert "address" in form.errors