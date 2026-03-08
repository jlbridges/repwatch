# core/services/usps_service.py

import os
import requests

USPS_URL = "https://secure.shippingapis.com/ShippingAPI.dll"


def validate_address(address1, city, state, zipcode):
    user_id = os.getenv("USPS_API_KEY")

    if not user_id:
        raise ValueError("USPS_API_KEY environment variable not set.")

    xml = f"""
    <AddressValidateRequest USERID="{user_id}">
        <Address ID="0">
            <Address1></Address1>
            <Address2>{address1}</Address2>
            <City>{city}</City>
            <State>{state}</State>
            <Zip5>{zipcode}</Zip5>
            <Zip4></Zip4>
        </Address>
    </AddressValidateRequest>
    """

    params = {
        "API": "Verify",
        "XML": xml
    }

    response = requests.get(USPS_URL, params=params, timeout=10)

    if response.status_code != 200:
        return False

    if "<Error>" in response.text:
        return False

    return True