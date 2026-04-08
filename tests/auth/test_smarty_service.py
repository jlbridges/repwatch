from django.test import TestCase
from unittest.mock import patch, MagicMock

from core.services.smarty_service import validate_address


class SmartyServiceTests(TestCase):

    @patch("core.services.smarty_service.ClientBuilder")
    def test_valid_address(self, mock_builder):

        mock_client = MagicMock()
        mock_builder.return_value.build_us_street_api_client.return_value = mock_client

        mock_result = MagicMock()
        mock_result.delivery_line_1 = "1101 Oberlin Rd"
        mock_result.components.city_name = "Raleigh"
        mock_result.components.state_abbreviation = "NC"
        mock_result.components.zipcode = "27605"
        mock_result.analysis.dpv_match_code = "Y"

        mock_lookup = MagicMock()
        mock_lookup.result = [mock_result]

        mock_client.send_lookup.side_effect = lambda lookup: setattr(lookup, "result", mock_lookup.result)

        result = validate_address("1101 Oberlin Rd", "Raleigh", "NC", "27605")

        self.assertIsNotNone(result)
        self.assertEqual(result["city"], "Raleigh")


    @patch("core.services.smarty_service.ClientBuilder")
    def test_invalid_address(self, mock_builder):

        mock_client = MagicMock()
        mock_builder.return_value.build_us_street_api_client.return_value = mock_client

        mock_result = MagicMock()
        mock_result.analysis.dpv_match_code = "N"

        mock_lookup = MagicMock()
        mock_lookup.result = [mock_result]

        mock_client.send_lookup.side_effect = lambda lookup: setattr(lookup, "result", mock_lookup.result)

        result = validate_address("123 Fake St", "Nowhere", "NC", "99999")

        self.assertIsNone(result)


    @patch("core.services.smarty_service.ClientBuilder")
    def test_no_candidates_returned(self, mock_builder):

        mock_client = MagicMock()
        mock_builder.return_value.build_us_street_api_client.return_value = mock_client

        mock_client.send_lookup.side_effect = lambda lookup: setattr(lookup, "result", [])

        result = validate_address("Fake Address", "City", "NC", "12345")

        self.assertIsNone(result)