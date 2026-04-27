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

def get_bill_details_summary_API_call(congress, bill_type, bill_number):   
    url = f"https://api.congress.gov/v3/bill/{congress}/{bill_type.lower()}/{bill_number}/summaries"     
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
def save_bill_detail(bill):    
    data = get_bill_details(bill.congress, bill.type, bill.number)
    try:         
        summary_result=get_bill_details_summary_API_call(bill.congress, bill.type, bill.number)       
        summary=summary_result['summaries'][0]['text']
    except Exception as e:
        print('error geting data from summary')
        summary = 'not reproted'       
    
    # saves bill details to database
    bbd = BillDetail.objects.update_or_create(
        bill_header = bill,
        number=data['bill']['number'],
        congress=data['bill']['congress'],
        type=data['bill']['type'],
        bill_subject = data['bill']['policyArea']['name'],
        originChamber = data['bill']['originChamber'],
        sponsor_bioguideId = data['bill']['sponsors'][0]['bioguideId'],
        firstName = data['bill']['sponsors'][0]['firstName'],
        lastName = data['bill']['sponsors'][0]['lastName'],
        party = data['bill']['sponsors'][0]['party'],
        introducedDate = data['bill']['introducedDate'],
        actionDesc = data['bill']['latestAction']['text'],
        bill_summary=summary,
    )
    #bbd.save()