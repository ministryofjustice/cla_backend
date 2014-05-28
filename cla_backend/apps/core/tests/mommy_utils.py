from model_mommy import mommy

from django.conf import settings


def make_recipe(model_def, **kwargs):
    app, model_name = model_def.split('.')
    return mommy.make_recipe(
        u'%s.tests.%s' % (app.lower(), model_name.lower()),
        **kwargs
    )

def make_user(**kwargs):
    return mommy.make(settings.AUTH_USER_MODEL, **kwargs)
