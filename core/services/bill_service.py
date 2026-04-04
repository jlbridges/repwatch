import requests
from django.conf import settings
from core.models import BillHeader


def get_bill_headers():
    url = "https://api.congress.gov/v3/bill"
    
    params = {
        "api_key": settings.CONGRESS_API_KEY,
        "format": "json"
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()

        bills = data.get("bills", [])

        for bill in bills:
            BillHeader.objects.update_or_create(
                number=bill.get("number"),
                congress=bill.get("congress"),
                type=bill.get("type"),
                defaults={
                    "originChamberCode": bill.get("originChamber"),
                    "title": bill.get("title"),
                }
            )

        print("Bills saved successfully")

    else:
        print("Error fetching bills")