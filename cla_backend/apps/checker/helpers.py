from django.conf import settings
from govuk_notify.api import GovUkNotify


def notify_callback_created(case):
    to = settings.CALL_CENTRE_NOTIFY_EMAIL_ADDRESS
    if not to:
        return

    case_url = "https://{0}/call_centre/{1}/"
    contact_third_party = bool(case.thirdparty_details and case.thirdparty_details.personal_details)
    template_id = settings.GOVUK_NOTIFY_TEMPLATES["CALLBACK_CREATED_PERSONAL"]
    if contact_third_party:
        template_id = settings.GOVUK_NOTIFY_TEMPLATES["CALLBACK_CREATED_THIRD_PARTY"]

    personalisation = {
        "reference": case.reference,
        "contact_third_party": contact_third_party,
        "contact_personal": not contact_third_party,
        "personal_full_name": case.personal_details.full_name,
        "case_url": case_url.format(settings.FRONTEND_HOST_NAME, case.reference),
        "callback_time_string": case.callback_time_string,
    }
    if personalisation["contact_third_party"]:
        personalisation.update(
            {
                "third_party_full_name": case.thirdparty_details.personal_details.full_name,
                "third_party_phone": case.thirdparty_details.personal_details.mobile_phone,
            }
        )
    else:
        personalisation.update({"personal_mobile_phone": case.personal_details.mobile_phone})

    email = GovUkNotify()
    email.send_email(email_address=to, template_id=template_id, personalisation=personalisation)
