import pytest
from django.urls import reverse
from core.models import BillHeader

pytestmark = pytest.mark.django_db


def test_search_by_title(client, test_user, test_password, login_url):
    client.post(login_url, {
        "email": test_user.email,
        "password": test_password,
    })

    BillHeader.objects.create(
        number="1",
        congress=118,
        type="hr",
        title="Healthcare Reform Act"
    )

    response = client.get(reverse("dashboard"), {
        "q": "healthcare"
    })

    assert b"Healthcare Reform Act" in response.content


def test_search_by_congress(client, test_user, test_password, login_url):
    client.post(login_url, {
        "email": test_user.email,
        "password": test_password,
    })

    BillHeader.objects.create(
        number="2",
        congress=117,
        type="hr",
        title="Old Bill"
    )

    response = client.get(reverse("dashboard"), {
        "congress": "117"
    })

    assert b"Old Bill" in response.content


def test_search_by_type(client, test_user, test_password, login_url):
    client.post(login_url, {
        "email": test_user.email,
        "password": test_password,
    })

    BillHeader.objects.create(
        number="3",
        congress=118,
        type="s",
        title="Senate Bill"
    )

    response = client.get(reverse("dashboard"), {
        "bill_type": "s"
    })

    assert b"Senate Bill" in response.content