#!/bin/sh

sleep 1

export PYTHONPATH="/usr/src/app"
echo "PYTHONPATH set to $PYTHONPATH"

# python manage.py migrate

# python manage.py makemigrations

python manage.py migrate

# python manage.py create_default_admin
python manage.py collectstatic --no-input

# python manage.py loaddata fixtures/regions.json
# python manage.py loaddata fixtures/districts.json
# python manage.py loaddata fixtures/tik.json
# python manage.py loaddata fixtures/ethnicity.json



django-admin compilemessages -l en -l ru -l ky

gunicorn core.wsgi:application --bind 0.0.0.0:8000 --access-logfile - --reload -w 4 --timeout 1200