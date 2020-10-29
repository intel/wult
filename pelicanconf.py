# -*- coding: utf-8 -*- #
# vim: ts=4 sw=4 tw=100 et ai si

AUTHOR = "Artem Bityutskiy"
SITENAME = "Wult"
SITEURL = ""

PATH = "content"
TIMEZONE = "UTC"
DEFAULT_LANG = "en"

DELETE_OUTPUT_DIRECTORY = True

DISPLAY_CATEGORIES_ON_MENU = False
DISPLAY_PAGES_ON_MENU = False

FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

DEFAULT_PAGINATION = False
RELATIVE_URLS = True

THEME="../pelican-themes/fresh"

STATIC_PATHS=["results", "images"]
ARTICLE_EXCLUDES=["results"]

SYNTAX_THEME = "github"

MENUITEMS = (
    ("Overview", "/index.html"),
    ("Install", "/pages/install-guide.html"),
    ("Use", "/pages/user-guide.html"),
    ("Ndl", "/pages/ndl.html"),
)
