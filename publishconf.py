# -*- coding: utf-8 -*- #
# vim: ts=4 sw=4 tw=100 et ai si

# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys
sys.path.append(os.curdir)
from pelicanconf import *

SITEURL = "https://intel.github.io/wult"

MENUITEMS = (
    ("How it works", "/pages/how-it-works.html"),
    ("Install", "/pages/install-guide.html"),
    ("Use", "/pages/user-guide.html"),
    ("Howto", "/pages/howto.html"),
    ("Ndl", "/pages/ndl.html"),
)
