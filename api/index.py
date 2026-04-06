import os
import sys
from django.core.wsgi import get_wsgi_application

# api/index.py is in the api/ folder. We need to go up one level to reach the root.
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
project_path = os.path.join(root_path, "django_project", "danadjango")

# Add the project directory and the app directory to sys.path
sys.path.append(project_path)
sys.path.append(os.path.join(project_path, "danadjango"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "danadjango.settings")

application = get_wsgi_application()
app = application
