web: gunicorn --pythonpath="$PWD/instatool" config.wsgi:application
worker: python instatool/manage.py rqworker high default low
