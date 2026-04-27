import pytest
from django.urls import reverse
from core.models import Representative

pytestmark = pytest.mark.django_db


def test_logout_clears_reps(client, test_user, test_password, login_url, logout_url):
    # Login
    client.post(login_url, {
        "email": test_user.email,
        "password": test_password,
    })

    # Create fake rep and attach user
    rep = Representative.objects.create(
        Bioguide_id="X123",
        first_name="Test",
        last_name="Rep",
        state="NC",
        party="D",
        type="representative"
    )
    rep.constituents.add(test_user)

    assert rep.constituents.count() == 1

    # Logout
    client.post(logout_url)

    rep.refresh_from_db()

    # Should remove user from reps
    assert rep.constituents.count() == 0