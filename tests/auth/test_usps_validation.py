import pytest
import responses

from core.services.test_usps_service import validate_address

USPS_URL = "https://secure.shippingapis.com/ShippingAPI.dll"

#test for correct address validation. USPS uses XML instead of JSON
@responses.activate
def test_valid_usps_address(monkeypatch):

    monkeypatch.setenv("USPS_API_KEY", "TESTKEY")

    responses.add(
        responses.GET,
        USPS_URL,
        body="""
        <AddressValidateResponse>
            <Address>
                <Address2>123 MAIN ST</Address2>
                <City>RALEIGH</City>
                <State>NC</State>
                <Zip5>27603</Zip5>
            </Address>
        </AddressValidateResponse>
        """,
        status=200
    )

    result = validate_address(
        "123 Main St",
        "Raleigh",
        "NC",
        "27603"
    )

    assert result is True

#invalid address test agaisnt usps
@responses.activate
def test_invalid_usps_address(monkeypatch):

    monkeypatch.setenv("USPS_API_KEY", "TESTKEY")

    responses.add(
        responses.GET,
        USPS_URL,
        body="""
        <Error>
            <Description>Address Not Found</Description>
        </Error>
        """,
        status=200
    )

    result = validate_address(
        "999 Fake St",
        "Raleigh",
        "NC",
        "99999"
    )

    assert result is False


#failure test for failed retrevial of API
@responses.activate
def test_usps_api_failure(monkeypatch):

    monkeypatch.setenv("USPS_API_KEY", "TESTKEY")

    responses.add(
        responses.GET,
        USPS_URL,
        status=500
    )

    result = validate_address(
        "123 Main St",
        "Raleigh",
        "NC",
        "27603"
    )

    assert result is False


#fail test for a missing api key
def test_usps_missing_api_key(monkeypatch):

    monkeypatch.delenv("USPS_API_KEY", raising=False)

    with pytest.raises(ValueError):
        validate_address(
            "123 Main St",
            "Raleigh",
            "NC",
            "27603"
        )