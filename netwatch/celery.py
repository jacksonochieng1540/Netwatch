import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'netwatch.settings')
app = Celery('netwatch')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'poll-all-devices':  {'task': 'monitoring.tasks.poll_all_devices',  'schedule': 30.0},
    'evaluate-faults':   {'task': 'monitoring.tasks.evaluate_faults',   'schedule': 35.0},
    'cleanup-old-events':{'task': 'monitoring.tasks.cleanup_old_events','schedule': 3600.0},
}
