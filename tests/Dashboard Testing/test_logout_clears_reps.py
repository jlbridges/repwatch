
import pytest

from django.contrib.auth.models import User
from django.urls import reverse

from core.models import Representative



@pytest.mark.django_db
def test_logout_clears_reps(client):
    user = User.objects.create_user(username="test", password="pass123")
    client.login(username="test", password="pass123")

    rep = Representative.objects.create(
        Bioguide_id="A123",
        name="Test Rep",
        district_number=1,
        first_name="Test",
        last_name="Rep",
        state="NC",
        party="D",
        type="representative",
        photo_url="http://test.com"
    )
    rep.constituents.add(user)

    client.post(reverse("accountlogout"))

    assert Representative.objects.filter(constituents=user).count() == 0