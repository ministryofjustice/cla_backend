import requests


class LaaLaaError(Exception):
    pass


class LaalaaProviderCategoriesApiClient(object):
    instance = None

    def __init__(self, laalaa_base_url, category_translator):
        self.categories = {}
        self.category_translator = category_translator
        self.laalaa_base_url = laalaa_base_url

    def get_categories(self):
        return self.categories or self._load_categories()

    def _load_categories(self):
        categories = self._fetch_categories()
        # Translate categories and force keys to lower case
        for category in categories:
            code = category["code"].lower()
            self.categories[code] = self.category_translator(category["name"])
        return self.categories

    def _fetch_categories(self):
        url = "{host}/categories_of_law".format(host=self.laalaa_base_url)
        try:
            response = requests.get(url)
            return response.json()
        except (requests.exceptions.RequestException, ValueError) as e:
            raise LaaLaaError(e)

    @classmethod
    def singleton(cls, *args, **kwargs):
        if not cls.instance:
            cls.instance = cls(*args, **kwargs)
        return cls.instance
