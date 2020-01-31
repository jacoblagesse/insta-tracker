web: gunicorn --pythonpath="$PWD/followtracker" config.wsgi:application
worker: python followtracker/manage.py rqworker high default low
