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
        "api_key": api_key,
        "format": "json",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print("REQUEST ERROR:", e)
        return None

    data = response.json()
    print("CONGRESS RAW JSON:", data)

    member = data.get("member")
    if not member:
        print("ERROR: member key not found")
        return None

    return {
        "current_member": member.get("currentMember"),
        "district": member.get("district"),
        "state": member.get("state"),
        "official_website": member.get("officialWebsiteUrl"),
        "sponsored_legislation": (
            member.get("sponsoredLegislation", {}).get("count",0)
            if isinstance(member.get("sponsoredLegislation"), dict)
            else 0
        ),
        "cosponsored_legislation": (
            member.get("cosponsoredLegislation", {}).get("count", 0)
            if isinstance(member.get("cosponsoredLegislation"), dict)
            else 0
        ),
        "party": (
            member.get("partyHistory", [{}])[0].get("partyName")
            if member.get("partyHistory")
            else None
        ),
        "type": (
            member.get("terms", [{}])[0].get("memberType")
            if member.get("terms")
            else None
        ),
        "congress": (
            member.get("terms", [{}])[-1].get("congress")
            if member.get("terms")
            else None
        ),
    }