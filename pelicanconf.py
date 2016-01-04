#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Aleksandr Sinayev'
SITENAME = u'Aleksandr Sinayev'
SITEURL = 'blog'
THEME = 'cait'

PATH = 'content'

TIMEZONE = 'EST'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('Pelican', 'http://getpelican.com/'),
         ('Python.org', 'http://python.org/'),
         ('Jinja2', 'http://jinja.pocoo.org/'))

# Social widget
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)

DEFAULT_PAGINATION = 5

USE_CUSTOM_MENU = True
CUSTOM_MENUITEMS = (('Blog', 'blog'),
             ('Contact', 'contact'),
             ('Projects', 'pages/projects'),
             ('About', 'about-me'))

STATIC_PATHS = ['blog', 'notblog']
ARTICLE_PATHS = ['blog', 'notblog']
#ARTICLE_SAVE_AS = '{date:%Y}/{slug}.html'
#ARTICLE_URL = '{date:%Y}/{slug}.html'

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True
#USE_FOLDER_AS_CATEGORY = True
