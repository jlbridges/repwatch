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
    billList = []
    if response.status_code == 200:
        data = response.json()

        bills = data.get("bills", [])
        
        for bill in bills:
           
            leg_data = {
                "number":bill.get("number"),
                "congress":bill.get("congress"),
                "type":bill.get("type"),               
                "title": bill.get("title"),
             #"originChamberCode": bill.get("originChamber"),
            }
            billList.append(leg_data)
            
       # print("Bills saved successfully")
        
    else:
        print("Error fetching bills")
    return billList