from __future__ import absolute_import
import os
from celery import Celery

# Задаем настройки для celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.accept_content = ('json', 'msgpack')
app.autodiscover_tasks()
app.conf.broker_connection_retry_on_startup = True

@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))