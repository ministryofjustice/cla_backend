# coding=utf-8
from decimal import Decimal
from cla_common.services import translate


TWO_DP = Decimal(".01")
ZERO_DP = Decimal("1")


class MoneyInterval(object):
    value = None  # in pennies
    interval_period = None
    per_interval_value = None  # in pennies
    # interval_name, user_copy_name, multiply_factor (to get monthly value)
    _intervals = [
        ("per_week", translate("per week"), 52.0 / 12.0),
        ("per_2week", translate("2 weekly"), 26.0 / 12.0),
        ("per_4week", translate("4 weekly"), 13.0 / 12.0),
        ("per_month", translate("per month"), 1.0),
        ("per_year", translate("per year"), 1.0 / 12.0),
    ]

    _intervals_dict = {i[0]: {"user_copy_name": i[1], "multiply_factor": i[2]} for i in _intervals}

    def __init__(self, interval_period, pennies=None, pounds=None):
        if interval_period not in self._intervals_dict.keys():
            raise ValueError("Invalid interval period")

        if (pennies == None and pounds == None) or (pennies != None and pounds != None):  # noqa E711
            raise ValueError("Amount needs to be set")

        self.interval_period = interval_period

        if pennies != None:  # noqa E711
            self._set_as_pennies(pennies)
        else:
            self._set_as_pennies(int(Decimal(pounds * 100).quantize(ZERO_DP)))

    def is_valid_interval_period(self, interval_period):
        return interval_period in self._intervals_dict

    def _set_as_pennies(self, per_interval_value=None):
        self.per_interval_value = per_interval_value
        multiply_factor = self._intervals_dict[self.interval_period]["multiply_factor"]
        self.value = multiply_factor * self.per_interval_value

    @staticmethod
    def get_intervals_for_widget():
        """
        @return: list of tuples for dropdown widget
        """
        return [(i[0], i[1]) for i in MoneyInterval._intervals]

    def as_monthly(self):
        """
        @param interval_value: Decimal
        @param interval_name: enum from MoneyInterval._intervals
        @return: float
        """
        multiply_factor = float(MoneyInterval._intervals_dict[self.interval_period]["multiply_factor"])
        per_month = float(self.per_interval_value) * multiply_factor
        return int(per_month)

    def as_dict(self):
        return {
            "interval_period": self.interval_period,
            "per_interval_value": self.per_interval_value,
            "per_month": self.as_monthly(),
        }

    def __cmp__(self, other):
        if other == None or not isinstance(other, self.__class__):  # noqa E711
            return -1
        return self.as_monthly().__cmp__(other.as_monthly())

    def __str__(self):
        return u"{interval_value} pounds {interval_period} ({as_monthly} pounds per month)".format(
            interval_value=self.per_interval_value, interval_period=self.interval_period, as_monthly=self.as_monthly()
        )

    @classmethod
    def from_dict(cls, d):
        return cls(d["interval_period"], pennies=d["per_interval_value"])
