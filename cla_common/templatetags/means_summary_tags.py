from django import template
from django.utils.translation import gettext_lazy as _
import re
from .helpers import in_pounds


register = template.Library()


def text_yesno(value, true_str, false_str, **format_kwargs):

    if isinstance(value, dict) and "per_interval_value" in value:
        text = true_str if value["per_interval_value"] > 0 else false_str
    else:
        text = true_str if value else false_str

    default_format_kwargs = {"val": value}
    default_format_kwargs.update(format_kwargs)

    return _(text.format(**default_format_kwargs))


def text_plural(value, singular, plural):
    if isinstance(value, list):
        value = len(value)

    text = singular if value == 1 else plural
    return _(text.format(count=value))


def text_exists(value, true_str):
    if value:
        return _(true_str.format(val=value))
    return None


def default_dict(data, key):
    value = data.get(key)
    return value or {}


def money_interval_str(value):
    if not isinstance(value, dict) or "per_interval_value" not in value:
        return ""

    return u"%s %s" % (in_pounds(value["per_interval_value"]), value["interval_period"].replace("_", " "))


class MeansSummaryFormatter(object):
    def get_your_details(self, data):
        if not data:
            return data

        items = [
            text_exists(data.get("category"), "You are looking for help about {val}"),
            text_exists(data.get("your_problem_notes"), "Additional details about your problem: {val}"),
            text_yesno(data.get("has_partner"), "You live with a partner", "You don't live with a partner"),
            text_yesno(
                data.get("on_passported_benefits"),
                "You or your partner are on Income Support benefits",
                "You or your partner are not on Income Support benefits",
            ),
            text_yesno(
                data.get("has_children"),
                "You have children dependent on you",
                "You don't have children dependent on you",
            ),
            text_yesno(
                data.get("is_you_or_your_partner_over_60"),
                "You or your partner are 60 or over",
                "You or your partner are not 60 or over",
            ),
        ]

        # if your_details:
        #     items += [
        #         text_yesno(
        #             your_details.get('caring_responsibilities'),
        #             'You have other caring responsibilities',
        #             "You don't have any other caring responsibilities"
        #         ),
        #         text_yesno(
        #             your_details.get('own_property'),
        #             'You or your partner own a property',
        #             "You or your partner don't own a property"
        #         ),
        #         text_yesno(
        #             your_details.get('risk_homeless'),
        #             'You are in danger of losing your home',
        #             "You are not in danger of losing your home"
        #         ),
        #     ]

        return {"header": _("Details you've already given"), "step": "your_problem", "items": filter(None, items)}

    def get_your_finances(self, data):
        if not data:
            return data

        props = data.get("property_set")
        your_savings = default_dict(data, "you").get("savings")
        partners_savings = default_dict(data, "partner").get("savings")

        if not props and not your_savings and not partners_savings:
            return None

        items = []
        if props:
            items += [text_plural(props, "You have one property", "You have {count} properties")]

            for index, prop in enumerate(props, 1):
                items += [
                    _(
                        "Property {counter}: Your property is worth &pound{val}".format(
                            counter=index, val=in_pounds(prop.get("value"))
                        )
                    ),
                    text_yesno(
                        prop.get("mortgage_left"),
                        "Property {counter}: You have &pound;{val} left to pay on the mortgage",
                        "Property {counter}: You have no outstanding mortgage on the property",
                        counter=index,
                        val=in_pounds(prop.get("mortgage_left")),
                    ),
                    # text_yesno(
                    #     prop.get('owner'),
                    #     'Property {counter}: The property is not held in joint names.',
                    #     "Property {counter}: The property is held in joint names.",
                    #     counter=index
                    # ),
                    _(
                        "Property {counter}: You own {val}% of the property".format(
                            counter=index, val=prop.get("share")
                        )
                    ),
                    text_yesno(
                        prop.get("disputed"),
                        "Property {counter}: This is a disputed property",
                        "Property {counter}: This is not a disputed property",
                        counter=index,
                    ),
                ]

        if your_savings:
            items += [
                text_yesno(
                    your_savings.get("bank_balance"),
                    "You have &pound;{val} saved in a bank or building society",
                    "You don't have any money saved in a bank or building society",
                    val=in_pounds(your_savings.get("bank_balance")),
                ),
                text_yesno(
                    your_savings.get("investment_balance"),
                    "You have &pound;{val} in investments, shares, ISAs",
                    "You don't have any money in investments, shares, ISAs",
                    val=in_pounds(your_savings.get("investment_balance")),
                ),
                text_yesno(
                    your_savings.get("asset_balance"),
                    "You have valuable items worth &pound;{val}",
                    "You don't have any valuable items",
                    val=in_pounds(your_savings.get("asset_balance")),
                ),
                text_yesno(
                    your_savings.get("credit_balance"),
                    "You have &pound;{val} owned to you",
                    "You don't have any money owned to you",
                    val=in_pounds(your_savings.get("credit_balance")),
                ),
            ]

        if partners_savings:
            items += [
                text_yesno(
                    partners_savings.get("bank_balance"),
                    "Your partner has &pound;{val} saved in a bank or building society",
                    "Your partner doesn't have any money saved in a bank or building society",
                    val=in_pounds(partners_savings.get("bank_balance")),
                ),
                text_yesno(
                    partners_savings.get("investment_balance"),
                    "Your partner has &pound;{val} in investments, shares, ISAs",
                    "Your partner doesn't have any money in investments, shares, ISAs",
                    val=in_pounds(partners_savings.get("investment_balance")),
                ),
                text_yesno(
                    partners_savings.get("asset_balance"),
                    "Your partner has valuable items worth &pound;{val}",
                    "Your partner doesn't have any valuable items",
                    val=in_pounds(partners_savings.get("asset_balance")),
                ),
                text_yesno(
                    partners_savings.get("credit_balance"),
                    "Your partner has &pound;{val} owned to them",
                    "Your partner doesn't have any money owned to them",
                    val=in_pounds(partners_savings.get("credit_balance")),
                ),
            ]

        return {"header": _("Your finances"), "step": "your_capital", "items": filter(None, items)}

    def get_your_income(self, data):
        if not data:
            return data

        your_income = default_dict(data, "you").get("income")
        partners_income = default_dict(data, "partner").get("income")
        dependants_young = data.get("dependants_young")
        dependants_old = data.get("dependants_old")

        if not your_income and not partners_income:
            return None

        items = []
        if your_income:
            earnings = money_interval_str(your_income.get("earnings"))
            other_income = money_interval_str(your_income.get("other_income"))
            items += [
                text_yesno(
                    your_income.get("earnings"), "Your earnings: &pound;{val}", "You don't have earnings", val=earnings
                ),
                text_yesno(your_income.get("self_employed"), "You are self employed", "You are not self employed"),
                text_yesno(
                    your_income.get("other_income"),
                    "Your other income: &pound;{val}",
                    "You don't have any other income",
                    val=other_income,
                ),
            ]

        if partners_income:
            earnings = money_interval_str(partners_income.get("earnings"))
            other_income = money_interval_str(partners_income.get("other_income"))
            items += [
                text_yesno(
                    partners_income.get("earnings"),
                    "Your partner's earnings: &pound;{val}",
                    "Your partner doesn't have earnings",
                    val=earnings,
                ),
                text_yesno(
                    partners_income.get("self_employed"),
                    "Your partner is self employed",
                    "Your partner is not self employed",
                ),
                text_yesno(
                    partners_income.get("other_income"),
                    "Your partner's other income: &pound;{val}",
                    "Your partner doesn't have any other income",
                    val=other_income,
                ),
            ]

        if dependants_young:
            items += [
                text_plural(
                    dependants_young,
                    "You have one child aged 15 and under",
                    "You have {count} children aged 15 and under",
                )
            ]

        if dependants_old:
            items += [
                text_plural(
                    dependants_old, "You have one child aged 16 and over", "You have {count} children aged 16 and over"
                )
            ]

        return {"header": _("Your income"), "step": "your_income", "items": filter(None, items)}

    def get_your_allowances(self, data):
        if not data:
            return data

        your_allowances = default_dict(data, "you").get("deductions")
        partners_allowances = default_dict(data, "partner").get("deductions")

        if not your_allowances and not partners_allowances:
            return None

        items = []

        if your_allowances:
            items += [
                _("Your mortgage: &pound;{val}".format(val=money_interval_str(your_allowances.get("mortgage")))),
                _("Your rent: &pound;{val}".format(val=money_interval_str(your_allowances.get("rent")))),
                _(
                    "Your national insurance: &pound;{val}".format(
                        val=money_interval_str(your_allowances.get("national_insurance"))
                    )
                ),
                _("Your income tax: &pound;{val}".format(val=money_interval_str(your_allowances.get("income_tax")))),
                _("Your maintenance: &pound;{val}".format(val=money_interval_str(your_allowances.get("maintenance")))),
                _("Your childcare: &pound;{val}".format(val=money_interval_str(your_allowances.get("childcare")))),
                _(
                    "Your payments being made towards a contribution order: &pound;{val}".format(
                        val=in_pounds(your_allowances.get("criminal_legalaid_contributions"))
                    )
                ),
            ]

        if partners_allowances:
            items += [
                _(
                    "Your partner's mortgage: &pound;{val}".format(
                        val=money_interval_str(partners_allowances.get("mortgage"))
                    )
                ),
                _("Your partner's rent: &pound;{val}".format(val=money_interval_str(partners_allowances.get("rent")))),
                _(
                    "Your partner's national insurance: &pound;{val}".format(
                        val=money_interval_str(partners_allowances.get("national_insurance"))
                    )
                ),
                _(
                    "Your partner's income tax: &pound;{val}".format(
                        val=money_interval_str(partners_allowances.get("income_tax"))
                    )
                ),
                _(
                    "Your partner's maintenance: &pound;{val}".format(
                        val=money_interval_str(partners_allowances.get("maintenance"))
                    )
                ),
                _(
                    "Your partner's childcare: &pound;{val}".format(
                        val=money_interval_str(partners_allowances.get("childcare"))
                    )
                ),
                _(
                    "Your partner's payments being made towards a contribution order: &pound;{val}".format(
                        val=in_pounds(partners_allowances.get("criminal_legalaid_contributions"))
                    )
                ),
            ]

        return {"header": _("Your expenses"), "step": "your_allowances", "items": filter(None, items)}

    def format(self, data):
        d = [
            self.get_your_details(data),
            self.get_your_finances(data),
            self.get_your_income(data),
            self.get_your_allowances(data),
        ]

        return filter(None, d)


class MeansSummaryNode(template.Node):
    def __init__(self, data, var_name):
        self.data = template.Variable(data)
        self.var_name = var_name

    def render(self, context):
        data = self.data.resolve(context)

        formatter = MeansSummaryFormatter()
        context[self.var_name] = formatter.format(data)
        return ""


@register.tag
def get_means_summary(parser, token):
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires arguments" % token.contents.split()[0])

    m = re.search(r"(.*?) as (\w+)", arg)
    if not m:
        raise template.TemplateSyntaxError("%r tag had invalid arguments" % tag_name)
    data, var_name = m.groups()
    return MeansSummaryNode(data, var_name)
