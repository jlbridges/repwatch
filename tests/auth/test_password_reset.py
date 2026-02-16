
# test_password_reset.py

from django.core import mail
import pytest
pytestmark = pytest.mark.django_db  # utilizing the provided django DB

@pytest.mark.django_db  # checks agaisnt the provided login, and dashboard html provided
def test_password_reset_sends_email(client, test_user, password_reset_url):
    response = client.post(password_reset_url, {"email": test_user.email})

    assert response.status_code == 302
    assert len(mail.outbox) == 1
    assert test_user.email.lower() in [e.lower() for e in mail.outbox[0].to]


@pytest.mark.django_db
def test_password_reset_for_unknown_email_is_silent(client, password_reset_url):
    response = client.post(password_reset_url, {"email": "unknown@example.com"})

    assert response.status_code == 302
    # allauth does NOT reveal whether the email exists
    assert len(mail.outbox) == 0