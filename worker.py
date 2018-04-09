
import os

import redis
from rq import Worker, Queue, Connection


listen = ['high', 'default', 'low']

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "baseapp.settings")
    import django
    django.setup()

    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
