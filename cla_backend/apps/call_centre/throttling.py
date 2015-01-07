from rest_framework.throttling import UserRateThrottle


class OBIEERateThrottle(UserRateThrottle):
    rate = '20/day'
