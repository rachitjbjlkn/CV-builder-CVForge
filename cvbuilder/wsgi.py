import os
import sys
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cvbuilder.settings')

# For Render deployment - try migrations silently
if 'gunicorn' in sys.argv:
    try:
        from django.core.management import execute_from_command_line
        execute_from_command_line(['manage.py', 'migrate', '--run-syncdb', '--noinput'])
    except:
        pass  # Ignore errors - DB might already be set up

application = get_wsgi_application()