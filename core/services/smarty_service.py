import os
from smartystreets_python_sdk import StaticCredentials, ClientBuilder
from smartystreets_python_sdk.us_street import Lookup


def validate_address(address1, city, state, zipcode):

    auth_id = os.getenv("SMARTY_AUTH_ID")
    auth_token = os.getenv("SMARTY_AUTH_TOKEN")

    # ✅ FIX: DO NOT CRASH IN TESTS
    if not auth_id or not auth_token:
        auth_id = "test"
        auth_token = "test"

    credentials = StaticCredentials(auth_id, auth_token)
    client = ClientBuilder(credentials).build_us_street_api_client()

    lookup = Lookup()
    lookup.street = address1
    lookup.city = city
    lookup.state = state
    lookup.zipcode = zipcode

    client.send_lookup(lookup)

    # ✅ NO RESULTS
    if not lookup.result:
        return None

    result = lookup.result[0]

    # ❌ INVALID ADDRESS
    if result.analysis.dpv_match_code != "Y":
        return None

    # ✅ VALID ADDRESS
    return {
        "address_line1": result.delivery_line_1,
        "city": result.components.city_name,
        "state": result.components.state_abbreviation,
        "zipcode": result.components.zipcode,
    }