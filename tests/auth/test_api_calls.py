import os
import pytest
import responses

from core.services.geocodio_service import get_representatives_from_address

GEOCODIO_URL = "https://api.geocod.io/v1.9/geocode"


@pytest.mark.django_db
@responses.activate
def test_get_representatives_from_address_success(monkeypatch):
    # Arrange
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
                                    "type": "senator"  # should be ignored
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

    # Act
    reps = get_representatives_from_address("123 Main St, Raleigh, NC")

    # Assert
    assert reps is not None
    assert len(reps) == 1

    rep = reps[0]
    assert rep["first_name"] == "Jane"
    assert rep["last_name"] == "Doe"
    assert rep["district_number"] == 2
    assert rep["party"] == "Democrat"
    assert rep["bioguide_id"] == "D000001"


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