import os
import sys
from pathlib import Path

# Vercel imports this module from the repository root, while local Django
# commands run with `backend/` as the working directory. Ensure both contexts
# can resolve `config` and the project apps consistently.
BACKEND_DIR = str(Path(__file__).resolve().parent.parent)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()
