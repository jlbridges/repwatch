import os
import requests

BASE_URL = "https://api.geocod.io/v1.9/geocode"


def get_representatives_from_address(address):
    """
    Calls the Geocodio API and returns structured representative data
    matching the Representative model.
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

        district_number = district_info["district_number"]
        district_name = district_info.get("name")
        congress_number = district_info.get("congress_number")

        legislators = district_info["current_legislators"]

        reps = []

        for person in legislators:

            if person.get("type") in ["representative", "senator"]:

                bio = person.get("bio", {})
                references = person.get("references", {})

                rep_data = {

                    # IDs
                    "bioguide_id": references.get("bioguide_id"),
                    "thomas_id": references.get("thomas_id"),

                    # district info
                    "district_number": district_number,
                    "congress_number": congress_number,

                    # names
                    "first_name": bio.get("first_name"),
                    "last_name": bio.get("last_name"),

                    # district label
                    "name": district_name,

                    # political info
                    "party": bio.get("party"),
                    "type": person.get("type"),

                    # image
                    "photo_url": bio.get("photo_url"),

                    # contact form (from Geocodio)
                    "contact_form": person.get("contact_form")
                }

                reps.append(rep_data)

        return reps

    except (KeyError, IndexError):
        return None
    
