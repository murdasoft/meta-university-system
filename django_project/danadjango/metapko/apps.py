from django.apps import AppConfig


class MetapkoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'metapko'
    verbose_name = 'Meta-PKO (интеграции)'

    def ready(self):
        # Регистрация моделей на отдельном AdminSite
        import metapko.admin  # noqa: F401
