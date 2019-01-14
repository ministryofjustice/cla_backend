from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """
    Limits the rate of API calls that may be made to login endpoint.

    The IP address of the request will be used as the unique cache key.
    """

    scope = "login"
