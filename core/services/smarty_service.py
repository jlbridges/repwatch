import os
import sys
import re
from smartystreets_python_sdk import StaticCredentials, ClientBuilder
from smartystreets_python_sdk.us_street import Lookup


def validate_address(address1, city, state, zipcode):

    # HANDLE EMPTY INPUT FIRST
    if not address1 or not city or not state or not zipcode:
        return None

    import re

    if not re.match(r"^\d+\s+.+", address1):
        return None

    if not re.match(r"^\d{5}$", zipcode):
        return None

    if not re.match(r"^[A-Z]{2}$", state):
        return None

    auth_id = os.getenv("SMARTY_AUTH_ID")
    auth_token = os.getenv("SMARTY_AUTH_TOKEN")

    if not auth_id or not auth_token:
        return None   # ❗ do NOT raise

    credentials = StaticCredentials(auth_id, auth_token)
    client = ClientBuilder(credentials).build_us_street_api_client()

    lookup = Lookup()
    lookup.street = address1
    lookup.city = city
    lookup.state = state
    lookup.zipcode = zipcode

    try:
        client.send_lookup(lookup)
    except Exception:
        return None

    if len(lookup.result) == 0:
        return None

    result = lookup.result[0]

    if result.analysis.dpv_match_code not in ["Y", "S", "D"]:
        return None

    return {
        "address_line1": result.delivery_line_1,
        "city": result.components.city_name,
        "state": result.components.state_abbreviation,
        "zipcode": result.components.zipcode
    }