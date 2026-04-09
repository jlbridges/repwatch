import os
import requests

BASE_URL = "https://api.geocod.io/v1.9/geocode"


def get_representatives_from_address(address):
    api_key = os.getenv("GEOCODIO_API_KEY")

    if not api_key:
        raise ValueError("Missing GEOCODIO_API_KEY")

    params = {
        "q": address,
        "fields": "cd",
        "api_key": api_key
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
    except requests.RequestException as e:
        print("❌ Request failed:", e)
        return None

    if response.status_code != 200:
        print("❌ Bad response:", response.status_code, response.text)
        return None

    data = response.json()
    print("GEOCODIO RAW:", data)

    try:
        results = data.get("results", [])
        if not results:
            print("❌ No results")
            return None

        districts = results[0].get("fields", {}).get("congressional_districts", [])
        if not districts:
            print("❌ No districts")
            return None

        legislators = districts[0].get("current_legislators", [])
        district_number = districts[0].get("district_number")

        reps = []

        for person in legislators:
            bio = person.get("bio", {})
            references = person.get("references", {})

            bioguide_id = references.get("bioguide_id")
            if not bioguide_id:
                continue

            rep_data = {
                "bioguide_id": bioguide_id,
                "district_number": district_number,
                "first_name": bio.get("first_name"),
                "last_name": bio.get("last_name"),
                "name": f"{bio.get('first_name')} {bio.get('last_name')}",
                "party": bio.get("party"),
                "type": person.get("type"),
                "photo_url": bio.get("photo_url"),
            }

            reps.append(rep_data)

        print("✅ PARSED REPS:", reps)
        return reps

    except Exception as e:
        print("❌ Parsing error:", e)
        return None