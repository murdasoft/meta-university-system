import os
import sys
from django.core.wsgi import get_wsgi_application

# Add project root to sys.path
# This script is at /api/index.py, root is /
current_directory = os.path.dirname(os.path.abspath(__file__))
project_directory = os.path.join(os.path.dirname(current_directory), "django_project", "danadjango")

if project_directory not in sys.path:
    sys.path.insert(0, project_directory)

# Set settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "danadjango.settings")

# Expose 'app' for Vercel
try:
    app = get_wsgi_application()
except Exception as e:
    # Fallback to a simple error reporter if Django fails to load
    print(f"CRITICAL: Failed to load Django application: {e}")
    def app(environ, start_response):
        status = '500 Internal Server Error'
        output = f"Django initialization failed: {e}".encode()
        response_headers = [('Content-type', 'text/plain'), ('Content-Length', str(len(output)))]
        start_response(status, response_headers)
        return [output]
