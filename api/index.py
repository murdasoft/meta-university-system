import os
import sys
from django.core.wsgi import get_wsgi_application

# Add the nested django_project to the path
path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(path, "django_project/danadjango"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "danadjango.settings")

application = get_wsgi_application()
app = application
