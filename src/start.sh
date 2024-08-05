#!/bin/bash
echo "migrations"
#python manage.py flush --no-input
python manage.py makemigrations
python manage.py migrate
echo "init"
python manage.py initapp
echo "collectstatic"
python manage.py collectstatic --no-input
echo "starting app"
uvicorn config.asgi:abcdjango --port 80 --host 0.0.0.0 --reload --reload-include '*.html'

# daphne config.asgi:abcdjango --port 80 --bind 0.0.0.0 -v2
# python manage.py addmod -a website -m default -f index