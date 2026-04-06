import os
import sys
from django.core.wsgi import get_wsgi_application

# Robust path handling for Vercel
# Root is at base of repo. api/ is one level deep.
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_root = os.path.join(path, "django_project", "danadjango")

if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "danadjango.settings")

# Global 'app' object for Vercel scanner
app = get_wsgi_application()
