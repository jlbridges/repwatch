import pytest
from django.urls import reverse
from django.conf import settings
from django.contrib.sessions.models import Session
from django.utils import timezone
from datetime import timedelta


@pytest.mark.django_db
def test_session_timeout(client, test_user, test_password, login_url):
    # Login
    client.post(login_url, {
        "email": test_user.email,
        "password": test_password,
    })

    # Get session key
    session_key = client.session.session_key

    # Force session to expire (simulate timeout)
    session = Session.objects.get(session_key=session_key)
    session.expire_date = timezone.now() - timedelta(minutes=1)
    session.save()

    # Try accessing dashboard
    response = client.get(reverse("dashboard"))

    # Should redirect to login (should be logged out)
    assert response.status_code == 302
    assert "/login" in response.url