# -*- coding: utf-8 -*-
import os, sys
sys.path.insert(0, '/var/www/u1822157/data/www/voronezh.bsktaxi.ru/bsktaxi')
sys.path.insert(1, '/var/www/u1822157/data/www/voronezh.bsktaxi.ru/venv/lib/python3.9/site-packages')
os.environ['DJANGO_SETTINGS_MODULE'] = 'bsktaxi.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()