from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save

from .signals import log_user_created, log_user_modified


def get_web_user():
    web_user, created = User.objects.get_or_create(username='web')
    if created:
        web_user.set_unusable_password()
        web_user.save()
    return web_user


post_save.connect(log_user_created, sender=User)
pre_save.connect(log_user_modified, sender=User)
