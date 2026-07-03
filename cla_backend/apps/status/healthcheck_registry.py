from importlib import import_module

from django.conf import settings


def import_string(path):
    module_path, attribute = path.rsplit(".", 1)
    module = import_module(module_path)
    return getattr(module, attribute)


class HealthcheckRegistry(object):
    def __init__(self):
        self._registry = []

    def load_healthchecks(self):
        self._registry = []
        for dotted_path in getattr(settings, "HEALTHCHECKS", []):
            self._registry.append(import_string(dotted_path))


registry = HealthcheckRegistry()