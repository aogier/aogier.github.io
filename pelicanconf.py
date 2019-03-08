#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Alessandro Ogier'
SITENAME = 'aogier'
SITEURL = ''

PATH = 'content'

TIMEZONE = 'Europe/Rome'

DEFAULT_LANG = 'it'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('Pelican', 'http://getpelican.com/'),
         ('Python.org', 'http://python.org/'),
         ('Jinja2', 'http://jinja.pocoo.org/'),
         ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

PLUGIN_PATHS = ['plugins', 'plugins_external']
PLUGINS = [
    'minify',
    'assets',
    'pelican-ipynb.markup',
    'extract_toc',
    'tipue_search'
]
DIRECT_TEMPLATES = ['index', 'tags', 'categories', 'authors', 'archives', 'search']

MINIFY = {
    'remove_comments': True,
    'remove_all_empty_space': True,
}

THEME = 'elegant'

IGNORE_FILES = [".ipynb_checkpoints"]

MARKUP = ('md', 'ipynb')

IPYNB_USE_METACELL = True

# CACHE_CONTENT = True
# LOAD_CONTENT_CACHE = True

CATEGORIES_URL = 'categories.html'
TAGS_URL = 'tags.html'
