import os
import requests
from django.conf import settings
from core.models import BillHeader


BASE_URL = "https://api.congress.gov/v3/bill"


def get_bill_headers():
    """
    Fetch bill data from Congress API and save to BillHeader model
    """

    api_key = getattr(settings, "CONGRESS_API_KEY", None)

    if not api_key:
        print("❌ Missing CONGRESS_API_KEY")
        return []

    params = {
        "api_key": api_key,
        "format": "json",
        "limit": 10  # you can increase later
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
    except requests.RequestException as e:
        print("❌ Request error:", e)
        return []

    if response.status_code != 200:
        print("❌ Bad response:", response.status_code)
        return []

    data = response.json()

    bills = data.get("bills", [])

    if not bills:
        print("❌ No bills returned")
        return []

    saved_bills = []

    for bill in bills:

        try:
            number = bill.get("number")
            congress = bill.get("congress")
            bill_type = bill.get("type")
            origin = bill.get("originChamberCode")
            title = bill.get("title")

            if not number or not congress:
                continue

            obj, created = BillHeader.objects.update_or_create(
                number=number,
                congress=congress,
                type=bill_type,
                defaults={
                    "originChamberCode": origin,
                    "title": title,
                }
            )

            saved_bills.append(obj)

        except Exception as e:
            print("❌ Error saving bill:", e)

    print("✅ Bills saved successfully")

    return saved_bills