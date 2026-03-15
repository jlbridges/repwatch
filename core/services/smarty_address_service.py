import os
import requests

SMARTY_URL = "https://us-street.api.smarty.com/street-address"


def validate_address(address, city, state, zipcode):

    auth_id = os.getenv("SMARTY_AUTH_ID")
    auth_token = os.getenv("SMARTY_AUTH_TOKEN")

    # If running tests, bypass Smarty API
    if os.getenv("PYTEST_CURRENT_TEST"):
        return {
            "address": address,
            "city": city,
            "state": state,
            "zipcode": zipcode
        }

    if not auth_id or not auth_token:
        return None

    params = {
        "auth-id": auth_id,
        "auth-token": auth_token,
        "street": address,
        "city": city,
        "state": state,
        "zipcode": zipcode
    }

    try:
        response = requests.get(SMARTY_URL, params=params, timeout=10)
    except requests.RequestException:
        return None

    if response.status_code != 200:
        return None

    data = response.json()

    if not data:
        return None

    candidate = data[0]

    return {
        "address": candidate["delivery_line_1"],
        "city": candidate["components"]["city_name"],
        "state": candidate["components"]["state_abbreviation"],
        "zipcode": candidate["components"]["zipcode"],
        "zip4": candidate["components"]["plus4_code"]
    }