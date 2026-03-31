import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch

from core.models import BillHeader


@pytest.fixture
def auth_client(client):
    user = User.objects.create_user(username="test", password="pass123")
    client.login(username="test", password="pass123")
    return client

#Testing the search by keyword only
@pytest.mark.django_db
@patch("core.views.get_representatives_from_address", return_value=[])
@patch("core.views.get_member_details", return_value={})
def test_search_by_keyword(mock_congress, mock_geo, auth_client):

    BillHeader.objects.create(number=1, title="Healthcare Reform", congress=118, type="h")
    BillHeader.objects.create(number=2, title="Education Bill", congress=118, type="s")

    response = auth_client.get(reverse("dashboard"), {"q": "Health"})

    content = response.content.decode()

    assert "Healthcare Reform" in content
    assert "Education Bill" not in content

#Testing the search by congress only
@pytest.mark.django_db
@patch("core.views.get_representatives_from_address", return_value=[])
@patch("core.views.get_member_details", return_value={})
def test_search_by_congress(mock_congress, mock_geo, auth_client):

    BillHeader.objects.create(number=1, title="Bill A", congress=118, type="h")
    BillHeader.objects.create(number=2, title="Bill B", congress=117, type="h")

    response = auth_client.get(reverse("dashboard"), {"congress": "118"})

    content = response.content.decode()

    assert "Bill A" in content
    assert "Bill B" not in content

#Testing for search by bill type only
@pytest.mark.django_db
@patch("core.views.get_representatives_from_address", return_value=[])
@patch("core.views.get_member_details", return_value={})
def test_search_by_type(mock_congress, mock_geo, auth_client):

    BillHeader.objects.create(number=1, title="House Bill", congress=118, type="h")
    BillHeader.objects.create(number=2, title="Senate Bill", congress=118, type="s")

    response = auth_client.get(reverse("dashboard"), {"bill_type": "h"})

    content = response.content.decode()

    assert "House Bill" in content
    assert "Senate Bill" not in content

#testing for combined filters
@pytest.mark.django_db
@patch("core.views.get_representatives_from_address", return_value=[])
@patch("core.views.get_member_details", return_value={})
def test_search_combined_filters(mock_congress, mock_geo, auth_client):

    BillHeader.objects.create(number=1, title="Health Bill", congress=118, type="h")
    BillHeader.objects.create(number=2, title="Health Bill", congress=117, type="h")

    response = auth_client.get(reverse("dashboard"), {
        "q": "Health",
        "congress": "118"
    })

    content = response.content.decode()

    assert content.count("Health Bill") == 1

#testing that the dashboard requires login
@pytest.mark.django_db
def test_dashboard_requires_login(client):

    response = client.get(reverse("dashboard"))

    assert response.status_code == 302