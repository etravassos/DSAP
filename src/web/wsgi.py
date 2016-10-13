"""
WSGI config for dsap project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

"""
Using WhiteNoise: self contained application. WhiteNoise should be able to handle
a very large amount of traffic running behind a CDN, otherwise look into nginx or apache
"""

from whitenoise.django import DjangoWhiteNoise
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.web.settings")

application = get_wsgi_application()
application = DjangoWhiteNoise(application)