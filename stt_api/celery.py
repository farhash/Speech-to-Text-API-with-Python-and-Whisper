import os
from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stt_api.settings")
app = Celery("stt_api", broker=settings.CELERY_BROKER_URL)
app.conf.broker_connection_retry_on_startup = True
