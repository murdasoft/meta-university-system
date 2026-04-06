import os
import sys
from django.core.wsgi import get_wsgi_application

# Robust path handling for Vercel functions
# current_dir is /var/task/api
current_dir = os.path.dirname(os.path.abspath(__file__))
# root_dir is /var/task
root_dir = os.path.dirname(current_dir)
# project_dir is /var/task/django_project/danadjango
project_dir = os.path.join(root_dir, "django_project", "danadjango")

# Inject paths into sys.path
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Set settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "danadjango.settings")

# Try to get application
try:
    application = get_wsgi_application()
    app = application
except Exception as e:
    print(f"Error loading WSGI application: {e}")
    raise
