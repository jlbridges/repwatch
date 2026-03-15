import os
import requests

BASE_URL = "https://api.congress.gov/v3/member"


def get_member_details(bioguide_id):
    """
    Fetch detailed information about a representative
    using the Congress API.
    """

    api_key = os.getenv("CONGRESS_API_KEY")

    if not api_key:
        raise ValueError("CONGRESS_API_KEY environment variable not set.")

    url = f"{BASE_URL}/{bioguide_id}"

    params = {
        "api_key": api_key
    }

    try:
        response = requests.get(url, params=params, timeout=10)
    except requests.RequestException:
        return None

    if response.status_code != 200:
        return None

    data = response.json()

    try:
        member = data["member"]

        return {
            "official_website": member["depiction"]["officialWebsiteUrl"],
            "sponsored_legislation": member["sponsoredLegislation"]["count"],
            "cosponsored_legislation": member["cosponsoredLegislation"]["count"],
            "current_member": member["currentMember"]
        }

    except (KeyError, IndexError):
        return None