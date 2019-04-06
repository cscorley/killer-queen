web: gunicorn baseapp.wsgi --log-file -
worker: python worker.py
release: python manage.py migrate
