
from django.contrib.auth.models import User
from django.urls import reverse
import pytest

@pytest.fixture
def test_password():
    return "SuperSecret123"

@pytest.fixture
def test_user(db, test_password):
    return User.objects.create_user(
        username="john@example.com",
        email="john@example.com",
        password=test_password,
    )

@pytest.fixture
def login_url():
    return reverse("login")

@pytest.fixture
def logout_url():
    return reverse("account_logout")

@pytest.fixture
def signup_url():
    return reverse("account_signup")

@pytest.fixture
def dashboard_url():
    return reverse("dashboard")

@pytest.fixture
def password_reset_url():
    return reverse("account_reset_password")