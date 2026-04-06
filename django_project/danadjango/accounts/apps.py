from django.apps import AppConfig
from django.contrib.auth.signals import user_logged_in

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        # Disconnect update_last_login signal because Vercel's SQLite is read-only
        try:
            from django.contrib.auth.models import update_last_login
            user_logged_in.disconnect(update_last_login)
        except ImportError:
            pass
