# coding=utf-8

import unittest

import mock
import requests
import requests_mock

from cla_common.address_lookup.ordnance_survey import AddressLookup, FormattedAddressLookup


class TestAddressLookup(unittest.TestCase):
    os_url = "https://api.os.uk/search/places/v1/postcode"
    api_key = "DUMMY_KEY"
    postcode = "SW1H 9AG"
    prerecorded_api_response = {
        "results": [
            {
                "DPA": {
                    "ENTRY_DATE": "20/06/2012",
                    "POSTAL_ADDRESS_CODE_DESCRIPTION": "A record which is linked to PAF",
                    "LOCAL_CUSTODIAN_CODE_DESCRIPTION": "CITY OF WESTMINSTER",
                    "LOCAL_CUSTODIAN_CODE": 5990,
                    "POSTCODE": "SW1H 9AG",
                    "UPRN": "10033617916",
                    "UDPRN": "52712028",
                    "ORGANISATION_NAME": "MINISTRY OF JUSTICE",
                    "POST_TOWN": "LONDON",
                    "LANGUAGE": "EN",
                    "CLASSIFICATION_CODE_DESCRIPTION": "Office",
                    "THOROUGHFARE_NAME": "QUEEN ANNES GATE",
                    "Y_COORDINATE": 179549.0,
                    "BUILDING_NUMBER": "52",
                    "RPC": "1",
                    "LAST_UPDATE_DATE": "10/02/2016",
                    "LOGICAL_STATUS_CODE": "1",
                    "BLPU_STATE_CODE_DESCRIPTION": "In use",
                    "LNG": -0.1346249,
                    "MATCH_DESCRIPTION": "EXACT",
                    "STATUS": "APPROVED",
                    "TOPOGRAPHY_LAYER_TOID": "osgb1000001796535716",
                    "BLPU_STATE_DATE": "20/06/2012",
                    "X_COORDINATE": 529576.0,
                    "MATCH": 1.0,
                    "POSTAL_ADDRESS_CODE": "D",
                    "ADDRESS": "MINISTRY OF JUSTICE " "52" "QUEEN ANNES GATE" "LONDON" "SW1H 9AG",
                    "LAT": 51.5000351,
                    "BLPU_STATE_CODE": "2",
                }
            }
        ]
    }

    def test_request_timeout(self):
        with requests_mock.Mocker() as rm, mock.patch("cla_common.address_lookup.ordnance_survey.log") as log_mock:
            rm.register_uri("GET", self.os_url, exc=requests.exceptions.ConnectTimeout)
            addresses = AddressLookup(key=self.api_key).by_postcode(self.postcode)
            self.assertEqual(log_mock.error.call_count, 1)
            self.assertIn("OS Places request timed out: ", "{}".format(log_mock.error.call_args))
            self.assertEquals([], addresses)

    def test_failed_request_logging(self):
        with requests_mock.Mocker() as rm, mock.patch("cla_common.address_lookup.ordnance_survey.log") as log_mock:
            rm.register_uri("GET", self.os_url, status_code=500)
            addresses = AddressLookup(key=self.api_key).by_postcode(self.postcode)
            self.assertEqual(log_mock.error.call_count, 1)
            self.assertIn("OS Places request error: ", "{}".format(log_mock.error.call_args))
            self.assertEquals([], addresses)

    def test_malformed_result(self):
        with requests_mock.Mocker() as rm, mock.patch("cla_common.address_lookup.ordnance_survey.log") as log_mock:
            rm.register_uri("GET", self.os_url, content="{malformed: 'json'}")
            addresses = AddressLookup(key=self.api_key).by_postcode(self.postcode)
            self.assertEqual(log_mock.warning.call_count, 1)
            self.assertIn("OS Places response JSON parse error: ", "{}".format(log_mock.warning.call_args))
            self.assertEquals([], addresses)

    def test_address_formatting(self):
        expected_result = ["Ministry of Justice\n52 Queen Annes Gate\nLondon\nSW1H 9AG"]

        with requests_mock.Mocker() as rm:
            rm.get(self.os_url, json=self.prerecorded_api_response)
            formatted_addresses = FormattedAddressLookup(key=self.api_key).by_postcode(self.postcode)
            self.assertEqual(expected_result, formatted_addresses)
