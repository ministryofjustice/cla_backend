import functools
import vcr
import os
from freezegun import freeze_time

# match on POST body otherwise CFE-civil will just match on URL which isn't very good
custom_vcr = vcr.VCR(match_on=['method', 'scheme', 'host', 'port', 'path', 'query', 'body'])


def use_vcr_cassette(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        # freeze time to an arbitrary (pre MTR) date so that the cfe-civil requests
        # all have the same fixed submission date (and hence the same payload)
        with freeze_time("2024-01-15"):
            test_dir = os.path.dirname(f.func_code.co_filename)
            cassette_name = test_dir + "/cassettes/" + f.func_name + ".yml"
            with custom_vcr.use_cassette(cassette_name):
                return f(*args, **kwargs)
    return wrapper
