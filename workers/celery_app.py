from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

celery_app = Celery(
    'ocrengine',
    broker=redis_url,
    backend=redis_url,
    include=['workers.tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)
