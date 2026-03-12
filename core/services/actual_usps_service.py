import os
import requests
import xml.etree.ElementTree as ET

USPS_URL = "https://secure.shippingapis.com/ShippingAPI.dll"


def validate_address(address, city, state, zipcode):

    api_key = os.getenv("USPS_API_KEY")

    if not api_key:
        raise ValueError("USPS_API_KEY not set")

    xml_request = f"""
    <AddressValidateRequest USERID="{api_key}">
        <Address ID="0">
            <Address1></Address1>
            <Address2>{address}</Address2>
            <City>{city}</City>
            <State>{state}</State>
            <Zip5>{zipcode}</Zip5>
            <Zip4></Zip4>
        </Address>
    </AddressValidateRequest>
    """

    params = {
        "API": "Verify",
        "XML": xml_request
    }

    response = requests.get(USPS_URL, params=params, timeout=10)

    if response.status_code != 200:
        return None

    root = ET.fromstring(response.text)

    if root.find(".//Error") is not None:
        return None

    return {
        "address": root.findtext(".//Address2"),
        "city": root.findtext(".//City"),
        "state": root.findtext(".//State"),
        "zipcode": root.findtext(".//Zip5"),
    }