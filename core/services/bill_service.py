import os
import requests

BASE_URL = "https://api.congress.gov/v3/bill"


def get_bill_headers(congress=119, limit=10, offset=0):
    """
    Fetch bill header data from Congress API
    """

    api_key = os.getenv("CONGRESS_API_KEY")

    if not api_key:
        raise ValueError("CONGRESS_API_KEY not set")

    url = f"{BASE_URL}/{congress}"

    params = {
        "api_key": api_key,
        "format": "json",
        "limit": limit,
        "offset": offset
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print("BILL API ERROR:", e)
        return []

    data = response.json()
    print("BILL RAW DATA:", data)

    bills = data.get("bills", [])

    results = []

    for bill in bills:
        results.append({
            "number": bill.get("number"),
            "congress": bill.get("congress"),
            "originChamberCode": bill.get("originChamberCode"),
            "type": bill.get("type"),
            "title": bill.get("title"),
        })

    return results