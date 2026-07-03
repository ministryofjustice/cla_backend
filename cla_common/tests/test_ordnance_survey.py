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
                u"DPA": {
                    u"ENTRY_DATE": u"20/06/2012",
                    u"POSTAL_ADDRESS_CODE_DESCRIPTION": u"A record which is linked to PAF",
                    u"LOCAL_CUSTODIAN_CODE_DESCRIPTION": u"CITY OF WESTMINSTER",
                    u"LOCAL_CUSTODIAN_CODE": 5990,
                    u"POSTCODE": u"SW1H 9AG",
                    u"UPRN": u"10033617916",
                    u"UDPRN": u"52712028",
                    u"ORGANISATION_NAME": u"MINISTRY OF JUSTICE",
                    u"POST_TOWN": u"LONDON",
                    u"LANGUAGE": u"EN",
                    u"CLASSIFICATION_CODE_DESCRIPTION": u"Office",
                    u"THOROUGHFARE_NAME": u"QUEEN ANNES GATE",
                    u"Y_COORDINATE": 179549.0,
                    u"BUILDING_NUMBER": u"52",
                    u"RPC": u"1",
                    u"LAST_UPDATE_DATE": u"10/02/2016",
                    u"LOGICAL_STATUS_CODE": u"1",
                    u"BLPU_STATE_CODE_DESCRIPTION": u"In use",
                    u"LNG": -0.1346249,
                    u"MATCH_DESCRIPTION": u"EXACT",
                    u"STATUS": u"APPROVED",
                    u"TOPOGRAPHY_LAYER_TOID": u"osgb1000001796535716",
                    u"BLPU_STATE_DATE": u"20/06/2012",
                    u"X_COORDINATE": 529576.0,
                    u"MATCH": 1.0,
                    u"POSTAL_ADDRESS_CODE": u"D",
                    u"ADDRESS": u"MINISTRY OF JUSTICE " u"52" u"QUEEN ANNES GATE" u"LONDON" u"SW1H 9AG",
                    u"LAT": 51.5000351,
                    u"BLPU_STATE_CODE": u"2",
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
