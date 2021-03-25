from django.test import TestCase
from django.contrib.auth.models import Permission, Group, ContentType
from django.core.management import call_command
from django.contrib.auth.models import User
from core.tests.mommy_utils import make_user


class ArticleCategoryClaSuperUsersPermissionCommandTest(TestCase):
    def test_command(self):
        group = Group.objects.get(name="CLA Superusers")
        cla_superuser = make_user()
        group.user_set.add(cla_superuser)

        content_type = ContentType.objects.get(app_label="knowledgebase", model="articlecategory")
        perms = [
            "knowledgebase.{}".format(perm.codename) for perm in Permission.objects.filter(content_type=content_type)
        ]
        self.assertFalse(cla_superuser.has_perms(perms))

        call_command("grant_cla_superusers_article_categories_permissions")

        # Reload the user object
        user = User.objects.get(pk=cla_superuser.pk)
        self.assertTrue(user.has_perms(perms))
