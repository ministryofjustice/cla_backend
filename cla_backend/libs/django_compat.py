from django.urls import include, path, re_path


def patterns(prefix, *args):
    """Compatibility helper for removed django.conf.urls.patterns."""
    return list(args)


# Preserve old import style: from ... import url
url = re_path
