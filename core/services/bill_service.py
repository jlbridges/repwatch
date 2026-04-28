import html
import re

import requests
from django.conf import settings
from django.utils.html import strip_tags

from core.models import BillHeader, BillDetail


def _clean_summary(text):
    if not text:
        return ''
    text = strip_tags(text)
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# New version of get_bill_headers
# Takes user to determine if bills are already saved and visually display that on search results
def get_bill_header_data(user):
    congress = 119
    url = f"https://api.congress.gov/v3/bill/{congress}"
    params = {
        "api_key": settings.CONGRESS_API_KEY,
        "limit": 250,
        "format": "json"
    }

    response = requests.get(url, params=params)

    saved_bills = dict(BillHeader.objects.filter(saved_by=user).values_list("number", "id"))

    bills_list = []

    if response.status_code == 200:
        bills = response.json().get("bills", [])
        for bill in bills:
            number = bill.get("number")
            bill_type = bill.get("type")
            chamber = bill.get("originChamberCode").lower()
            title = bill.get("title")
            saved_id = saved_bills.get(int(number))

            bills_list.append({
                "number": number,
                "bill_type": bill_type,
                "chamber": chamber,
                "title": title,
                "saved": saved_id is not None,
                "saved_id": saved_id,
            })
    else:
        print("Error fetching bills:", response.status_code)

    return {
        "meta": {"congress": congress, "pages": len(bills_list) / 20},
        "bills": bills_list,
    }



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
            originChamber = bill.get("originChamber")
            bill_type = bill.get("type")
            title = bill.get("title")
            

            if not number or not bill_type:
                continue

            leg_data = {
                "number": number,
                "congress": congress, 
                "type": bill_type,
                "title": title,
                "originChamber":originChamber
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



def _fetch_bill_summary(bill_block):
    congress = bill_block.get('congress')
    bill_type = bill_block.get('type')
    bill_number = bill_block.get('number')
    if not (congress and bill_type and bill_number):
        return ''
    result = get_bill_details_summary_API_call(congress, bill_type, bill_number)
    if not result:
        return ''
    items = result.get('summaries') or []
    if not items:
        return ''
    return _clean_summary(items[0].get('text', ''))


class DuplicateBillError(Exception):
    pass


def save_bill_for_user(user, *, number, congress, bill_type, title=""):
    try:
        bill, created = BillHeader.objects.get_or_create(
            number=number,
            congress=congress,
            type=bill_type,
            defaults={"title": title or ""},
        )
    except BillHeader.MultipleObjectsReturned:
        raise DuplicateBillError(
            f"Duplicate BillHeader rows for {bill_type} {number} congress {congress}"
        )

    bill.saved_by.add(user)
    save_bill_detail(bill)
    return bill, created


def remove_bill_for_user(user, bill_id):
    bill = BillHeader.objects.get(id=bill_id)
    bill.saved_by.remove(user)
    return bill


def save_bill_detail(bill):
    data = get_bill_details(bill.congress, bill.type, bill.number)
    if not data or 'bill' not in data:
        print(f"No bill details returned for {bill.type} {bill.number}")
        return

    bill_block = data['bill']
    summary = _fetch_bill_summary(bill_block)

    sponsors = bill_block.get('sponsors') or []
    sponsor = sponsors[0] if sponsors else {}
    policy_area = bill_block.get('policyArea') or {}
    latest_action = bill_block.get('latestAction') or {}

    BillDetail.objects.update_or_create(
        bill_header=bill,
        defaults={
            'number': bill_block.get('number'),
            'congress': bill_block.get('congress'),
            'type': bill_block.get('type', ''),
            'bill_subject': policy_area.get('name', '') or '',
            'originChamber': bill_block.get('originChamber', '') or '',
            'sponsor_bioguideId': sponsor.get('bioguideId', '') or '',
            'firstName': sponsor.get('firstName', '') or '',
            'lastName': sponsor.get('lastName', '') or '',
            'party': sponsor.get('party', '') or '',
            'introducedDate': bill_block.get('introducedDate'),
            'actionDesc': latest_action.get('text', '') or '',
            'bill_summary': summary,
        },
    )