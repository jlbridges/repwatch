import os
import requests

BASE_URL = "https://api.geocod.io/v1.9/geocode"


def get_representatives_from_address(address):
    """
    Calls the Geocodio API and returns structured legislator data
    (representatives + senators).
    """

    api_key = os.getenv("GEOCODIO_API_KEY")

    if not api_key:
        raise ValueError("GEOCODIO_API_KEY environment variable not set.")

    params = {
        "q": address,
        "fields": "cd",
        "api_key": api_key
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
    except requests.RequestException:
        return None

    if response.status_code != 200:
        return None

    data = response.json()

    try:
        result = data["results"][0]
        district_info = result["fields"]["congressional_districts"][0]

        district_number = district_info.get("district_number")
        legislators = district_info.get("current_legislators", [])

        reps = []

        for person in legislators:
            # ✅ Include BOTH representatives and senators
            if person.get("type") not in ["representative", "senator"]:
                continue

            bio = person.get("bio", {})
            references = person.get("references", {})

            # ✅ Skip completely empty entries (extra safety)
            if not bio:
                continue

            first = bio.get("first_name")
            last = bio.get("last_name")

            rep_data = {
                "bioguide_id": references.get("bioguide_id"),
                "district_number": district_number,
                "first_name": first,
                "last_name": last,
                "name": f"{first} {last}" if first and last else None,
                "party": bio.get("party"),
                "photo_url": bio.get("photo_url"),
                "type": person.get("type"),  # 🔥 helpful if you want to distinguish later
            }

            reps.append(rep_data)

        return reps

    except (KeyError, IndexError, TypeError):
        return None