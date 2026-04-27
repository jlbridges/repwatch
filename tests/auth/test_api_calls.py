import os
import pytest
import responses

from core.services.geocodio_service import get_representatives_from_address

GEOCODIO_URL = "https://api.geocod.io/v1.12/geocode"


@pytest.mark.django_db
@responses.activate
def test_get_representatives_from_address_success(monkeypatch):

    monkeypatch.setenv("GEOCODIO_API_KEY", "test-key")

    mock_response = {
        "results": [
            {
                "fields": {
                    "congressional_districts": [
                        {
                            "district_number": 2,
                            "current_legislators": [
                                {
                                    "type": "representative",
                                    "bio": {
                                        "first_name": "Jane",
                                        "last_name": "Doe",
                                        "party": "Democrat",
                                        "photo_url": "http://example.com/photo.jpg",
                                    },
                                    "references": {
                                        "bioguide_id": "D000001"
                                    }
                                },
                                {
                                    "type": "senator",
                                    "bio": {
                                        "first_name": "John",
                                        "last_name": "Smith",
                                        "party": "Republican",
                                        "photo_url": "http://example.com/senator1.jpg",
                                    },
                                    "references": {
                                        "bioguide_id": "S000001"
                                    }
                                },
                                {
                                    "type": "senator",
                                    "bio": {
                                        "first_name": "Emily",
                                        "last_name": "Brown",
                                        "party": "Democrat",
                                        "photo_url": "http://example.com/senator2.jpg",
                                    },
                                    "references": {
                                        "bioguide_id": "S000002"
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        ]
    }

    responses.add(
        responses.GET,
        GEOCODIO_URL,
        json=mock_response,
        status=200,
    )

    reps = get_representatives_from_address("123 Main St, Raleigh, NC")

    assert reps is not None
    assert len(reps) == 3

    representatives = [r for r in reps if r["first_name"] == "Jane"]
    senators = [r for r in reps if r["first_name"] in {"John", "Emily"}]

    assert len(representatives) == 1
    assert len(senators) == 2


@responses.activate
def test_get_representatives_malformed_response(monkeypatch):

    monkeypatch.setenv("GEOCODIO_API_KEY", "test-key")

    responses.add(
        responses.GET,
        GEOCODIO_URL,
        json={"unexpected": "data"},
        status=200,
    )

    result = get_representatives_from_address("123 Main St")

    assert result is None


@responses.activate
def test_get_representatives_api_failure(monkeypatch):

    monkeypatch.setenv("GEOCODIO_API_KEY", "test-key")

    responses.add(
        responses.GET,
        GEOCODIO_URL,
        status=500,
    )

    result = get_representatives_from_address("123 Main St")

    assert result is None


def test_get_representatives_missing_api_key(monkeypatch):

    monkeypatch.delenv("GEOCODIO_API_KEY", raising=False)

    with pytest.raises(ValueError):
        get_representatives_from_address("123 Main St")