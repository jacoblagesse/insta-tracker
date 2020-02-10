release: python manage.py migrate
web: gunicorn instatool.wsgi
worker: python manage.py rqworker default
