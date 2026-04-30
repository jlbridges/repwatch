import pytest
from unittest.mock import patch
from django.urls import reverse
from core.models import BillHeader

pytestmark = pytest.mark.django_db


@patch("core.services.bill_service.save_bill_detail")
def test_user_can_save_bill(mock_detail, client, test_user, test_password, login_url):
    client.post(login_url, {
        "email": test_user.email,
        "password": test_password,
    })

    bill = BillHeader.objects.create(
        number="123",
        congress=118,
        type="hr",
        title="Test Bill"
    )

    response = client.post(reverse("save_bill", args=[bill.number]), {
        "congress": bill.congress,
        "type": bill.type,
        "title": bill.title,
    })

    bill.refresh_from_db()

    assert test_user in bill.saved_by.all()
    assert response.status_code == 302
