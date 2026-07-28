from model_bakery import baker as mommy
from model_bakery.utils import import_from_str

from django.conf import settings


def make_recipe(model_def, **kwargs):
    app, model_name = model_def.split(".")
    recipe_name = model_name.lower()

    # Existing project recipes live in tests.mommy_recipes.
    try:
        recipe = import_from_str(f"{app.lower()}.tests.mommy_recipes.{recipe_name}")
    except ModuleNotFoundError:
        # Keep compatibility with model_bakery's default baker_recipes lookup.
        return mommy.make_recipe("%s.tests.%s" % (app.lower(), recipe_name), **kwargs)

    return recipe.make(**kwargs)


def make_user(**kwargs):
    return mommy.make(settings.AUTH_USER_MODEL, **kwargs)
