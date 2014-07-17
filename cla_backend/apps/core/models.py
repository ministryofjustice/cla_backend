from django.contrib.auth.models import User


def get_web_user():
    web_user, created = User.objects.get_or_create(username='web')
    if created:
        web_user.set_unusable_password()
        web_user.save()
    return web_user
