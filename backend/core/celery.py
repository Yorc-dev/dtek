from __future__ import absolute_import
import os
from celery import Celery
from celery.schedules import crontab

# Задаем настройки для celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.accept_content = ('json', 'msgpack')
app.autodiscover_tasks()
app.conf.broker_connection_retry_on_startup = True

app.conf.beat_schedule = {
    # Каждые 6 часов: отправлять заявки без номера СЭД
    'enqueue-applications-without-sedo-code-every-6h': {
        'task': 'core.tasks.enqueue_applications_without_sedo_code',
        'schedule': crontab(minute=0, hour='*/6'),
    },
    # Каждый 1 час: генерировать документы для лицензий без документа
    'enqueue-licenses-without-document-every-1h': {
        'task': 'core.tasks.enqueue_licenses_without_document',
        'schedule': crontab(minute=0),
    },
}

@app.task(bind=True)
def debug_task(self):
    print("Request: {0!r}".format(self.request))