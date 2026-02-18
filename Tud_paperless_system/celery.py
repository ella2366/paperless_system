import os
from celery import Celery

# I-set ang default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Tud_paperless_system.settings')

app = Celery('Tud_paperless_system')

# Basahin ang config mula sa settings.py gamit ang CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Kusa nitong hahanapin ang tasks.py sa loob ng iyong apps
app.autodiscover_tasks()