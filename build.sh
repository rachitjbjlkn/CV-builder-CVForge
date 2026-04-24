#!/bin/bash
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
python -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@cvbuilder.com', 'admin123')
    print('Superuser created')
else:
    print('Superuser already exists')
"