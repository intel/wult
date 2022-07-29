# -*- coding: utf-8 -*- #
# vim: ts=4 sw=4 tw=100 et ai si

AUTHOR = "Artem Bityutskiy"
SITENAME = "Wult"
SITEURL = "http://localhost:8000"

PATH = "content"
TIMEZONE = "UTC"
DEFAULT_LANG = "en"

DELETE_OUTPUT_DIRECTORY = True

DISPLAY_CATEGORIES_ON_MENU = False
DISPLAY_PAGES_ON_MENU = False
DISPLAY_ARTICLE_INFO_ON_INDEX=False
HIDE_SIDEBAR=True
HIDE_CATEGORIES=True

FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

DEFAULT_PAGINATION = False
#RELATIVE_URLS = True

THEME = "../pelican-chameleon"

STATIC_PATHS = ["results", "images"]
ARTICLE_EXCLUDES = ["results"]

MENUITEMS = (
    ("How it works", "/pages/how-it-works.html"),
    ("Install", [
        ("Local usage (standard case)", "/pages/install-local.html"),
        ("Remote usage", "/pages/install-remote.html"),
    ]),
    ("Use", "/pages/user-guide.html"),
    ("Howto", "/pages/howto.html"),
    ("Ndl", "/pages/ndl.html"),
)
