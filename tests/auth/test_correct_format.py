# testing for the correct format in address entry

import pytest
from core.forms import CustomSignupForm

@pytest.mark.django_db
def test_valid_address():
    form = CustomSignupForm(data={
        "email": "test@example.com",
        "password1": "StrongPass123!",
        "password2": "StrongPass123!",
        "first_name": "Kevin",
        "address": "123 Main St, Raleigh, NC 27603"
    })
    assert form.is_valid() is True


@pytest.mark.django_db
def test_invalid_address():
    form = CustomSignupForm(data={
        "email": "test@example.com",
        "password1": "StrongPass123!",
        "password2": "StrongPass123!",
        "first_name": "Kevin",
        "address": "Main St, Raleigh, NC"  # invalid
    })
    assert form.is_valid() is False
    assert "address" in form.errors