import glob
import re

from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.management.base import BaseCommand

from cla_backend.settings.base import root


class Command(BaseCommand):
    help = "Rewrites static file paths within our compiled css file, to be aware of our storage backend"
    css_dir = root("assets", "css")
    js_dir = root("assets", "scripts")

    regex_patterns = {
        "css": r"url\((?P<url>\"?(?:{static_url}|\.\.)(?P<path>.*?)\"?)\)",
        "js": r"""url\: ?['"](?P<url>(?:{static_url})(?P<path>.*?))['"]""",
    }

    def handle(self, *args, **kwargs):
        paths = [
            ("css", glob.glob("{dir}/*.css".format(dir=self.css_dir))),
            ("js", glob.glob("{dir}/*.js".format(dir=self.js_dir))),
        ]
        for file_type, file_paths in paths:
            for file_path in file_paths:
                self.stdout.write("Rewriting paths in {file_path}".format(file_path=file_path))
                with open(file_path, "r") as static_file:
                    contents = static_file.read()
                    matches = re.findall(
                        self.regex_patterns[file_type].format(static_url=settings.STATIC_URL), contents
                    )
                    for url, path in matches:
                        try:
                            # Set expiry to one week
                            new_url = staticfiles_storage.url(path, expire=604800)
                        except TypeError:
                            # Backend doesn't take an expire argument, so don't pass it
                            new_url = staticfiles_storage.url(path)
                        self.stdout.write("  Rewriting {old_url} to {new_url}".format(old_url=url, new_url=new_url))
                        contents = contents.replace(url, new_url)
                with open(file_path, "w") as static_file:
                    static_file.write(contents)
                    self.stdout.write("  Done")
