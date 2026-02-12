from django.core import mail
from django.urls import reverse


def test_password_reset_sends_email(client, test_user):
    url = reverse("account_reset_password")

    response = client.post(url, {"email": test_user.email})

    assert response.status_code == 302
    assert len(mail.outbox) == 1
    assert test_user.email in mail.outbox[0].to


def test_password_reset_for_unknown_email_is_silent(client):
    url = reverse("account_reset_password")

    response = client.post(url, {"email": "unknown@example.com"})

    # still redirect, but no email
    assert response.status_code == 302
    assert len(mail.outbox) == 0