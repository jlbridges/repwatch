import pytest
import responses

from core.services.smarty_address_service import validate_address

SMARTY_URL = "https://us-street.api.smarty.com/street-address"


@responses.activate
def test_smarty_valid_address(monkeypatch):

    monkeypatch.setenv("SMARTY_AUTH_ID", "test")
    monkeypatch.setenv("SMARTY_AUTH_TOKEN", "test")

    responses.add(
        responses.GET,
        SMARTY_URL,
        json=[{
            "delivery_line_1": "123 MAIN ST",
            "components": {
                "city_name": "RALEIGH",
                "state_abbreviation": "NC",
                "zipcode": "27601",
                "plus4_code": "1234"
            }
        }],
        status=200
    )

    result = validate_address("123 Main St", "Raleigh", "NC", "27601")

    assert result["zipcode"] == "27601"