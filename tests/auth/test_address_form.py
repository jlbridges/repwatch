import pytest

pytestmark = pytest.mark.django_db


def test_address_missing(client):
    response = client.post("/register/", {})
    assert b"address" in response.content


def test_address_no_street_number(client):
    response = client.post("/register/", {
        "address_line1": "Main Street",
        "city": "Raleigh",
        "state": "NC",
        "zipcode": "27601",
    })
    assert b"Enter a valid address" in response.content