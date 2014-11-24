import datetime

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def notify_callback_created(case):
    to = settings.CALL_CENTRE_NOTIFY_EMAIL_ADDRESS
    if not to:
        return
    from_address = 'no-reply@digital.justice.gov.uk'
    subject = 'Callback for CLA Case {ref} has been requested'.format(ref=case.reference)
    case_url = 'https://{0}/call_centre/{1}/'
    template_params = {
        'now': datetime.datetime.now(),
        'case_url': case_url.format(settings.SITE_HOSTNAME, case.reference),
        'case': case}
    template = 'call_centre/email/case_cb1_created.{0}'
    text = render_to_string(template.format('txt'), template_params)
    email = EmailMultiAlternatives(
        subject, text, from_address, [to])
    email.send()
