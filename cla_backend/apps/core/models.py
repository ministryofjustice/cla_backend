from django.contrib.auth.models import User


def get_web_user():
    return User.objects.get(username='web')
