# coding=utf-8
import logging
import re

import requests

log = logging.getLogger(__name__)


class AddressLookup(object):
    def __init__(self, key, url=None):
        if not key:
            raise Exception("OS Places API key required")
        self.key = key
        if not url:
            url = "https://api.os.uk/search/places/v1/postcode"
        self.url = url

    def by_postcode(self, postcode):
        params = {"postcode": postcode, "key": self.key, "output_srs": "WGS84", "dataset": "DPA"}
        try:
            os_places_response = requests.get(self.url, params=params, timeout=3)
            os_places_response.raise_for_status()
        except requests.exceptions.ConnectTimeout as e:
            log.error("OS Places request timed out: {}".format(e))
        except requests.exceptions.RequestException as e:
            log.error("OS Places request error: {}".format(e))
        else:
            try:
                return os_places_response.json().get("results", [])
            except ValueError as e:
                log.warning("OS Places response JSON parse error: {}".format(e))
        return []


class FormattedAddressLookup(AddressLookup):
    def format_address_from_result(self, raw_result):
        dpa_result = raw_result.get("DPA")
        if dpa_result:
            return self.format_address_from_dpa_result(dpa_result)

    def format_address_from_dpa_result(self, raw_result):
        address_format = [
            {"fields": ["ORGANISATION_NAME"]},
            {"fields": ["SUB_BUILDING_NAME"]},
            {"fields": ["BUILDING_NAME"]},
            {"fields": ["BUILDING_NUMBER", "THOROUGHFARE_NAME"]},
            {"fields": ["DEPENDENT_LOCALITY"]},
            {"fields": ["POST_TOWN"]},
            {"fields": ["POSTCODE"], "transform": "upper"},
        ]
        formatted_lines = self.format_lines(address_format, raw_result)
        return "\n".join([c for c in formatted_lines if c])

    def format_lines(self, address_format, raw_result):
        for line_format in address_format:
            line_components = []
            for field in line_format["fields"]:
                line_components.append(raw_result.get(field, ""))
            line_string = " ".join(line_components)
            transform = line_format.get("transform")
            if transform:
                transformed_line = getattr(line_string, transform)()
            else:
                transformed_line = self.special_title_case(line_string)
            yield transformed_line.strip()

    @staticmethod
    def special_title_case(original_string, exceptions=None):
        if not exceptions:
            exceptions = ["of", "the"]
        word_list = re.split(" ", original_string.lower())
        final = [word_list[0].capitalize()]
        for word in word_list[1:]:
            final.append(word if word in exceptions else word.title())
        return " ".join(final)

    def by_postcode(self, postcode):
        os_places_results = super(FormattedAddressLookup, self).by_postcode(postcode)
        return [self.format_address_from_result(result) for result in os_places_results]
