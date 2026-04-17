import requests
from django.conf import settings
from core.models import BillHeader, BillDetail


def get_bill_headers(congress):
    url = f"https://api.congress.gov/v3/bill/{congress}"

    params = {
        "api_key": settings.CONGRESS_API_KEY,
        "format": "json"
    }

    response = requests.get(url, params=params)
    billList = []

    if response.status_code == 200:
        data = response.json()
        bills = data.get("bills", [])

        for bill in bills:

            number = bill.get("number")
            bill_type = bill.get("type")
            title = bill.get("title")

            if not number or not bill_type:
                continue

            leg_data = {
                "number": number,
                "congress": congress,   # ✅ use passed value
                "type": bill_type,
                "title": title,
            }

            billList.append(leg_data)

           

    else:
        print("Error fetching bills:", response.status_code)

    return billList


def get_bill_details(congress, bill_type, bill_number):
    url = f"https://api.congress.gov/v3/bill/{congress}/{bill_type}/{bill_number}"

    params = {
        "api_key": settings.CONGRESS_API_KEY,
        "format": "json"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return None

    data = response.json()
    
    
    return data
#implement bill details structure - list item added to a new function save_bill_detail
def save_bill_detail(data, bill):
    print('data from save bill')
    print(data)
    # saves bill details to database
    bbd = BillDetail.objects.create(
        bill_header = bill,
        number=data['bill']['number'],
        congress=data['bill']['congress'],
        type=data['bill']['type'],
    )
    bbd.save()