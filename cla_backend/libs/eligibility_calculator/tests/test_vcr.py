import functools
import vcr

custom_vcr = vcr.VCR()


def use_vcr_cassette(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        cassette_name = "cassettes/" + f.__name__ + ".yml"
        with custom_vcr.use_cassette(cassette_name):
            return f(*args, **kwargs)
    return wrapper
