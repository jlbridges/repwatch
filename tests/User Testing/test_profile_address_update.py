import pytest
from django.urls import reverse
from core.models import Profile

pytestmark = pytest.mark.django_db


def test_profile_update_valid_address(client, test_user, test_password, login_url):
    # Login
    client.post(login_url, {
        "email": test_user.email,
        "password": test_password,
    })

    # Ensure profile exists
    profile, _ = Profile.objects.get_or_create(user=test_user)

    # Submit valid address 
    response = client.post(reverse("updateSettings"), {
        "hidden_id": test_user.id,
        "address_line1": "222 W Hargett St",
        "city": "Raleigh",
        "state": "NC",
        "zipcode": "27601",
    })

    # Reload profile
    profile.refresh_from_db()

    # Assert updated 
    assert "222" in profile.address_line1
    assert "hargett" in profile.address_line1.lower()
    assert profile.city.lower() == "raleigh"
    assert profile.state == "NC"
    assert profile.zipcode == "27601"

    # redirect expected
    assert response.status_code == 302


def test_profile_update_invalid_address(client, test_user, test_password, login_url):
    #Login
    client.post(login_url, {
        "email": test_user.email,
        "password": test_password,
    })

    # Create initial profile
    profile, _ = Profile.objects.get_or_create(user=test_user)
    profile.address_line1 = "456 Old St"
    profile.city = "Raleigh"
    profile.state = "NC"
    profile.zipcode = "27601"
    profile.save()

    #Submit invalid address (no street number)
    response = client.post(reverse("updateSettings"), {
        "hidden_id": test_user.id,
        "address_line1": "Main Street",  # ❌ invalid
        "city": "Raleigh",
        "state": "NC",
        "zipcode": "27601",
    }, follow=True)

    profile.refresh_from_db()

    #Should NOT change the address if its busted
    assert profile.address_line1 == "456 Old St"

    #Should show error
    assert b"Enter a valid address" in response.content