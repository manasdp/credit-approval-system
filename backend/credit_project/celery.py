# backend/credit_project/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'credit_project.settings')
app = Celery('credit_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()