import os
import sys
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cvbuilder.settings')

# Run migrations and create superuser on startup (for Render deployment)
if 'gunicorn' in sys.argv or 'runserver' not in sys.argv:
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'migrate', '--noinput'])
    
    # Create superuser if not exists
    from django.contrib.auth import get_user_model
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Superuser created: admin / admin123")

application = get_wsgi_application()
